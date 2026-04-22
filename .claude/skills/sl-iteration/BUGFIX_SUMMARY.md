# Snapshot State Detection Bug Fix - Summary

## Problem

The snapshot command showed all 26 cards as "Open (not started)" when several cards actually had "Dev Done", "QA_VERIFIED", and other state labels.

**Root causes:**
1. Hard-coded state label IDs instead of using actual IDs fetched from the board
2. Missing QA_VERIFIED label in state detection
3. No validation to catch state detection failures

## What Was Fixed

### 1. Updated SKILL.md with Enhanced State Detection

**File**: `.claude/skills/sl-iteration/SKILL.md`

#### 1.1 New 6-State Legend (was 5-state)

Renamed "PROD" to "Shipped" and added new "Ready To Ship" state:

| State | ph-WIP Labels | Meaning |
|-------|---------------|---------|
| **Shipped** | SHIPPED, PROD | Deployed to production |
| **Ready To Ship** | QA_VERIFIED | QA verified, ready to deploy (NEW) |
| BUG REPORTED | BUG REPORTED | Bug found in QA |
| QA READY | QA Reported, Ready for QA, Dev Done | In QA testing (not verified yet) |
| DEV | DEV | Active development |
| Open (not started) | (no label) | Not started |

**Key change**: QA_VERIFIED is now "Ready To Ship" instead of "QA READY"

#### 1.2 Enhanced `resolve_ph_wip_state_labels()` Function

Added **mandatory validation** after fetching labels:

```python
# Fetch labels with limit=1000 (critical!)
GET /boards/{ph_wip_board_id}/labels?fields=name,color,id&limit=1000

# Build state label map
state_label_map = {}
for state_name in ['SHIPPED', 'PROD', 'QA_VERIFIED', 'QA Reported', 'Ready for QA', 'Dev Done', 'DEV', 'BUG REPORTED']:
    matching_labels = [lbl for lbl in labels if lbl['name'].strip().lower() == state_name.lower()]
    state_label_map[state_name] = {lbl['id'] for lbl in matching_labels}

# CRITICAL VALIDATION
CRITICAL_LABELS = ['Dev Done', 'QA_VERIFIED', 'PROD', 'SHIPPED', 'DEV']
missing = [name for name in CRITICAL_LABELS if not state_label_map.get(name)]

if missing:
    raise Exception(f"❌ CRITICAL: Missing state labels on ph-WIP: {missing}")
```

**Why this prevents the bug:**
- Always fetches labels dynamically (never hard-codes IDs)
- Uses `limit=1000` (default is only 50, causing silent truncation)
- Validates that critical labels exist before proceeding
- Fails fast with clear error message if labels are missing

#### 1.3 New Step 7: Post-Detection Verification

Added verification step to catch state detection failures:

```python
# Pick 3 sample cards from each non-empty state bucket
# For each sample, fetch from Trello and verify actual labels match expected state
# Report mismatches immediately

STATE_EXPECTATIONS = {
    'Shipped': ['SHIPPED', 'PROD'],
    'Ready To Ship': ['QA_VERIFIED'],
    'QA READY': ['Dev Done', 'Ready for QA', 'QA Reported'],
    'DEV': ['DEV'],
    'BUG REPORTED': ['BUG REPORTED'],
    'Open': []  # No state labels
}
```

**Output includes verification table:**
```
## Verification: Trello vs Release File

| State | Release Count | Sample Cards Checked | Mismatches |
|-------|---------------|---------------------|------------|
| Shipped | 0 | 0 | 0 ✓ |
| Ready To Ship | 3 | 3 | 0 ✓ |
| QA READY | 18 | 3 | 0 ✓ |
| DEV | 0 | 0 | 0 ✓ |
| Open | 5 | 3 | 0 ✓ |

Sample spot-checks:
- ZI-048 (Ready To Ship): has QA_VERIFIED label ✓
- ZI-071 (QA READY): has Dev Done label ✓
- ZI-058 (Open): no state labels ✓
```

#### 1.4 Enhanced Step 8 Report

Added diagnostic output to every snapshot:

```
## Snapshot MCSL 377
- File: wiki/product/releases/MCSL-377.md (refreshed)
- Board: 63e1e0414b6026c45be1087c
- Cards total: 26  (Shipped: 0, Ready To Ship: 3, Support Closed: 0, BUG REPORTED: 0, QA READY: 18, DEV: 0, Open: 5)
- State labels found: 8/8 ✓
  - SHIPPED: 1 label(s)
  - PROD: 1 label(s)
  - QA_VERIFIED: 1 label(s)
  - Dev Done: 1 label(s)
  - DEV: 1 label(s)
  - QA Reported: 1 label(s)
  - Ready for QA: 2 label(s)
  - BUG REPORTED: 1 label(s)
- Verification: 9 sample cards checked, 0 mismatches ✓
- git_reference: 2f900682c634fd789a1374aa61a107c0bc601d81
- Cards missing close-reason: 0
- Cards without ph-WIP match: 0
- Drift: 0 cards dropped since last snapshot
- Warnings: None
```

**Why this helps:**
- Shows exactly which labels were found (catches "0 labels found" immediately)
- Reports verification results inline
- Makes it obvious when state detection fails

### 2. Created Standalone Validation Script

**File**: `.claude/skills/sl-iteration/validate_snapshot.py`

**Purpose**: Run after any snapshot to verify correctness against live Trello data.

**Usage:**
```bash
python3 .claude/skills/sl-iteration/validate_snapshot.py MCSL-377
```

**What it validates:**

1. **State detection accuracy**
   - Fetches sample cards from each state bucket in the release file
   - Fetches actual labels from Trello for those cards
   - Verifies the detected state matches the actual labels
   - Reports mismatches with card names, URLs, and label details

2. **Label availability**
   - Confirms all 8 state labels exist on the board
   - Fails if critical labels (SHIPPED, PROD, QA_VERIFIED, Dev Done, DEV) are missing
   - Warns if optional labels (QA Reported, Ready for QA, BUG REPORTED) are missing

3. **Count consistency**
   - Verifies frontmatter counts match Summary table counts
   - Catches markdown formatting errors or calculation bugs

**Exit codes:**
- `0` - All validations passed ✓
- `1` - Validation failures found
- `2` - Error (missing file, API failure, etc.)

**Example output:**
```
======================================================================
VALIDATE SNAPSHOT: MCSL-377
======================================================================

Step 1: Parsing release file wiki/product/releases/MCSL-377.md...
  ✓ Release file parsed
  ✓ Board: 63e1e0414b6026c45be1087c
  ✓ Lane filter: SL MCSL 377: Iteration backlog
  ✓ Total cards in file: 26

Step 2: Fetching labels from board...
  ✓ Fetched 174 labels
  ✓ All critical state labels found

Step 3: Verifying sample cards against live Trello state...
  ✓ XOMzbVqD: Ready To Ship (label: QA_VERIFIED)
  ✓ 5IrdjdB5: Ready To Ship (label: QA_VERIFIED)
  ✓ 6d6xn2el: Ready To Ship (label: QA_VERIFIED)
  ✓ Nad1fC51: QA READY (label: Dev Done)
  ✓ gvXEqh1o: QA READY (label: Dev Done)
  ✓ vxt5hVgw: QA READY (label: Dev Done)
  ✓ sSi9UvRe: Open (not started) (label: None)
  ✓ zeDfg5F5: Open (not started) (label: None)
  ✓ v6cIPFyE: Open (not started) (label: None)

Step 4: Validating count consistency...
  ✓ Frontmatter and table counts match

======================================================================
VALIDATION SUMMARY
======================================================================

✓ Cards checked: 9
✓ State labels found: 8/8

✅ ALL VALIDATIONS PASSED
   No state mismatches, no count discrepancies
```

**When to run:**
- After first snapshot (baseline creation)
- After any changes to board labels
- If state counts look suspicious
- Periodically as a health check

### 3. Fixed MCSL-377.md Release File

**File**: `wiki/product/releases/MCSL-377.md`

**Before (all wrong):**
- QA READY: 0
- DEV: 0
- Open (not started): 26

**After (correct):**
- Shipped: 0
- Ready To Ship: 3 (ZI-048, ZI-035, ZI-046)
- QA READY: 18 (ZI-071, ZI-041, ZI-033, etc.)
- DEV: 0
- Open (not started): 5 (ZI-058, ZI-043, ZI-023, ZI-051, ZI-018)

**Updated frontmatter:**
```yaml
cards_total: 26
cards_shipped: 0
cards_ready_to_ship: 3  # NEW FIELD
cards_support_closed: 0
cards_bug_reported: 0
cards_open: 26  # Excludes shipped, includes Ready To Ship
```

**Updated Summary table:**
```markdown
| State | Count |
|-------|-------|
| Shipped | 0 |
| Ready To Ship | 3 |  ← NEW STATE
| Support Closed | 0 |
| BUG REPORTED | 0 |
| QA READY | 18 |  ← Was 0, now correct
| DEV | 0 |
| Open (not started) | 5 |  ← Was 26, now correct
| **Total** | **26** |
```

**Updated Legend:**
```markdown
- **Shipped** — deployed to production (ph-WIP SHIPPED or PROD label)
- **Ready To Ship** — QA verified, ready to deploy (ph-WIP QA_VERIFIED label) ← NEW
- **QA READY** — code complete, in QA (ph-WIP Dev Done, Ready for QA, or QA Reported labels — NOT yet verified)
- **DEV** — active development (ph-WIP DEV label)
- **Open (not started)** — in product backlog but dev hasn't started (no ph-WIP state label)
```

## How to Prevent This Bug in the Future

### 1. **Always Run Validation After Snapshot**

```bash
# After running snapshot
/sl-iteration snapshot MCSL-377

# Immediately validate
python3 .claude/skills/sl-iteration/validate_snapshot.py MCSL-377

# Exit code 0 = success, 1 = failures, 2 = error
```

### 2. **Never Hard-Code Label IDs**

**Bad (causes the bug):**
```python
state_label_map = {
    'Dev Done': {'69dee68e859ad71d70b6f49c'},  # WRONG - hard-coded ID
    'QA_VERIFIED': {'69dee61cee9cf0cd01bbd7f8'},  # WRONG
}
```

**Good (prevents the bug):**
```python
# Always fetch labels dynamically
labels = fetch_json(f"{BASE_URL}/boards/{board_id}/labels?fields=name,id&limit=1000")

state_label_map = {}
for state_name in STATE_LABEL_NAMES:
    matching = [lbl for lbl in labels if lbl['name'].lower() == state_name.lower()]
    state_label_map[state_name] = {lbl['id'] for lbl in matching}
```

### 3. **Always Use limit=1000 When Fetching Labels**

The default limit is **50 labels**, but ph-WIP has **174+ labels**. Without `limit=1000`, you get silent truncation and miss critical state labels.

**Wrong:**
```bash
GET /boards/{id}/labels  # Only returns 50 labels!
```

**Correct:**
```bash
GET /boards/{id}/labels?limit=1000  # Returns all labels
```

### 4. **Check Validation Output in Snapshot Report**

The snapshot command now outputs diagnostic info. Look for:

```
- State labels found: 8/8 ✓  ← Should be 8/8, not 0/8!
  - SHIPPED: 1 label(s)  ← Should be >0, not 0!
  - PROD: 1 label(s)
  - QA_VERIFIED: 1 label(s)  ← This was missing before!
  - Dev Done: 1 label(s)
  ...
- Verification: 9 sample cards checked, 0 mismatches ✓  ← Should be 0 mismatches!
```

**Red flags:**
- "State labels found: 0/8" or "3/8" → labels not fetched correctly
- "Dev Done: 0 label(s)" → critical label missing
- "Verification: X mismatches" → state detection is wrong

### 5. **Spot-Check Against Trello**

After any suspicious snapshot (e.g., all cards showing as "Open"):

1. Pick 2-3 cards from different states in the release file
2. Open them in Trello
3. Verify they have the expected labels

**Example:**
- Release file says ZI-048 is "Ready To Ship"
- Open https://trello.com/c/XOMzbVqD in browser
- Verify it has "QA_VERIFIED" label ✓

## Verification of Fix

Ran the updated snapshot command and validation on MCSL-377:

**Result:**
- ✅ 26 cards processed
- ✅ 8/8 state labels found
- ✅ 9 sample cards verified against Trello
- ✅ 0 state mismatches
- ✅ 0 count discrepancies

**State distribution:**
- Shipped: 0
- Ready To Ship: 3 (QA_VERIFIED label)
- QA READY: 18 (Dev Done, Ready for QA, QA Reported labels)
- DEV: 0
- Open: 5 (no state labels)

## Files Changed

1. `.claude/skills/sl-iteration/SKILL.md` - Enhanced with validation, 6-state legend, mandatory label checks
2. `.claude/skills/sl-iteration/validate_snapshot.py` - New standalone validation script
3. `wiki/product/releases/MCSL-377.md` - Regenerated with correct state detection
4. `.claude/skills/sl-iteration/BUGFIX_SUMMARY.md` - This file

## Summary

**Root cause**: Hard-coded label IDs instead of dynamic fetching

**Fix**:
1. Always fetch labels dynamically with `limit=1000`
2. Validate critical labels exist
3. Verify sample cards against Trello
4. Provide diagnostic output in every snapshot

**Prevention**:
1. Run `validate_snapshot.py` after every snapshot
2. Check validation output for "State labels found: 8/8 ✓"
3. Never hard-code label IDs
4. Spot-check suspicious results against Trello

**Impact**: Bug cannot recur because:
- Skill now fetches labels dynamically (not hard-coded)
- Validation script catches state detection failures immediately
- Diagnostic output makes failures obvious
- Multiple layers of verification (inline + standalone script)
