---
name: git-co-change-graph
description: Build and incrementally maintain a file co-change coupling map from git history of raw/storepep-react. Files that frequently change together in the same commit are likely coupled even without direct imports — surfaces hidden blast-radius dependencies. Use when the user wants to initialise the coupling map, update it after submodule changes, or find co-change partners for a specific file before making a change.
argument-hint: init [--since <period>] [--threshold N] | delta | query <filepath>
allowed-tools: Bash, Read, Write, Edit
disable-model-invocation: false
---

# Git Co-Change Graph

Three modes:

| Mode | What it does |
|------|-------------|
| `init` | Process git history within `--since` window; create `coupling-data.json` and `coupling-map.md` from scratch |
| `delta` | Process only new commits since last `git_reference`; merge into JSON store; regenerate summary page |
| `query` | Look up a specific file in the JSON store and report its top co-change partners. No writes. |

## Dispatch

Parse `$ARGUMENTS` first token:

| First token | Mode |
|-------------|------|
| `init` | Init |
| `delta` | Delta |
| `query` | Query |
| missing / other | Ask: "Did you mean `init` (first time), `delta` (incremental update), or `query <filepath>` (blast-radius lookup)?" |

---

## Output Files

| File | Purpose | Committed? |
|------|---------|------------|
| `.claude/cache/coupling-data.json` | Full raw pair counts — machine-readable store | No — gitignored cache |
| `wiki/architecture/coupling-map.md` | Human summary: top pairs + domain tables | Yes |

The markdown page is always **generated from** the JSON. It is never the source of truth for counts.

---

## Constants

```python
SOURCE_PATH      = "raw/storepep-react"
DATA_FILE        = ".claude/cache/coupling-data.json"
WIKI_PAGE        = "wiki/architecture/coupling-map.md"
DEFAULT_THRESHOLD = 3          # min co-changes to appear in summary tables
DEFAULT_SINCE    = "6 months ago"
MAX_COMMIT_FILES = 30          # skip commits touching more files than this (mass reformats)

EXCLUDE_PATTERNS = [
    "package-lock.json", "yarn.lock",
    ".min.js", "/dist/", "/build/",
    "migrations/",          # DB migrations — always batch-changed
    ".test.js", ".test.ts", ".spec.js", ".spec.ts", "__snapshots__/",
    ".md", "CHANGELOG",
]

# Domain classification — first matching prefix wins
DOMAIN_MAP = [
    ("server/src/shared/API/carriers/",  "carriers"),
    ("server/src/shared/orders/",        "orders"),
    ("server/src/shared/",               "shared"),
    ("server/src/routes/",               "routes"),
    ("server/src/models/",               "models"),
    ("client/src/actions/",              "redux-actions"),
    ("client/src/reducers/",             "redux-reducers"),
    ("client/src/components/",           "ui-components"),
    ("client/src/",                      "client"),
    ("server/",                          "server"),
]

DOMAIN_ORDER = [
    "cross-domain", "carriers", "orders", "shared", "routes", "models",
    "redux-actions", "redux-reducers", "ui-components", "client", "server", "other",
]
```

---

## Step 1 — Parse arguments

```python
tokens = $ARGUMENTS.split()
mode  = tokens[0] if tokens else None

# init flags
since     = DEFAULT_SINCE
threshold = DEFAULT_THRESHOLD

if "--since" in tokens:
    i = tokens.index("--since")
    since = tokens[i + 1]          # e.g. "6 months ago", "1 year ago", "2024-01-01"

if "--threshold" in tokens:
    i = tokens.index("--threshold")
    threshold = int(tokens[i + 1])

# query target
query_file = " ".join(tokens[1:]) if mode == "query" else None
```

`--since` accepts any value git understands: `"6 months ago"`, `"1 year ago"`, `"90 days ago"`, `"2024-01-01"`.

---

## Step 2 — Precondition checks (init and delta)

```bash
# Submodule must be checked out
[ -d raw/storepep-react/.git ] || {
  echo "ERROR: raw/storepep-react not checked out."
  echo "Run: git submodule update --init raw/storepep-react"
  exit 1
}

CURRENT_REF=$(git -C raw/storepep-react rev-parse HEAD)
```

**Init only** — if `wiki/architecture/coupling-map.md` already exists, confirm before overwriting:
```
⚠️  coupling-map.md already exists (git_reference: <ref>, since: <window>).
    init will rebuild from scratch. Use `delta` to add only new commits. Proceed? [y/N]
```

**Delta only** — read stored state from frontmatter:
```bash
PRIOR_REF=$(yq eval '.git_reference' wiki/architecture/coupling-map.md)
threshold=$(yq eval '.threshold'     wiki/architecture/coupling-map.md)
since=$(yq eval '.since_window'      wiki/architecture/coupling-map.md)
```

If `coupling-map.md` missing → hard error: `Run /git-co-change-graph init first.`

If `PRIOR_REF == CURRENT_REF` → print `No new commits since <short_ref>. Nothing to do.` and exit.

If `PRIOR_REF` not in history → warn, fall back to `HEAD~50` as prior ref, note in report.

**Cold-start recovery (delta only)** — if `coupling-map.md` exists but `.claude/cache/coupling-data.json` is missing (e.g. fresh clone, gitignored cache was lost):
- Rebuild the JSON store from full `--since` window before applying the delta:
  ```
  ℹ️  coupling-data.json not found. Rebuilding store from last <since_window> window first.
  ```
  Run Steps 3–5 (init path) using the stored `since_window`, then continue with the delta on top.

---

## Step 3 — Extract commit→file data

Run via Bash. Outputs `<hash>\t<filepath>` lines to `/tmp/ccg_raw.tsv`.

```bash
python3 << 'PYEOF'
import subprocess, sys

source   = "raw/storepep-react"
mode     = sys.argv[1]   # "init" or "delta"
range_arg = sys.argv[2]  # since-string (init) or "PRIOR..CURRENT" (delta)

cmd = ["git", "-C", source, "log",
       "--pretty=format:COMMIT %H",
       "--name-only",
       "--diff-filter=ACDMR"]

if mode == "init":
    cmd += ["--since", range_arg]
else:
    cmd.append(range_arg)   # "PRIOR_REF..CURRENT_REF"

result = subprocess.run(cmd, capture_output=True, text=True)

current = None
for line in result.stdout.splitlines():
    line = line.strip()
    if line.startswith("COMMIT "):
        current = line[7:]
    elif line and current:
        print(f"{current}\t{line}")
PYEOF
```

- Init call:  `python3 ... init "6 months ago"`
- Delta call: `python3 ... delta "PRIOR_REF..CURRENT_REF"`

---

## Step 4 — Count co-change pairs

Reads `/tmp/ccg_raw.tsv`, writes to `/tmp/ccg_pairs.tsv`.

```bash
python3 << 'PYEOF'
import sys
from collections import defaultdict
from itertools import combinations

EXCLUDE = [
    "package-lock.json", "yarn.lock", ".min.js", "/dist/", "/build/",
    "migrations/", ".test.js", ".test.ts", ".spec.js", ".spec.ts",
    "__snapshots__/", ".md", "CHANGELOG",
]
MAX_FILES = 30

def excluded(p):
    return any(x in p for x in EXCLUDE)

commit_files = defaultdict(list)
with open("/tmp/ccg_raw.tsv") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t", 1)
        if len(parts) == 2 and not excluded(parts[1]):
            commit_files[parts[0]].append(parts[1])

counts = defaultdict(int)
used = skipped = 0
for files in commit_files.values():
    files = sorted(set(files))
    if len(files) < 2:       continue
    if len(files) > MAX_FILES: skipped += 1; continue
    used += 1
    for a, b in combinations(files, 2):
        counts[(a, b)] += 1

for (a, b), n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{n}\t{a}\t{b}")

print(f"commits={used} skipped={skipped} pairs={len(counts)}", file=sys.stderr)
PYEOF
```

Capture the stderr line for the report. Working pairs are in `/tmp/ccg_pairs.tsv`.

---

## Step 5 — Build / merge JSON store

### Init

Reads `/tmp/ccg_pairs.tsv`, writes `.claude/cache/coupling-data.json` from scratch.

```bash
mkdir -p .claude/cache

python3 << 'PYEOF'
import json

store = {}
with open("/tmp/ccg_pairs.tsv") as f:
    for line in f:
        parts = line.strip().split("\t", 2)
        if len(parts) == 3:
            store[f"{parts[1]}|{parts[2]}"] = int(parts[0])

with open(".claude/cache/coupling-data.json", "w") as f:
    json.dump(store, f, separators=(",", ":"))

print(f"store_size={len(store)}")
PYEOF
```

### Delta

Reads existing `.claude/cache/coupling-data.json`, merges delta counts in, writes back.

```bash
python3 << 'PYEOF'
import json

with open(".claude/cache/coupling-data.json") as f:
    store = json.load(f)

delta = {}
with open("/tmp/ccg_pairs.tsv") as f:
    for line in f:
        parts = line.strip().split("\t", 2)
        if len(parts) == 3:
            delta[f"{parts[1]}|{parts[2]}"] = int(parts[0])

new_keys = sum(1 for k in delta if k not in store)
for key, count in delta.items():
    store[key] = store.get(key, 0) + count

with open(".claude/cache/coupling-data.json", "w") as f:
    json.dump(store, f, separators=(",", ":"))

print(f"store={len(store)} new_pairs={new_keys}")
PYEOF
```

---

## Step 6 — Generate summary page

Reads `.claude/cache/coupling-data.json`, writes `wiki/architecture/coupling-map.md`.

```bash
python3 << 'PYEOF'
import json, sys
from collections import defaultdict
from datetime import date

DOMAIN_MAP = [
    ("server/src/shared/API/carriers/",  "carriers"),
    ("server/src/shared/orders/",        "orders"),
    ("server/src/shared/",               "shared"),
    ("server/src/routes/",               "routes"),
    ("server/src/models/",               "models"),
    ("client/src/actions/",              "redux-actions"),
    ("client/src/reducers/",             "redux-reducers"),
    ("client/src/components/",           "ui-components"),
    ("client/src/",                      "client"),
    ("server/",                          "server"),
]
DOMAIN_ORDER = [
    "cross-domain", "carriers", "orders", "shared", "routes", "models",
    "redux-actions", "redux-reducers", "ui-components", "client", "server", "other",
]

def classify(p):
    for prefix, domain in DOMAIN_MAP:
        if p.startswith(prefix): return domain
    return "other"

threshold    = int(sys.argv[1])
current_ref  = sys.argv[2]
since_window = sys.argv[3]
commits      = sys.argv[4]
today        = date.today().isoformat()
short_ref    = current_ref[:8]

with open(".claude/cache/coupling-data.json") as f:
    store = json.load(f)

pairs = []
for key, count in store.items():
    if count < threshold: continue
    a, b = key.split("|", 1)
    da, db = classify(a), classify(b)
    domain = da if da == db else "cross-domain"
    pairs.append((count, a, b, domain))
pairs.sort(reverse=True)

by_domain = defaultdict(list)
for item in pairs:
    by_domain[item[3]].append(item)

out = []
out.append(f"""---
title: File Co-Change Coupling Map
category: architecture
sources: [storepep-react]
status: complete
last_updated: {today}
git_reference: {current_ref}
since_window: "{since_window}"
commits_analyzed: {commits}
pairs_above_threshold: {len(pairs)}
threshold: {threshold}
---

# File Co-Change Coupling Map

Files that frequently appear in the same commit are likely coupled — changing one
probably requires reviewing the others. Generated from `raw/storepep-react` git history.

**Window**: last {since_window} · **Commits**: {commits} · **Threshold**: ≥{threshold} · **Pairs**: {len(pairs)}
**Last updated**: {today} @ `{short_ref}`

## How to Use

To find blast-radius partners for a specific file before making a change:
```
/git-co-change-graph query server/src/routes/orders.js
```

> Commits touching >{30} files are excluded (mass reformats). Test files, lock files, and migrations are also excluded.

---

## Top Coupled Pairs

| # | Co-changes | File A | File B | Domain |
|---|------------|--------|--------|--------|
""")

for i, (count, a, b, domain) in enumerate(pairs[:50], 1):
    out.append(f"| {i} | {count} | `{a}` | `{b}` | {domain} |\n")

out.append("\n---\n\n## By Domain\n\n")
out.append("> **Cross-domain** pairs have the largest blast radius.\n\n")

for domain in DOMAIN_ORDER:
    dp = by_domain.get(domain)
    if not dp: continue
    out.append(f"### {domain.title()} ({len(dp)} pairs)\n\n")
    out.append("| Co-changes | File A | File B |\n|------------|--------|--------|\n")
    for count, a, b, _ in dp[:20]:
        out.append(f"| {count} | `{a}` | `{b}` |\n")
    if len(dp) > 20:
        out.append(f"\n_...and {len(dp) - 20} more. Run `query` for the full list._\n")
    out.append("\n")

out.append("""---

## Noise Filter

| Excluded | Reason |
|----------|--------|
| `package-lock.json`, `yarn.lock` | Changed in nearly every dependency update |
| `migrations/` | One-off batch additions — not structural coupling |
| `*.test.js`, `*.spec.ts` | Mirror their source file |
| `/dist/`, `/build/` | Generated files |
| `*.md`, `CHANGELOG` | Changed opportunistically in PRs |
| Commits touching >30 files | Mass reformats / lint sweeps |

---

## Related

- [Features & Test Coverage](../features.md)
- [Architecture Overview](overview.md)
- [Backend Architecture](backend-architecture.md)
""")

import os
os.makedirs("wiki/architecture", exist_ok=True)
with open("wiki/architecture/coupling-map.md", "w") as f:
    f.writelines(out)

print(f"wrote coupling-map.md: {len(pairs)} pairs above threshold")
PYEOF
```

Call as: `python3 ... <threshold> <CURRENT_REF> "<since_window>" <commits_analyzed>`

---

## Step 6b — Query mode

No writes. Reads `.claude/cache/coupling-data.json` and reports top partners.

```bash
python3 << 'PYEOF'
import json, sys

query = sys.argv[1]

with open(".claude/cache/coupling-data.json") as f:
    store = json.load(f)

results = []
for key, count in store.items():
    a, b = key.split("|", 1)
    if a == query:   results.append((count, b))
    elif b == query: results.append((count, a))

results.sort(reverse=True)

if not results:
    print(f"No co-change partners found for: {query}")
    print("Check path is relative to storepep-react root (e.g. server/src/routes/orders.js)")
    sys.exit(0)

print(f"\nCo-change partners for: {query}\n")
print(f"  {'Count':>6}  File")
print(f"  {'-'*60}")
for count, partner in results[:20]:
    print(f"  {count:>6}×  {partner}")
if len(results) > 20:
    print(f"\n  ...and {len(results) - 20} more")
PYEOF
```

Present the output with a note:
> These files changed in the same commit as `<query_file>` most often. Add them to your review scope and check for affected tests in [features.md](../features.md).

---

## Step 7 — Update index and log (init and delta only)

### `wiki/index.md`

Add under `## Architecture` if not already present:
```markdown
- [File Co-Change Coupling Map](architecture/coupling-map.md) — Files that frequently change together; blast-radius reference for planned changes
```

### `wiki/log.md`

```markdown
## [<YYYY-MM-DD HH:MM>] <init|delta> | Co-Change Coupling Map
- Mode: <init (since: <window>) | delta (N new commits)>
- Source: `raw/storepep-react` @ `<CURRENT_REF>`
- Prior ref: `<PRIOR_REF>` (delta only)
- Commits analyzed: N (N skipped — >30 files)
- Pairs above threshold (≥N): N
- Written: `wiki/architecture/coupling-map.md`
- Summary: <one-liner, e.g. "Top coupling: orders.js ↔ OrderProcessingService.js (47×)">
```

---

## Step 8 — Report to user

```
## Git Co-Change Graph — <init|delta>

Source : raw/storepep-react @ <short_ref>
Window : last <since>
Commits: N analyzed, N skipped (>30 files)
Store  : N total pairs  →  N above threshold (≥N)

Top 5:
  47×  server/src/routes/orders.js  ↔  server/src/services/OrderProcessingService.js  [orders]
  31×  client/src/actions/labelActions.js  ↔  client/src/reducers/labelReducer.js     [redux-actions]
  ...

Cache : .claude/cache/coupling-data.json
Page  : wiki/architecture/coupling-map.md
```

---

## Error Handling

| Case | Action |
|------|--------|
| `init` on existing files | Confirm before overwriting |
| `delta` with no `coupling-map.md` | Hard error: run `init` first |
| `delta` with missing `coupling-data.json` | Rebuild store from `since_window`, then apply delta |
| `PRIOR_REF` not in git history | Warn; fall back to `HEAD~50`; note in report |
| `PRIOR_REF == CURRENT_REF` | "Nothing to do" — exit cleanly |
| Zero pairs above threshold | Warn: try `--threshold 1` or verify submodule has commits |
| Submodule not checked out | Hard error with `git submodule update --init` instruction |
| `coupling-data.json` unparseable | Hard error: delete it and re-run `init` |
| `query` file not found in store | Report with path-format hint |
| `python3` not available | Hard error |
