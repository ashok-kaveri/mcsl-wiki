---
name: sl-iteration
description: Copy release-tagged cards from StoryLab to ph-WIP as iteration backlog, run AI code analysis on ph-WIP cards, and run the release closure workflow (sync / snapshot / ship) for a release tag. Use when the user wants to plan an iteration, move story cards to ph-WIP, analyze cards, sync Zendesk deltas to a release, snapshot a release's Trello state into the wiki, ship/close a release, or says "sl-iteration".
argument-hint: <release-tag> | <release-tag> ZI-NNN | analyze <tag> <ZI-NNN|next|all|@name> | reassess <ZI-NNN> | remove <release-tag> ZI-NNN | sync <tag> [board] [lane] [--no-sync] | snapshot <tag> [board] [lane] [--no-sync] | ship <tag> [board] [lane] [--no-sync] [--force]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, WebFetch, TodoWrite, AskUserQuestion
disable-model-invocation: false
---

# StoryLab to ph-WIP Iteration Backlog, plus Release Closure

Five modes:
- **copy** (Mode 1): move StoryLab cards tagged with a release label into a ph-WIP `SL <tag>: Iteration backlog` lane.
- **analyze** (Mode 2): run AI code analysis on ph-WIP cards; classify confidence; update StoryLab dev-status labels.
- **release** (Mode 3): close the loop between Trello + Zendesk and the wiki via three read-leaning subcommands — `sync`, `snapshot`, `ship`.
- **copy-single** (Mode 4): move a single StoryLab card (by ZI ID) from default StoryLab board to ph-WIP `SL <tag>: Iteration backlog` lane with duplicate check.
- **remove-tag** (Mode 5): remove a release tag label from a ph-WIP card.

**Arguments**:
- `<release-tag-name>` — Mode 1 copy all tagged cards
- `release-single <release-tag> ZI-NNN` — Mode 4 copy a single card by ZI ID (always from default StoryLab to standard ph-WIP lane)
- `analyze <release-tag> <ZI-NNN>` — Mode 2 analyze a specific card
- `analyze <release-tag> next` — Mode 2 analyze the next unanalyzed card in the named ph-WIP lane
- `analyze <release-tag> all` — Mode 2 analyze all unanalyzed cards in the named ph-WIP lane
- `analyze <release-tag> @<name>` — Mode 2 analyze only cards assigned to a member (matches by username or full name)
- `reassess <ZI-NNN>` — Mode 2 re-run analysis (ph-WIP lane auto-detected)
- `remove <release-tag> ZI-NNN` — Mode 5 remove release tag label from a ph-WIP card
- `sync <release-tag> [board] [lane]` — Mode 3a: diff Zendesk JSONs vs the release's last `git_reference`, regen summaries, post compact delta comments on tagged StoryLab cards (optionally filtered to a specific lane)
- `snapshot <release-tag> [board] [lane]` — Mode 3b: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current StoryLab + ph-WIP state (optionally filtered to a specific lane)
- `ship <release-tag> [board] [lane] [--force]` — Mode 3c: freeze the release in wiki (status=shipped, backlog + log updates); no Trello writes (optionally filtered to a specific lane)

**Lane resolution (Mode 2 only)**: The `<release-tag>` in analyze commands identifies the ph-WIP lane `SL <release-tag>: Iteration backlog`. If the lane doesn't exist, list all `SL *` lanes and ask user to pick.

**Board default (Mode 3)**: StoryLab (`69dd9134576a26fcb79b670d`) when `[board]` is omitted.

**Examples**:
- `/sl-iteration MCSL 377` — Mode 1 copy all release-tagged cards
- `/sl-iteration release-single MCSL 377 ZI-035` — Mode 4 copy single card ZI-035 to ph-WIP
- `/sl-iteration remove MCSL 377 ZI-035` — Mode 5 remove MCSL 377 tag from ZI-035 in ph-WIP
- `/sl-iteration analyze MCSL 377 all` — Mode 2 analyze all cards in `SL MCSL 377: Iteration backlog`
- `/sl-iteration analyze MCSL 377 @ajeesh` — Mode 2 analyze cards assigned to Ajeesh
- `/sl-iteration analyze MCSL 377 ZI-035` — Mode 2 analyze ZI-035
- `/sl-iteration snapshot MCSL 377` — Mode 3b first-time snapshot (creates release.md baseline)
- `/sl-iteration snapshot MCSL 377 63e1e0414b6026c45be1087c SL MCSL 377: Iteration backlog` — Mode 3b snapshot from ph-WIP board, filtered to specific lane
- `/sl-iteration snapshot MCSL 377 --no-sync` — Mode 3b snapshot, skip submodule updates
- `/sl-iteration sync MCSL 377` — Mode 3a delta sync (snapshot must have run first)
- `/sl-iteration ship MCSL 377 --force` — Mode 3c ship even with non-terminal cards
- `/sl-iteration ship MCSL 377 --no-sync --force` — Mode 3c ship with multiple flags

## Dispatch

Parse `$ARGUMENTS` as a token list. Match the **first token**:

| First token | Mode |
|-------------|------|
| `analyze` | Mode 2 analyze |
| `reassess` | Mode 2 reassess |
| `release-single` | Mode 4 copy single card |
| `remove` | Mode 5 remove tag |
| `sync` | Mode 3a |
| `snapshot` | Mode 3b |
| `ship` | Mode 3c |
| anything else | Mode 1 (bulk copy) |

For Mode 3 commands: everything after the subcommand, minus any trailing `--force` flag and any trailing token matching a Trello board URL (`^https://trello\.com/b/`) or bare shortLink (alphanumeric, ≥8 chars), is the tag. Tags may be multi-word.

---

## Argument Parsing (Mode 1 and Mode 3)

### Mode 1 (Copy)

All tokens in `$ARGUMENTS` are treated as the tag name (may be multi-word). Mode 1 has no board parameter - always uses `DEFAULT_STORYLAB_BOARD`.

```python
tag = ' '.join(sys.argv[1:])  # or $ARGUMENTS
board_id = DEFAULT_STORYLAB_BOARD
```

### Mode 3 (sync/snapshot/ship)

Parse `$ARGUMENTS` to extract subcommand, tag, optional board, optional lane, optional --force flag, optional --no-sync flag.

**Parsing algorithm:**

```python
import re

tokens = $ARGUMENTS.split()
subcommand = tokens[0]  # "sync" | "snapshot" | "ship"
remaining = tokens[1:]

# Strip flags from end (order-independent)
force_flag = False
no_sync_flag = False
while remaining and remaining[-1].startswith('--'):
    if remaining[-1] == '--force':
        force_flag = True
        remaining = remaining[:-1]
    elif remaining[-1] == '--no-sync':
        no_sync_flag = True
        remaining = remaining[:-1]
    else:
        break

# Find board token position (scan from left to right for first match)
board_id = None
board_pos = None
for i, token in enumerate(remaining):
    # Match Trello board URL pattern
    url_match = re.match(r'^https://trello\.com/b/([a-zA-Z0-9]{8,})/?', token)
    if url_match:
        board_id = url_match.group(1)
        board_pos = i
        break
    # Match bare shortLink (alphanumeric, ≥8 chars)
    elif len(token) >= 8 and token.isalnum():
        board_id = token
        board_pos = i
        break

# Split tokens based on board position
if board_pos is not None:
    tag = ' '.join(remaining[:board_pos])
    lane = ' '.join(remaining[board_pos + 1:]) if board_pos + 1 < len(remaining) else None
else:
    # No board specified
    board_id = DEFAULT_STORYLAB_BOARD
    tag = ' '.join(remaining)
    lane = None
```

**Examples:**
- `/sl-iteration sync MCSL 377` → tag="MCSL 377", board=DEFAULT_STORYLAB_BOARD, lane=None
- `/sl-iteration snapshot MCSL 377 abc12345` → tag="MCSL 377", board="abc12345", lane=None
- `/sl-iteration snapshot MCSL 377 abc12345 Dev Done` → tag="MCSL 377", board="abc12345", lane="Dev Done"
- `/sl-iteration snapshot MCSL 377 63e1e0414b6026c45be1087c SL MCSL 377: Iteration backlog` → tag="MCSL 377", board="63e1e0414b6026c45be1087c", lane="SL MCSL 377: Iteration backlog"
- `/sl-iteration ship Multi Word Tag xyz12345 My Lane --force` → tag="Multi Word Tag", board="xyz12345", lane="My Lane", force=True

---

## Pre-flight (MANDATORY — run before ANY operation)

### 1. Update All Sources

**Skip if `--no-sync` flag is present in arguments.**

```bash
cd <wiki-root> && git submodule update --remote raw/storepep-react raw/mcsl-test-automation 2>&1
```

This ensures code analysis is based on the latest codebase, not a stale snapshot. If the submodule update fails, warn the user and ask whether to proceed with stale data.

Record the current commit hash after update:
```bash
cd raw/storepep-react && git rev-parse HEAD
```

**`--no-sync` flag**: Pass this flag to skip submodule updates. Useful when submodules are already up-to-date or when working offline. Example: `/sl-iteration snapshot MCSL 377 --no-sync`

### 2. Agent Permissions — Known Limitation

**Subagent permissions do NOT propagate from the parent session.** Even if `.claude/settings.local.json` has `Bash(curl *)`, `Bash(python3 *)`, `Bash(rg *)` — subagents spawned via the Agent tool will NOT inherit these. This is a Claude Code platform limitation.

**Consequence**: `analyze all` CANNOT use parallel agents for deep analysis. Agents will be blocked on Bash (needed for Trello API calls via curl).

**Required approach**: Always process cards in the **main thread** using a single `python3` script that:
1. Reads all StoryLab cards via urllib
2. Searches code via subprocess `rg`
3. Reads source files for deep analysis
4. Updates all Trello cards via urllib

This is sequential but reliable — the main thread has full Bash access.

### 3. Batch Size (Context Length Control)

**Maximum 3 cards per agent** (if agents ever gain Bash access in future). Deep analysis is token-heavy — each card requires reading the StoryLab description, multiple grep searches, reading 2-3 source files, and writing detailed analysis.

**For main-thread processing**: No batch limit needed — the python script handles all cards in one run.

**Never assign more than 3 cards to a single agent.** This is a hard constraint learned from production runs where 9-card batches produced deep analysis for only the first 2-3 cards.

---

## Board IDs

```python
DEFAULT_STORYLAB_BOARD = '69dd9134576a26fcb79b670d'
PH_WIP_BOARD = '63e1e0414b6026c45be1087c'  # Always hardcoded - this is the target
```

| Board | ID | Parameterized? |
|-------|-----|----------------|
| **StoryLab** (source) | `69dd9134576a26fcb79b670d` (default) | ✅ Yes (Mode 1, Mode 3) |
| **ph-WIP** (target) | `63e1e0414b6026c45be1087c` | ❌ No (always hardcoded) |

## Dev Labels to Exclude from Copy (never copy these)

| Label | ID |
|-------|-----|
| `🛠️ DEV` | `69ddcada5e444b9157da951d` |
| `✅ DEV DONE` | `69ddcadb130379d4cb79b4ef` |
| `🧪 QA` | `69ddcadb1d2769d25b6a6f92` |
| `🚀 PROD` | `69ddcadcd5d8f116d99db5f4` |
| `📋 BACKLOG` | `69ddcadcd2bfb5a850ffb2cc` |

```
DEV_LABEL_IDS="69ddcada5e444b9157da951d,69ddcadb130379d4cb79b4ef,69ddcadb1d2769d25b6a6f92,69ddcadcd5d8f116d99db5f4,69ddcadcd2bfb5a850ffb2cc"
```

## Confidence Labels on ph-WIP

| Label | ID | Color |
|-------|-----|-------|
| `CONFIDENCE:HIGH` | `69dee0a642a39a86a39ca652` | green |
| `CONFIDENCE:MEDIUM` | `69dee0a7a906af81b31a6831` | yellow |
| `CONFIDENCE:LOW` | `69dee0a86d18af6f40e61d2f` | orange |
| `CONFIDENCE:POOR` | `69dee0a8c0ebc650c9ddafaf` | red |

```
CONFIDENCE_LABEL_IDS="69dee0a642a39a86a39ca652,69dee0a7a906af81b31a6831,69dee0a86d18af6f40e61d2f,69dee0a8c0ebc650c9ddafaf"
```

---

## API Details

Credentials from environment:
- `$TRELLO_API_KEY`
- `$TRELLO_TOKEN`

Base URL: `https://api.trello.com/1`

All requests append `?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN`.

Use `curl` via Bash for POST/PUT/DELETE requests (WebFetch is GET-only).

---

# Mode 1: Copy Cards

## Execution

### Step 1: Parse arguments and find the release tag label

**Parse arguments:**
```python
tag = ' '.join(sys.argv[1:])  # All tokens = tag name (may be multi-word)
board_id = DEFAULT_STORYLAB_BOARD  # Mode 1 always uses default board
```

**Resolve label:**
```
GET /boards/{board_id}/labels?fields=name,color,id&limit=1000
```

Find label matching `tag` (case-insensitive). If not found — show available labels and ask.

Record `RELEASE_LABEL_ID`, `RELEASE_LABEL_NAME`, `RELEASE_LABEL_COLOR`.

### Step 2: Collect qualifying cards in order

Fetch lanes (left → right):
```
GET /boards/{board_id}/lists?fields=name,id
```

For each lane, fetch cards (top → bottom):
```
GET /lists/{listId}/cards?fields=name,desc,idLabels,pos,shortUrl
```

Filter: keep cards where `idLabels` contains `RELEASE_LABEL_ID`. Build ordered list.

### Step 3: Ensure swimlane on ph-WIP

```
GET /boards/63e1e0414b6026c45be1087c/lists?fields=name,id
```

Look for `SL <RELEASE_LABEL_NAME>: Iteration backlog`. If missing:

```bash
curl -s -X POST "https://api.trello.com/1/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "SL <NAME>: Iteration backlog", "idBoard": "63e1e0414b6026c45be1087c", "pos": "top"}'
```

### Step 4: Fetch existing ph-WIP labels

```
GET /boards/63e1e0414b6026c45be1087c/labels?fields=name,color,id
```

Build lookup: `"SL: <name>"` → label ID.

### Step 5: Fetch existing cards in target lane (idempotency)

```
GET /lists/{TARGET_LIST_ID}/cards?fields=name,desc
```

Build set of all `shortUrl` values found in `desc` fields.

### Step 6: For each qualifying card

#### 6.1 Idempotency check
If source card's `shortUrl` is in the existing set → **skip**.

#### 6.2 Resolve labels
- Skip dev label IDs (`DEV_LABEL_IDS` set) — do NOT skip the release tag label (e.g. MCSL 378); it must be mapped too
- For each remaining label (including the release tag label): look up `SL: <original name>` in ph-WIP labels
- If missing: `POST /boards/63e1e0414b6026c45be1087c/labels` with `name=SL: <name>`, `color=<color>`
- Add to lookup map for reuse

#### 6.3 Create card
```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idList": "<TARGET_LIST_ID>",
    "name": "From SL: <original card name>",
    "desc": "<source card shortUrl>",
    "idLabels": "<comma-separated SL: label IDs>",
    "pos": "bottom"
  }'
```

### Step 7: Report

```
## SL Iteration Backlog — <RELEASE_LABEL_NAME>
- Lane: SL <NAME>: Iteration backlog (created / reused)
- Cards created: X
- Cards skipped (duplicates): Y
- Labels created on ph-WIP: Z
```

---

# Mode 2: Analyze Cards

## Confidence Levels

| Level | Criteria |
|-------|----------|
| **HIGH** | Found specific file + function, error message matches, clear code path |
| **MEDIUM** | Found module/area, 2-3 candidate files, needs dev confirmation |
| **LOW** | Found general area, issue spans multiple files or is architectural |
| **POOR** | No meaningful code match, or purely product/UX decision with no code to anchor to |

## Execution

### Step 0: Resolve the target lane

Parse the `<release-tag>` from the argument. Then:

1. Fetch ph-WIP lanes: `GET /boards/63e1e0414b6026c45be1087c/lists?fields=name,id`
2. Find lane named `SL <release-tag>: Iteration backlog` (case-insensitive match)
3. If found — use its `id` as `TARGET_LIST_ID`
4. If NOT found — list all lanes starting with `SL ` and ask user to pick:
   ```
   No lane found for "MCSL 378". Available SL lanes:
   1. SL MCSL 377: Iteration backlog (28 cards)
   2. SL MCSL 376: Iteration backlog (15 cards)
   Which lane?
   ```

**For `reassess ZI-NNN`** (no release-tag argument): search ALL `SL *` lanes on ph-WIP for a card matching the ZI ID in its name. Use that card's lane.

### Step 1: Read ALL context from the card

Three sources — read all of them:

1. **ph-WIP card description**: `GET /cards/{cardId}?fields=name,desc,idLabels,shortUrl`
   - The first line is the StoryLab `shortUrl`
   - May already contain a previous `## AI Code Analysis` section (if reassessing)
   - May contain additional notes added by devs

2. **ph-WIP card comments**: `GET /cards/{cardId}/actions?filter=commentCard`
   - Devs may have added context, file paths, error logs, clarifications

3. **StoryLab card**: Follow the `shortUrl` from the ph-WIP description → `GET /cards/{shortId}?fields=name,desc`
   - Contains full ticket summary, user story, acceptance criteria

**Extract search terms from ALL three sources**: error messages, carrier names, feature names, UI element references, file paths, API endpoints, component names.

### Step 2: Search the codebase

Search `raw/storepep-react/` using Grep:
- Error strings and log messages
- Carrier names and service codes
- Component names and function names
- API route patterns
- File paths mentioned in comments

Read the most relevant files to understand data flow. Follow imports to identify the call chain.

**Key directories to search**:
- `server/src/shared/API/carriers/` — carrier-specific logic
- `server/src/shared/orders/` — order processing, bulk actions
- `server/src/routes/` — API endpoints
- `server/src/shared/` — shared helpers (processShipment, packageHelper, etc.)
- `client/src/components/form/` — UI components
- `client/src/actions/` — Redux actions

### Step 3: Search test coverage

Search `raw/mcsl-test-automation/` using Grep for related Playwright tests. Cross-reference with `wiki/features.md` if the area is documented.

### Step 4: Assess confidence

Based on Steps 1-3 results, assign: HIGH, MEDIUM, LOW, or POOR.

### Step 5: Write analysis

**For HIGH / MEDIUM / LOW** — build this markdown:

```markdown
<StoryLab shortUrl>

---

## AI Code Analysis

**Confidence**: HIGH | MEDIUM | LOW

**Affected Files**:
- `server/path/to/file.js:L123` — <what this file does and why it's relevant>
- `server/path/to/other.js:L456` — <relevance>

**Root Cause / Gap**:
<1-2 sentences explaining why the bug exists or where the feature gap is>

**Suggested Approach**:
- <bullet 1>
- <bullet 2>
- <bullet 3>

**Test Coverage**:
- Existing: <test file paths covering this area, or "None">
- Needed: <what tests should be added>

**Blast Radius**:
<what else could break if this code is changed — other carriers, other features, shared modules>
```

**For POOR** — one-liner only:

```markdown
<StoryLab shortUrl>

---

## AI Code Analysis

**Confidence**: POOR
Needs human triage — no code match found. Issue is too vague or requires product decision before code analysis.
```

**File path format**: Use paths relative to `storepepSAAS/` (e.g., `server/src/routes/bulkActions.js:98`). Include line numbers when referencing specific code.

### Step 6: Apply confidence label + update card

1. **Remove any existing confidence label** from the card:
   ```bash
   # For each of the 4 confidence label IDs, try DELETE (ignore 404):
   curl -s -X DELETE "https://api.trello.com/1/cards/{cardId}/idLabels/{labelId}?key=...&token=..."
   ```

2. **Update card description** — replace the entire desc (StoryLab link + analysis):
   ```bash
   curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=...&token=..." \
     -H "Content-Type: application/json" \
     -d '{"desc": "<full new description>"}'
   ```

3. **Add new confidence label**:
   ```bash
   curl -s -X POST "https://api.trello.com/1/cards/{cardId}/idLabels?key=...&token=..." \
     -H "Content-Type: application/json" \
     -d '{"value": "<confidence label ID>"}'
   ```

### Step 7: Report and proceed

Print for user review:
- Card name
- Confidence level
- Key affected files (top 3)
- Root cause summary (1 sentence)

Wait for user to say "next" before processing the next card.

## Reassessment

When user says `reassess ZI-NNN`:

1. Re-run Steps 1-6 for that card
2. Step 1 picks up new context (comments, enriched description)
3. Step 4 may produce a **different confidence level** (can go up or down)
4. Step 5 **replaces** the existing `## AI Code Analysis` section — does NOT append a second one
5. Step 6 **removes old confidence label**, applies new one

**Idempotency**: Parse existing desc, find `---\n\n## AI Code Analysis` marker, replace everything from there onward. Preserve the StoryLab link and any content between the link and the analysis marker.

## Finding the Next Unanalyzed Card

For `analyze next`:
1. Fetch all cards in the target lane: `GET /lists/{listId}/cards?fields=name,desc,idLabels`
2. Find the first card whose `idLabels` does NOT contain any of the 4 confidence label IDs
3. Run analysis on that card

## Filtering Cards by Member (`analyze <release-tag> @<name>`)

### Resolving the member

1. Fetch board members: `GET /boards/63e1e0414b6026c45be1087c/members?fields=id,username,fullName`
2. Match `<name>` against both `username` and `fullName` (case-insensitive, partial match OK)
   - e.g., `@ajeesh` matches `fullName: "Ajeesh PU"` or `username: "ajeeshpu"`
   - e.g., `@john` matches `fullName: "John Doe"` or `username: "johndoe"`
3. If multiple matches — list them and ask user to pick
4. If no match — list all board members and ask user to pick

### Filtering

1. Fetch all cards in the target lane: `GET /lists/{listId}/cards?fields=name,desc,idLabels,idMembers`
2. Filter: keep only cards where `idMembers` contains the resolved member ID
3. Optionally further filter to unanalyzed only (no confidence label)
4. Process matching cards using the standard analysis workflow

### Report

After filtering, show:
```
Found X cards assigned to @<username> (Y unanalyzed):
1. From SL: ZI-NNN — <title> [ANALYZED / PENDING]
2. ...

Proceeding to analyze Y unanalyzed cards.
```

If all assigned cards are already analyzed, report: "All X cards assigned to @<username> already have AI analysis. Use `reassess ZI-NNN` to re-run any."

---

# Mode 4: Copy Single Card

## Purpose

Copy a single StoryLab card (identified by ZI ID in the card name) to ph-WIP with duplicate check. If a card with the same ZI ID already exists in the target lane, abort with a warning.

**Board constraints**: Mode 4 ALWAYS uses `DEFAULT_STORYLAB_BOARD` as the source and ALWAYS copies to the standard `SL <tag>: Iteration backlog` lane on ph-WIP. No board parameter is supported.

## Execution

### Step 1: Parse arguments

```python
import re

tokens = $ARGUMENTS.split()
# tokens[0] = "release-single"
# tokens[1:] = tag tokens + ZI-NNN

zi_pattern = re.compile(r'^ZI-\d+$')
zi_id = None
tag_tokens = []

for token in tokens[1:]:  # Skip "release-single"
    if zi_pattern.match(token):
        zi_id = token
    else:
        tag_tokens.append(token)

tag = ' '.join(tag_tokens)
board_id = DEFAULT_STORYLAB_BOARD  # Mode 4 always uses default StoryLab - no board parameter
```

### Step 2: Resolve release tag label

```
GET /boards/{board_id}/labels?fields=name,color,id&limit=1000
```

Find label matching `tag` (case-insensitive). If not found — show available labels and ask.

Record `RELEASE_LABEL_ID`, `RELEASE_LABEL_NAME`, `RELEASE_LABEL_COLOR`.

### Step 3: Find the source card on StoryLab

Fetch all cards with the release tag:
```
GET /boards/{board_id}/cards?fields=name,desc,idLabels,shortUrl
```

Filter: keep cards where `idLabels` contains `RELEASE_LABEL_ID`.

Search for card with `{zi_id}` in the name (case-insensitive, must match the pattern `ZI-\d+` exactly).

If not found: abort with error:
```
Card {zi_id} not found with tag {tag} on StoryLab.
Available tagged cards: ZI-001, ZI-005, ZI-012...
```

If multiple matches: list all and ask user to confirm (shouldn't happen if ZI IDs are unique).

Record the source card.

### Step 4: Ensure target lane exists on ph-WIP

```
GET /boards/63e1e0414b6026c45be1087c/lists?fields=name,id
```

Look for `SL <RELEASE_LABEL_NAME>: Iteration backlog`. This is always the target lane for Mode 4 - no custom lane parameter is supported. If missing, create it (same as Mode 1 Step 3).

### Step 5: Check for duplicates in target lane

```
GET /lists/{TARGET_LIST_ID}/cards?fields=name,desc
```

Search all cards in the target lane:
- Check if any card name contains `{zi_id}` (case-insensitive)
- OR check if any card desc contains the source card's `shortUrl`

If duplicate found: **abort** with warning:
```
⚠️ Duplicate detected: {zi_id} already exists in lane "SL {tag}: Iteration backlog"
Existing card: {duplicate_card.name}
URL: {duplicate_card.shortUrl}

Not copying. Use the existing card or remove it first with:
/sl-iteration remove {tag} {zi_id}
```

### Step 6: Fetch existing ph-WIP labels

```
GET /boards/63e1e0414b6026c45be1087c/labels?fields=name,color,id&limit=1000
```

Build lookup: `"SL: <name>"` → label ID.

### Step 7: Resolve labels for the new card

Same as Mode 1 Step 6.2:
- Skip dev label IDs (`DEV_LABEL_IDS` set) — do NOT skip the release tag label
- For each remaining label (including the release tag label): look up `SL: <original name>` in ph-WIP labels
- If missing: `POST /boards/63e1e0414b6026c45be1087c/labels` with `name=SL: <name>`, `color=<color>`

### Step 8: Create the card

```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idList": "<TARGET_LIST_ID>",
    "name": "From SL: <original card name>",
    "desc": "<source card shortUrl>",
    "idLabels": "<comma-separated SL: label IDs>",
    "pos": "bottom"
  }'
```

### Step 9: Report

```
## Copy Single Card — {zi_id}

✅ Copied to ph-WIP lane: SL {tag}: Iteration backlog
- Source: {source_card.name}
- StoryLab URL: {source_card.shortUrl}
- ph-WIP card: From SL: {source_card.name}
- Labels copied: {N}
```

---

# Mode 5: Remove Release Tag

## Purpose

Remove the release tag label from a ph-WIP card (identified by ZI ID). This is used to move a card out of a release scope.

## Execution

### Step 1: Parse arguments

```python
tokens = $ARGUMENTS.split()
# tokens[0] = "remove"
# tokens[1:] = tag tokens + ZI-NNN

import re
zi_pattern = re.compile(r'^ZI-\d+$')
zi_id = None
tag_tokens = []

for token in tokens[1:]:  # Skip "remove"
    if zi_pattern.match(token):
        zi_id = token
    else:
        tag_tokens.append(token)

tag = ' '.join(tag_tokens)
```

### Step 2: Resolve the SL-prefixed tag label on ph-WIP

```
GET /boards/63e1e0414b6026c45be1087c/labels?fields=name,color,id&limit=1000
```

Look for label with name `SL: {tag}` (case-insensitive, note the space after colon).

If not found: abort with error:
```
Label "SL: {tag}" not found on ph-WIP board.
Available SL labels: SL: MCSL 377, SL: MCSL 376, ...
```

Record `TAG_LABEL_ID`.

### Step 3: Find all SL lanes on ph-WIP

```
GET /boards/63e1e0414b6026c45be1087c/lists?fields=name,id
```

Filter: keep lanes starting with `SL ` (case-sensitive).

### Step 4: Search for the card by ZI ID

For each SL lane:
```
GET /lists/{listId}/cards?fields=name,desc,idLabels,shortUrl
```

Search for card with `{zi_id}` in the name (case-insensitive).

If found: record the card and its lane. Break.

If not found in any lane: abort with error:
```
Card {zi_id} not found in any SL lane on ph-WIP.
Searched lanes: SL MCSL 377: Iteration backlog, SL MCSL 376: Iteration backlog, ...
```

### Step 5: Verify the card has the tag label

Check if `TAG_LABEL_ID` is in the card's `idLabels`.

If not present: abort with warning:
```
⚠️ Card {zi_id} does not have label "SL: {tag}"
Current labels on card: {list of label names}

Nothing to remove.
```

### Step 6: Remove the label

```bash
curl -s -X DELETE "https://api.trello.com/1/cards/{cardId}/idLabels/{TAG_LABEL_ID}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

Check response:
- 200 OK: success
- 404: label was already removed (treat as success, idempotent)
- Other: error, abort

### Step 7: Report

```
## Remove Tag — {zi_id}

✅ Removed label "SL: {tag}" from ph-WIP card
- Card: {card.name}
- Lane: {lane_name}
- Card URL: {card.shortUrl}
- Remaining labels: {list of remaining label names}
```

---

# Mode 3: Release Workflow

Three subcommands that close the loop between Trello + Zendesk and the wiki, **per release tag** (e.g., `MCSL 377`):

- **sync**: delta-based pull of Zendesk JSONs → regen wiki summaries → post compact delta comments on tagged StoryLab cards.
- **snapshot**: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current Trello state.
- **ship**: freeze the release in wiki state; update backlog + log. **No Trello writes.**

**Design principle (read-leaning)**: Trello (StoryLab tags, ph-WIP lanes) and Zendesk raw JSONs are upstream sources. Wiki files (release.md, backlog.md, Zendesk summaries) are the downstream derivatives this workflow maintains. The **only** Trello write is sync posting comments on tagged StoryLab cards. Ship never moves cards, never changes labels, never creates lanes.

**Delta anchor**: per-release `git_reference` in `wiki/product/releases/<TAG-slug>.md` frontmatter. snapshot sets it on first creation; sync advances it every run. No separate state file.

## 6-State Legend (coarsening for release reports)

Release views classify each tagged StoryLab card by the HIGHEST-precedence **label** found on ANY matching ph-WIP card (matched by Zendesk ticket ID in the card name/desc/attachments/comments). Lane membership is NOT used for state — labels are the authoritative delivery signal.

**Do NOT read StoryLab dev labels** (`🛠️ DEV`, `✅ DEV DONE`, `🧪 QA`, `🚀 PROD`, `📋 BACKLOG`). Those are cached projections from Mode 2 analyze and may be stale. Always read ph-WIP labels live.

**ph-WIP label precedence** (high → low, match by NAME not ID — ph-WIP has multiple labels with the same name and varying colors):

```
SHIPPED  >  PROD  >  QA_VERIFIED  >  QA Reported  >  Ready for QA  >  Dev Done  >  DEV
```

**Coarsening to 6-state legend**:

| Legend state | ph-WIP label name(s) | Meaning |
|--------------|----------------------|---------|
| `Shipped` | `SHIPPED`, `PROD` | Deployed to production |
| `Ready To Ship` | `QA_VERIFIED` | QA verified, ready to deploy |
| `BUG REPORTED` | `BUG REPORTED` | Bug found in QA |
| `QA READY` | `QA Reported`, `Ready for QA`, `Dev Done` | In QA testing (not yet verified) |
| `DEV` | `DEV` | Active development |
| `Open (not started)` | NO state label on any matching ph-WIP card | Not started |
| `Support Closed` | StoryLab card carries `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label | Closed without code (precedence — overrides any ph-WIP state) |

**Do NOT exclude SL-copy cards** (cards named `From SL: ...` in `SL <tag>: Iteration backlog` lanes). Devs often apply state labels directly to the SL-copy rather than creating separate dev cards. Search ALL ph-WIP matches for state labels.

**Closed** = {Shipped, Support Closed}. **Open** = {Open, DEV, BUG REPORTED, QA READY, Ready To Ship}. Ship refuses non-terminal cards unless `--force`.

**Ignored labels** (noise, not part of the release state machine): `READY FOR DEPLOY`, `L3-DEV`, `DEV_ONLY`, `Completed`.

## Per-card closure (Trello-native)

Users close a card **manually on Trello** — no skill subcommand needed:

1. Move the StoryLab card to `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label
2. Add a comment on the card with a structured reason:
   ```
   [close-reason: <kind>] <optional detail>
   ```
   where `<kind>` ∈ {`dup-of=ZI-NNN`, `wontfix`, `stale`, `customer-resolved`, `out-of-scope`, `superseded-by=ZI-NNN`}.

snapshot and ship parse these comments (newest-first, first match wins) and surface the reason in the `## Support Closed` section of release.md. Missing reason → flagged but not fatal.

## Shared Utilities (Mode 3)

Use these helpers across all three subcommands. All run in the main thread (same permission model as Mode 2 Pre-flight §2).

### Pagination Verification (MANDATORY)

**Critical**: Always verify that Trello API responses are complete. Silent truncation is a common source of incorrect release state.

| Endpoint | Default Limit | Correct Usage | Verification |
|----------|--------------|---------------|--------------|
| `/boards/{id}/labels` | 50 | `limit=1000` | If `len(result) == 1000`, warn about possible truncation |
| `/boards/{id}/cards` | Returns all | No `limit` param | No verification needed (returns all by default) |
| `/boards/{id}/actions` (comments) | 1000 | `limit=1000`, paginate with `before` if needed | **MANDATORY**: If `len(result) == 1000`, paginate until exhausted |
| `/boards/{id}/lists` | Returns all | No limit needed | No verification needed |

**Comments pagination pattern**:
```python
all_comments = []
before = None
while True:
    url = f'/boards/{id}/actions?filter=commentCard&limit=1000&key={KEY}&token={TOKEN}'
    if before:
        url += f'&before={before}'
    batch = json.load(urllib.request.urlopen(url))
    if not batch:
        break
    all_comments.extend(batch)
    if len(batch) < 1000:
        break
    before = batch[-1]['id']
```

**Labels**: ph-WIP currently has 162+ labels; StoryLab has 60+. ALWAYS pass `limit=1000` when fetching labels or you will silently miss state labels like `SHIPPED`, `DEV`, `PROD`.

### `resolve_tag_label(storylab_board_id, tag)`
`GET /boards/{id}/labels?fields=name,color,id&limit=1000`; case-insensitive match on `name`.

**Multi-tag resolution (MANDATORY)**: ALWAYS search for BOTH label variants:
1. `{tag}` (e.g., "MCSL 377")
2. `SL: {tag}` (e.g., "SL: MCSL 377") — **NOTE the space after colon**

Return ALL matching label IDs as a list (can be empty, 1, or 2 IDs). This ensures snapshot captures both:
- Original tagged cards on StoryLab
- SL-prefixed copies on ph-WIP (created by Mode 1)

If no matches found for either variant, list available labels and ask user to pick (same pattern as Mode 1 Step 1).

### `resolve_support_closed_label_ids(storylab_board_id)`
Look up labels on StoryLab whose name (case-insensitive, trimmed) equals either `Closed by Support` OR `SL: Closed By Support`. Return the **set** of matching label IDs (can be empty, one, or more than one — both names might exist, and each could have multiple color-variants). A card is "Support Closed" if ANY of its label IDs is in this set. **Do NOT auto-create** — user controls board structure. If the set is empty, warn once and treat all cards as not-Support-Closed.

### `resolve_ph_wip_state_labels(ph_wip_board_id)`
Fetch all ph-WIP labels with `limit=1000` (the default limit is 50 — missing this causes silent truncation). Build a map of `{state_name: set(label_ids)}` for each of the 8 state-label names: `SHIPPED`, `PROD`, `BUG REPORTED`, `QA_VERIFIED`, `QA Reported`, `Ready for QA`, `Dev Done`, `DEV`. ph-WIP has multiple labels with the same name (different colors) — treat them as equivalent.

**Implementation:**
```python
GET /boards/{ph_wip_board_id}/labels?fields=name,color,id&limit=1000

state_label_map = {}
STATE_LABEL_NAMES = ['SHIPPED', 'PROD', 'QA_VERIFIED', 'QA Reported', 'Ready for QA', 'Dev Done', 'DEV', 'BUG REPORTED']

for state_name in STATE_LABEL_NAMES:
    matching_labels = [lbl for lbl in labels if lbl['name'].strip().lower() == state_name.lower()]
    state_label_map[state_name] = {lbl['id'] for lbl in matching_labels}
```

**CRITICAL VALIDATION**: After building the map, validate that critical labels were found:
```python
CRITICAL_LABELS = ['Dev Done', 'QA_VERIFIED', 'PROD', 'SHIPPED', 'DEV']
missing = [name for name in CRITICAL_LABELS if not state_label_map.get(name)]

if missing:
    raise Exception(f"❌ CRITICAL: Missing state labels on ph-WIP: {missing}. State detection will fail. Check board configuration.")

# Warn about optional labels
OPTIONAL_LABELS = ['QA Reported', 'Ready for QA', 'BUG REPORTED']
missing_optional = [name for name in OPTIONAL_LABELS if not state_label_map.get(name)]
if missing_optional:
    print(f"⚠️  WARNING: Missing optional state labels: {missing_optional}")
```

**Return**: `state_label_map` (dict) and `labels_found_count` (int) for diagnostic reporting.

### `fetch_tagged_storylab_cards(board_id, tag_label_ids, lane_name=None)`
Single bulk `GET /boards/{board_id}/cards?attachments=true&fields=name,desc,idList,idLabels,shortUrl`. Filter in-memory where `idLabels` contains ANY of the `tag_label_ids` (can be a list or single ID). If `lane_name` is specified, additionally filter by lane: fetch all lists, find the list whose name matches `lane_name` (case-sensitive exact match), and keep only cards where `idList` matches that list ID.

### `fetch_ph_wip_snapshot()`
2 calls:
- `GET /boards/<PH_WIP>/cards?fields=name,desc,idList,shortUrl&attachments=true`
- `GET /boards/<PH_WIP>/lists?fields=name,id`

Build `{ph_wip_cardId: lane_name}` map. Cache for the run.

### `fetch_all_card_comments(board_id)`
Fetch ALL comments with pagination: `GET /boards/{id}/actions?filter=commentCard&limit=1000`. **MANDATORY**: If result count == 1000, paginate with `before` parameter until exhausted (see Pagination Verification above). Index by cardId. Used for: (a) StoryLab card close-reason parsing; (b) ph-WIP card correlation fallback when name/desc/attachments miss.

### `match_storylab_card_to_ph_wip(storylab_card, ph_wip_cards, ph_wip_comments_by_card)`
Adapt the ph-WIP Correlation pattern from **story-cards SKILL.md:400-414**. Primary signal: Zendesk ticket ID in card names. Story-cards uses naming convention `ZI-NNN — <title> [#<ticketId>]` on StoryLab; ph-WIP cards also carry the ticket ID in name/desc/attachments.

Match order:
1. StoryLab card's `[#<ticketId>]` → search ph-WIP card names for `#<ticketId>`, `<ticketId>`, `[#<ticketId>]`
2. Fall back: desc contains ticket id
3. Fall back: attachment name/URL contains ticket id
4. Fall back: one of the card's comments contains ticket id

Return a list of matching ph-WIP cards (can be 0, 1, or >1). Store the first match's lane for state coarsening; note multi-matches in report output.

### Lane classification (deprecated for state detection)
Do NOT use ph-WIP lane names to classify state. State comes from ph-WIP **labels** (see `best_ph_wip_state_label`). Lane names are only rendered in release.md as reference context (not authoritative). The story-cards Dev Status Classification table (lines 417-425 of story-cards SKILL.md) is used by Mode 2 analyze for a different purpose (writing StoryLab dev-status labels for planning views) and should not be applied in Mode 3.

### `best_ph_wip_state_label(ph_matches, state_label_ids, sl_lane_id)`
Walks the 8 state-label names in precedence order (`SHIPPED`, `PROD`, `BUG REPORTED`, `QA_VERIFIED`, `QA Reported`, `Ready for QA`, `Dev Done`, `DEV`). Scans only the **current release's SL-copy cards** (those in `sl_lane_id`) first; falls back to all `ph_matches` only if no state label is found there. Returns `(label_name, chosen_card)` or `(None, None)` if no state label is present on any match.

**Why lane-preference matters**: multiple ZI issues from different releases can reference the same Zendesk ticket ID. Without scoping to the current release's lane first, a `Dev Done` label on an MCSL 377 card bleeds into an MCSL 378 card that shares the same ticket, producing false QA READY classifications.

**Important**: do NOT filter out SL-copy cards (named `From SL: ...` in `SL <tag>: Iteration backlog` lane). Devs often apply state labels directly to the SL-copy — this is the primary signal source.

### `coarsen_state(storylab_card, ph_wip_label_name_or_none)`
Decision order:
1. If `support_closed_label_id` is set AND `storylab_card.idLabels` contains it → return `Support Closed`.
2. If `ph_wip_label_name_or_none is None` → return `Open (not started)`.
3. Map the ph-WIP label name:
   - `SHIPPED` or `PROD` → `Shipped`
   - `QA_VERIFIED` → `Ready To Ship`
   - `BUG REPORTED` → `BUG REPORTED`
   - `QA Reported`, `Ready for QA`, or `Dev Done` → `QA READY`
   - `DEV` → `DEV`

### `parse_close_reason(storylab_card_comments)`
Regex: `\[close-reason:\s*([a-z-]+)(?:=([A-Z]+-\d+))?\]\s*(.*)` (case-sensitive for kind keywords).
- Walk comments newest-first; return the first match as `(kind, zi_ref_or_None, detail)`.
- If no comment matches, return `None`.

### `read_release_frontmatter(tag_slug)` / `write_release_frontmatter(tag_slug, fields)`
Read/write YAML frontmatter on `wiki/product/releases/<tag_slug>.md`:
- Read: parse `--- ... ---` block at top of file, return dict. Refuse if file missing (caller's responsibility to check existence first).
- Write (partial update): read → merge `fields` → rewrite the frontmatter block, leave body unchanged. Atomic write (read, mutate, write).
- If frontmatter block unparseable YAML → refuse to proceed, surface the error verbatim to the user (never silently rewrite corrupt frontmatter).

### `git_diff_tickets(prior_ref, current_ref)`
```bash
git diff <prior_ref>..<current_ref> --name-only -- raw/zendesk/
```
Returns list of file paths (strings, relative to wiki root).

Fallback: if `git cat-file -e <prior_ref>` fails (ref no longer in history, e.g., after rebase/squash) → warn and use `HEAD~1..HEAD` instead. Include the warning in the report output.

---

## Mode 3a: `/sl-iteration sync <tag> [board] [lane]`

**Purpose**: pull Zendesk deltas since the release's last sync point; regen summaries; post compact delta comments on tagged cards. Optionally filter to cards in a specific lane on the source board.

### Flow

**Step 1 — Precondition check**: Require `wiki/product/releases/<TAG-slug>.md` to exist.
- If missing → hard error:
  ```
  No release file for MCSL 377. Run /sl-iteration snapshot MCSL 377 first to establish the release baseline.
  ```
  Never create it from sync; snapshot owns creation.

**Step 1.5 — Parse arguments:**

```python
# Parse: sync <tag> [board] [lane]
# Use same algorithm as general Mode 3 parsing
import re

tokens = $ARGUMENTS.split()
subcommand = tokens[0]  # "sync"
remaining = tokens[1:]

# Find board token position
board_id = None
board_pos = None
for i, token in enumerate(remaining):
    url_match = re.match(r'^https://trello\.com/b/([a-zA-Z0-9]{8,})/?', token)
    if url_match:
        board_id = url_match.group(1)
        board_pos = i
        break
    elif len(token) >= 8 and token.isalnum():
        board_id = token
        board_pos = i
        break

# Split tokens based on board position
if board_pos is not None:
    tag = ' '.join(remaining[:board_pos])
    lane = ' '.join(remaining[board_pos + 1:]) if board_pos + 1 < len(remaining) else None
else:
    board_id = DEFAULT_STORYLAB_BOARD
    tag = ' '.join(remaining)
    lane = None
```

**Step 2 — Read anchor**: Parse release.md frontmatter.
- `PRIOR_REF = frontmatter['git_reference']`
- `IS_SHIPPED = (frontmatter['status'] == 'shipped')`
- `CURRENT_REF = git rev-parse HEAD`

**Step 3 — Compute delta**: Run `git_diff_tickets(PRIOR_REF, CURRENT_REF)`.
- If empty AND `PRIOR_REF == CURRENT_REF`: report `0 tickets changed since <ref>`. Still bump `last_synced` on release.md. Exit with no Trello writes.
- If `PRIOR_REF` not in git history: fallback to `HEAD~1..HEAD` (handled by helper); warn the user.

**Step 4 — Fetch tagged cards**: `resolve_tag_label(board_id, tag)` → `tag_label_id`; then `fetch_tagged_storylab_cards(board_id, tag_label_id, lane)`. Only cards with `<tag>` label (and in specified lane, if any) will get delta comments.

**Step 5 — Process each delta ticket**: For each JSON path from the diff, parse the ticket ID from the filename.
- Inline-regenerate `wiki/zendesk/summaries/<ticket>.md` using the **zendesk-summarize Step 3 logic ported to python** (reading JSON once, comments in reverse, extracting Open / Resolved Issues per the template). Preserve product detection from directory path (`raw/zendesk/shopify/` → shopify; `raw/zendesk/other_platforms/` → derive from tags).
- `match_storylab_card_to_ph_wip` is NOT used here (sync doesn't touch ph-WIP). Instead, find StoryLab cards matching the ticket directly: search tagged cards' names for `[#<ticketId>]`.
- If card(s) matched AND `IS_SHIPPED == false`:
  - Post ONE compact comment per matching StoryLab card:
    ```
    🔄 ZI-NNN: N new customer comments since YYYY-MM-DD → [summary](../../zendesk/summaries/<ticket>.md)
    ```
    where `N` = count of new Zendesk comments between `PRIOR_REF` and `CURRENT_REF` (diff the `comments` array on the old vs new JSON; if too complex, use "recent customer activity" with no count).
  - If ticket JSON's `status` ∈ {`solved`, `closed`} at CURRENT_REF: append a second line to the same comment:
    ```
    ⚠️ Ticket marked {solved|closed} on YYYY-MM-DD by support. Consider moving to Closed by Support.
    ```
    (suggestion only — never auto-labels)
- If `IS_SHIPPED == true`: skip comment posting (release is frozen — keep shipped cards clean). Still regen the summary.
- If ticket has NO matching StoryLab card with `<tag>`: skip comment posting, count as "untagged" in report.

**Step 6 — Advance anchor**: Update release.md frontmatter:
```yaml
git_reference: <CURRENT_REF>
last_synced: <now ISO-8601>
tickets_delta_on_last_sync: <N>
```
Use `write_release_frontmatter`.

**Step 7 — Report**:
```
## Sync MCSL 377
- Tickets in delta: N
- Summaries regenerated: N
- Cards with delta comments posted: N
- Cards skipped (no tag): N
- Cards skipped (release shipped): N  [only if IS_SHIPPED]
- PRIOR_REF: <hash>
- CURRENT_REF: <hash>
- Warnings: <list>  [empty if none]
```

### Trello API — sync writes only

**Post card comment**:
```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "<compact comment>"}'
```

Throttle 100ms between posts. 429 → exponential backoff 1s/2s/4s then fail with the failed URL + response body.

---

## Mode 3b: `/sl-iteration snapshot <tag> [board] [lane]`

**Purpose**: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current StoryLab + ph-WIP live state. Optionally filter to cards in a specific lane on the source board.

### Flow

**Step 1 — File existence check**: Does `wiki/product/releases/<TAG-slug>.md` exist?
- If NO: this is the first snapshot. Mark `is_first_snapshot = true`. The new frontmatter will set `git_reference = HEAD` (establishes sync baseline).
- If YES: read existing frontmatter. Preserve `git_reference` (snapshot NEVER bumps it — sync owns it), preserve `status` and `shipped_at` if `status == "shipped"`.

**Step 1.5 — Parse arguments:**

```python
# Parse: snapshot <tag> [board] [lane]
# Use same algorithm as general Mode 3 parsing (see Argument Parsing section)
import re

tokens = $ARGUMENTS.split()
subcommand = tokens[0]  # "snapshot"
remaining = tokens[1:]

# Find board token position (scan from left to right for first match)
board_id = None
board_pos = None
for i, token in enumerate(remaining):
    url_match = re.match(r'^https://trello\.com/b/([a-zA-Z0-9]{8,})/?', token)
    if url_match:
        board_id = url_match.group(1)
        board_pos = i
        break
    elif len(token) >= 8 and token.isalnum():
        board_id = token
        board_pos = i
        break

# Split tokens based on board position
if board_pos is not None:
    tag = ' '.join(remaining[:board_pos])
    lane = ' '.join(remaining[board_pos + 1:]) if board_pos + 1 < len(remaining) else None
else:
    # No board specified
    board_id = DEFAULT_STORYLAB_BOARD
    tag = ' '.join(remaining)
    lane = None
```

**Step 2 — Fetch Trello state**:
- `resolve_tag_label(board_id, tag)` → `tag_label_id`
- `resolve_support_closed_label_ids(board_id)` → `support_closed_label_ids` (set, or empty with warning)
- `fetch_tagged_storylab_cards(board_id, tag_label_id, lane)` → tagged cards (filtered by lane if specified)
- `fetch_all_card_comments(board_id)` → source board comments by cardId (for close-reason parsing)
- `fetch_ph_wip_snapshot()` → ph-WIP cards + lane map (only if board != PH_WIP_BOARD; else skip for efficiency)
- `fetch_all_card_comments(PH_WIP_BOARD)` → ph-WIP comments (only if board != PH_WIP_BOARD; else reuse source board comments)

**Step 3 — Correlate & coarsen**: For each tagged StoryLab card:
- `ph_wip_matches = match_storylab_card_to_ph_wip(storylab_card, ph_wip_cards, ph_wip_comments_by_card)`
- `ph_wip_lane = lane_map[ph_wip_matches[0].id] if ph_wip_matches else None`
- `state = coarsen_state(storylab_card, ph_wip_lane)`
- Extract: `zi_id` (from card name `ZI-NNN — ...`), `ticket_id` (from `[#<ticketId>]`), `theme` / `carrier` / `product` labels

**Step 4 — Parse close reasons**: For cards where `state == "Support Closed"`:
- `close_reason = parse_close_reason(storylab_comments[card.id])`
- If `None`: flag the card in "cards missing close-reason" count

**Step 5 — Sort & group**:
Sort buckets: PROD → Support Closed → BUG REPORTED → QA READY → DEV → Open (not started).

**Step 6 — Rewrite release.md body** (preserving protected frontmatter fields from Step 1):

**YAML quoting**: Always quote string values that contain colons, spaces, or special characters (like `lane_filter: "SL MCSL 377: Iteration backlog"`).

```markdown
---
title: "Release <TAG>"
category: product-release
tag: "<TAG>"
tag_slug: <TAG-slug>
board_id: <board_id>
lane_filter: "<lane_name if specified, else null>"
status: <preserved, or "draft" if first snapshot>
last_synced: <now>
shipped_at: <preserved, or null>
git_reference: <preserved, or HEAD on first snapshot>
tickets_delta_on_last_sync: <preserved, or 0 on first snapshot>
cards_total: <N>
cards_shipped: <N>
cards_ready_to_ship: <N>
cards_support_closed: <N>
cards_bug_reported: <N>
cards_open: <N>
---

# Release <TAG>

> **Status**: <status> · **Last synced**: <YYYY-MM-DD HH:MM UTC> · **Board**: [StoryLab](https://trello.com/b/d1xk25XH/storylab)

## Summary

| State | Count |
|-------|-------|
| Shipped | <N> |
| Ready To Ship | <N> |
| Support Closed | <N> |
| BUG REPORTED | <N> |
| QA READY | <N> |
| DEV | <N> |
| Open (not started) | <N> |
| **Total** | **<N>** |

## Legend

- **Shipped** — deployed to production (ph-WIP SHIPPED or PROD label)
- **Ready To Ship** — QA verified, ready to deploy (ph-WIP QA_VERIFIED label)
- **Support Closed** — StoryLab card has `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label; closed without code via support action
- **BUG REPORTED** — code is in QA, bug has been reported (ph-WIP BUG REPORTED label)
- **QA READY** — code complete, in QA (ph-WIP Dev Done, Ready for QA, or QA Reported labels — NOT yet verified)
- **DEV** — active development (ph-WIP DEV label)
- **Open (not started)** — in product backlog but dev hasn't started (no ph-WIP state label)

## Shipped (<N>)

| ZI | Ticket | Theme | Carriers | Card |
|----|--------|-------|----------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | ... | ... | [SL](shortUrl) |

## Ready To Ship (<N>)

| ZI | Ticket | Theme | Card |
|----|--------|-------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | ... | [ph-WIP](shortUrl) |

## Support Closed (<N>)

| ZI | Ticket | Reason | Detail | Card |
|----|--------|--------|--------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | <kind> | <detail or ZI-ref> | [SL](shortUrl) |

## BUG REPORTED (<N>)

| ZI | Ticket | Theme | Card |
|----|--------|-------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | ... | [SL](shortUrl) |

## Still Open (<N>)

### QA READY (<N>)

| ZI | Ticket | Theme | ph-WIP Lane | Card |
|----|--------|-------|-------------|------|

### DEV (<N>)

| ZI | Ticket | Theme | ph-WIP Lane | Card |
|----|--------|-------|-------------|------|

### Open / not started (<N>)

| ZI | Ticket | Theme | Card |
|----|--------|-------|------|

## Notes

- Cards missing `[close-reason: ...]` comment: <N>
- Cards with no ph-WIP correlation: <N>
- Cards dropped since last snapshot: <N> (state drift, if any)
- Warnings: <list>

## Cross-Links

- [Backlog](../backlog.md)
- [Latest Zendesk daily index](../../zendesk/YYYY-MM-DD.md)
```

**Step 7 — Verify against Trello** (sanity check to catch state detection bugs):

Re-check a sample of cards directly in Trello to verify state detection worked correctly:

```python
# State expectations
STATE_EXPECTATIONS = {
    'Shipped': ['SHIPPED', 'PROD'],
    'Ready To Ship': ['QA_VERIFIED'],
    'QA READY': ['Dev Done', 'Ready for QA', 'QA Reported'],
    'DEV': ['DEV'],
    'BUG REPORTED': ['BUG REPORTED'],
    'Open': []  # No state labels
}

# Pick 3 sample cards from each non-empty state bucket
samples = {
    'Shipped': cards_by_state['Shipped'][:3],
    'Ready To Ship': cards_by_state['Ready To Ship'][:3],
    'QA READY': cards_by_state['QA READY'][:3],
    'DEV': cards_by_state['DEV'][:3],
    'Open': cards_by_state['Open (not started)'][:3]
}

# For each sample, check its actual labels in Trello
for state, cards in samples.items():
    for card in cards:
        actual_label_names = [lbl['name'] for lbl in card['labels']]  # from cached data
        expected_labels = STATE_EXPECTATIONS[state]

        if state == 'Open':
            # Open should have NO state labels
            has_state_label = any(lbl in actual_label_names for lbl in ALL_STATE_LABELS)
            if has_state_label:
                print(f"⚠️  MISMATCH: {card['name']} classified as Open but has state label: {actual_label_names}")
        else:
            # Other states should have expected label
            if not any(exp in actual_label_names for exp in expected_labels):
                print(f"⚠️  MISMATCH: {card['name']} classified as {state} but has labels: {actual_label_names}")
```

**Output verification table**:
```
## Verification: Trello vs Release File

| State | Release Count | Sample Cards Checked | Mismatches |
|-------|---------------|---------------------|------------|
| Shipped | N | N | 0 ✓ |
| Ready To Ship | N | N | 0 ✓ |
| QA READY | N | N | 0 ✓ |
| DEV | N | N | 0 ✓ |
| Open | N | N | 0 ✓ |

Sample spot-checks:
- ZI-048 (Ready To Ship): has QA_VERIFIED label ✓
- ZI-071 (QA READY): has Dev Done label ✓
- ZI-058 (Open): no state labels ✓
```

If ANY mismatches found, report them as warnings and suggest re-running with fresh label fetch.

**Step 8 — Report**:
```
## Snapshot <TAG>
- File: wiki/product/releases/<TAG-slug>.md (created | refreshed)
- Board: <board_id>
- Cards total: N  (Shipped: N, Ready To Ship: N, Support Closed: N, BUG REPORTED: N, QA READY: N, DEV: N, Open: N)
- State labels found: 8/8 ✓ (or list missing)
  - SHIPPED: N label(s)
  - PROD: N label(s)
  - QA_VERIFIED: N label(s)
  - Dev Done: N label(s)
  - DEV: N label(s)
  - QA Reported: N label(s)
  - Ready for QA: N label(s)
  - BUG REPORTED: N label(s)
- Verification: N sample cards checked, 0 mismatches ✓
- git_reference: <unchanged | set to HEAD on first snapshot>
- Cards missing close-reason: N
- Cards without ph-WIP match: N
- Drift: N cards dropped since last snapshot  (if any)
- Warnings: <list>
```

### Idempotency guarantees

Running snapshot twice in sequence produces byte-identical body except for `last_synced`. If ph-WIP lanes changed in between, the body may differ in state rows — but the structure is deterministic.

### Post-snapshot validation (recommended)

After running snapshot, validate the results using the validation script:

```bash
python3 .claude/skills/sl-iteration/validate_snapshot.py MCSL-377
```

**What it validates:**
1. **State detection accuracy**: Fetches sample cards from Trello and verifies their state labels match the classification in the release file
2. **Label availability**: Confirms all 8 critical state labels exist on the board
3. **Count consistency**: Verifies frontmatter counts match Summary table counts

**Exit codes:**
- `0` - All validations passed ✓
- `1` - Validation failures found (state mismatches or count discrepancies)
- `2` - Error (missing file, API failure, missing environment variables)

**When to run:**
- After first snapshot (baseline creation)
- After any changes to board labels
- If state counts look suspicious (e.g., all cards showing as "Open")
- Periodically as a health check

**Example output:**
```
======================================================================
VALIDATION SUMMARY
======================================================================

✓ Cards checked: 9
✓ State labels found: 8/8

✅ ALL VALIDATIONS PASSED
   No state mismatches, no count discrepancies
```

If validation fails, the script will report specific mismatches with card names, URLs, expected vs actual states, and label details.

---

## Mode 3c: `/sl-iteration ship <tag> [board] [lane] [--force]`

**Purpose**: freeze the release in wiki state. Propagate shipped work to `wiki/product/backlog.md` and append an entry to `wiki/log.md`. **No Trello writes** at all (no comments, no label changes, no moves, no new lanes). Optionally filter to cards in a specific lane on the source board.

### Flow

**Step 1 — Parse arguments and run snapshot:**

**Parse arguments:**
```python
# Parse: ship <tag> [board] [lane] [--force]
# Use same algorithm as general Mode 3 parsing
import re

tokens = $ARGUMENTS.split()
subcommand = tokens[0]  # "ship"
remaining = tokens[1:]

# Strip --force from end
force_flag = False
if remaining and remaining[-1] == '--force':
    force_flag = True
    remaining = remaining[:-1]

# Find board token position
board_id = None
board_pos = None
for i, token in enumerate(remaining):
    url_match = re.match(r'^https://trello\.com/b/([a-zA-Z0-9]{8,})/?', token)
    if url_match:
        board_id = url_match.group(1)
        board_pos = i
        break
    elif len(token) >= 8 and token.isalnum():
        board_id = token
        board_pos = i
        break

# Split tokens based on board position
if board_pos is not None:
    tag = ' '.join(remaining[:board_pos])
    lane = ' '.join(remaining[board_pos + 1:]) if board_pos + 1 < len(remaining) else None
else:
    board_id = DEFAULT_STORYLAB_BOARD
    tag = ' '.join(remaining)
    lane = None
```

**Run snapshot**: Execute full Mode 3b logic with `board_id`, `tag`, and `lane`. Ensures release.md is current.

**Step 2 — Parse latest snapshot**: Re-read the freshly written release.md. Count cards by state.

**Step 3 — Safety gate**:
- If any card is in `{Open, DEV, BUG REPORTED, QA READY}`:
  - If `--force` NOT passed:
    - Print blocker table:
      ```
      Cannot ship MCSL 377 — N non-terminal cards:

      | ZI | State | ph-WIP Lane | Card |
      | ZI-NNN | DEV | In Dev | [SL](shortUrl) |
      | ...
      ```
    - Offer options (AskUserQuestion): `Pass --force`, `Abort`.
    - Exit without writes if aborted.
  - If `--force` IS passed: proceed, but record the blocker list for inclusion in the release.md `## Warnings` section.
- If all cards are `{PROD, Support Closed}`: proceed without warnings.

**Step 4 — Detect already-shipped**:
- If `frontmatter['status'] == 'shipped'`: prompt `Re-ship MCSL 377? [y/N]` (default N).
  - On N: no-op, exit with status report.
  - On y: proceed with re-ship — preserve `shipped_at`, append new timestamp to `re_shipped_at` array (create array if absent).

**Step 5 — Freeze release.md**:
Update frontmatter:
```yaml
status: shipped
shipped_at: <now>  # or preserved on re-ship
re_shipped_at: [ ... <now> ]  # append on re-ship only
```

If `--force` was used with blockers, append a `## Warnings` section to the body:
```markdown
## Warnings

Shipped with `--force` despite non-terminal cards:

| ZI | State | ph-WIP Lane | Card |
|----|-------|-------------|------|
```

Also update header banner in the body: `> **Status**: SHIPPED 2026-04-16 · ...`.

**Step 6 — Propagate to backlog.md**:
Append (or extend if already present) a `## Shipped in <TAG>` section at the bottom of `wiki/product/backlog.md`:

```markdown
---

## Shipped in <TAG> — <YYYY-MM-DD>

| ZI | Title | Ticket | Theme | Card |
|----|-------|--------|-------|------|
| ZI-NNN | <title> | [#NNNNNN](../../raw/zendesk/<product>/<ticketId>.json) | <theme> | [SL](shortUrl) |
```

Also refresh the `Shipped: N` column in the Active Backlog table. Recompute per cluster by scanning all `wiki/product/releases/*.md` with `status: shipped` and summing ZI counts per cluster. If the `Shipped:` column doesn't exist, add it after the Status column.

**Step 7 — Log entry**:
Append to `wiki/log.md`:
```markdown
## [<YYYY-MM-DD HH:MM>] ship | Release <TAG>
- Release: `wiki/product/releases/<TAG-slug>.md` (status: shipped, shipped_at: <timestamp>)
- Cards shipped (PROD): N
- Cards support-closed: N
- Cards forced (non-terminal at ship): N  [only if --force]
- Git reference: <HEAD>
- Summary: Shipped <TAG> with N total cards. <optional one-liner>
```

**Step 8 — Report**:
```
## Ship <TAG>
- Status: shipped (shipped_at: <timestamp>)
- PROD cards: N
- Support Closed cards: N
- Non-terminal cards at ship: N  [only with --force]
- backlog.md: updated (Shipped in <TAG> section added/extended)
- log.md: entry appended
- Trello writes: 0  (ship is pure wiki write)
```

---

## Backfill Historical Releases (one-time, not a subcommand)

When adopting the release workflow, there are likely StoryLab cards with `🚀 PROD` label that never got a release tag. Backfill them manually:

**Step 1 — Inventory PROD-labeled cards without a release tag**:
```bash
python3 <<'PY'
import json, urllib.request, os
KEY = os.environ['TRELLO_API_KEY']; TOKEN = os.environ['TRELLO_TOKEN']
BOARD = DEFAULT_STORYLAB_BOARD  # Or user-specified board
PROD_LABEL = '69ddcadcd5d8f116d99db5f4'
url = f'https://api.trello.com/1/boards/{BOARD}/cards?fields=name,idLabels,shortUrl&key={KEY}&token={TOKEN}'
cards = json.load(urllib.request.urlopen(url))
# Filter: has PROD label, no release tag (MCSL ...)
release_labels = {L['id'] for L in json.load(urllib.request.urlopen(f'https://api.trello.com/1/boards/{BOARD}/labels?key={KEY}&token={TOKEN}')) if L['name'].startswith('MCSL ')}
orphan = [c for c in cards if PROD_LABEL in c['idLabels'] and not (release_labels & set(c['idLabels']))]
for c in orphan:
    print(f"{c['shortUrl']}  {c['name']}")
PY
```

**Step 2 — Ask the user**: "These N PROD cards aren't release-tagged — which historical release shipped them?" (use AskUserQuestion batches).

**Step 3 — User tags cards manually** on Trello with `MCSL 370`, `MCSL 373`, etc.

**Step 4 — For each historical tag**:
```
/sl-iteration snapshot <tag> [board]
/sl-iteration ship <tag> [board] --force
```

If using a non-default board, pass the board ID/URL to both commands.

Wiki ends up with one release.md per historical tag, each `status: shipped`. Trello state is unchanged (user owns all card moves).

---

## Release Workflow — Error Handling

| Case | Handling |
|------|----------|
| sync before any snapshot exists for the tag | Hard error: `Run /sl-iteration snapshot <tag> first to establish the release baseline.` No writes. |
| snapshot first-run | Creates release.md with `git_reference: HEAD`. sync diffs forward from there; historical Zendesk activity pre-snapshot is NOT comment-posted. |
| `PRIOR_REF` not in git history (rebase/squash) | Warn; fall back to `HEAD~1..HEAD`; include warning in report. |
| sync on a shipped release (`status: shipped`) | Still regen summaries for changed tickets (wiki stays current); SKIP Trello comment posting (frozen cards stay clean). Report notes "release shipped, skipping comments". |
| `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) missing on StoryLab | Warn one-liner; treat all cards as not-Support-Closed; do NOT auto-create (user controls board structure). |
| Multiple StoryLab cards match same ticket (sync) | Post delta comment to each; list all in release.md. |
| StoryLab card has no ph-WIP match AND no Support Closed label | Coarsens to "Open (not started)". |
| StoryLab card has Support Closed AND ph-WIP match | Support Closed wins. Report info: "N cards support-closed while dev tracked on ph-WIP". |
| ph-WIP lane not in Dev Status Classification | Default to `DEV`; log warning naming the lane so the table can be extended. |
| Ship with `--force` on blockers | Proceed; add `## Warnings` section listing forced cards and their ph-WIP lanes. |
| Ship re-run on shipped release | Prompt, default no-op. On yes → snapshot refresh + append to `re_shipped_at`. |
| release.md frontmatter corrupt (unparseable YAML) | Refuse to proceed; ask user to fix manually or delete the file and re-run snapshot. Never silently rewrite. |
| Trello 429 | Exponential backoff 1s/2s/4s; then fail with URL + response body. |
| Empty release (0 tagged cards) | Write release.md with "No cards" note; skip backlog + log changes. |
| Backlog has no entry for a shipped ZI | Log a warning; don't create phantom entry. |
| ph-WIP bulk fetch fails (network) | Abort snapshot/ship with a clear error — cannot determine state without ph-WIP. |

---

## Error Handling

- **No matching release tag** (copy mode): List all StoryLab labels, ask user to pick
- **No qualifying cards**: Report "0 cards found" and exit
- **Card not found** (analyze mode): Show available cards in the lane
- **API failure**: Show failed request URL and response, ask user how to proceed
- **Codebase search returns nothing**: Mark as CONFIDENCE:POOR with one-liner
