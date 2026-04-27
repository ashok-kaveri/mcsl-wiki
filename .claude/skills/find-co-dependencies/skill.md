# Find Co-Dependencies

Unified blast-radius analysis combining test coverage, code coupling, and customer-reported issue overlap. Given a file or feature area, shows the complete dependency footprint across all three dimensions.

**The insight**: Files that test together, change together, and break together in customer reports form a dependency cluster. This skill surfaces the complete blast radius.

## Modes

| Mode | What it does |
|------|-------------|
| `query <file-or-area>` | Blast-radius lookup combining all three technical maps (test + code + ZI) |
| `semantic <card-file-or-text>` | LLM-assisted semantic analysis: identify modules conceptually related to a feature card |
| `full <card-file-or-text>` | Complete blast-radius: semantic analysis + technical coupling for all identified modules |
| `build` | Rebuild all three dependency maps in topological order |
| `delta` | Update all three maps incrementally |

**Default** (no args): Error — query/semantic/full requires a target

## Options

| Option | Applies to | What it does |
|--------|-----------|--------------|
| `--derive-actionable-items` | query, semantic, full | Translates blast-radius findings into **input recommendations**: suggested acceptance criteria, regression test plan, code review checklist. Developer reviews and adapts these for the card. |

**Purpose**: Provides a starting point for card planning. Developer should review, refine, and adapt based on specific card context.

**Usage**: Add the flag after the command:
```bash
/find-co-dependencies query label-generation --derive-actionable-items
/find-co-dependencies full <card> --derive-actionable-items
```

## Dispatch

Parse first token:

| First token | Mode |
|-------------|------|
| `query` | Query — remainder is file path or area name |
| `semantic` | Semantic — remainder is card file or description |
| `full` | Full — remainder is card file or description |
| `build` | Build |
| `delta` | Delta |
| missing | Error: "Usage: /find-co-dependencies query <file-or-area> \| semantic <card> \| full <card> \| build \| delta" |
| other (looks like file path or area name) | Query mode with the entire arg as target |

---

## Query Mode

**Input**: File path (e.g., `server/src/shared/orders/OrderProcessingService.js`) or ZI area name (e.g., `label-generation`)

**Output**: Combined blast-radius report across three dimensions

### Step 1 — Classify Input

```bash
python3 << 'PYEOF'
import sys, os

query = sys.argv[1].strip()

# Check if it's a file path (contains / or ends in .js/.ts)
if '/' in query or query.endswith(('.js', '.ts', '.jsx', '.tsx')):
    print("file")
else:
    print("area")
PYEOF
```

Call as: `python3 ... "<query>"`

Store result as `INPUT_TYPE` (either "file" or "area")

### Step 2a — Query for File Path

If `INPUT_TYPE == "file"`:

**Test Coverage Dimension:**

```bash
python3 << 'PYEOF'
import json, sys, os

file_path = sys.argv[1]

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    sys.exit(1)

try:
    with open(os.path.join(wiki_root, "wiki/architecture/reverse-test-coverage.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("⚠️  reverse-test-coverage.md not found — run /reverse-test-coverage build first")
    sys.exit(0)

# Parse the Direct Coverage table
# Format: | source_file | test_count | test_files |
in_table = False
found = False
for line in content.split('\n'):
    line = line.strip()
    if line.startswith("| Source File |") and "Test Count" in line:
        in_table = True
        continue
    if in_table and line.startswith("|---"):
        continue
    if in_table and line.startswith("|"):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 3:
            src = cols[0].strip("`")
            if src == file_path:
                test_count = cols[1]
                test_files = cols[2]
                print(f"✅ **Direct Test Coverage**: {test_count} tests")
                print(f"   Tests: {test_files}")
                found = True
                break
    elif in_table and not line.startswith("|"):
        in_table = False

if not found:
    print("❌ **No Direct Test Coverage** — no Playwright tests directly import this file")

# Also check co-change coverage
print("\n**Co-Change Test Coverage**:")
in_cochange = False
found_cochange = False
for line in content.split('\n'):
    line = line.strip()
    if "## Co-Change Coverage" in line:
        in_cochange = True
        continue
    if in_cochange and line.startswith("| Source File |"):
        continue
    if in_cochange and line.startswith("|---"):
        continue
    if in_cochange and line.startswith("|"):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 3:
            src = cols[0].strip("`")
            if src == file_path:
                partner_count = cols[1]
                partners = cols[2]
                print(f"   {partner_count} co-change partners have test coverage")
                print(f"   Partners: {partners}")
                found_cochange = True
                break
    elif in_cochange and line.startswith("#"):
        break

if not found_cochange:
    print("   No co-change partners with test coverage detected")
PYEOF
```

**Code Coupling Dimension:**

```bash
python3 << 'PYEOF'
import json, sys, os

file_path = sys.argv[1]

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    sys.exit(1)

try:
    with open(os.path.join(wiki_root, "wiki/architecture/coupling-map.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("\n⚠️  coupling-map.md not found — run /git-co-change-graph init")
    sys.exit(0)

# Parse the Top Coupled Pairs table
# Format: | # | co-changes | fileA | fileB | domain |
in_table = False
partners = []
for line in content.split('\n'):
    line = line.strip()
    if line.startswith("| # |") and "Co-changes" in line:
        in_table = True
        continue
    if in_table and line.startswith("|---"):
        continue
    if in_table and line.startswith("|"):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 4:
            count = cols[1]
            file_a = cols[2].strip("`")
            file_b = cols[3].strip("`")
            if file_a == file_path:
                partners.append((count, file_b))
            elif file_b == file_path:
                partners.append((count, file_a))
    elif in_table and not line.startswith("|"):
        break

print("\n**Code Co-Change Coupling**:")
if partners:
    print(f"   {len(partners)} co-change partners detected")
    # Show top 10
    partners.sort(key=lambda x: -int(x[0]))
    for count, partner in partners[:10]:
        print(f"   {count:>4}×  {partner}")
    if len(partners) > 10:
        print(f"   ... +{len(partners)-10} more")
else:
    print("   ❌ No co-change coupling detected")
PYEOF
```

**ZI Area Dimension:**

```bash
python3 << 'PYEOF'
import sys, os

file_path = sys.argv[1]

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    sys.exit(1)

# Map file path to ZI area
# This is heuristic-based
DOMAIN_MAP = {
    "server/src/shared/API/carriers/": "carrier-config",
    "server/src/shared/orders/": "order-management",
    "server/src/routes/": "order-management",
    "client/src/components/": "other",
    "client/src/": "other",
}

area = None
for prefix, zi_area in DOMAIN_MAP.items():
    if file_path.startswith(prefix):
        area = zi_area
        break

if not area:
    print("\n**ZI Area Coupling**: Cannot map file to ZI area")
    sys.exit(0)

print(f"\n**ZI Area Coupling** (mapped to area: `{area}`):")

try:
    with open(os.path.join(wiki_root, "wiki/zendesk/area-coupling.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("   ⚠️  area-coupling.md not found — run /zendesk-overlap build first")
    sys.exit(0)

# Parse the Area Co-Occurrence table
# Format: | AreaA | AreaB | Tickets | Code Signal |
in_table = False
results = []
for line in content.split('\n'):
    line = line.strip()
    if line.startswith("| AreaA |") or line.startswith("| Area A |"):
        in_table = True
        continue
    if in_table and line.startswith("|---"):
        continue
    if in_table and line.startswith("|"):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 4:
            area_a = cols[0].strip("`")
            area_b = cols[1].strip("`")
            count = int(cols[2])
            code_signal = cols[3]
            if area_a == area:
                results.append((count, area_b, code_signal))
            elif area_b == area:
                results.append((count, area_a, code_signal))
    elif in_table and not line.startswith("|"):
        break

results.sort(reverse=True)

if results:
    print(f"   {len(results)} co-occurring areas in customer-reported failures")
    for count, partner, code_signal in results[:5]:
        print(f"   {count:>2}×  {partner:<25}  ({code_signal})")
    if len(results) > 5:
        print(f"   ... +{len(results)-5} more")
else:
    print("   ❌ No area coupling detected")
PYEOF
```

Call all three in sequence, then combine into a final summary.

### Step 2b — Query for Area Name

If `INPUT_TYPE == "area"`:

**ZI Area Dimension (primary):**

```bash
python3 << 'PYEOF'
import sys, os

area = sys.argv[1].strip().lower()

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    sys.exit(1)

try:
    with open(os.path.join(wiki_root, "wiki/zendesk/area-coupling.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("⚠️  area-coupling.md not found — run /zendesk-overlap build first")
    sys.exit(0)

# Parse the Area Co-Occurrence table
# Format: | AreaA | AreaB | Tickets | Code Signal |
in_table = False
results = []
known_areas = set()
for line in content.split('\n'):
    line = line.strip()
    if line.startswith("| AreaA |") or line.startswith("| Area A |"):
        in_table = True
        continue
    if in_table and line.startswith("|---"):
        continue
    if in_table and line.startswith("|"):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 4:
            area_a = cols[0].strip("`")
            area_b = cols[1].strip("`")
            known_areas.add(area_a)
            known_areas.add(area_b)
            count = int(cols[2])
            code_signal = cols[3]
            if area_a == area:
                results.append((count, area_b, code_signal))
            elif area_b == area:
                results.append((count, area_a, code_signal))
    elif in_table and not line.startswith("|"):
        break

results.sort(reverse=True)

print(f"**ZI Area Coupling** for `{area}`:")
if results:
    print(f"   {len(results)} co-occurring areas in customer-reported failures")
    for count, partner, code_signal in results:
        print(f"   {count:>2}×  {partner:<25}  ({code_signal})")
else:
    print("   ❌ No area coupling detected")
    if known_areas:
        print(f"   Known areas: {', '.join(sorted(known_areas))}")
PYEOF
```

**Code Coupling Dimension (mapped from area):**

```bash
python3 << 'PYEOF'
import sys, os

area = sys.argv[1].strip().lower()

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    sys.exit(1)

# Map ZI area to code domains
AREA_TO_DOMAIN = {
    "carrier-config":    ["server/src/shared/API/carriers/"],
    "carrier-migration": ["server/src/shared/API/carriers/"],
    "rate-shopping":     ["server/src/shared/API/carriers/", "server/src/shared/orders/"],
    "label-generation":  ["server/src/shared/orders/"],
    "international":     ["server/src/shared/API/carriers/", "server/src/shared/orders/"],
    "order-management":  ["server/src/shared/orders/", "server/src/routes/"],
    "product-management":["server/src/shared/", "server/src/models/"],
    "tracking":          ["server/src/shared/orders/"],
    "returns":           ["server/src/shared/orders/", "server/src/shared/API/carriers/"],
    "onboarding":        ["client/src/"],
    "feature-request":   [],
    "other":             [],
}

domains = AREA_TO_DOMAIN.get(area, [])

print(f"\n**Code Coupling** (from area `{area}` → domains: {', '.join(domains) if domains else 'none'}):")

if not domains:
    print("   Cannot map area to code domains")
    sys.exit(0)

try:
    with open(os.path.join(wiki_root, "wiki/architecture/coupling-map.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("   ⚠️  coupling-map.md not found — run /git-co-change-graph init")
    sys.exit(0)

# Find files in those domains and their coupling partners
in_table = False
partners = {}  # file → [(count, partner), ...]

for line in content.split('\n'):
    line = line.strip()
    if line.startswith("| # |") and "Co-changes" in line:
        in_table = True
        continue
    if in_table and line.startswith("|---"):
        continue
    if in_table and line.startswith("|"):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 4:
            count = cols[1]
            file_a = cols[2].strip("`")
            file_b = cols[3].strip("`")
            # Check if either file is in our domains
            a_match = any(file_a.startswith(d) for d in domains)
            b_match = any(file_b.startswith(d) for d in domains)
            if a_match and not b_match:
                if file_a not in partners:
                    partners[file_a] = []
                partners[file_a].append((int(count), file_b))
            elif b_match and not a_match:
                if file_b not in partners:
                    partners[file_b] = []
                partners[file_b].append((int(count), file_a))
    elif in_table and not line.startswith("|"):
        break

if partners:
    total = sum(len(p) for p in partners.values())
    print(f"   {total} coupling relationships across {len(partners)} files in this area")
    # Show top coupled files
    top_files = sorted(partners.items(), key=lambda x: -sum(c for c, _ in x[1]))[:5]
    for file, file_partners in top_files:
        total_weight = sum(c for c, _ in file_partners)
        print(f"   {file} → {len(file_partners)} partners, {total_weight} total co-changes")
else:
    print("   ❌ No code coupling detected for files in this area")
PYEOF
```

**Test Coverage Dimension:**

```bash
python3 << 'PYEOF'
import sys, os

area = sys.argv[1].strip().lower()

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    sys.exit(1)

# Map ZI area to test directories
AREA_TO_TESTS = {
    "carrier-config":    ["carrierOtherDetails/"],
    "label-generation":  ["orderGrid/labelGenerationFromGrid/", "packagingTypes/", "specialServices/"],
    "order-management":  ["orderGrid/actionMenu/", "orderSummary/"],
    "tracking":          ["trackingFromGrid/"],
    "rate-shopping":     ["carrierOtherDetails/"],
    "international":     ["specialServices/"],
    "product-management":["shopifyUI/"],
    "onboarding":        ["shopifyUI/"],
}

test_dirs = AREA_TO_TESTS.get(area, [])

print(f"\n**Test Coverage** (from area `{area}` → test dirs: {', '.join(test_dirs) if test_dirs else 'none'}):")

if not test_dirs:
    print("   Cannot map area to test directories")
    sys.exit(0)

try:
    with open(os.path.join(wiki_root, "wiki/features.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("   ⚠️  features.md not found")
    sys.exit(0)

# Count tests in this area
# Parse features.md for test files in the mapped directories
import re
test_count = 0
tests = []

for line in content.split('\n'):
    # Look for test file references like `automationRules/...spec.ts`
    match = re.search(r'`([^`]+\.spec\.ts)`', line)
    if match:
        test_file = match.group(1)
        if any(test_file.startswith(d) for d in test_dirs):
            test_count += 1
            tests.append(test_file)

if test_count > 0:
    print(f"   ✅ {test_count} automated tests covering this area")
    for test in tests[:10]:
        print(f"      • {test}")
    if len(tests) > 10:
        print(f"      ... +{len(tests)-10} more")
else:
    print(f"   ❌ No automated tests found for this area")
PYEOF
```

### Step 3 — Generate Summary Report

Combine all dimensions into a unified blast-radius report:

```text
# Blast Radius for <target>

## Summary
- **Test Coverage**: X tests directly, Y via co-change partners
- **Code Coupling**: N co-change partners (M high-frequency)
- **ZI Area Coupling**: P co-occurring areas in customer reports

## Recommendation
When working on <target>:
1. Run these tests: <list>
2. Review these files: <list>
3. Check these areas for side effects: <list>

See full details above.
```

---

## Output Formats

Query mode supports two output formats:

### Standard Format (default)

Full technical report with three dimensions:
- **Test Coverage**: all direct + indirect tests listed
- **Code Coupling**: all co-change partners with counts
- **ZI Area Coupling**: all co-occurring areas with ticket counts

**Use for**: Deep-dive investigations, technical analysis

### Card Format (for card analysis)

Concise blast-radius summary optimized for card analysis integration.

**Structure**:
```text
# Blast Radius: <target>

[Risk indicator: ⚠️ High-risk / ℹ️ Medium-risk / ✅ Low-risk]

## Test Coverage
- Direct: N tests (list top test dirs)
- Indirect: M tests via co-change (list if significant)

## Code Coupling (High-Frequency Partners)
- List top 5 files with co-change counts (≥10 co-changes only)
- Omit low-frequency coupling to reduce noise

## Customer Impact
- Co-occurring areas from ZI issues
- Related ticket numbers (if available)

## Recommendations
✅ Test Strategy: specific suites to run
⚠️ Code Review: files to check for side effects
ℹ️ Customer Validation: test scenarios from tickets
```

**Risk Assessment**:
- **⚠️ High-risk**: ≥10 co-change partners OR ≥5 ZI area overlaps OR critical path files
- **ℹ️ Medium-risk**: 3-9 co-change partners OR 2-4 ZI area overlaps
- **✅ Low-risk**: <3 co-change partners AND <2 ZI area overlaps

**Use for**: Card analysis, acceptance criteria, implementation planning

---

## Derive Actionable Items

When `--derive-actionable-items` flag is present, add an additional section to the blast-radius output that translates findings into concrete action items for the developer.

### Detection

Check if `--derive-actionable-items` appears anywhere in the arguments:
```bash
if [[ "$*" == *"--derive-actionable-items"* ]]; then
    DERIVE_ITEMS=true
fi
```

### Processing

After generating the normal blast-radius output (from query/semantic/full mode), perform LLM-assisted analysis to derive actionable items.

**Analysis Prompt** (internal reasoning):

```text
Given this blast-radius analysis:
{BLAST_RADIUS_OUTPUT}

Derive concrete actionable items for the developer picking up this card.

Focus on:
1. **Acceptance Criteria Additions** - What should be added to the card's acceptance criteria based on identified dependencies?
2. **Regression Test Plan** - Which specific features/scenarios need retesting? Be specific about test suites and user workflows.
3. **Code Review Checklist** - Which files need careful review for unintended side effects?
4. **Customer Validation Plan** - Based on ZI issues, which scenarios need manual customer-perspective testing?

Be specific and actionable. Reference:
- Exact test suite paths from test coverage
- Specific file names from code coupling
- Feature names and ZI issue IDs from area coupling
- User workflows from semantic coupling
```

### Output Format

Append this section to the blast-radius report:

```text
---

## 🎯 Recommended Input for Card Planning

**Note**: These are LLM-generated recommendations based on blast-radius analysis. Review and adapt based on your specific card context, implementation approach, and domain knowledge.

### 1. Suggested Acceptance Criteria

Consider adding these to the card's acceptance criteria (review and adapt as needed):

- [ ] **No regression in {identified-area}**
  - Rationale: {area} has {N} co-occurrences with this feature area in customer tickets
  - Suggested validation: Test scenarios from ZI-XXX, ZI-YYY
  - 💡 *Review*: Is this area actually affected by your implementation approach?

- [ ] **{Coupled-feature} continues to work**
  - Rationale: {file} has {N} co-changes with target files
  - Suggested validation: Run {specific-test-suite}
  - 💡 *Review*: Does your change touch this coupling point?

- [ ] **{Integration-point} integration unaffected**
  - Rationale: Semantic coupling detected via {workflow/data-flow/etc}
  - Suggested validation: {specific checks}
  - 💡 *Review*: Is this integration in scope for your card?

### 2. Suggested Regression Test Plan

**Automated Tests (Starting Point):**

| Test Suite | Priority | Reason | Review Needed? |
|------------|----------|--------|----------------|
| `{test-dir}/*.spec.ts` | MUST | Direct test coverage of modified code | ✓ Confirm scope |
| `{test-dir}/*.spec.ts` | SHOULD | Co-change partner coverage ({N}× coupling) | ✓ Check if coupling point touched |
| `{test-dir}/*.spec.ts` | CONSIDER | Semantic coupling ({area} conceptually related) | ✓ Verify relevance to your change |

💡 **Review**: Adjust priorities based on your actual implementation plan. Some high-coupling areas may not be affected by your specific approach.

**Suggested Manual Test Scenarios:**

Based on ZI area coupling, consider manually verifying:
- **Scenario**: {User workflow from ZI-XXX}
  - Why: {area-A} ↔ {area-B} co-occur in {N} customer tickets
  - Suggested steps: {derive from ticket summaries}
  - 💡 *Review*: Read the full ticket summaries to understand context

- **Scenario**: {User workflow from ZI-YYY}
  - Why: {reasoning}
  - Suggested steps: {steps}
  - 💡 *Review*: Adapt steps to your specific implementation

### 3. Suggested Code Review Checklist

Consider focusing code review on these high-coupling files (if your changes touch these areas):

- [ ] **{filename}** ({N}× co-changes)
  - Suggested focus: {specific concerns based on file's domain}
  - Areas to review: {specific functions/sections}
  - 💡 *Review*: Only include if your changes interact with this file

- [ ] **{filename}** ({N}× co-changes)
  - Suggested focus: {concerns}
  - Areas to review: {specifics}
  - 💡 *Review*: Check git history to understand why coupling exists

**Suggested review focus areas:**
- Data flow: {files involved in data pipeline} — *if your change affects data flow*
- Validation logic: {files with business rules} — *if your change adds/modifies validations*
- API contracts: {files defining interfaces} — *if your change touches APIs*

💡 **Review**: Cross-reference with your implementation plan. Exclude files your approach won't touch.

### 4. Suggested Customer Validation Scenarios

Consider testing these scenarios from customer perspective (derived from ZI tickets):

1. **{Feature-area from ZI coupling}**
   - Derived from: ZI-XXX, ZI-YYY ({N} related tickets)
   - Suggested test: {end-to-end user workflow}
   - Expected: {outcome}
   - 💡 *Review*: Read full ticket summaries at `wiki/zendesk/summaries/{ticketId}.md` for context

2. **{Another feature-area}**
   - Derived from: ZI-ZZZ ({N} related tickets)
   - Suggested test: {workflow}
   - Expected: {outcome}
   - 💡 *Review*: Adapt based on your specific implementation

**Suggested customer success criteria:**
- All scenarios in regression plan pass
- No increase in tickets for coupled areas post-deployment
- Performance metrics unchanged for coupled workflows

💡 **Review**: These are based on historical coupling. Your implementation may mitigate some risks — adjust accordingly.

---

## How to Use These Recommendations

1. **Start here**: Use as a checklist during card planning
2. **Review & filter**: Remove items not relevant to your implementation approach
3. **Adapt & expand**: Modify based on domain knowledge and specific requirements
4. **Cross-reference**: Read ticket summaries and module pages for full context
5. **Iterate**: Update as you learn more during implementation

**Summary**: {N} suggested acceptance criteria, {M} test suites, {P} review files, {Q} customer scenarios
```

### Derivation Guidelines

**IMPORTANT**: These are heuristic-based recommendations, not prescriptive requirements. The developer must review and filter based on their specific implementation approach.

**Acceptance Criteria (Suggested):**
- Generate from coupling strength:
  - High coupling (≥10 co-changes) → Suggest as acceptance criteria (review needed)
  - Medium coupling (3-9) → Suggest with "consider" language
  - ZI area overlap (≥3 tickets) → Suggest customer validation (read summaries first)
  - Semantic high-confidence → Suggest integration/workflow checks
- Always include 💡 review prompts: "Does your change touch this area?"

**Regression Test Plan (Starting Point):**
- MUST: All direct test coverage (but confirm scope)
- SHOULD: Tests for co-change partners with ≥10 co-changes (if coupling point touched)
- CONSIDER: Tests for semantic coupling modules (verify relevance)
- Manual: ZI scenarios from tickets (read summaries, adapt steps)
- Add "Review Needed?" column to flag assumptions

**Code Review Checklist (Conditional):**
- Include files with ≥10 co-changes (with review prompts)
- Include semantic high-confidence module files (if implementation touches them)
- For each file, suggest review focus based on domain:
  - Orders → data integrity, state transitions
  - Carriers → API contracts, error handling
  - Label generation → field mapping, format validation
  - Rates → calculation logic, caching
- Always add: "Only include if your changes interact with this file"

**Customer Validation (Derived, Not Final):**
- For each ZI area with ≥3 co-occurrences:
  - Read ticket summaries from `wiki/zendesk/summaries/`
  - Extract user workflows from Open Issues
  - Suggest test scenarios (developer adapts based on implementation)
  - Reference ZI issue IDs for deep-dive
- Add review notes: "Read full summaries for context"

**Output Philosophy:**
- Provide breadth (all potential dependencies) over precision
- Developer filters based on implementation approach
- Include review prompts to encourage critical thinking
- Reference source material (tickets, module pages) for validation

### Example: Actionable Items from Query Mode

**Input**: `/find-co-dependencies query label-generation --derive-actionable-items`

**Blast-radius found:**
- 23 tests (direct)
- 47 code coupling relationships (5 files with ≥10 co-changes)
- 8 ZI area overlaps (international: 12×, carrier-config: 8×, order-management: 6×)

**Derived recommendations:**

```text
## 🎯 Recommended Input for Card Planning

**Note**: These are LLM-generated recommendations based on blast-radius analysis. Review and adapt based on your specific card context, implementation approach, and domain knowledge.

### 1. Suggested Acceptance Criteria

- [ ] **No regression in international shipping workflows**
  - Rationale: `international` area has 12 co-occurrences with `label-generation` in customer tickets
  - Suggested validation: Test customs declaration, commercial invoice, dangerous goods scenarios from ZI-156, ZI-169, ZI-203
  - 💡 *Review*: Read ticket summaries to understand actual issues

- [ ] **Carrier configuration changes don't affect label generation**
  - Rationale: `carrier-config` area has 8 co-occurrences with `label-generation`
  - Suggested validation: Test label generation for all carriers after config changes (ZI-187, ZI-201)
  - 💡 *Review*: Check if your change touches carrier config paths

- [ ] **Order data integrity maintained**
  - Rationale: OrderProcessingService.js has 67 co-changes with label generation code
  - Suggested validation: Run orderSummary/*.spec.ts, verify order status updates correctly
  - 💡 *Review*: Does your implementation touch order state?

### 2. Suggested Regression Test Plan

**Automated Tests (Starting Point):**

| Test Suite | Priority | Reason | Review Needed? |
|------------|----------|--------|----------------|
| `orderGrid/labelGenerationFromGrid/*.spec.ts` | MUST | Direct test coverage | ✓ Confirm scope |
| `packagingTypes/*.spec.ts` | MUST | Direct test coverage | ✓ Confirm scope |
| `specialServices/*.spec.ts` | MUST | Direct test coverage | ✓ Confirm scope |
| `orderGrid/actionMenu/*.spec.ts` | SHOULD | bulkactionHelper.js 45× co-changes | ✓ Check if coupling touched |
| `orderSummary/*.spec.ts` | SHOULD | OrderProcessingService.js 67× co-changes | ✓ Check if coupling touched |
| `carrierOtherDetails/*.spec.ts` | CONSIDER | carrier-config area coupling (8 tickets) | ✓ Verify relevance |

💡 **Review**: Adjust priorities based on your implementation plan. Some tests may not be relevant to your approach.

**Suggested Manual Test Scenarios:**

- **Scenario: Generate international labels with customs data**
  - Why: international ↔ label-generation co-occur in 12 tickets
  - Suggested steps: (from ZI-156) Create order with international destination, add customs info, generate label, verify customs declaration on label
  - 💡 *Review*: Read wiki/zendesk/summaries/ZI-156.md for full context

- **Scenario: Label generation after carrier credential update**
  - Why: carrier-config ↔ label-generation co-occur in 8 tickets
  - Suggested steps: (from ZI-187) Update FedEx credentials, generate labels for multiple carriers, verify all succeed
  - 💡 *Review*: Adapt if your change doesn't touch carrier config

### 3. Suggested Code Review Checklist

- [ ] **server/src/shared/orders/OrderProcessingService.js** (67× co-changes)
  - Suggested focus: Order state transitions, data integrity
  - Areas to review: Label generation hooks, order status updates
  - 💡 *Review*: Only include if your changes interact with this file

- [ ] **server/src/shared/orders/bulkactionHelper.js** (45× co-changes)
  - Suggested focus: Batch operation logic, error handling
  - Areas to review: Bulk label generation, transaction rollback
  - 💡 *Review*: Check git history to understand coupling

- [ ] **server/src/routes/orders.js** (34× co-changes)
  - Suggested focus: API endpoint contracts, request validation
  - Areas to review: Label generation endpoints, response formats
  - 💡 *Review*: Only if your change touches API layer

- [ ] **server/src/shared/API/carriers/CarrierAdaptorFactory.js** (28× co-changes)
  - Suggested focus: Carrier routing logic, adapter selection
  - Areas to review: Label API calls, carrier-specific formatting
  - 💡 *Review*: Only if your change affects carrier interactions

💡 **Review**: Cross-reference with your implementation plan. Exclude files your approach won't touch.

### 4. Suggested Customer Validation Scenarios

1. **International shipping workflows**
   - Derived from: ZI-156, ZI-169, ZI-203 (12 related tickets)
   - Suggested test: End-to-end international order → label with customs → shipment tracking
   - Expected: All customs fields appear correctly, label generates without errors
   - 💡 *Review*: Read full summaries for context, adapt to your change

2. **Multi-carrier label generation**
   - Derived from: ZI-187, ZI-201 (8 related tickets)
   - Suggested test: Generate labels for FedEx, UPS, USPS in same batch
   - Expected: All labels generate correctly, no carrier-specific failures
   - 💡 *Review*: May not apply if your change is carrier-agnostic

3. **Order status accuracy after label generation**
   - Derived from: ZI-144, ZI-178 (6 related tickets)
   - Suggested test: Generate label, check order status, verify tracking number stored
   - Expected: Order transitions to correct state, tracking visible in grid
   - 💡 *Review*: Only if your change touches order state management

---

## How to Use These Recommendations

1. **Start here**: Use as a checklist during card planning
2. **Review & filter**: Remove items not relevant to your implementation approach
3. **Adapt & expand**: Modify based on domain knowledge and specific requirements
4. **Cross-reference**: Read ticket summaries and module pages for full context
5. **Iterate**: Update as you learn more during implementation

**Summary**: 3 suggested acceptance criteria, 9 test suites, 4 review files, 3 customer scenarios
```

---

## Integration with Card Analysis Workflow

This skill should be invoked **automatically when analyzing any card** that involves code changes.

### When to Use

**Always run during card analysis** for:
- Feature implementation cards
- Bug fix cards that touch code
- Refactoring or tech debt cards
- Migration cards (e.g., API version upgrades)

**Skip for**:
- Documentation-only changes
- Configuration changes (no code)
- Lifecycle/onboarding tickets (no implementation)

### How to Integrate

**Two workflows available**:

**A. Known Target (area/file already identified)**:
1. Extract the target from the card (area or file)
2. Run `/find-co-dependencies query <target>`
3. Include technical coupling in card analysis

**B. Unfamiliar Feature (don't know what modules it touches)**:
1. Run `/find-co-dependencies semantic <card-description>` OR `/find-co-dependencies full <card-description>`
2. Semantic mode identifies conceptually related modules
3. Full mode provides both semantic + technical coupling in one pass
4. Include complete blast radius in card analysis

**Recommended**: Use `full` mode for initial card analysis — provides comprehensive view.

### Integration Steps

1. **Extract the target from the card**:
   - Feature area mentioned (e.g., "label generation") → use `query` mode
   - Specific files mentioned → use `query` mode
   - Module/domain mentioned → map to area, use `query` mode
   - **Unclear or unfamiliar feature** → use `semantic` or `full` mode

2. **Run the analysis**:
   ```bash
   # Known target
   /find-co-dependencies query <target>

   # Unfamiliar feature (semantic only)
   /find-co-dependencies semantic <card-description>

   # Unfamiliar feature (complete analysis)
   /find-co-dependencies full <card-description>
   ```

3. **Include results in card analysis**:
   - Add **Blast Radius** section to card notes/summary
   - List required test suites in acceptance criteria
   - Flag high-risk co-dependencies for code review scope
   - Note customer-facing areas for regression testing

4. **Update acceptance criteria**:
   - All direct tests must pass
   - High-coupling partners (≥10 co-changes) need spot-check review
   - ZI area partners need exploratory testing if strong overlap (≥3 tickets)

### Example Workflow

**Card**: "Add customs declaration support for FedEx REST"

**Step 1 - Extract target**:
- Card mentions FedEx + customs → map to `international` area
- Also mentions REST migration → check `carrier-migration` area

**Step 2 - Run query**:
```bash
/find-co-dependencies query international
```

**Step 3 - Analyze output**:
- Test coverage: 10 direct tests in specialServices/
- Code coupling: High coupling with carriers/ and orders/
- ZI overlap: international ↔ label-generation (8 tickets)

**Step 4 - Update card**:

Option A — Manual extraction from blast-radius:
```markdown
## Acceptance Criteria
- [ ] All customs fields saved correctly
- [ ] FedEx REST API integration working
- [ ] All 10 international tests passing
- [ ] No regression in label-generation workflow (blast-radius risk)

## Test Plan
- Run specialServices/*.spec.ts (direct)
- Run labelGenerationFromGrid/*.spec.ts (coupling risk)
- Manual: Verify customs on non-FedEx carriers (ZI-156, ZI-169)

## Code Review Focus
- CarrierAdaptorFactory changes
- OrderHelper customs logic
```

Option B — Use `--derive-actionable-items` flag:
```bash
/find-co-dependencies query international --derive-actionable-items
```
Copy the "🎯 Actionable Items" section directly into the card.

---

## Semantic Mode

**Input**: File path to feature card OR inline card description text

**Output**: List of wiki modules semantically likely to be affected by this feature

**Purpose**: Identify conceptual coupling when you know what you're building but don't know what architectural surface it touches.

### Step 1 — Read Card Content

Parse the input:
- If input is a file path to a markdown file → read file content
- Otherwise → treat entire input as card description text

Extract from the card:
- Feature title / summary
- Problem statement
- User stories / acceptance criteria
- Mentioned features, areas, or domains

### Step 2 — Build Module Catalog

Read `wiki/index.md` to extract all documented modules with their descriptions.

Use this Python script:

```bash
python3 << 'PYEOF'
import re, json, os

# Detect wiki root
wiki_root = os.getcwd()
while wiki_root != '/':
    if (os.path.isfile(os.path.join(wiki_root, 'CLAUDE.md')) and
        os.path.isdir(os.path.join(wiki_root, 'wiki')) and
        os.path.isdir(os.path.join(wiki_root, 'raw'))):
        break
    wiki_root = os.path.dirname(wiki_root)
else:
    print("Error: Could not find wiki root", file=sys.stderr)
    exit(1)

try:
    with open(os.path.join(wiki_root, "wiki/index.md")) as f:
        content = f.read()
except FileNotFoundError:
    print("⚠️  wiki/index.md not found")
    exit(1)

# Extract module links from index
# Format: - [Module Name](path/to/module.md) - Description
modules = []
for line in content.split('\n'):
    match = re.search(r'-\s+\[([^\]]+)\]\(([^)]+\.md)\)\s+-\s+(.+)', line)
    if match:
        name = match.group(1)
        path = match.group(2)
        desc = match.group(3)
        modules.append({
            'name': name,
            'path': os.path.join(wiki_root, "wiki", path),
            'description': desc
        })

# For each module, read its Overview section
enriched = []
for mod in modules:
    try:
        with open(mod['path']) as f:
            content = f.read()
            # Extract Overview section
            overview_match = re.search(r'## Overview\s*\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
            overview = overview_match.group(1).strip()[:400] if overview_match else mod['description']

            # Extract domain from frontmatter
            domain_match = re.search(r'^domain:\s*(.+)$', content, re.MULTILINE)
            domain = domain_match.group(1).strip() if domain_match else 'unknown'

            enriched.append({
                'name': mod['name'],
                'path': mod['path'],
                'domain': domain,
                'description': mod['description'],
                'overview': overview
            })
    except FileNotFoundError:
        enriched.append(mod)

# Output module catalog
for m in enriched:
    print(f"- **{m['name']}** (domain: {m['domain']})")
    print(f"  Path: {m['path']}")
    print(f"  Description: {m['description']}")
    if 'overview' in m:
        print(f"  Overview: {m['overview']}")
    print()
PYEOF
```

Store the output as `MODULE_CATALOG` for the next step.

### Step 3 — LLM Semantic Analysis

**This is an LLM reasoning task.** Use direct analysis (not Task tool) to identify semantically related modules.

**Analysis Prompt** (internal reasoning):

```text
Given this feature card:
{CARD_CONTENT}

And these available modules:
{MODULE_CATALOG}

Identify which modules are semantically likely to be affected.

Consider:
1. **Direct involvement**: Modules explicitly mentioned or obviously required
2. **Data flow**: If the feature touches data, what creates/reads/updates that data?
3. **User journey**: What steps in the user workflow might be affected?
4. **Validation/rules**: What business logic might need updating?
5. **Integration points**: What external systems or APIs might be involved?
6. **Conceptual coupling**: What related features share concepts?
   - Example: "labels" → "manifests" → "carriers"
   - Example: "orders" → "products" → "inventory"
   - Example: "rates" → "carriers" → "configuration"

For each affected module:
- Module name
- Coupling type: direct | data-flow | workflow | validation | integration | conceptual
- Confidence: high | medium | low
- Reasoning: 1-2 sentences

Sort by confidence (high → medium → low).
```

**Execute the analysis** and format the output.

### Step 4 — Format Output

Present the semantic blast radius report:

```text
# Semantic Blast Radius: {feature-title}

**Analysis**: Identified N modules semantically likely to be affected

## High Confidence (direct involvement)

- **[Module Name](path/to/module.md)** — {coupling-type}
  {reasoning - why this module is affected}

## Medium Confidence (indirect coupling)

- **[Module Name](path/to/module.md)** — {coupling-type}
  {reasoning}

## Low Confidence (possible side effects)

- **[Module Name](path/to/module.md)** — {coupling-type}
  {reasoning}

## Recommendations

Based on this semantic analysis:

1. **Must Review**: {list high-confidence modules}
2. **Should Review**: {list medium-confidence modules}
3. **Consider**: {list low-confidence modules}

**Next Steps**:
- Run `/find-co-dependencies query <area>` for each identified module to get technical coupling
- Cross-reference with test coverage in features.md
- Review module pages to understand implementation details
```

---

## Full Mode

**Input**: File path to feature card OR inline card description text

**Output**: Complete blast-radius analysis combining semantic + technical coupling

**Purpose**: One-shot comprehensive analysis for card planning.

### Workflow

1. **Run Semantic Analysis** (Semantic Mode Step 1-4)
   - Identify conceptually related modules
   - Categorize by confidence level

2. **For each HIGH confidence module**:
   - Map module to ZI area or file path
   - Run Query Mode analysis to get technical coupling (test + code + ZI)
   - Aggregate results

3. **Format Combined Report**:

```text
# Complete Blast Radius: {feature-title}

## Semantic Analysis

{output from semantic mode}

---

## Technical Coupling (High Confidence Modules)

### Module: {module-name-1}

{output from query mode for this module's area}

### Module: {module-name-2}

{output from query mode for this module's area}

---

## Unified Recommendations

### Test Strategy
- Direct tests to run: {aggregate from all modules}
- Indirect tests (co-change): {aggregate from all modules}

### Code Review Focus
- High-frequency coupling: {files with ≥10 co-changes across all modules}
- Medium coupling: {files with 3-9 co-changes}

### Customer Validation
- ZI areas with strong overlap: {areas with ≥3 tickets}
- Related tickets: {ticket numbers}

### Implementation Checklist
- [ ] Review {N} high-confidence modules
- [ ] Run {M} test suites
- [ ] Check {P} high-coupling files for side effects
- [ ] Validate {Q} customer scenarios from ZI issues
```

**Use case**: Initial card analysis — provides both "what conceptually relates?" and "what technically couples?" in one pass.

---

## Build Mode

Rebuild all three dependency maps in topological order.

**Dependencies:**
1. Zendesk summaries must exist first (for zendesk-overlap)
2. All three maps are otherwise independent
3. Order: zendesk-overlap → reverse-test-coverage → git-co-change-graph

**Rationale**: Build zendesk first since it's fastest and most likely to be stale, then test coverage (medium), then git co-change (slowest).

### Step 1 — Check Prerequisites

```bash
# Check if zendesk summaries exist
if [ ! -d "wiki/zendesk/summaries" ] || [ -z "$(ls -A wiki/zendesk/summaries)" ]; then
    echo "⚠️  No Zendesk summaries found — run /zendesk-summarize first"
    exit 1
fi

# Check if test automation exists
if [ ! -d "raw/mcsl-test-automation" ]; then
    echo "⚠️  Test automation submodule not found at raw/mcsl-test-automation"
    exit 1
fi

# Check if codebase submodule exists
if [ ! -d "raw/storepep-react" ]; then
    echo "⚠️  Codebase submodule not found at raw/storepep-react"
    exit 1
fi
```

### Step 2 — Build Zendesk Overlap

Use the Skill tool to invoke zendesk-overlap:

```
Skill(skill="zendesk-overlap", args="build")
```

Wait for completion. Check output for errors.
If error: report to user and stop cascade.

### Step 3 — Build Reverse Test Coverage

Use the Skill tool to invoke reverse-test-coverage:

```
Skill(skill="reverse-test-coverage", args="build")
```

Wait for completion. Check output for errors.
If error: report to user and stop cascade.

### Step 4 — Build Git Co-Change Graph

Use the Skill tool to invoke git-co-change-graph:

```
Skill(skill="git-co-change-graph", args="delta")
```

Wait for completion. Check output for errors.
If error: report to user and stop cascade.

### Step 5 — Report Summary

Combine results from all three skills and report:

```text
# Dependency Map Build Complete

## Zendesk Area Coupling
- Tickets analyzed: N
- ZI issues: M
- Area pairs: P
- Wiki: wiki/zendesk/area-coupling.md
- Status: ✅ Complete

## Reverse Test Coverage
- Source files: X
- Test files: Y
- Direct coverage entries: Z
- Wiki: wiki/architecture/reverse-test-coverage.md
- Status: ✅ Complete

## Git Co-Change Graph
- File pairs: A
- Commits analyzed: B
- Coupling threshold: ≥3
- Wiki: wiki/architecture/coupling-map.md
- Status: ✅ Complete

All three dependency maps are now synchronized.

Use `/find-co-dependencies query <file-or-area>` to query.
```

---

## Delta Mode

Update all three maps incrementally.

### Step 1 — Check Prerequisites

Same as Build Mode Step 1.

### Step 2 — Run Delta Updates

Use the Skill tool to invoke each dependency skill's delta mode in sequence:

1. **Zendesk Overlap**:
   ```
   Skill(skill="zendesk-overlap", args="delta")
   ```
   Wait for completion. Check output for errors.
   If error: report to user and stop cascade.

2. **Reverse Test Coverage**:
   ```
   Skill(skill="reverse-test-coverage", args="delta")
   ```
   Wait for completion. Check output for errors.
   If error: report to user and stop cascade.

3. **Git Co-Change Graph**:
   ```
   Skill(skill="git-co-change-graph", args="delta")
   ```
   Wait for completion. Check output for errors.
   If error: report to user and stop cascade.

Capture results from each skill invocation.

### Step 3 — Report Summary

Combine delta results from all three skills and report:

```text
# Dependency Map Delta Update Complete

## Zendesk Area Coupling
- New ZI issues: N
- New area pairs: M
- Wiki: wiki/zendesk/area-coupling.md
- Status: ✅ Updated

## Reverse Test Coverage
- New source files: X
- New test files: Y
- Wiki: wiki/architecture/reverse-test-coverage.md
- Status: ✅ Updated

## Git Co-Change Graph
- New commits: A
- New file pairs: B
- Wiki: wiki/architecture/coupling-map.md
- Status: ✅ Updated

All three maps updated incrementally.
```

---

## Error Handling

| Case | Action |
|------|--------|
| No zendesk summaries | Hard error: run `/zendesk-summarize` first |
| No test automation submodule | Hard error: check `raw/mcsl-test-automation` |
| No codebase submodule | Hard error: check `raw/storepep-react` |
| Missing wiki files in query mode | Warn and suggest running `/find-co-dependencies build` |
| Query target not found | Suggest similar targets if possible |
| Skill invocation fails in build/delta | Capture error, report to user, stop cascade |
| One dimension unavailable in query | Show other two dimensions, warn about missing data |

---

## Output

**Query mode**: Text report to stdout (shown to user)
- Reads from: `wiki/architecture/coupling-map.md`, `wiki/architecture/reverse-test-coverage.md`, `wiki/zendesk/area-coupling.md`
- Writes: Nothing (read-only queries)

**Build mode**: Status updates + final summary
- Invokes: `/zendesk-overlap build`, `/reverse-test-coverage build`, `/git-co-change-graph delta`
- Writes: Nothing directly (delegated skills write their own wiki files)

**Delta mode**: Status updates + final summary
- Invokes: `/zendesk-overlap delta`, `/reverse-test-coverage delta`, `/git-co-change-graph delta`
- Writes: Nothing directly (delegated skills write their own wiki files)

This skill orchestrates other skills and queries their wiki outputs.

---

## Examples

**Query a file (technical coupling):**
```bash
/find-co-dependencies query server/src/shared/orders/OrderProcessingService.js
```

**Query an area (technical coupling):**
```bash
/find-co-dependencies query label-generation
```

**Query with actionable items:**
```bash
/find-co-dependencies query label-generation --derive-actionable-items
```

**Semantic analysis from card file:**
```bash
/find-co-dependencies semantic wiki/product/features/dangerous-goods.md
```

**Semantic analysis from text:**
```bash
/find-co-dependencies semantic "Add support for Saturday delivery as a special service option"
```

**Complete analysis (semantic + technical):**
```bash
/find-co-dependencies full wiki/product/features/customs-declarations.md
```

**Complete analysis with actionable items (recommended for card planning):**
```bash
/find-co-dependencies full wiki/product/features/customs-declarations.md --derive-actionable-items
```

**Rebuild all maps:**
```bash
/find-co-dependencies build
```

**Update all maps:**
```bash
/find-co-dependencies delta
```

---

## Related Skills

This skill orchestrates these dependency analysis skills:
- `/zendesk-overlap` - ZI area co-occurrence analysis
- `/reverse-test-coverage` - Source → test mapping
- `/git-co-change-graph` - File co-change coupling

## Four Dimensions of Blast Radius

This skill provides **four dimensions** of dependency analysis:

### Technical Coupling (Query Mode)
1. **Test Coverage** — What tests cover this code? (from reverse-test-coverage)
2. **Code Coupling** — What files change together? (from git-co-change-graph)
3. **ZI Area Coupling** — What areas break together in customer reports? (from zendesk-overlap)

### Semantic Coupling (Semantic/Full Mode)
4. **Semantic Coupling** — What modules are conceptually related to this feature? (LLM-assisted)

**Modes**:
- `query <file-or-area>` — Technical coupling only (dimensions 1-3)
- `semantic <card>` — Semantic coupling only (dimension 4)
- `full <card>` — Complete analysis (all 4 dimensions)

**Recommended workflow**:
- **Known target**: Use `query` mode for direct technical analysis
- **Unfamiliar feature**: Use `full` mode for comprehensive semantic + technical analysis
