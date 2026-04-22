---
name: zendesk-overlap
description: Build a ZI issue area co-occurrence map to surface coupling between feature areas in customer-reported failures, cross-referenced against the code co-change graph. Files that break together in tickets are likely coupled in code even without a direct import.
argument-hint: [build|delta|query <area>]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, TodoWrite
disable-model-invocation: false
---

# Zendesk Area Overlap

Builds an area co-occurrence matrix from ZI issues, then cross-references it against `wiki/architecture/coupling-map.md` to confirm whether areas that co-fail in customer reports are also coupled in the code commit graph.

**The insight**: the code coupling map shows what changes together. This skill shows what *breaks together* in user reports. Together they give a complete blast-radius picture.

## Modes

| Mode | What it does |
|------|-------------|
| `build` | Full rebuild from current daily index + backlog + coupling-map |
| `delta` | Update from ZI issues added since `git_reference` in `area-coupling.md` frontmatter |
| `query <area>` | Print co-occurring areas for a given area. No writes. |

**Default** (no args): `build`

## Dispatch

Parse `$ARGUMENTS` first token:

| First token | Mode |
|-------------|------|
| `build` | Build |
| `delta` | Delta |
| `query` | Query — remainder is the area name |
| missing | Build |
| other | Ask: "Did you mean `build` (full rebuild), `delta` (incremental update), or `query <area>` (blast-radius lookup)?" |

---

## Output Files

| File | Purpose | Committed? |
|------|---------|------------|
| `.claude/cache/zendesk-overlap-data.json` | Full co-occurrence counts — machine-readable store | No — gitignored cache |
| `wiki/zendesk/area-coupling.md` | Human summary: area pairs + blast-radius table | Yes |

The markdown page is always **generated from** the JSON. It is never the source of truth for counts.

---

## Constants

```python
DAILY_INDEX_DIR  = "wiki/zendesk"
BACKLOG_FILE     = "wiki/product/backlog.md"
COUPLING_MAP     = "wiki/architecture/coupling-map.md"
DATA_FILE        = ".claude/cache/zendesk-overlap-data.json"
WIKI_PAGE        = "wiki/zendesk/area-coupling.md"
MIN_TICKET_PAIRS = 2   # minimum ticket co-occurrences to appear in output
MIN_CLUSTER_PAIRS = 1  # minimum cluster co-occurrences to appear in output

# Mapping from ZI feature area → code domains in coupling-map.md
# Used to cross-reference ticket co-failures with code co-changes
AREA_TO_DOMAIN = {
    "carrier-config":      ["carriers"],
    "carrier-migration":   ["carriers"],
    "rate-shopping":       ["carriers", "orders"],
    "label-generation":    ["orders", "shared"],
    "international":       ["carriers", "orders"],
    "order-management":    ["orders", "routes"],
    "product-management":  ["shared", "models"],
    "tracking":            ["orders", "shared"],
    "returns":             ["orders", "carriers"],
    "onboarding":          ["client"],
    "feature-request":     [],   # not mappable to a single domain
    "other":               [],
}
```

---

## Step 1 — Resolve daily index

Find the most recent `wiki/zendesk/YYYY-MM-DD.md` file:

```bash
python3 << 'PYEOF'
import os, re, sys

index_dir = "wiki/zendesk"
files = [f for f in os.listdir(index_dir) if re.match(r'\d{4}-\d{2}-\d{2}\.md', f)]
if not files:
    print("ERROR: No daily index found in wiki/zendesk/", file=sys.stderr)
    sys.exit(1)
latest = sorted(files)[-1]
print(os.path.join(index_dir, latest))
PYEOF
```

Store the result as `INDEX_FILE`. If missing → hard error: `Run /zendesk-summarize first to create the daily index.`

**Delta only** — read `git_reference` from `wiki/zendesk/area-coupling.md` frontmatter. If `area-coupling.md` missing → fall back to `build` mode and note it.

---

## Step 2 — Parse ZI issues from daily index

```bash
python3 << 'PYEOF'
import re, json, sys

index_file = sys.argv[1]

# Parse the Issue Index table
# Columns: | ID | Issue | Ticket | Product | Area |
issues = []
in_table = False
with open(index_file) as f:
    for line in f:
        line = line.strip()
        if line.startswith("| ID |") and "Issue" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 5:
                zi_id   = cols[0].strip()
                title   = cols[1].strip()
                # Extract ticket ID from markdown link e.g. [218195](summaries/218195.md)
                ticket_match = re.search(r'\[(\d+)\]', cols[2])
                ticket_id = ticket_match.group(1) if ticket_match else cols[2].strip()
                product = cols[3].strip()
                area    = cols[4].strip()
                # Normalise compound areas like "carrier-config / feature-request"
                # Split on " / " and take the first tag as primary, rest as secondary
                area_parts = [a.strip() for a in re.split(r'\s*/\s*', area)]
                primary_area = area_parts[0]
                # Strip parenthetical qualifiers e.g. "onboarding (account / billing)" → "onboarding"
                primary_area = re.sub(r'\s*\(.*?\)', '', primary_area).strip()
                issues.append({
                    "zi_id": zi_id,
                    "title": title,
                    "ticket_id": ticket_id,
                    "product": product,
                    "area": primary_area,
                    "area_raw": area,
                })
        elif in_table and not line.startswith("|"):
            in_table = False

print(json.dumps(issues))
PYEOF
```

Call as: `python3 ... <INDEX_FILE>`

---

## Step 3 — Build co-occurrence matrix

### 3a — Within-ticket pairs (primary signal)

```bash
python3 << 'PYEOF'
import json, sys
from collections import defaultdict
from itertools import combinations

issues = json.loads(sys.argv[1])

# Group by ticket
by_ticket = defaultdict(list)
for issue in issues:
    by_ticket[issue["ticket_id"]].append(issue)

ticket_pairs = {}   # "area_a|area_b" → {count, tickets, zi_ids}

for ticket_id, ticket_issues in by_ticket.items():
    areas = sorted(set(i["area"] for i in ticket_issues))
    if len(areas) < 2:
        continue
    for a, b in combinations(areas, 2):
        key = f"{a}|{b}"
        if key not in ticket_pairs:
            ticket_pairs[key] = {"count": 0, "tickets": [], "zi_ids": []}
        ticket_pairs[key]["count"] += 1
        if ticket_id not in ticket_pairs[key]["tickets"]:
            ticket_pairs[key]["tickets"].append(ticket_id)
        for i in ticket_issues:
            if i["area"] in (a, b) and i["zi_id"] not in ticket_pairs[key]["zi_ids"]:
                ticket_pairs[key]["zi_ids"].append(i["zi_id"])

print(json.dumps(ticket_pairs))
PYEOF
```

### 3b — Within-cluster pairs (secondary signal)

```bash
python3 << 'PYEOF'
import re, json, sys
from collections import defaultdict
from itertools import combinations

issues_json = sys.argv[1]   # all ZI issues as JSON
backlog_file = sys.argv[2]

issues = json.loads(issues_json)
zi_area = {i["zi_id"]: i["area"] for i in issues}

# Parse backlog cluster detail tables
# Each cluster starts with "#### #N <cluster name>" and contains
# a table with ZI | Title | Ticket | Area columns
cluster_pairs = {}

current_cluster = None
in_table = False

with open(backlog_file) as f:
    for line in f:
        line = line.rstrip()
        m = re.match(r'^#### #\d+ (.+?) \(', line)
        if m:
            current_cluster = m.group(1).strip()
            in_table = False
            current_zis = []
            continue
        if current_cluster and line.startswith("| ZI |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if cols and cols[0].startswith("ZI-"):
                current_zis.append(cols[0])
        elif in_table and current_cluster:
            # End of table — compute area pairs for this cluster
            areas = sorted(set(zi_area.get(zi, "other") for zi in current_zis))
            for a, b in combinations(areas, 2):
                key = f"{a}|{b}"
                if key not in cluster_pairs:
                    cluster_pairs[key] = {"clusters": [], "zi_ids": []}
                if current_cluster not in cluster_pairs[key]["clusters"]:
                    cluster_pairs[key]["clusters"].append(current_cluster)
                for zi in current_zis:
                    if zi_area.get(zi) in (a, b) and zi not in cluster_pairs[key]["zi_ids"]:
                        cluster_pairs[key]["zi_ids"].append(zi)
            in_table = False

print(json.dumps(cluster_pairs))
PYEOF
```

Call as: `python3 ... '<issues_json>' <BACKLOG_FILE>`

---

## Step 4 — Parse coupling-map.md (always run)

Read `wiki/architecture/coupling-map.md` to extract co-change counts by domain pair. This is used to cross-reference ZI area pairs against code-level coupling.

```bash
python3 << 'PYEOF'
import re, json, sys
from collections import defaultdict

coupling_file = sys.argv[1]

DOMAIN_MAP = [
    ("server/src/shared/API/carriers/", "carriers"),
    ("server/src/shared/orders/",       "orders"),
    ("server/src/shared/",              "shared"),
    ("server/src/routes/",              "routes"),
    ("server/src/models/",              "models"),
    ("client/src/actions/",             "redux-actions"),
    ("client/src/reducers/",            "redux-reducers"),
    ("client/src/components/",          "ui-components"),
    ("client/src/",                     "client"),
    ("server/",                         "server"),
]

def classify(p):
    for prefix, domain in DOMAIN_MAP:
        if p.startswith(prefix): return domain
    return "other"

# Tally co-change counts by domain pair from the Top Coupled Pairs table
domain_pair_counts = defaultdict(int)
in_table = False

with open(coupling_file) as f:
    for line in f:
        line = line.strip()
        if line.startswith("| # |") and "Co-changes" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            # Format: | N | count | `fileA` | `fileB` | domain |
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 4:
                try:
                    count = int(cols[1])
                except ValueError:
                    continue
                file_a = cols[2].strip("`")
                file_b = cols[3].strip("`")
                da = classify(file_a)
                db = classify(file_b)
                pair = "|".join(sorted([da, db]))
                domain_pair_counts[pair] += count
        elif in_table and not line.startswith("|"):
            in_table = False

print(json.dumps(dict(domain_pair_counts)))
PYEOF
```

Call as: `python3 ... <COUPLING_MAP>`

Store as `domain_pair_counts`. Used in Step 5 to annotate area pairs.

---

## Step 5 — Build JSON store

```bash
python3 << 'PYEOF'
import json, sys, os
from datetime import date

ticket_pairs    = json.loads(sys.argv[1])
cluster_pairs   = json.loads(sys.argv[2])
domain_counts   = json.loads(sys.argv[3])
git_ref         = sys.argv[4]
zi_count        = int(sys.argv[5])
ticket_count    = int(sys.argv[6])

AREA_TO_DOMAIN = {
    "carrier-config":    ["carriers"],
    "carrier-migration": ["carriers"],
    "rate-shopping":     ["carriers", "orders"],
    "label-generation":  ["orders", "shared"],
    "international":     ["carriers", "orders"],
    "order-management":  ["orders", "routes"],
    "product-management":["shared", "models"],
    "tracking":          ["orders", "shared"],
    "returns":           ["orders", "carriers"],
    "onboarding":        ["client"],
    "feature-request":   [],
    "other":             [],
}

def code_signal(area_a, area_b):
    """Compute total co-change count for all domain-pair combinations of two areas."""
    domains_a = AREA_TO_DOMAIN.get(area_a, [])
    domains_b = AREA_TO_DOMAIN.get(area_b, [])
    total = 0
    pairs = set()
    for da in domains_a:
        for db in domains_b:
            if da == db:
                continue
            key = "|".join(sorted([da, db]))
            pairs.add(key)
            total += domain_counts.get(key, 0)
    return {"total_co_changes": total, "domain_pairs": sorted(pairs)}

# Annotate ticket_pairs with code signal
for key, data in ticket_pairs.items():
    a, b = key.split("|", 1)
    data["code_signal"] = code_signal(a, b)

store = {
    "generated": date.today().isoformat(),
    "git_reference": git_ref,
    "tickets_analyzed": ticket_count,
    "zi_issues_analyzed": zi_count,
    "ticket_pairs": ticket_pairs,
    "cluster_pairs": cluster_pairs,
}

os.makedirs(".claude/cache", exist_ok=True)
with open(".claude/cache/zendesk-overlap-data.json", "w") as f:
    json.dump(store, f, indent=2)

print(f"store written: {len(ticket_pairs)} ticket-pairs, {len(cluster_pairs)} cluster-pairs")
PYEOF
```

Call as: `python3 ... '<ticket_pairs_json>' '<cluster_pairs_json>' '<domain_counts_json>' <GIT_REF> <ZI_COUNT> <TICKET_COUNT>`

**Delta mode**: Load existing `.claude/cache/zendesk-overlap-data.json`, merge new ticket_pairs counts in (add to existing counts), then re-run Steps 4–5 to refresh code signal with latest coupling-map.

---

## Step 6 — Generate `wiki/zendesk/area-coupling.md`

```bash
python3 << 'PYEOF'
import json, sys
from datetime import date

with open(".claude/cache/zendesk-overlap-data.json") as f:
    store = json.load(f)

today           = date.today().isoformat()
git_ref         = store["git_reference"]
tickets_analyzed = store["tickets_analyzed"]
zi_analyzed     = store["zi_issues_analyzed"]
ticket_pairs    = store["ticket_pairs"]
cluster_pairs   = store["cluster_pairs"]

MIN_TICKET = 2
MIN_CLUSTER = 1

def strength(count):
    if count >= 8: return "🔴 Strong"
    if count >= 4: return "🟡 Medium"
    return "🟢 Weak"

# Sort ticket pairs by count desc
sorted_tpairs = sorted(
    [(k, v) for k, v in ticket_pairs.items() if v["count"] >= MIN_TICKET],
    key=lambda x: -x[1]["count"]
)

# Sort cluster pairs by cluster count desc
sorted_cpairs = sorted(
    [(k, v) for k, v in cluster_pairs.items() if len(v["clusters"]) >= MIN_CLUSTER],
    key=lambda x: -len(x[1]["clusters"])
)

# Build blast-radius lookup (per area, what co-occurs)
from collections import defaultdict
blast = defaultdict(list)
for key, data in sorted_tpairs:
    a, b = key.split("|", 1)
    cs = data["code_signal"]
    code_note = f"{cs['total_co_changes']} code co-changes ({', '.join(cs['domain_pairs'])})" if cs["total_co_changes"] else "no code overlap detected"
    blast[a].append((b, data["count"], code_note))
    blast[b].append((a, data["count"], code_note))

lines = []
lines.append(f"""---
title: "ZI Area Coupling Map"
category: support
sources: [zendesk, storepep-react]
status: complete
last_updated: {today}
git_reference: {git_ref}
tickets_analyzed: {tickets_analyzed}
zi_issues_analyzed: {zi_analyzed}
---

# ZI Area Coupling Map

Areas that co-appear in the same Zendesk ticket or backlog cluster signal coupled surfaces in user-reported failures — even if no direct import exists between them. Code co-change counts from [`coupling-map.md`](../architecture/coupling-map.md) confirm whether the coupling is also visible in git history.

**Tickets analyzed**: {tickets_analyzed} | **ZI issues**: {zi_analyzed} | **As of**: {today}

---

## Area Co-Occurrence (by ticket)

Pairs ranked by frequency. Threshold: ≥{MIN_TICKET} co-occurring tickets.

| Pair | Co-Occurrences | Strength | Code Co-Changes | Sample Tickets | Sample ZIs |
|------|----------------|----------|-----------------|----------------|-----------|
""")

for key, data in sorted_tpairs:
    a, b = key.split("|", 1)
    cs = data["code_signal"]
    code_str = f"{cs['total_co_changes']} ({', '.join(cs['domain_pairs'])})" if cs["total_co_changes"] else "—"
    tickets_str = ", ".join(f"#{t}" for t in data["tickets"][:3])
    zi_str = ", ".join(data["zi_ids"][:3])
    if len(data["tickets"]) > 3:
        tickets_str += f" +{len(data['tickets'])-3}"
    lines.append(f"| {a} ↔ {b} | {data['count']} | {strength(data['count'])} | {code_str} | {tickets_str} | {zi_str} |\n")

lines.append(f"""
---

## Area Overlap by Backlog Cluster

Which areas appear together in the same cluster — indicates the engineering footprint spans both surfaces.

| Backlog Item | Areas in Cluster | ZI Count |
|---|---|---|
""")

for key, data in sorted_cpairs:
    a, b = key.split("|", 1)
    clusters_str = "; ".join(data["clusters"])
    zi_count = len(data["zi_ids"])
    lines.append(f"| {clusters_str} | {a}, {b} | {zi_count} |\n")

lines.append(f"""
---

## Blast-Radius Lookup

> If your card touches area X, also review area Y.

| If you touch… | Also check… | Evidence | Code co-changes |
|---|---|---|---|
""")

for area in sorted(blast.keys()):
    for partner, count, code_note in sorted(blast[area], key=lambda x: -x[1]):
        lines.append(f"| {area} | {partner} | {strength(count)} ({count} tickets) | {code_note} |\n")

lines.append(f"""
---

## How to Read This

- **Co-Occurrences**: how many Zendesk tickets had open issues in *both* areas simultaneously
- **Code Co-Changes**: from [`coupling-map.md`](../architecture/coupling-map.md) — total co-change weight across the relevant code domains for that area pair. High = confirmed code coupling.
- **Strength**: 🔴 Strong ≥8 tickets · 🟡 Medium 4-7 · 🟢 Weak 2-3
- **A pair with high ticket co-occurrence AND high code co-changes** is a blast-radius risk: changes in one area almost certainly require reviewing the other.

---

## Related

- [Backlog](../product/backlog.md)
- [Code Co-Change Coupling Map](../architecture/coupling-map.md)
- [Daily ZI Index](./{ sorted([f for f in __import__('os').listdir('wiki/zendesk') if f[:4].isdigit()])[-1] if False else '2026-04-20.md' })
""")

import os
os.makedirs("wiki/zendesk", exist_ok=True)
with open("wiki/zendesk/area-coupling.md", "w") as f:
    f.writelines(lines)

print(f"wrote area-coupling.md: {len(sorted_tpairs)} ticket-pairs, {len(sorted_cpairs)} cluster-pairs")
PYEOF
```

**Note on the "Related" daily index link**: resolve the most recent `wiki/zendesk/YYYY-MM-DD.md` filename dynamically (same as Step 1) and embed it in the "Related" section.

---

## Step 6b — Query mode

No writes. Reads `.claude/cache/zendesk-overlap-data.json`.

```bash
python3 << 'PYEOF'
import json, sys

query = sys.argv[1].strip().lower()

try:
    with open(".claude/cache/zendesk-overlap-data.json") as f:
        store = json.load(f)
except FileNotFoundError:
    print("No cache found. Run /zendesk-overlap build first.")
    sys.exit(1)

ticket_pairs = store["ticket_pairs"]

results = []
for key, data in ticket_pairs.items():
    a, b = key.split("|", 1)
    if a == query:
        results.append((data["count"], b, data))
    elif b == query:
        results.append((data["count"], a, data))

results.sort(reverse=True)

if not results:
    print(f"No co-occurring areas found for: {query}")
    print(f"Known areas: {sorted(set(k.split('|')[0] for k in ticket_pairs) | set(k.split('|')[1] for k in ticket_pairs))}")
    sys.exit(0)

print(f"\nAreas that co-occur with '{query}' in the same ticket:\n")
print(f"  {'Count':>6}  {'Area':<25}  Code co-changes")
print(f"  {'-'*65}")
for count, partner, data in results:
    cs = data["code_signal"]
    code_str = f"{cs['total_co_changes']} ({', '.join(cs['domain_pairs'])})" if cs["total_co_changes"] else "no code overlap"
    print(f"  {count:>6}×  {partner:<25}  {code_str}")
PYEOF
```

Present the output with a note:
> These areas co-appeared in the same Zendesk ticket as `<query>`. If you're working on `<query>`, check these areas too — and see [`coupling-map.md`](wiki/architecture/coupling-map.md) for the file-level blast radius.

---

## Step 7 — Update index and log (build and delta only)

### `wiki/index.md`

Add under `## Zendesk` (or create the section) if not already present:
```markdown
- [Area Coupling Map](zendesk/area-coupling.md) — ZI area co-occurrence map; blast-radius reference cross-referenced against code coupling
```

### `wiki/log.md`

```markdown
## [<YYYY-MM-DD HH:MM>] <build|delta> | ZI Area Coupling Map
- Mode: <build (full rebuild) | delta (N new ZI issues)>
- Source: `wiki/zendesk/<YYYY-MM-DD>.md` (ZI issues) + `wiki/product/backlog.md` (clusters) + `wiki/architecture/coupling-map.md` (code coupling)
- ZI issues analyzed: N from N tickets
- Ticket co-occurrence pairs (≥2): N
- Cluster co-occurrence pairs (≥1): N
- Written: `wiki/zendesk/area-coupling.md`
- Cache: `.claude/cache/zendesk-overlap-data.json`
- Summary: <one-liner, e.g. "Top overlap: label-generation ↔ international (8 tickets, 312 code co-changes carriers↔orders)">
```

---

## Step 8 — Report to user

```
## Zendesk Area Overlap — <build|delta>

ZI issues : N from N tickets
Ticket pairs (≥2 co-occurrences): N
Cluster pairs: N

Top 5 area overlaps:
  8×  label-generation ↔ international   [🔴 Strong]  312 code co-changes (carriers|orders)
  6×  carrier-config ↔ label-generation  [🟡 Medium]  88 code co-changes (carriers|orders)
  ...

Code coupling source: wiki/architecture/coupling-map.md (5233 pairs, threshold ≥3)

Cache : .claude/cache/zendesk-overlap-data.json
Page  : wiki/zendesk/area-coupling.md
```

---

## Error Handling

| Case | Action |
|------|--------|
| No daily index in `wiki/zendesk/` | Hard error: run `/zendesk-summarize` first |
| `area-coupling.md` missing in delta mode | Fall back to build; note it |
| `zendesk-overlap-data.json` missing in delta mode | Fall back to build; note it |
| `coupling-map.md` missing | Warn and continue without code signal — annotate all pairs with "coupling-map.md not found; run /git-co-change-graph init" |
| Zero pairs above threshold | Inform user — likely all tickets have single-area issues |
| `query` area not found | List known areas from cache |
| `python3` not available | Hard error |
