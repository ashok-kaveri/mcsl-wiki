---
name: reverse-test-coverage
description: Invert the wiki's forward coverage map (feature → test) into a reverse map (source file / module → tests). Given a source file path or module name, reports which Playwright test specs directly cover it, and which additional test suites cover co-change partners of that file — surfacing hidden test dependencies the import graph cannot show. Use when a developer wants to know which tests to run before changing a file, or when a feature card names a change area.
argument-hint: build [--threshold N] | query <file-or-module> | delta
allowed-tools: Bash, Read, Write, Edit
disable-model-invocation: false
---

# Reverse Test Coverage

Three modes:

| Mode | What it does |
|------|-------------|
| `build` | Parse all wiki module pages + features.md → assemble JSON store → generate wiki page |
| `query` | Look up a source file or module slug; return direct + indirect test suites. No writes. |
| `delta` | Re-index only wiki module pages that changed since last build; rebuild indirect tests if coupling data changed |

## Dispatch

Parse `$ARGUMENTS` first token:

| First token | Mode |
|-------------|------|
| `build` | Build |
| `query` | Query |
| `delta` | Delta |
| missing / other | Ask: "Did you mean `build` (first time), `delta` (incremental update), or `query <file-or-module>` (coverage lookup)?" |

---

## Output Files

| File | Purpose | Committed? |
|------|---------|------------|
| `.claude/cache/reverse-test-coverage.json` | Full reverse index — machine-readable store | No — gitignored cache |
| `wiki/architecture/reverse-test-coverage.md` | Human-readable: module coverage table, unindexed modules, resolution stats | Yes |

The markdown page is always **generated from** the JSON. It is never the source of truth.

---

## Constants

```python
MODULES_ROOT     = "wiki/modules"
FEATURES_FILE    = "wiki/features.md"
COUPLING_MAP     = "wiki/architecture/coupling-map.md"   # read-only input; never modified
STORE_FILE       = ".claude/cache/reverse-test-coverage.json"
WIKI_PAGE        = "wiki/architecture/reverse-test-coverage.md"

COUPLING_PREFIX  = "storepepSAAS/"   # prefix used in all coupling-map.md file paths
MAX_PARTNERS     = 20                # max coupling partners to surface per source file
```

---

## Step 1 — Parse arguments

```python
tokens = $ARGUMENTS.split()
mode   = tokens[0] if tokens else None

threshold = COUPLING_THRESHOLD
if "--threshold" in tokens:
    i = tokens.index("--threshold")
    threshold = int(tokens[i + 1])

query_target = " ".join(tokens[1:]).strip() if mode == "query" else None
```

---

## Step 2 — Precondition checks

**Build / delta**: check whether `COUPLING_MAP` exists (soft — indirect tests are optional):
```bash
if [ -f wiki/architecture/coupling-map.md ]; then
  COUPLING_AVAILABLE=true
else
  COUPLING_AVAILABLE=false
  echo "ℹ️  wiki/architecture/coupling-map.md not found — indirect tests will be skipped."
  echo "   Run /git-co-change-graph init to enable indirect test lookup."
fi
```

**Delta / query**: verify store exists:
```bash
[ -f .claude/cache/reverse-test-coverage.json ] || {
  echo "ERROR: reverse-test-coverage.json not found."
  echo "Run: /reverse-test-coverage build"
  exit 1
}
```

**Build only** — if `wiki/architecture/reverse-test-coverage.md` already exists, proceed without prompting (build is idempotent).

---

## Step 3 — Parse wiki module pages (build and delta)

Parse all `wiki/modules/**/*.md`. For each file:

1. Detect whether the page has a `## Test Coverage` section
2. If yes, extract table rows with `.spec.ts` paths → `module_test_map`
3. Extract source file references (`.js`/`.ts` paths, not specs) → `module_source_map`

```bash
python3 << 'PYEOF'
import os, re, json, sys
from pathlib import Path
from glob import glob

mode = sys.argv[1]  # "build" or "delta"

# For delta: load existing store and get module mtimes
store = {}
if mode == "delta":
    with open(".claude/cache/reverse-test-coverage.json") as f:
        store = json.load(f)
    old_mtimes = store.get("meta", {}).get("module_mtimes", {})
else:
    old_mtimes = {}

# Regex patterns
test_row_re = re.compile(
    r'\|\s*\*{0,2}([^|*\n]+?)\*{0,2}\s*\|\s*`([^`]+\.spec\.ts)`\s*\|\s*([\u2705\ud83d\udd34\u26a0\ufe0f\u274c\ud83d\udea7][^\|]*)',
    re.UNICODE
)
src_ref_re = re.compile(r'`([a-zA-Z0-9_/. -]+\.(?:js|ts))(?::[0-9-]+)?`')
spec_ref_re = re.compile(r'\.spec\.(ts|js)$')

module_test_map   = {}   # slug -> [(feature, spec_path, status)]
module_source_map = {}   # slug -> [raw_wiki_ref]
module_has_coverage = {} # slug -> bool
module_mtimes     = {}
changed_modules   = []

all_md = sorted(glob("wiki/modules/**/*.md", recursive=True))

for md_path in all_md:
    rel = os.path.relpath(md_path, "wiki/modules")
    slug = rel.replace(".md", "").replace(os.sep, "/")
    mtime = str(os.path.getmtime(md_path))
    module_mtimes[md_path] = mtime

    # Delta: skip unchanged pages
    if mode == "delta" and old_mtimes.get(md_path) == mtime:
        continue
    changed_modules.append(slug)

    content = Path(md_path).read_text(encoding="utf-8")

    # Find ## Test Coverage section
    cov_match = re.search(r'^## Test Coverage', content, re.MULTILINE)
    if not cov_match:
        module_has_coverage[slug] = False
        module_test_map[slug] = []
        module_source_map[slug] = []
        continue

    module_has_coverage[slug] = True
    section = content[cov_match.start():]
    next_sec = re.search(r'\n## ', section[3:])
    if next_sec:
        section = section[:next_sec.start() + 3]

    # Extract test rows
    tests = []
    for m in test_row_re.finditer(section):
        feature = m.group(1).strip()
        spec    = m.group(2).strip()
        status  = m.group(3).strip().split()[0]
        tests.append((feature, spec, status))
    module_test_map[slug] = tests

    # Extract source refs (whole file, not just coverage section)
    src_refs = []
    for m in src_ref_re.finditer(content):
        ref = m.group(1).strip()
        if not spec_ref_re.search(ref):
            src_refs.append(ref)
    # Deduplicate, preserve order
    seen = set()
    deduped = []
    for r in src_refs:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    module_source_map[slug] = deduped

# Output as JSON for next step
result = {
    "module_test_map":   module_test_map,
    "module_source_map": module_source_map,
    "module_has_coverage": module_has_coverage,
    "module_mtimes":     module_mtimes,
    "changed_modules":   changed_modules,
    "all_slugs":         [
        os.path.relpath(p, "wiki/modules").replace(".md","").replace(os.sep,"/")
        for p in all_md
    ],
}
with open("/tmp/rtc_modules.json", "w") as f:
    json.dump(result, f)

print(f"modules_scanned={len(all_md)} with_coverage={sum(1 for v in module_has_coverage.values() if v)} changed={len(changed_modules)}")
PYEOF
```

---

## Step 4 — Parse coupling-map.md and resolve source refs

Parse `wiki/architecture/coupling-map.md` to extract co-change pairs, then resolve wiki source refs against the file paths found there.

If coupling-map.md does not exist, write an empty result and continue (indirect tests will be empty).

```bash
python3 << 'PYEOF'
import json, os, re
from pathlib import Path

with open("/tmp/rtc_modules.json") as f:
    parsed = json.load(f)

COUPLING_PREFIX = "storepepSAAS/"
COUPLING_MAP    = "wiki/architecture/coupling-map.md"

# ── Parse coupling-map.md ────────────────────────────────────────────────────
coupling_pairs = {}   # "A|B" -> count  (A < B lexicographically, deduplicated)
coupling_map_mtime = None

if os.path.exists(COUPLING_MAP):
    coupling_map_mtime = str(os.path.getmtime(COUPLING_MAP))
    content = Path(COUPLING_MAP).read_text(encoding="utf-8")

    # Matches both table formats:
    #   | # | count | `A` | `B` | domain |   (Top Coupled Pairs)
    #   | count | `A` | `B` |                (By Domain sections)
    row_re = re.compile(
        r'^\|\s*(?:\d+\s*\|)?\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`',
        re.MULTILINE
    )
    for m in row_re.finditer(content):
        count = int(m.group(1))
        a, b  = m.group(2).strip(), m.group(3).strip()
        key   = f"{min(a,b)}|{max(a,b)}"
        coupling_pairs[key] = max(coupling_pairs.get(key, count), count)

# Build set of all unique file paths appearing in coupling pairs
coupling_files = set()
for key in coupling_pairs:
    a, b = key.split("|", 1)
    coupling_files.add(a)
    coupling_files.add(b)

# ── Resolve wiki source refs → coupling paths ────────────────────────────────
def resolve(raw_ref, coupling_files):
    """Returns (resolution_type, [coupling_paths])"""
    candidate = COUPLING_PREFIX + raw_ref
    if candidate in coupling_files:
        return ("resolved", [candidate])
    basename = raw_ref.split("/")[-1]
    matches = sorted(f for f in coupling_files if f.endswith("/" + basename))
    if len(matches) == 1: return ("resolved", matches)
    if len(matches) > 1:  return ("ambiguous", matches)
    suffix = "/" + raw_ref
    matches = sorted(f for f in coupling_files if f.endswith(suffix))
    if len(matches) == 1: return ("resolved", matches)
    if len(matches) > 1:  return ("ambiguous", matches)
    return ("unresolved", [])

module_resolved  = {}
source_to_modules = {}
filename_index   = {}

for slug, refs in parsed["module_source_map"].items():
    resolved_list, ambiguous_list, unresolved_list = [], [], []
    for raw_ref in refs:
        rtype, paths = resolve(raw_ref, coupling_files)
        if rtype == "resolved":
            cp = paths[0]
            resolved_list.append(cp)
            source_to_modules.setdefault(cp, [])
            if slug not in source_to_modules[cp]:
                source_to_modules[cp].append(slug)
            bn = cp.split("/")[-1]
            filename_index.setdefault(bn, [])
            if cp not in filename_index[bn]:
                filename_index[bn].append(cp)
        elif rtype == "ambiguous":
            ambiguous_list.append({"wiki_ref": raw_ref, "candidates": paths})
            for cp in paths:
                bn = cp.split("/")[-1]
                filename_index.setdefault(bn, [])
                if cp not in filename_index[bn]:
                    filename_index[bn].append(cp)
        else:
            unresolved_list.append(raw_ref)
    module_resolved[slug] = {
        "resolved": resolved_list,
        "ambiguous": ambiguous_list,
        "unresolved": unresolved_list,
    }

result = {
    "module_resolved":   module_resolved,
    "source_to_modules": source_to_modules,
    "filename_index":    filename_index,
    "coupling_pairs":    coupling_pairs,
    "coupling_map_mtime": coupling_map_mtime,
    "coupling_files_count": len(coupling_files),
}
with open("/tmp/rtc_resolved.json", "w") as f:
    json.dump(result, f)

total_refs      = sum(len(v) for v in parsed["module_source_map"].values())
resolved_count  = sum(len(v["resolved"])   for v in module_resolved.values())
ambiguous_count = sum(len(v["ambiguous"])  for v in module_resolved.values())
unresolved_count= sum(len(v["unresolved"]) for v in module_resolved.values())
print(f"coupling_pairs={len(coupling_pairs)} coupling_files={len(coupling_files)}")
print(f"source_refs={total_refs} resolved={resolved_count} ambiguous={ambiguous_count} unresolved={unresolved_count}")
PYEOF
```

---

## Step 5 — Build coupling partner → indirect test map

```bash
python3 << 'PYEOF'
import json

with open("/tmp/rtc_modules.json") as f:
    parsed = json.load(f)
with open("/tmp/rtc_resolved.json") as f:
    resolved = json.load(f)

MAX_PARTNERS = 20
coupling_pairs   = resolved["coupling_pairs"]    # "A|B" -> count, from coupling-map.md
source_to_modules = resolved["source_to_modules"]

# For each resolved source file, find top coupling partners from coupling-map.md
partner_map = {}  # coupling_path -> [(count, partner_path)]

for cp in source_to_modules:
    partners = []
    for key, count in coupling_pairs.items():
        a, b = key.split("|", 1)
        if a == cp:
            partners.append((count, b))
        elif b == cp:
            partners.append((count, a))
    partners.sort(reverse=True)
    partner_map[cp] = partners[:MAX_PARTNERS]

# Build indirect test map: which tests do I get via coupling partners?
# indirect_tests[source_file] = [(spec, feature, status, via_module, via_partner, co_change_count)]
indirect_map = {}
partners_checked = {}  # coupling_path -> [{path, count, has_coverage}]

for cp, partners in partner_map.items():
    checked = []
    indirect = []
    for count, partner in partners:
        has_coverage = partner in source_to_modules
        checked.append({"path": partner, "co_change_count": count, "has_test_coverage": has_coverage})
        if has_coverage:
            for partner_slug in source_to_modules[partner]:
                for feat, spec, status in parsed["module_test_map"].get(partner_slug, []):
                    indirect.append({
                        "spec": spec,
                        "feature": feat,
                        "status": status,
                        "via_module": partner_slug,
                        "via_partner": partner,
                        "co_change_count": count,
                    })
    indirect_map[cp] = indirect
    partners_checked[cp] = checked

result = {
    "indirect_map": indirect_map,
    "partners_checked": partners_checked,
}
with open("/tmp/rtc_indirect.json", "w") as f:
    json.dump(result, f)

total_indirect = sum(len(v) for v in indirect_map.values())
print(f"source_files_with_partners={len(partner_map)} total_indirect_tests={total_indirect}")
PYEOF
```

Replace `__THRESHOLD__` with the actual threshold value before running.

---

## Step 6 — Assemble JSON store

```bash
python3 << 'PYEOF'
import json, os
from datetime import datetime, timezone
from glob import glob

with open("/tmp/rtc_modules.json") as f:
    parsed = json.load(f)
with open("/tmp/rtc_resolved.json") as f:
    resolved = json.load(f)
with open("/tmp/rtc_indirect.json") as f:
    indirect_data = json.load(f)

# Build by_source_file index
by_source_file = {}
for cp, slugs in resolved["source_to_modules"].items():
    # Collect wiki_refs (all raw refs that resolved to this coupling path)
    wiki_refs = []
    for slug, res in resolved["module_resolved"].items():
        for rp in res["resolved"]:
            if rp == cp:
                # Find original raw refs that resolved here
                for raw_ref in parsed["module_source_map"].get(slug, []):
                    bn = raw_ref.split("/")[-1]
                    if cp.endswith("/" + bn) or cp == "storepepSAAS/" + raw_ref:
                        if raw_ref not in wiki_refs:
                            wiki_refs.append(raw_ref)

    # Collect direct tests from all modules that reference this source file
    direct_tests = []
    seen_specs = set()
    for slug in slugs:
        for feat, spec, status in parsed["module_test_map"].get(slug, []):
            key = (spec, slug)
            if key not in seen_specs:
                seen_specs.add(key)
                direct_tests.append({
                    "spec": spec,
                    "feature": feat,
                    "status": status,
                    "via_module": slug,
                })

    by_source_file[cp] = {
        "wiki_refs": wiki_refs,
        "modules": slugs,
        "direct_tests": direct_tests,
        "indirect_tests": indirect_data["indirect_map"].get(cp, []),
        "coupling_partners_checked": indirect_data["partners_checked"].get(cp, []),
    }

# Build by_module index
by_module = {}
for slug in parsed["all_slugs"]:
    all_specs = list(set(spec for _, spec, _ in parsed["module_test_map"].get(slug, [])))
    by_module[slug] = {
        "wiki_path": f"wiki/modules/{slug}.md",
        "has_test_coverage_section": parsed["module_has_coverage"].get(slug, False),
        "direct_test_count": len(all_specs),
        "direct_tests": all_specs,
        "source_files": resolved["module_resolved"].get(slug, {"resolved":[],"ambiguous":[],"unresolved":[]}),
    }

# Resolve counts for meta
total_refs = sum(len(v) for v in parsed["module_source_map"].values())
resolved_count = sum(len(v["resolved"]) for v in resolved["module_resolved"].values())
ambiguous_count = sum(len(v["ambiguous"]) for v in resolved["module_resolved"].values())
unresolved_count = sum(len(v["unresolved"]) for v in resolved["module_resolved"].values())

store = {
    "meta": {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "modules_scanned": len(parsed["all_slugs"]),
        "modules_with_coverage": sum(1 for v in parsed["module_has_coverage"].values() if v),
        "specs_indexed": len(set(
            spec
            for tests in parsed["module_test_map"].values()
            for _, spec, _ in tests
        )),
        "source_refs_total": total_refs,
        "source_refs_resolved": resolved_count,
        "source_refs_ambiguous": ambiguous_count,
        "source_refs_unresolved": unresolved_count,
        "coupling_map_mtime": resolved["coupling_map_mtime"],   # None if coupling-map.md absent
        "module_mtimes": parsed["module_mtimes"],
    },
    "by_source_file": by_source_file,
    "by_module": by_module,
    "filename_index": resolved["filename_index"],
}

os.makedirs(".claude/cache", exist_ok=True)
with open(".claude/cache/reverse-test-coverage.json", "w") as f:
    json.dump(store, f, separators=(",", ":"))

print(f"store written: {len(by_source_file)} source files, {len(by_module)} modules")
PYEOF
```

Replace `__THRESHOLD__` before running.

---

## Step 7 — Generate wiki page

```bash
python3 << 'PYEOF'
import json, os
from datetime import date

with open(".claude/cache/reverse-test-coverage.json") as f:
    store = json.load(f)

meta      = store["meta"]
by_module = store["by_module"]
by_sf     = store["by_source_file"]
today     = date.today().isoformat()

# Sort modules: with coverage first, then alphabetical
def sort_key(slug):
    m = by_module[slug]
    return (0 if m["has_test_coverage_section"] else 1, slug)

sorted_modules = sorted(by_module.keys(), key=sort_key)
with_cov    = [s for s in sorted_modules if by_module[s]["has_test_coverage_section"]]
without_cov = [s for s in sorted_modules if not by_module[s]["has_test_coverage_section"]]

# Top source files by direct test count
top_sources = sorted(
    by_sf.items(),
    key=lambda kv: (len(kv[1]["direct_tests"]) + len(kv[1]["indirect_tests"])),
    reverse=True
)[:15]

out = []
out.append(f"""---
title: Reverse Test Coverage Map
category: architecture
sources: [wiki/modules, wiki/features.md, coupling-data.json]
status: complete
last_updated: {today}
modules_scanned: {meta['modules_scanned']}
modules_with_coverage: {meta['modules_with_coverage']}
specs_indexed: {meta['specs_indexed']}
---

# Reverse Test Coverage Map

Inverts the forward coverage map (feature → test) into a reverse index: source file or module → test suites.
Indirect tests surface hidden dependencies via file co-change coupling — test suites that exercise files
that frequently co-change with your target, even when there's no direct import relationship.

**Built**: {today} · **Modules**: {meta['modules_scanned']} · **Specs indexed**: {meta['specs_indexed']}
**Direct coverage**: {meta['modules_with_coverage']} modules · **Coupling source**: [coupling-map.md](coupling-map.md)

## How to Use

Before changing a source file or module, run:
```
/reverse-test-coverage query fedexShipmentHelper.js
/reverse-test-coverage query shipping/label-generation
/reverse-test-coverage query server/src/routes/orders.js
```

> Source file → test mapping is **module-level** (Playwright tests use POM, not direct imports).
> Indirect tests are found via [coupling-map.md](coupling-map.md) co-change partners.

---

## Coverage by Module

| Module | Wiki Page | Direct Tests | Source Refs Resolved | Notes |
|--------|-----------|:------------:|:--------------------:|-------|
""")

for slug in with_cov:
    m = by_module[slug]
    sf = m["source_files"]
    resolved_count = len(sf.get("resolved", []))
    notes = f"{len(sf.get('ambiguous',[]))} ambiguous, {len(sf.get('unresolved',[]))} unresolved" if sf.get("ambiguous") or sf.get("unresolved") else "—"
    wiki_link = f"[link](../modules/{slug}.md)"
    out.append(f"| `{slug}` | {wiki_link} | {m['direct_test_count']} | {resolved_count} | {notes} |\n")

out.append(f"""
---

## Modules Without Test Coverage Section

These {len(without_cov)} module pages have no `## Test Coverage` section and are not in the reverse index.
Add the section to include them in future builds:

""")
for slug in without_cov:
    out.append(f"- `{slug}` — [`wiki/modules/{slug}.md`](../modules/{slug}.md)\n")

out.append(f"""
---

## Source File Resolution

Of {meta['source_refs_total']} source file references extracted from module pages:

| Resolution | Count | Notes |
|------------|------:|-------|
| Resolved (1:1 match in coupling data) | {meta['source_refs_resolved']} | Used for direct + indirect lookup |
| Ambiguous (multiple candidates) | {meta['source_refs_ambiguous']} | All candidates included; flagged in query output |
| Unresolved (not in coupling data) | {meta['source_refs_unresolved']} | No coupling partners available |

---

## Top Source Files by Test Coverage

| Source File | Modules | Direct Tests | Indirect Tests |
|-------------|---------|:------------:|:--------------:|
""")

for cp, rec in top_sources:
    basename = cp.split("/")[-1]
    modules = ", ".join(f"`{m}`" for m in rec["modules"])
    out.append(f"| `{basename}` | {modules} | {len(rec['direct_tests'])} | {len(rec['indirect_tests'])} |\n")

out.append(f"""
---

## Related

- [Features & Test Coverage](../features.md)
- [File Co-Change Coupling Map](coupling-map.md)
- [Backend Architecture](backend-architecture.md)
""")

os.makedirs("wiki/architecture", exist_ok=True)
with open("wiki/architecture/reverse-test-coverage.md", "w") as f:
    f.writelines(out)

print(f"wrote reverse-test-coverage.md")
PYEOF
```

---

## Step 7b — Query mode

No writes. Load store, apply four-pass lookup, print results.

```bash
python3 << 'PYEOF'
import json, sys

target = sys.argv[1]

with open(".claude/cache/reverse-test-coverage.json") as f:
    store = json.load(f)

by_module  = store["by_module"]
by_sf      = store["by_source_file"]
fn_index   = store["filename_index"]

def print_source_result(cp, rec):
    basename = cp.split("/")[-1]
    print(f"\nReverse Test Coverage: {basename}")
    print("=" * 60)
    print(f"Path    : {cp}")
    print(f"Modules : {', '.join(rec['modules'])}")

    direct = rec["direct_tests"]
    print(f"\n── Direct Tests ({len(direct)} specs) {'─'*30}")
    if not direct:
        print("  (none — module page exists but has no test rows)")
    for t in direct[:10]:
        print(f"  {t['status']}  {t['spec']}")
        print(f"       Feature : {t['feature']}")
        print(f"       Module  : {t['via_module']}")
    if len(direct) > 10:
        print(f"  ...and {len(direct) - 10} more")

    indirect = rec["indirect_tests"]
    if indirect:
        print(f"\n── Indirect Tests via Co-Change Partners ({len(indirect)} specs) {'─'*10}")
        by_partner = {}
        for t in indirect:
            by_partner.setdefault(t["via_partner"], []).append(t)
        for partner, tests in sorted(by_partner.items(), key=lambda x: -x[1][0]["co_change_count"]):
            pname = partner.split("/")[-1]
            print(f"\n  Partner : {pname}  ({tests[0]['co_change_count']}× co-changes)")
            print(f"  Full    : {partner}")
            for t in tests[:5]:
                print(f"    {t['status']}  {t['spec']}  [{t['via_module']}]")
            if len(tests) > 5:
                print(f"    ...and {len(tests)-5} more")

    uncovered = [p for p in rec["coupling_partners_checked"] if not p["has_test_coverage"]]
    if uncovered:
        print(f"\n── Co-Change Partners with No Test Coverage ({len(uncovered)}) {'─'*5}")
        for p in uncovered[:5]:
            print(f"  {p['co_change_count']:4}×  {p['path'].split('/')[-1]}")

    print(f"\n── Summary {'─'*50}")
    covered_partners = len(set(t["via_partner"] for t in indirect))
    print(f"  Direct test suites   : {len(direct)}")
    print(f"  Indirect test suites : {len(indirect)}  (via {covered_partners} covered co-change partner(s))")
    print(f"  Uncovered partners   : {len(uncovered)}")

def print_module_result(slug, m):
    print(f"\nReverse Test Coverage: {slug}")
    print("=" * 60)
    print(f"Wiki page : {m['wiki_path']}")
    has_cov = m["has_test_coverage_section"]
    print(f"Coverage section : {'yes' if has_cov else 'NO — add ## Test Coverage section to include in index'}")

    specs = m["direct_tests"]
    print(f"\n── Direct Tests ({len(specs)} specs) {'─'*35}")
    for sp in specs[:10]:
        print(f"  ✅  {sp}")
    if len(specs) > 10:
        print(f"  ...and {len(specs)-10} more")
    if not specs:
        print("  (none)")

    sf = m["source_files"]
    if sf.get("resolved"):
        print(f"\n── Resolved Source Files ({len(sf['resolved'])}) {'─'*30}")
        for cp in sf["resolved"][:5]:
            print(f"  {cp.split('/')[-1]}")
            # Show indirect tests via this source file
            if cp in by_sf:
                indirect = by_sf[cp]["indirect_tests"]
                if indirect:
                    print(f"    → {len(indirect)} indirect tests via co-change partners")
        if len(sf["resolved"]) > 5:
            print(f"  ...and {len(sf['resolved'])-5} more")

# ─── Lookup algorithm ────────────────────────────────────────────────────────

results_found = False

# Pass 1: exact module slug
if target in by_module:
    print_module_result(target, by_module[target])
    results_found = True

# Pass 2: full or suffix path match in by_source_file
if not results_found:
    matched = []
    for cp in by_sf:
        if cp == target or cp == "storepepSAAS/" + target or cp.endswith("/" + target):
            matched.append(cp)
    if matched:
        for cp in matched:
            print_source_result(cp, by_sf[cp])
        results_found = True

# Pass 3: basename in filename_index
if not results_found:
    basename = target.split("/")[-1]
    if basename in fn_index:
        candidates = fn_index[basename]
        if len(candidates) == 1:
            print_source_result(candidates[0], by_sf[candidates[0]])
        else:
            print(f"\n(Ambiguous: {len(candidates)} files match '{basename}')")
            for cp in candidates:
                print_source_result(cp, by_sf[cp])
        results_found = True

# Pass 4: fuzzy substring on module slugs
if not results_found:
    fuzzy = [s for s in by_module if target.lower() in s.lower()]
    if fuzzy:
        for slug in fuzzy:
            print_module_result(slug, by_module[slug])
        results_found = True

if not results_found:
    print(f"\nNo coverage data found for: {target}")
    print("\nTry:")
    print("  Module slug  : shipping/label-generation")
    print("  Filename     : fedexShipmentHelper.js")
    print("  Partial path : server/src/routes/orders.js")
    print("\nAll indexed modules:")
    for slug in sorted(by_module):
        mark = "✅" if by_module[slug]["has_test_coverage_section"] else "  "
        print(f"  {mark}  {slug}")
PYEOF
```

Present the output to the user with a note:
> Indirect tests cover files that co-change with your target. Run the direct tests first; if any indirect tests cover shared utilities, add them to your regression scope.

---

## Step 8 — Delta mode

Delta re-indexes only changed module pages, merging fresh data into the existing store.

```bash
python3 << 'PYEOF'
import json, hashlib

with open(".claude/cache/reverse-test-coverage.json") as f:
    store = json.load(f)

with open("/tmp/rtc_modules.json") as f:
    parsed = json.load(f)
with open("/tmp/rtc_resolved.json") as f:
    resolved_data = json.load(f)
with open("/tmp/rtc_indirect.json") as f:
    indirect_data = json.load(f)

changed = parsed["changed_modules"]

if not changed:
    print("NOTHING_CHANGED")
else:
    # Remove stale entries for changed modules from by_module and by_source_file
    for slug in changed:
        # Get old resolved source files
        old_sf = store["by_module"].get(slug, {}).get("source_files", {}).get("resolved", [])
        for cp in old_sf:
            if cp in store["by_source_file"]:
                rec = store["by_source_file"][cp]
                rec["modules"] = [m for m in rec["modules"] if m != slug]
                rec["direct_tests"] = [t for t in rec["direct_tests"] if t["via_module"] != slug]
                if not rec["modules"]:
                    del store["by_source_file"][cp]

    # Merge fresh data from Steps 3-5 into store
    # (by_source_file and by_module rebuilt from /tmp files for changed modules)
    # Load the freshly-built full store from Step 6 temp output
    with open("/tmp/rtc_new_store.json") as f:
        new_store = json.load(f)

    for slug in changed:
        store["by_module"][slug] = new_store["by_module"][slug]
    for cp, rec in new_store["by_source_file"].items():
        if any(m in changed for m in rec["modules"]):
            store["by_source_file"][cp] = rec

    # Update meta
    store["meta"].update({
        "built_at": new_store["meta"]["built_at"],
        "module_mtimes": parsed["module_mtimes"],
        "coupling_sha256": resolved_data["coupling_sha"],
    })
    store["filename_index"] = resolved_data["filename_index"]

    with open(".claude/cache/reverse-test-coverage.json", "w") as f:
        json.dump(store, f, separators=(",", ":"))

    print(f"delta: re-indexed {len(changed)} modules: {', '.join(changed)}")
PYEOF
```

If output is `NOTHING_CHANGED`: print "Nothing changed since last build. Store is up to date." and exit.

If `wiki/architecture/coupling-map.md` mtime changed (compare `meta.coupling_map_mtime` with `os.path.getmtime("wiki/architecture/coupling-map.md")` before running Step 4): warn user and recommend a full `build` for accurate indirect tests.

---

## Step 9 — Update index and log (build and delta)

### `wiki/index.md`

Add under `## Architecture` if not already present:
```markdown
- [Reverse Test Coverage Map](architecture/reverse-test-coverage.md) — Source file / module → test suite reverse lookup with co-change hidden dependency surfacing
```

### `wiki/log.md`

```markdown
## [<YYYY-MM-DD HH:MM>] <build|delta> | Reverse Test Coverage Map
- Mode: <build | delta (N modules re-indexed: slug1, slug2)>
- Modules scanned: N  (N with coverage section, N without)
- Source refs: N total (N resolved, N ambiguous, N unresolved)
- Specs indexed: N
- Written: `wiki/architecture/reverse-test-coverage.md`
- Cache: `.claude/cache/reverse-test-coverage.json`
- Summary: <one-liner, e.g. "shipping/label-generation has deepest coverage (20 direct, 3 indirect); 16 modules still lack ## Test Coverage sections">
```

---

## Step 10 — Report to user

```
## Reverse Test Coverage — <build|delta>

Modules  : N scanned  (N with coverage section, N without)
Refs     : N source refs extracted → N resolved, N ambiguous, N unresolved
Specs    : N unique spec files indexed

Coverage by module:
  shipping/label-generation          20 direct  +  N indirect
  orders/order-bulk-actions          12 direct  +  N indirect
  automation/automation-actions      11 direct  +  N indirect
  stores/platform-connectors          5 direct  +  N indirect
  shipping/carrier-configuration      3 direct  +  N indirect
  shipping/shipment-tracking          1 direct  +  N indirect

16 modules have no ## Test Coverage section — run /reverse-test-coverage query <slug> to see what's available.

Cache : .claude/cache/reverse-test-coverage.json
Page  : wiki/architecture/reverse-test-coverage.md
```

---

## Error Handling

| Case | Action |
|------|--------|
| `coupling-map.md` missing | Soft warning — indirect tests skipped; direct tests still indexed. "Run /git-co-change-graph init to enable indirect lookup." |
| `reverse-test-coverage.json` missing at query/delta | Hard error: "Run /reverse-test-coverage build first" |
| Module page has no `## Test Coverage` | Included in `without_cov` list; `direct_test_count: 0`; not in `by_source_file` |
| Source ref ambiguous | All candidates stored and searched; query output flags "(ambiguous)" |
| Source ref unresolved | Stored as unresolved; no indirect tests possible |
| Query target matches nothing | Four-pass fallback then helpful hint listing all module slugs |
| Delta with changed coupling data | Warn; recommend full `build`; continue with stale indirect tests |
| Nothing changed in delta | Print "Nothing changed since last build." and exit cleanly |
