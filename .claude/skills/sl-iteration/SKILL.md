---
name: sl-iteration
description: Copy release-tagged cards from StoryLab to ph-WIP as iteration backlog, run AI code analysis on ph-WIP cards, refresh ph-WIP cards from StoryLab updates, and run the release closure workflow (sync / snapshot / ship) for a release tag. Use when the user wants to plan an iteration, move story cards to ph-WIP, analyze cards, refresh ph-WIP cards from StoryLab, sync Zendesk deltas to a release, snapshot a release's Trello state into the wiki, ship/close a release, or says "sl-iteration".
argument-hint: <release-tag> | <release-tag> ZI-NNN | analyze <tag> <ZI-NNN|next|all|@name> | reassess ZI-NNN [--release-tag <tag>] | remove <release-tag> ZI-NNN | swap ZI-OLD ZI-NEW --release <tag> | sync-single ZI-NNN [--name] [--desc] [--labels] | sync <tag> [board] [lane] [--no-sync] | snapshot <tag> [board] [lane] [--no-sync] | ship <tag> [board] [lane] [--no-sync] [--force]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, WebFetch, TodoWrite, AskUserQuestion
disable-model-invocation: false
---

# StoryLab to ph-WIP Iteration Backlog, plus Release Closure

Seven modes:
- **copy** (Mode 1): move StoryLab cards tagged with a release label into a ph-WIP `SL <tag>: Iteration backlog` lane.
- **analyze** (Mode 2): run AI code analysis on ph-WIP cards; classify confidence; update StoryLab dev-status labels.
- **release** (Mode 3): close the loop between Trello + Zendesk and the wiki via three read-leaning subcommands — `sync`, `snapshot`, `ship`.
- **copy-single** (Mode 4): move a single StoryLab card (by ZI ID) from default StoryLab board to ph-WIP `SL <tag>: Iteration backlog` lane with duplicate check.
- **remove-tag** (Mode 5): remove a release tag label from a ph-WIP card.
- **sync-single** (Mode 6): refresh ph-WIP card from StoryLab — sync name, description, and/or labels FROM StoryLab TO ph-WIP based on flags; preserves ph-WIP comments.
- **swap** (Mode 7): atomically swap two cards in a release — remove old card's tag, add new card with tag (combines Mode 5 + Mode 4).

**Arguments**:
- `<release-tag-name>` — Mode 1 copy all tagged cards
- `release-single <release-tag> ZI-NNN` — Mode 4 copy a single card by ZI ID (always from default StoryLab to standard ph-WIP lane)
- `analyze <release-tag> <ZI-NNN>` — Mode 2 analyze a specific card
- `analyze <release-tag> next` — Mode 2 analyze the next unanalyzed card in the named ph-WIP lane
- `analyze <release-tag> all` — Mode 2 analyze all unanalyzed cards in the named ph-WIP lane
- `analyze <release-tag> @<name>` — Mode 2 analyze only cards assigned to a member (matches by username or full name)
- `reassess ZI-NNN [--release-tag <tag>]` — Mode 2 re-run analysis (searches all SL lanes, or scoped to release-tag if provided)
- `remove <release-tag> ZI-NNN` — Mode 5 remove release tag label from a ph-WIP card
- `swap ZI-OLD ZI-NEW --release <tag>` — Mode 7 atomically swap two cards (remove tag from ZI-OLD, add ZI-NEW to release)
- `sync-single ZI-NNN [--name] [--desc] [--labels]` — Mode 6 refresh ph-WIP card from StoryLab (default: all three if no flags)
- `sync <release-tag> [board] [lane]` — Mode 3a: diff Zendesk JSONs vs the release's last `git_reference`, regen summaries, post compact delta comments on tagged StoryLab cards (optionally filtered to a specific lane)
- `snapshot <release-tag> [board] [lane]` — Mode 3b: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current StoryLab + ph-WIP state (optionally filtered to a specific lane)
- `ship <release-tag> [board] [lane] [--force]` — Mode 3c: freeze the release in wiki (status=shipped, backlog + log updates); no Trello writes (optionally filtered to a specific lane)

**Lane resolution (Mode 2 only)**: The `<release-tag>` in analyze commands identifies the ph-WIP lane `SL <release-tag>: Iteration backlog`. If the lane doesn't exist, list all `SL *` lanes and ask user to pick.

**Board default (Mode 3)**: StoryLab (`69dd9134576a26fcb79b670d`) when `[board]` is omitted.

**Examples**:
- `/sl-iteration MCSL 377` — Mode 1 copy all release-tagged cards
- `/sl-iteration release-single MCSL 377 ZI-035` — Mode 4 copy single card ZI-035 to ph-WIP
- `/sl-iteration remove MCSL 377 ZI-035` — Mode 5 remove MCSL 377 tag from ZI-035 in ph-WIP
- `/sl-iteration swap ZI-010 ZI-123 --release MCSL 378` — Mode 7 swap ZI-010 for ZI-123 in MCSL 378 release
- `/sl-iteration sync-single ZI-263` — Mode 6 sync all attributes (name + desc + labels)
- `/sl-iteration sync-single ZI-263 --name --desc` — Mode 6 sync only name and description
- `/sl-iteration analyze MCSL 377 all` — Mode 2 analyze all cards in `SL MCSL 377: Iteration backlog`
- `/sl-iteration analyze MCSL 377 @ajeesh` — Mode 2 analyze cards assigned to Ajeesh
- `/sl-iteration analyze MCSL 377 ZI-035` — Mode 2 analyze ZI-035
- `/sl-iteration reassess ZI-035` — Mode 2 reassess ZI-035 (searches all SL lanes)
- `/sl-iteration reassess ZI-035 --release-tag MCSL 377` — Mode 2 reassess ZI-035 (scoped to MCSL 377 lane)
- `/sl-iteration snapshot MCSL 377` — Mode 3b first-time snapshot (creates release.md baseline, default board: ph-wip)
- `/sl-iteration snapshot MCSL 377 --board storylab` — Mode 3b snapshot from StoryLab board
- `/sl-iteration snapshot MCSL 377 --lane "SL MCSL 377: Iteration backlog"` — Mode 3b snapshot with lane filter (default board: ph-wip)
- `/sl-iteration snapshot MCSL 377 --no-sync` — Mode 3b snapshot, skip submodule updates
- `/sl-iteration sync "MCSL 377"` — Mode 3a delta sync (snapshot must have run first, default board: ph-wip)
- `/sl-iteration sync "MCSL 377" --board storylab` — Mode 3a delta sync from StoryLab board
- `/sl-iteration sync "MCSL 377" --lane "SL MCSL 377: Iteration backlog"` — Mode 3a delta sync with lane filter (default board: ph-wip)
- `/sl-iteration ship "MCSL 377"` — Mode 3c ship release (default board: ph-wip)
- `/sl-iteration ship "MCSL 377" --board storylab` — Mode 3c ship from StoryLab board
- `/sl-iteration ship "MCSL 377" --lane "SL MCSL 377: Iteration backlog"` — Mode 3c ship with lane filter (default board: ph-wip)
- `/sl-iteration ship "MCSL 377" --force` — Mode 3c ship even with non-terminal cards
- `/sl-iteration ship "MCSL 377" --board ph-wip --force --no-sync` — Mode 3c ship with multiple flags

## Dispatch

Parse `$ARGUMENTS` as a token list. Match the **first token**:

| First token | Mode |
|-------------|------|
| `analyze` | Mode 2 analyze |
| `reassess` | Mode 2 reassess |
| `release-single` | Mode 4 copy single card |
| `remove` | Mode 5 remove tag |
| `swap` | Mode 7 swap cards |
| `sync-single` | Mode 6 |
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
- `/sl-iteration sync "MCSL 377"` → tag="MCSL 377", board=PH_WIP_BOARD (default), lane=None
- `/sl-iteration sync "MCSL 377" --board storylab` → tag="MCSL 377", board=DEFAULT_STORYLAB_BOARD, lane=None
- `/sl-iteration sync "MCSL 377" --lane "Dev Done"` → tag="MCSL 377", board=PH_WIP_BOARD (default), lane="Dev Done"
- `/sl-iteration snapshot "MCSL 377"` → tag="MCSL 377", board=PH_WIP_BOARD (default), lane=None
- `/sl-iteration snapshot "MCSL 377" --board storylab` → tag="MCSL 377", board=DEFAULT_STORYLAB_BOARD, lane=None
- `/sl-iteration snapshot "MCSL 377" --lane "SL MCSL 377: Iteration backlog"` → tag="MCSL 377", board=PH_WIP_BOARD (default), lane="SL MCSL 377: Iteration backlog"
- `/sl-iteration ship "MCSL 377" --lane "My Lane" --force` → tag="MCSL 377", board=PH_WIP_BOARD (default), lane="My Lane", force=True
- `/sl-iteration ship "Multi Word Tag" --board xyz12345 --lane "My Lane" --force` → tag="Multi Word Tag", board="xyz12345", lane="My Lane", force=True

**Board Names:**
- `ph-wip` → `63e1e0414b6026c45be1087c` (default)
- `storylab` → `69dd9134576a26fcb79b670d`
- Or use full board ID for other boards

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

### 4. Blast-Radius Analysis Prerequisites (Mode 2 only)

**Mode 2 analyze invokes the `/find-co-dependencies` skill** (via Skill tool) with `--derive-actionable-items` to generate comprehensive implementation checklists. This requires the following dependency maps to exist:

| Map | Built by skill | Check existence |
|-----|----------------|----------------|
| Test coverage | `/reverse-test-coverage build` | `wiki/architecture/reverse-test-coverage.md` |
| Code coupling | `/git-co-change-graph delta` | `wiki/architecture/coupling-map.md` |
| ZI area coupling | `/zendesk-overlap build` | `wiki/zendesk/area-coupling.md` |

**One-time setup**: The `/find-co-dependencies build` command orchestrates all three skills to build the maps. Run this once before first use of Mode 2 analyze.

**If maps are missing** (card analysis continues, but with limited recommendations):
- Blast-radius analysis is skipped
- A note is added to the card: "⚠️ Run `/find-co-dependencies build` to enable blast-radius analysis"
- User can run `/find-co-dependencies build` once, then use `reassess ZI-NNN` to regenerate the card with full recommendations

**How the skill invocation works**: Mode 2 uses the Skill tool to invoke find-co-dependencies:
```
Skill: find-co-dependencies
Args: query <file-or-area> --derive-actionable-items
```

The find-co-dependencies skill reads the three dependency maps and returns structured recommendations that are formatted into the card's "🎯 Implementation Checklist" section.

---

## Board IDs and Names

**Friendly board names** are supported for easier command usage:

| Board Name | Board ID | Default? | Usage |
|------------|----------|----------|-------|
| `ph-wip` | `63e1e0414b6026c45be1087c` | ✅ Yes (Mode 3) | Target board for iteration workflow (Mode 1 always uses this; Mode 3 default) |
| `storylab` | `69dd9134576a26fcb79b670d` | Yes (Mode 1) | Source board (Mode 1 default; Mode 3 can specify with `--board storylab`) |

**Using board names:**
- Mode 3 commands (sync, snapshot, ship) accept `--board <name>` flag: `--board storylab` or `--board ph-wip`
- If no `--board` flag is provided, defaults to `ph-wip` (iteration workflow board)
- Board IDs are still supported for other boards: `--board abc12345`

**Python constants:**
```python
DEFAULT_STORYLAB_BOARD = '69dd9134576a26fcb79b670d'
PH_WIP_BOARD = '63e1e0414b6026c45be1087c'

BOARD_NAMES = {
    'storylab': '69dd9134576a26fcb79b670d',
    'ph-wip': '63e1e0414b6026c45be1087c',
}
```

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

## Overview

Mode 2 performs comprehensive AI-assisted code analysis on ph-WIP cards, combining:
1. **Code search & analysis** — locate affected files, understand root cause
2. **Blast-radius analysis** — identify technical coupling via `/find-co-dependencies` skill
3. **Actionable recommendations** — generate acceptance criteria, test plans, review checklists

**Output**: Analysis uploaded as timestamped markdown attachment (`ZI-{id}-analysis-{YYYYMMDDHHMMSS}.md`):
- Affected files and root cause
- Suggested implementation approach
- Complete implementation checklist with test/review/validation recommendations
- Full history preserved (all analysis attachments retained)

## Skill Dependencies

**CRITICAL: Mode 2 depends on the `/find-co-dependencies` skill** for blast-radius analysis and actionable recommendations.

The analyze workflow invokes `/find-co-dependencies` with the `--derive-actionable-items` flag to:
- Identify code coupling (files that change together)
- Map test coverage (which tests exercise the affected code)
- Surface ZI area overlaps (features that break together in customer tickets)
- Generate implementation checklists (Must-Pass tests, Regression Watch areas, Manual Spot-Check scenarios)

**Prerequisites**: Before first use of Mode 2 analyze, run `/find-co-dependencies build` to initialize the dependency maps:
- Test coverage map (`wiki/architecture/reverse-test-coverage.md`)
- Code coupling map (`wiki/architecture/coupling-map.md`)
- ZI area coupling map (`wiki/zendesk/area-coupling.md`)

If these maps are missing, analysis continues without blast-radius recommendations (see Step 4.5 error handling).

## Confidence Levels

| Level | Criteria |
|-------|----------|
| **HIGH** | Found specific file + function, error message matches, clear code path |
| **MEDIUM** | Found module/area, 2-3 candidate files, needs dev confirmation |
| **LOW** | Found general area, issue spans multiple files or is architectural |
| **POOR** | No meaningful code match, or purely product/UX decision with no code to anchor to |

## Execution Overview

**All analyze commands use the same core workflow.** The different commands (`analyze ZI-NNN`, `analyze next`, `analyze all`, `analyze @member`, `reassess ZI-NNN`) differ only in **how they select which cards to process**. Once a card is selected, it goes through the identical analysis workflow (Steps 1-7 below).

**Card Selection Methods**:

| Command | Card Selection |
|---------|----------------|
| `analyze <tag> ZI-NNN` | Analyze specific card by ZI ID in the `SL <tag>: Iteration backlog` lane |
| `analyze <tag> next` | Analyze the first card without a confidence label in the `SL <tag>: Iteration backlog` lane |
| `analyze <tag> all` | Analyze all cards without confidence labels in the `SL <tag>: Iteration backlog` lane |
| `analyze <tag> @<member>` | Analyze all unanalyzed cards assigned to a specific member in the `SL <tag>: Iteration backlog` lane |
| `reassess ZI-NNN [--release-tag <tag>]` | Re-analyze a specific card (search all `SL *` lanes if no tag provided) |

**Key distinction between first-time and reassessment**:
- **First-time analysis**: Card has no existing analysis attachments (`ZI-{id}-analysis-*.md`) → upload first analysis attachment
- **Reassessment**: Card has existing analysis attachment(s) → upload new timestamped attachment (preserves history) AND post a summary comment

Both use the exact same Steps 1-7. Step 7 behavior differs based on whether analysis attachments exist.

---

## Core Workflow: Analyze Single Card

**This is the canonical workflow used for ALL analyze operations.** Whether you're analyzing one card, the next card, all cards, or reassessing—every card goes through these identical steps.

### Step 0: Resolve the target lane (card selection only)

**For `analyze <tag> ...` commands**:

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

**For `reassess ZI-NNN [--release-tag <tag>]`**:
- If `--release-tag <tag>` is provided: resolve the lane name `SL <tag>: Iteration backlog` (case-insensitive match), then search only that lane for the card
- If no `--release-tag` flag: search ALL `SL *` lanes on ph-WIP for a card matching the ZI ID in its name, use the first match found

**Argument parsing for reassess**:
```python
import re

tokens = args.split()  # ["reassess", "ZI-NNN", "--release-tag", "MCSL", "377"]
zi_id = tokens[1] if len(tokens) > 1 else None

# Check for --release-tag flag
release_tag = None
if '--release-tag' in tokens:
    tag_idx = tokens.index('--release-tag')
    # Collect all tokens after --release-tag as the tag (may be multi-word)
    release_tag = ' '.join(tokens[tag_idx + 1:])
```

### Step 1: Read ALL context from the card

Four sources — read all of them:

1. **ph-WIP card description**: `GET /cards/{cardId}?fields=name,desc,idLabels,shortUrl`
   - The first line is the StoryLab `shortUrl`
   - May already contain a previous `## AI Code Analysis` section (if reassessing)
   - May contain additional notes added by devs

2. **ph-WIP card comments**: `GET /cards/{cardId}/actions?filter=commentCard`
   - Devs may have added context, file paths, error logs, clarifications

3. **StoryLab card**: Follow the `shortUrl` from the ph-WIP description → `GET /cards/{shortId}?fields=name,desc`
   - Contains full ticket summary, user story, acceptance criteria
   - **CRITICAL**: Read and analyze the COMPLETE `desc` field (no truncation for display or analysis)
   - The entire StoryLab description provides essential context (problem statement, acceptance criteria, customer evidence)
   - When debugging, you may show a preview for logging, but the FULL content must be used for analysis

4. **Previous analysis** (if reassessment): `GET /cards/{cardId}/attachments?fields=name,url`
   - Check for existing `ZI-{id}-analysis-*.md` attachments
   - If found, read the **most recent** attachment (sorted by timestamp in filename)
   - Provides baseline: previous findings, confidence level, edge cases documented, developer feedback
   - Use to compare: what changed? new information? better understanding?

**Extract search terms from ALL four sources**: error messages, carrier names, feature names, UI element references, file paths, API endpoints, component names.

### Step 1.4: How to use previous analysis (reassessment only)

**If `is_reassessment == True`**, use the previous analysis content throughout Steps 2-5:

**During Step 2 (Search codebase)**:
- Previous analysis identified specific files? → Start search there
- Previous analysis flagged specific functions? → Read those first
- Previous analysis suggested approach? → Validate if still applicable

**During Step 3.5 (Edge scenarios)**:
- Previous analysis documented edge cases? → Verify they're still captured
- Add NEW edge cases discovered since last analysis
- Flag if edge scenario matrix changed significantly

**During Step 4 (Assess confidence)**:
- Previous confidence: HIGH → now finding contradictions? → May downgrade to MEDIUM
- Previous confidence: POOR → now found specific files? → Upgrade to MEDIUM/HIGH
- Same confidence → explain what additional validation was done

**During Step 5 (Write analysis)**:
- **Key Findings section**: Compare status
  - Previous: "📝 READY FOR DEV" → now: "✅ FIX IMPLEMENTED" (found merged PR)
  - Previous: "⏸️ BLOCKED" → now: "📝 READY FOR DEV" (blocker resolved)
- **Root Cause section**: Note if understanding changed
  - "Previous analysis identified X, but further investigation reveals Y"
  - "Confirms previous analysis: root cause is still X"
- **Affected Files**: Highlight if new files discovered
  - "Previous: 2 files; Now: 4 files (added Z, W)"
- **Edge Scenario Matrix**: Show delta
  - Mark scenarios from previous analysis with ✓ (already documented)
  - Mark new scenarios with 🆕

**Reassessment analysis should**:
- **Build on** previous work, not ignore it
- **Highlight deltas** (what changed? what's new?)
- **Acknowledge** if previous analysis was accurate or needed correction
- **Preserve** valid edge cases and recommendations from before

### Step 1.5: Read coding standards and testing guidelines

**BEFORE analyzing code or writing recommendations**, read:
- `.claude/docs/coding-standards.md` — coding standards and best practices
- `.claude/docs/testing-guide.md` — testing requirements and patterns

These documents inform:
- How to structure suggested code changes
- What testing approach to recommend
- Architectural patterns to follow
- Quality standards for the implementation

Apply these standards when writing the "Suggested Approach", "Test Coverage", and "Implementation Checklist" sections.

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

### Step 3.5: Identify edge scenarios

**CRITICAL**: Always work out edge scenarios for the feature/bug. Edge cases are where most bugs hide and where customer issues originate.

**Systematically analyze**:

1. **Boundary Conditions**
   - Zero values (0 products, $0.00 price, 0 quantity, empty shipping cost)
   - Null/undefined fields (missing customer data, optional fields not provided)
   - Empty collections (no line items, no packages, empty cart)
   - Maximum limits (max package count, max weight, max dimension values)
   - Minimum enforcement (minimum order value, minimum package weight)

2. **Multi-Entity Scenarios**
   - Multiple packages per order (2, 3, 10+ packages)
   - Mixed product types (physical + digital, hazmat + non-hazmat)
   - Multiple line items with edge prices (some $0, some >$0)
   - Multi-carrier scenarios (different carriers for different packages)
   - Bulk operations (100+ orders in batch)

3. **Toggle/Configuration Combinations**
   - Feature flags in different states (ON/OFF combinations)
   - Carrier settings overrides (global vs per-order settings)
   - Platform-specific behavior (Shopify vs WooCommerce vs Magento)
   - Plan-based features (free vs paid tier capabilities)

4. **Error Conditions**
   - API failures (carrier API down, timeout, 5xx errors)
   - Validation failures (invalid address, missing required fields)
   - Missing data (product without SKU, order without shipping address)
   - Stale data (order updated since page load, concurrent edits)
   - Partial failures (1 of 3 labels succeeds, 2 fail)

5. **Timing/State Issues**
   - Race conditions (two users editing same order)
   - State transitions (order canceled during label generation)
   - Retry scenarios (user clicks "generate" multiple times)
   - Async dependencies (address validation pending, rate fetch in progress)

6. **Backward Compatibility**
   - Old data format (orders created before field existed)
   - Migration scenarios (carrier API version upgrade)
   - Deprecated features (old UI still in use, old automation rules)
   - Missing new fields (existing orders without new shipmentType field)

**Output format for edge scenario matrix**:

Create a structured table of edge scenarios with expected vs actual behavior:

```
| # | Scenario | Input State | Expected Behavior | Risk Level | Mitigation |
|---|----------|-------------|-------------------|------------|-----------|
| 1 | Zero product price with shipping cost | Product=$0, Shipping=$50, Toggle=ON | Should return $50 | Medium | Test case needed |
| 2 | All zero with override toggle | Product=$0, Shipping=$0, Override=ON | Uses fallback (1) | High | Validation needed |
| 3 | Multi-package with mixed prices | 3 packages, prices: $0, $100, $50 | Proportional allocation | Medium | Review allocation logic |
```

**When to flag for manual testing**:
- Any scenario marked "High" risk requires explicit manual test case
- Complex combinations (3+ variables) require exploratory testing
- Scenarios involving $0 or null values need special attention
- Backward compatibility scenarios with old data formats

**Example edge matrix** (from provided image):
- Zero product + zero shipping + toggle ON → should use minimum (not return 0.00) ❌ BUG
- Zero product + zero shipping + toggle OFF → should use package price ❌ BUG
- Multi-package with all zero + fallback → should distribute per-package ⚠️ EDGE

### Step 4: Assess confidence

Based on Steps 1-3 results, assign: HIGH, MEDIUM, LOW, or POOR.

### Step 4.5: Run blast-radius analysis (invoke find-co-dependencies skill)

**For HIGH / MEDIUM / LOW confidence only** (skip for POOR):

**Use the Skill tool to invoke `/find-co-dependencies`** with `--derive-actionable-items` to identify technical coupling and generate actionable recommendations.

**Skill invocation syntax**:
```
Skill tool with skill="find-co-dependencies" and args="<command> <target> --derive-actionable-items"
```

**Choose the appropriate mode**:

1. **If specific files identified** (HIGH/MEDIUM confidence with file paths):
   ```
   Skill: find-co-dependencies
   Args: query <primary-file-path> --derive-actionable-items
   ```
   Example: If analysis identified `server/src/shared/orders/OrderProcessingService.js` as the primary file:
   ```
   Skill: find-co-dependencies
   Args: query server/src/shared/orders/OrderProcessingService.js --derive-actionable-items
   ```

2. **If area/domain identified but not specific files** (MEDIUM/LOW confidence):
   ```
   Skill: find-co-dependencies
   Args: query <area> --derive-actionable-items
   ```
   Example: If analysis identified `label-generation` area:
   ```
   Skill: find-co-dependencies
   Args: query label-generation --derive-actionable-items
   ```

   **Area mapping** (use these for query):
   - Carrier-related → `carrier-config`
   - Label generation → `label-generation`
   - Order processing → `order-management`
   - International/customs → `international`
   - Rates/pricing → `rate-shopping`
   - Tracking → `tracking`
   - Returns → `returns`

3. **If conceptual/feature-based** (LOW confidence or architectural):
   ```
   Skill: find-co-dependencies
   Args: semantic "<card description>" --derive-actionable-items
   ```
   Use when the issue is more conceptual (UX flow, business logic) than code-specific

   Example:
   ```
   Skill: find-co-dependencies
   Args: semantic "FedEx international shipments fail customs validation" --derive-actionable-items
   ```

**Process the output** into the checklist format (Step 5):

From find-co-dependencies output, extract and transform:

1. **Must-Pass** — Direct test coverage from "Automated Tests (Starting Point)" where Priority=MUST
2. **Regression Watch** — High-coupling files (≥10 co-changes) from "Suggested Code Review Checklist"
3. **Manual Spot-Check** — ZI area overlaps from "Suggested Customer Validation Scenarios", ranked by ticket count × co-change count
4. **Done Definition** — Synthesize from Must-Pass tests + top 2-3 manual scenarios

**Format as checkboxes** for developer action (not completed yet).

**If the find-co-dependencies skill invocation fails** (dependency maps not built, skill error, skill not available):
- Skip blast-radius analysis
- Include note in analysis: "⚠️ Run `/find-co-dependencies build` to enable blast-radius analysis"
- Continue with Step 5 (code analysis and root cause identification still proceed normally)

**Common failure reasons**:
- Maps not initialized: User hasn't run `/find-co-dependencies build` yet
- Skill error: The find-co-dependencies skill returned an error or unexpected output
- Skill unavailable: The find-co-dependencies skill is not installed or accessible

### Step 5a: Derive Key Findings

Before writing the detailed analysis, derive a concise executive summary:

**Status** - Determine implementation status:
1. Check git history for recent merges related to the card:
   ```bash
   cd raw/storepep-react && git log --oneline --all --since="30 days ago" | grep -i "<search-terms-from-card>"
   ```
2. If merged PR found → "✅ FIX IMPLEMENTED — PR #NNNN merged YYYY-MM-DD"
3. If branch exists but not merged → "🚧 IN PROGRESS — Branch: <name>"
4. If blocked/waiting → "⏸️ BLOCKED — <blocker>"
5. Otherwise → "📝 READY FOR DEV"

**Confidence** - Already derived in Step 4

**Affected Files** - Count and list:
```
N (file1.js, file2.js, ...)
```
Limit to top 3 files if more than 3.

**Root Cause** - One-sentence summary extracted from detailed analysis

**Solution** - One-sentence summary:
- If implemented: "Added X to Y, fixed Z in W"
- If not implemented: "Proposed approach: Add X to Y"

**Risk Level** - Derive from blast-radius:
- **⚠️ High**: ≥10 co-change partners OR ≥5 ZI area overlaps OR critical path files OR no test coverage
- **ℹ️ Medium**: 3-9 co-change partners OR 2-4 ZI area overlaps OR partial test coverage
- **✅ Low**: <3 co-change partners AND <2 ZI area overlaps AND good test coverage

**Next Step** - Based on status:
- If implemented → "QA verification using checklist below"
- If in progress → "Complete implementation, run tests"
- If ready for dev → "Implementation"
- If poor confidence → "Investigation / code search"

**PR Link** (optional) - If PR found in git history, extract link from commit message or construct:
```
https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/NNNN
```

### Step 5: Write analysis to temp file

**For HIGH / MEDIUM / LOW** — build this markdown and save to file:

**Filename format**: `ZI-{id}-analysis-{YYYYMMDDHHMMSS}.md` (e.g., `ZI-035-analysis-20260426143022.md`)

**File content**:

```markdown
# AI Code Analysis — ZI-{id}

**Generated**: {YYYY-MM-DD HH:MM:SS UTC}
**Confidence**: HIGH | MEDIUM | LOW

---

##### PR: [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/NNNN](link)

(Include PR line only if PR found in Step 5a)

---

## 📋 Key Findings

**Status**: <derived-status>
**Confidence**: HIGH | MEDIUM | LOW
**Affected Files**: N (file1, file2, ...)
**Root Cause**: <one-line summary>
**Solution**: <one-line summary>
**Risk Level**: ⚠️ High | ℹ️ Medium | ✅ Low
**Next Step**: <derived-next-step>

---

<If is_reassessment == True, include this section:>

## 🔄 Reassessment Delta

**Previous Analysis**: ZI-{id}-analysis-{previous-timestamp}.md
**Previous Confidence**: <confidence from previous analysis>
**New Confidence**: <current confidence> (<unchanged | upgraded | downgraded>)

**What Changed**:
- <bullet 1: new information discovered>
- <bullet 2: understanding refined>
- <bullet 3: previous assumption validated/corrected>

**Affected Files Delta**:
- Previous: {N} files
- Now: {M} files
- <Added | Removed | Same>: {file list if changed}

**Root Cause Evolution**:
- **Previous understanding**: <one-line from previous analysis>
- **Current understanding**: <one-line from this analysis>
- **Assessment**: <Confirmed | Refined | Corrected>

**Edge Scenarios Delta**:
- ✓ {N} scenarios from previous analysis preserved
- 🆕 {M} new scenarios identified
- ❌ {P} scenarios removed (no longer applicable)

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

**Blast Radius Summary**:
<1-2 sentence overview: what else could break if this code is changed — other carriers, other features, shared modules>

---

## 🎯 Implementation Checklist

**Note**: LLM-generated from blast-radius analysis. Review and adapt to your implementation.

### Acceptance Criteria to Verify

**Must-Pass (Direct Test Coverage)**
These specs directly exercise the affected files — all must pass before merge:

<For each test suite from direct coverage (output_mode=content):>
- [ ] `{test_path}` — {what it tests}

**Regression Watch (Indirect via Co-Change Partners)**
These aren't direct tests but break historically when this code changes:

<For each high-coupling file (≥10 co-changes):>
- [ ] {Feature area} still works — `{coupled_file}` co-changes {N}×; verify {specific behavior to check}

### Features to Manually Spot-Check

Ranked by customer impact (ticket volume × code coupling):

**{Area 1} ({N} tickets, {M} co-changes)** — highest blast radius
- {Specific scenario to test}
- {Another scenario}

**{Area 2} ({N} tickets, {M} co-changes)**
- {Scenario}

**{Area 3} ({N} tickets, {M} co-changes)**
- {Scenario}

### "Done" Definition for This Card

Before marking complete, the developer should be able to confirm:

| Check | Method |
|-------|--------|
| All {N} direct spec suites pass | Run Playwright specs |
| {High-risk feature 1} | {How to verify} |
| {High-risk feature 2} | {How to verify} |
| {Top customer scenario} | {How to verify} |

**The two highest-risk items to not skip**: {item 1} (most customer tickets) and {item 2} (most code coupling).

<If blast-radius analysis was skipped (POOR confidence or analysis failed), omit this entire section.>
```

**Markdown structure notes**:
- The "Blast Radius Summary" section provides a high-level overview (keep concise)
- The "🎯 Implementation Checklist" section includes the full actionable items from find-co-dependencies
- Use `---` horizontal rule to visually separate the code analysis from the implementation checklist
- Preserve all review prompts (💡) and formatting from find-co-dependencies output

**Example complete analysis file** (HIGH confidence with blast-radius):

```markdown
# AI Code Analysis — ZI-035

**Generated**: 2026-04-26 14:30:22 UTC
**Confidence**: HIGH

---

##### PR: https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/2567

---

## 📋 Key Findings

**Status**: 🚧 IN PROGRESS — Branch: feature/fedex-customs-fix
**Confidence**: HIGH
**Affected Files**: 2 (labelGeneration.js, FedExAdaptor.js)
**Root Cause**: FedEx REST API requires customsValue in commercialInvoice object, but current code only sends it at shipment level
**Solution**: Add customsValue extraction from order items, include in commercialInvoice object
**Risk Level**: ℹ️ Medium — isolated change but needs international shipping validation
**Next Step**: Complete implementation, verify with test suite

---

## AI Code Analysis

**Confidence**: HIGH

**Affected Files**:
- `server/src/shared/orders/labelGeneration.js:234` — Label generation logic for FedEx, handles customs data
- `server/src/shared/API/carriers/FedExAdaptor.js:567` — FedEx API integration, buildLabelRequest function

**Root Cause / Gap**:
FedEx REST API requires `customsValue` field in commercialInvoice object, but current code only sends `customsValue` at shipment level. API rejects with "Missing required field: commercialInvoice.customsValue".

**Suggested Approach**:
- Update `labelGeneration.js` to extract `customsValue` from order items
- Modify `FedExAdaptor.buildLabelRequest()` to include `customsValue` in commercialInvoice object
- Add validation to ensure customs value is present for international FedEx shipments

**Test Coverage**:
- Existing: `specialServices/customsDeclaration.spec.ts` covers customs data entry
- Needed: Add test for FedEx international label generation with customs value

**Blast Radius Summary**:
Changes affect FedEx carrier integration and customs handling. Other carriers (UPS, USPS) use different customs field structure, should not be impacted. International shipping workflow and label generation UI may need validation updates.

---

## 🎯 Implementation Checklist

**Note**: LLM-generated from blast-radius analysis. Review and adapt to your implementation.

### Acceptance Criteria to Verify

**Must-Pass (Direct Test Coverage)**
These specs directly exercise the affected files — all must pass before merge:

- [ ] `specialServices/customsDeclaration.spec.ts` — customs data entry and validation
- [ ] `orderGrid/labelGenerationFromGrid/generateLabels.spec.ts` — label generation from order grid

**Regression Watch (Indirect via Co-Change Partners)**
These aren't direct tests but break historically when this code changes:

- [ ] Label generation for other carriers — `labelGeneration.js` co-changes 45×; verify UPS, USPS international labels still generate
- [ ] Carrier adapter integrity — `CarrierAdaptorFactory.js` co-changes 28×; confirm FedEx routing unchanged for non-international shipments

### Features to Manually Spot-Check

Ranked by customer impact (ticket volume × code coupling):

**International shipping (12 tickets, 45 co-changes)** — highest blast radius
- Generate FedEx international label with commercial invoice (single item)
- Generate FedEx international label with multiple line items (verify customs value aggregation)
- Verify customs declaration fields appear on label PDF

**Carrier config (8 tickets, 34 co-changes)**
- Switch order's carrier from UPS to FedEx after initial assignment
- Verify rate fetch still works for FedEx international services

**Label generation workflow (6 tickets, 87 co-changes)**
- Batch label generation from grid with mixed domestic/international orders
- Verify international labels don't block batch if customs data missing

### "Done" Definition for This Card

Before marking complete, the developer should be able to confirm:

| Check | Method |
|-------|--------|
| All 2 direct spec suites pass | Run Playwright specs |
| FedEx international label with customs | Manual: Create order, generate label, verify commercial invoice |
| Other carriers unaffected | Manual: Generate UPS/USPS international label |
| Batch processing intact | Manual: Generate 5 labels (3 domestic, 2 international) |

**The two highest-risk items to not skip**: international label generation (most customer tickets) and label generation workflow (most code coupling).
```

**For POOR** — minimal file:

```markdown
# AI Code Analysis — ZI-{id}

**Generated**: {YYYY-MM-DD HH:MM:SS UTC}
**Confidence**: POOR

---

## AI Code Analysis

**Confidence**: POOR

Needs human triage — no code match found. Issue is too vague or requires product decision before code analysis.
```

**File path format**: Use paths relative to `storepepSAAS/` (e.g., `server/src/routes/bulkActions.js:98`). Include line numbers when referencing specific code.

**Save the analysis file** to a temp location (e.g., `/tmp/ZI-{id}-analysis-{YYYYMMDDHHMMSS}.md`) for upload in Step 6.

### Step 6: Upload analysis attachment + update card

**6.1 Check for existing analysis and read if present (determines first-time vs reassessment)**:

Check if the card already has any attachments with name pattern `ZI-{id}-analysis-*.md`, and if so, read the most recent one:

```python
import re, urllib.request

# Fetch attachments with name and URL
url = f'https://api.trello.com/1/cards/{cardId}/attachments?fields=name,url&key={KEY}&token={TOKEN}'
attachments = json.load(urllib.request.urlopen(url))

# Find analysis attachments
zi_id_pattern = rf"^{zi_id}-analysis-\d{{14}}\.md$"
analysis_attachments = [att for att in attachments if re.match(zi_id_pattern, att['name'])]

has_existing_analysis = len(analysis_attachments) > 0
is_reassessment = has_existing_analysis

# If reassessment, read the most recent analysis
previous_analysis_content = None
if is_reassessment:
    # Sort by timestamp in filename (descending)
    analysis_attachments.sort(key=lambda x: x['name'], reverse=True)
    latest_analysis = analysis_attachments[0]

    # Fetch analysis content
    analysis_response = urllib.request.urlopen(latest_analysis['url'])
    previous_analysis_content = analysis_response.read().decode('utf-8')

    print(f"📄 Reading previous analysis: {latest_analysis['name']}")
    print(f"   Previous confidence: {extract_confidence_from_markdown(previous_analysis_content)}")
    print(f"   Previous affected files: {extract_affected_files_from_markdown(previous_analysis_content)}")
```

**Helper functions** (to extract key info from previous analysis):

```python
def extract_confidence_from_markdown(content):
    """Extract confidence level from analysis markdown."""
    match = re.search(r'\*\*Confidence\*\*:\s*(HIGH|MEDIUM|LOW|POOR)', content)
    return match.group(1) if match else 'Unknown'

def extract_affected_files_from_markdown(content):
    """Extract affected files count from Key Findings."""
    match = re.search(r'\*\*Affected Files\*\*:\s*(\d+)', content)
    return match.group(1) if match else 'Unknown'
```

**Use previous analysis in Step 1-5**: When analyzing, compare new findings against `previous_analysis_content`:
- Has the root cause changed?
- Are there new affected files?
- Has confidence increased/decreased?
- What edge cases were already documented?
- Were there developer comments suggesting areas to focus on?

**6.2 Upload analysis as attachment**:

Upload the temp file created in Step 5 as a Trello attachment:

```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/attachments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -F "file=@/tmp/ZI-{id}-analysis-{YYYYMMDDHHMMSS}.md" \
  -F "name=ZI-{id}-analysis-{YYYYMMDDHHMMSS}.md"
```

**All analysis attachments are preserved** — Trello maintains full history. Users can view all past analyses sorted by timestamp in the attachment list.

**6.3 Simplify card description** (idempotent — safe to run multiple times):

Set description to minimal content:

```python
# Extract StoryLab URL from first line (always preserved)
existing_desc = card['desc']
lines = existing_desc.split('\n')
storylab_url = lines[0] if lines else ''

# Set minimal description
new_desc = f"{storylab_url}\n\n_Latest AI analysis: see attachments (sorted by date)_"
```

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"desc": "<new_desc from above>"}'
```

**Important**: This step is **idempotent** and preserves the StoryLab URL. If devs add manual notes between the URL and the AI note, they will be overwritten. **Devs should use comments** for manual notes, not the description.

**6.4 Remove any existing confidence label** from the card:
```bash
# For each of the 4 confidence label IDs, try DELETE (ignore 404):
curl -s -X DELETE "https://api.trello.com/1/cards/{cardId}/idLabels/{labelId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN"
```

**6.5 Add new confidence label**:
```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/idLabels?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "<confidence label ID>"}'
```

### Step 7: Report and (optionally) post reassessment comment

**7.1 Post reassessment comment** (only if `is_reassessment == True` from Step 6.1):

```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "**Reassessment completed** (sl-iteration analyze)\n\n**Confidence**: <LEVEL> (updated)\n**Status**: <status from Key Findings>\n\n**Root Cause Identified**: \n<one-sentence summary from analysis>\n\n**Key Files**:\n- <file:line>\n- <file:line>\n\n**Implementation**: <brief scope, e.g., \"One-line fix + tests\">.\n\n📎 **Full analysis**: See latest attachment `ZI-{id}-analysis-{YYYYMMDDHHMMSS}.md`"}'
```

This comment provides stakeholders with:
- Updated confidence level
- Current status (from Key Findings)
- Root cause summary
- Key affected files with line numbers
- Implementation scope summary
- Reference to the latest analysis attachment (timestamped)

**Skip comment posting if first-time analysis** (`is_reassessment == False`). First-time analysis uploads the attachment only—no comment needed.

**7.2 Print report** for user review:

- Card name
- Analysis type (First-time or Reassessment)
- Confidence level
- Key affected files (top 3)
- Root cause summary (1 sentence)
- Blast-radius: ✓ included (or "⚠️ skipped - maps not built")
- Attachment filename

**Report format**:
```
✅ Analyzed: ZI-NNN — <card title>

Type: First-time analysis | Reassessment
Confidence: HIGH
Affected files: 3 (labelGeneration.js, FedExAdaptor.js, OrderHelper.js)
Root cause: FedEx REST API requires customsValue in commercialInvoice object

Implementation checklist: ✓
- Must-Pass: 2 test suites
- Regression Watch: 2 high-coupling areas
- Manual Spot-Check: 3 features (ranked by impact)
- Done Definition: 4 checks before merge

Attachment uploaded: ZI-035-analysis-20260426143022.md
Comment posted: ✓ (reassessment summary for stakeholders) | ✗ (first-time, no comment)
Card updated: https://trello.com/c/ABC123
```

**7.3 Wait for user** to say "next" before processing the next card (for `analyze next`, `analyze all`, `analyze @member` modes).

---

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

## 11-State Legend (coarsening for release reports)

Release views classify each tagged StoryLab card by the HIGHEST-precedence **label** found on ANY matching ph-WIP card (matched by Zendesk ticket ID in the card name/desc/attachments/comments). Lane membership is NOT used for state — labels are the authoritative delivery signal.

**Do NOT read StoryLab dev labels** (`🛠️ DEV`, `✅ DEV DONE`, `🧪 QA`, `🚀 PROD`, `📋 BACKLOG`). Those are cached projections from Mode 2 analyze and may be stale. Always read ph-WIP labels live.

**ph-WIP label precedence** (high → low, match by NAME not ID — ph-WIP has multiple labels with the same name and varying colors):

```
SHIPPED  >  PROD  >  QA_VERIFIED  >  SL: Carrier Platform Issues  >  QA Reported  >  Ready for QA  >  Dev Done  >  DEV  >  Spill Over
```

**Coarsening to 11-state legend**:

| Legend state | Label source | Label name(s) | Meaning |
|--------------|--------------|---------------|---------|
| `Shipped` | ph-WIP | `SHIPPED`, `PROD` | Deployed to production |
| `Ready To Ship` | ph-WIP | `QA_VERIFIED` | QA verified, ready to deploy |
| `High Risk` | ph-WIP + StoryLab | `QA_VERIFIED` + (`SL: Carrier Platform Issues` OR `Unsupported Partnership`) | Cards with QA_VERIFIED and either external issue; possible use of customer credentials for verification |
| `Support Closed` | StoryLab | `Closed by Support`, `SL: Closed By Support` | Closed by support without code (case-insensitive) |
| `Unsupported Partnership` | StoryLab | `Unsupported Partnership For Carrier` | Unsupported carrier/partnership (case-insensitive) |
| `Carrier Platform Issues` | ph-WIP | `SL: Carrier Platform Issues` | External carrier/platform environment issues we cannot solve |
| `BUG REPORTED` | ph-WIP | `BUG REPORTED` | Bug found in QA |
| `QA READY` | ph-WIP | `QA Reported`, `Ready for QA`, `Dev Done` | In QA testing (not yet verified) |
| `DEV` | ph-WIP | `DEV` | Active development |
| `Open (not started)` | (none) | NO state label on any matching ph-WIP card | Not started |
| `Spill Over` | ph-WIP | `Spill Over` | Cards that could not be completed in the current iteration and were moved out |

**Label precedence rules**:
1. StoryLab closure labels (`Support Closed`, `Unsupported Partnership`) **override** any ph-WIP state
2. Within ph-WIP labels, precedence follows the order above (SHIPPED > PROD > QA_VERIFIED > SL: Carrier Platform Issues > ...)
3. **High Risk detection**: Cards with `QA_VERIFIED` AND (`SL: Carrier Platform Issues` OR `Unsupported Partnership`) are flagged in a separate "High Risk" section (after Ready To Ship). These cards inherit "Ready To Ship" state for precedence purposes but are highlighted due to possible use of customer credentials for verification.
4. If NO labels found → `Open (not started)`

**Do NOT exclude SL-copy cards** (cards named `From SL: ...` in `SL <tag>: Iteration backlog` lanes). Devs often apply state labels directly to the SL-copy rather than creating separate dev cards. Search ALL ph-WIP matches for state labels.

**Closed** = {Shipped, Support Closed, Unsupported Partnership, Carrier Platform Issues}. **Open** = {Open, DEV, BUG REPORTED, QA READY, Ready To Ship, High Risk, Spill Over}. Ship refuses non-terminal cards unless `--force`.

**Ignored labels** (noise, not part of the release state machine): `READY FOR DEPLOY`, `L3-DEV`, `DEV_ONLY`, `Completed`.

## Per-card closure (Trello-native)

Users close a card **manually on Trello** — no skill subcommand needed.

### Support Closed (requires close-reason comment)

1. Add `Closed by Support` or `Closed By Support` or `SL: Closed by Support` or `SL: Closed By Support` label to the StoryLab card (case-insensitive matching)
2. Add a comment on the card with a structured reason:
   ```
   [close-reason: <kind>] <optional detail>
   ```
   where `<kind>` ∈ {`dup-of=ZI-NNN`, `wontfix`, `stale`, `customer-resolved`, `out-of-scope`, `superseded-by=ZI-NNN`}.

snapshot and ship parse these comments (newest-first, first match wins) and surface the reason in the `## Support Closed` section of release.md. Missing reason → flagged but not fatal.

### Unsupported Partnership (no close-reason needed)

1. Add `Unsupported Partnership For Carrier` label to the StoryLab card (case-insensitive matching)

No close-reason comment required — the label is self-explanatory (carrier/partnership not supported by the platform).

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
Look up labels on StoryLab whose name (case-insensitive, trimmed) matches ANY of these variants:
- `Closed by Support` (lowercase "by")
- `Closed By Support` (uppercase "By")
- `SL: Closed by Support`
- `SL: Closed By Support`

**Implementation:**
```python
GET /boards/{storylab_board_id}/labels?fields=name,id&limit=1000

# All variants (case-insensitive matching, so we normalize to lowercase)
support_closed_variants = [
    'closed by support',  # Handles both "Closed by Support" and "Closed By Support"
    'sl: closed by support'  # Handles both "SL: Closed by Support" and "SL: Closed by Support"
]

support_closed_label_ids = set()
for label in labels:
    label_name_lower = label['name'].strip().lower()
    if label_name_lower in support_closed_variants:
        support_closed_label_ids.add(label['id'])
```

Return the **set** of matching label IDs (can be empty, one, or more than one — both names might exist, and each could have multiple color-variants). A card is "Support Closed" if ANY of its label IDs is in this set. **Do NOT auto-create** — user controls board structure. If the set is empty, warn once and treat all cards as not-Support-Closed.

### `resolve_unsupported_partnership_label_ids(storylab_board_id)`
Look up labels on StoryLab whose name (case-insensitive, trimmed) equals `Unsupported Partnership For Carrier`.

**Implementation:**
```python
GET /boards/{storylab_board_id}/labels?fields=name,id&limit=1000

unsupported_partnership_label_ids = set()
for label in labels:
    label_name_lower = label['name'].strip().lower()
    if label_name_lower == 'unsupported partnership for carrier':
        unsupported_partnership_label_ids.add(label['id'])
```

Return the **set** of matching label IDs (can be empty, one, or more than one — multiple color-variants may exist). A card is "Unsupported Partnership" if ANY of its label IDs is in this set. **Do NOT auto-create** — user controls board structure. If the set is empty, warn once and treat all cards as not-Unsupported-Partnership.

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

### `coarsen_state(storylab_card, ph_wip_label_name_or_none, support_closed_label_ids, unsupported_partnership_label_ids)`
Decision order (StoryLab closure labels override ph-WIP state):
1. If `support_closed_label_ids` is not empty AND `storylab_card.idLabels` contains any ID from this set → return `Support Closed`.
2. If `unsupported_partnership_label_ids` is not empty AND `storylab_card.idLabels` contains any ID from this set → return `Unsupported Partnership`.
3. If `ph_wip_label_name_or_none is None` → return `Open (not started)`.
4. Map the ph-WIP label name:
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
- **Use `yq` command-line tool** for parsing YAML (Python's yaml module is not available in Claude Code environment)
- Read: use `yq eval '{git_reference, status, shipped_at}' <file>` to extract specific fields. Refuse if file missing (caller's responsibility to check existence first).
- Write (partial update): read → merge `fields` → rewrite the frontmatter block, leave body unchanged. Atomic write (read, mutate, write).
- If frontmatter block unparseable YAML → refuse to proceed, surface the error verbatim to the user (never silently rewrite corrupt frontmatter).

**Example**:
```bash
# Read specific fields
yq eval '{git_reference, status, shipped_at}' wiki/product/releases/mcsl-377.md

# Read single field
yq eval '.git_reference' wiki/product/releases/mcsl-377.md

# Update a field (in-place)
yq eval -i '.status = "shipped"' wiki/product/releases/mcsl-377.md
```

### `git_diff_tickets(prior_ref, current_ref)`
```bash
git diff <prior_ref>..<current_ref> --name-only -- raw/zendesk/
```
Returns list of file paths (strings, relative to wiki root).

Fallback: if `git cat-file -e <prior_ref>` fails (ref no longer in history, e.g., after rebase/squash) → warn and use `HEAD~1..HEAD` instead. Include the warning in the report output.

---

## Mode 3a: `/sl-iteration sync <tag> [--board <name>] [--lane <name>]`

**Purpose**: pull Zendesk deltas since the release's last sync point; regen summaries; post compact delta comments on tagged cards. Optionally filter to cards in a specific lane on the source board.

**Flags:**
- `--board <name>` - Board name (ph-wip, storylab) or board ID (default: ph-wip)
- `--lane <name>` - Lane filter (optional)

**Examples:**
```bash
/sl-iteration sync "MCSL 377"
/sl-iteration sync "MCSL 377" --board storylab
/sl-iteration sync "MCSL 377" --lane "SL MCSL 377: Iteration backlog"
```

### Flow

**Step 1 — Precondition check**: Require `wiki/product/releases/<TAG-slug>.md` to exist.
- If missing → hard error:
  ```
  No release file for MCSL 377. Run /sl-iteration snapshot "MCSL 377" first to establish the release baseline.
  ```
  Never create it from sync; snapshot owns creation.

**Step 1.5 — Parse arguments:**

Parse flags to extract:
- `tag` (required positional argument)
- `--board <name>` → resolve to board ID (default: PH_WIP_BOARD)
- `--lane <name>` → lane filter (default: None)

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

## Python Script Infrastructure

**⚠️ CRITICAL: The snapshot workflow is implemented in Python scripts. DO NOT regenerate or reimplement these scripts.**

The Python scripts are part of the skill infrastructure and are maintained separately from the SKILL.md file. They are located in `.claude/skills/sl-iteration/`:

- `snapshot_release.py` — Fetches Trello data, resolves labels, saves to temp files
- `process_cards.py` — Processes cards, determines states, saves processed data
- `generate_release.py` — Generates the final release markdown file

**These scripts are the authoritative implementation.** The SKILL.md and the Python scripts should be kept in sync through version control.

### Execution

Run the **3-step Python pipeline** in sequence:

```bash
# Step 1-2: Fetch Trello data and resolve labels
python3 .claude/skills/sl-iteration/snapshot_release.py "<tag>" "<board_id>" "<lane_name>"

# Step 3: Process cards and determine states
python3 .claude/skills/sl-iteration/process_cards.py

# Step 4: Generate release markdown
python3 .claude/skills/sl-iteration/generate_release.py
```

**Arguments:**
- `<tag>` — Release tag name (e.g., "MCSL 378")
- `<board_id>` — Trello board ID or DEFAULT_STORYLAB_BOARD
- `<lane_name>` — Lane name filter (e.g., "SL MCSL 378: Iteration backlog") or empty string for no filter

The scripts implement the full 10-state legend (including Carrier Platform Issues and Spill Over). **Never reimplement this workflow inline** — always use the existing scripts.

### Internal Flow (Documentation Only)

**Note:** The following describes what happens inside the Python scripts. This is for reference only—do NOT reimplement this logic. Always use the Python scripts above.

**Step 1 — File existence check** (`snapshot_release.py`): Does `wiki/product/releases/<TAG-slug>.md` exist?
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

**Step 2 — Fetch Trello state** (`snapshot_release.py`):
- `resolve_tag_label(board_id, tag)` → `tag_label_id`
- `resolve_support_closed_label_ids(board_id)` → `support_closed_label_ids` (set, or empty with warning)
- `resolve_unsupported_partnership_label_ids(board_id)` → `unsupported_partnership_label_ids` (set, or empty with warning)
- `fetch_tagged_storylab_cards(board_id, tag_label_id, lane)` → tagged cards (filtered by lane if specified)
- `fetch_all_card_comments(board_id)` → source board comments by cardId (for close-reason parsing)
- `fetch_ph_wip_snapshot()` → ph-WIP cards + lane map (only if board != PH_WIP_BOARD; else skip for efficiency)
- `fetch_all_card_comments(PH_WIP_BOARD)` → ph-WIP comments (only if board != PH_WIP_BOARD; else reuse source board comments)

**Step 3 — Correlate & coarsen** (`process_cards.py`): For each tagged StoryLab card:
- `ph_wip_matches = match_storylab_card_to_ph_wip(storylab_card, ph_wip_cards, ph_wip_comments_by_card)`
- `ph_wip_lane = lane_map[ph_wip_matches[0].id] if ph_wip_matches else None`
- `state = coarsen_state(storylab_card, ph_wip_lane)`
- Extract: `zi_id` (from card name `ZI-NNN — ...`), `ticket_id` (from `[#<ticketId>]`), `theme` / `carrier` / `product` labels

**Step 4 — Parse close reasons** (`process_cards.py`): For cards where `state == "Support Closed"`:
- `close_reason = parse_close_reason(storylab_comments[card.id])`
- If `None`: flag the card in "cards missing close-reason" count

For cards where `state == "Unsupported Partnership"`: No close-reason parsing needed (label is self-explanatory).

**Step 5 — Sort & group** (`process_cards.py`):
Sort buckets: Shipped → Ready To Ship → Support Closed → Unsupported Partnership → Carrier Platform Issues → BUG REPORTED → QA READY → DEV → Open (not started) → Spill Over.

**Step 6 — Rewrite release.md body** (`generate_release.py`, preserving protected frontmatter fields from Step 1):

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
cards_unsupported_partnership: <N>
cards_carrier_platform_issues: <N>
cards_bug_reported: <N>
cards_qa_ready: <N>
cards_dev: <N>
cards_open: <N>
cards_spill_over: <N>
---

# Release <TAG>

> **Status**: <status> · **Last synced**: <YYYY-MM-DD HH:MM UTC> · **Board**: [StoryLab](https://trello.com/b/d1xk25XH/storylab)

## Summary

| State | Count |
|-------|-------|
| Shipped | <N> |
| Ready To Ship | <N> |
| Support Closed | <N> |
| Unsupported Partnership | <N> |
| Carrier Platform Issues | <N> |
| BUG REPORTED | <N> |
| QA READY | <N> |
| DEV | <N> |
| Open (not started) | <N> |
| Spill Over | <N> |
| **Total** | **<N>** |

## Legend

- **Shipped** — deployed to production (ph-WIP SHIPPED or PROD label)
- **Ready To Ship** — QA verified, ready to deploy (ph-WIP QA_VERIFIED label)
- **Support Closed** — StoryLab card has `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label; closed without code via support action
- **Unsupported Partnership** — StoryLab card has `Unsupported Partnership For Carrier` label (case-insensitive); unsupported carrier/partnership
- **Carrier Platform Issues** — external carrier/platform environment issues we cannot solve (ph-WIP `SL: Carrier Platform Issues` label)
- **BUG REPORTED** — code is in QA, bug has been reported (ph-WIP BUG REPORTED label)
- **QA READY** — code complete, in QA (ph-WIP Dev Done, Ready for QA, or QA Reported labels — NOT yet verified)
- **DEV** — active development (ph-WIP DEV label)
- **Open (not started)** — in product backlog but dev hasn't started (no ph-WIP state label)
- **Spill Over** — cards that could not be completed in the current iteration and were moved out (ph-WIP `Spill Over` label)

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

## Unsupported Partnership (<N>)

| ZI | Ticket | Theme | Card |
|----|--------|-------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | ... | [SL](shortUrl) |

## Carrier Platform Issues (<N>)

| ZI | Ticket | Carriers | Card |
|----|--------|----------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | ... | [SL](shortUrl) |

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

## Spill Over (<N>)

| ZI | Ticket | Card |
|----|--------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | [ph-WIP](shortUrl) |

## Notes

- Cards missing `[close-reason: ...]` comment: <N>
- Cards with no ph-WIP correlation: <N>
- Cards dropped since last snapshot: <N> (state drift, if any)
- Warnings: <list>

## Cross-Links

- [Backlog](../backlog.md)
- [Latest Zendesk daily index](../../zendesk/YYYY-MM-DD.md)
```

**Step 7 — Verify against Trello** (`generate_release.py` - optional validation, sanity check to catch state detection bugs):

The script can optionally re-check a sample of cards directly in Trello to verify state detection worked correctly:

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

**Step 8 — Report** (script output summary):
```
## Snapshot <TAG>
- File: wiki/product/releases/<TAG-slug>.md (created | refreshed)
- Board: <board_id>
- Cards total: N  (Shipped: N, Ready To Ship: N, Support Closed: N, Unsupported Partnership: N, BUG REPORTED: N, QA READY: N, DEV: N, Open: N)
- State labels found: 8/8 ✓ (or list missing)
  - SHIPPED: N label(s)
  - PROD: N label(s)
  - QA_VERIFIED: N label(s)
  - Dev Done: N label(s)
  - DEV: N label(s)
  - QA Reported: N label(s)
  - Ready for QA: N label(s)
  - BUG REPORTED: N label(s)
- StoryLab closure labels found:
  - Support Closed: N label(s)
  - Unsupported Partnership: N label(s)
- Verification: N sample cards checked, 0 mismatches ✓
- git_reference: <unchanged | set to HEAD on first snapshot>
- Cards missing close-reason: N (Support Closed only)
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

## Mode 3c: `/sl-iteration ship <tag> [--board <name>] [--lane <name>] [--force] [--no-sync]`

**Purpose**: freeze the release in wiki state. Propagate shipped work to `wiki/product/backlog.md` and append an entry to `wiki/log.md`. **No Trello writes** at all (no comments, no label changes, no moves, no new lanes). Optionally filter to cards in a specific lane on the source board.

**Flags:**
- `--board <name>` - Board name (ph-wip, storylab) or board ID (default: ph-wip)
- `--lane <name>` - Lane filter (optional)
- `--force` - Ship even with non-terminal cards (optional)
- `--no-sync` - Skip submodule updates (optional)

**Examples:**
```bash
/sl-iteration ship "MCSL 377"
/sl-iteration ship "MCSL 377" --board storylab
/sl-iteration ship "MCSL 377" --lane "SL MCSL 377: Iteration backlog"
/sl-iteration ship "MCSL 377" --force
/sl-iteration ship "MCSL 377" --lane "SL MCSL 377: Iteration backlog" --force --no-sync
```

### Flow

**Step 1 — Parse arguments and run snapshot:**

**CRITICAL: Parse ALL flags from the ship command first:**

Parse the ship command arguments using the Mode 3 argument parsing algorithm (see "Argument Parsing (Mode 1 and Mode 3)" section):
- Extract `tag` (required positional argument)
- Extract `--board <name>` → resolve to board ID using `BOARD_NAMES` mapping (default: PH_WIP_BOARD if not specified)
- Extract `--lane <name>` → lane filter (default: None if not specified)
- Extract `--force` flag (default: False)
- Extract `--no-sync` flag (default: False)

**CRITICAL: Preserve existing release parameters if they exist:**

Before running snapshot, check if the release file already exists and preserve its parameters:

```bash
TAG_SLUG=$(echo "$tag" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
RELEASE_FILE="wiki/product/releases/${TAG_SLUG}.md"

# If release file exists, read and preserve lane_filter
if [ -f "$RELEASE_FILE" ]; then
    EXISTING_LANE=$(yq eval '.lane_filter' "$RELEASE_FILE")

    # If no --lane was passed in ship command, use the existing lane_filter
    if [ -z "$lane_name" ] && [ "$EXISTING_LANE" != "null" ]; then
        lane_name="$EXISTING_LANE"
        echo "ℹ️  Preserving existing lane filter: $lane_name"
    fi
fi
```

**Run snapshot with ALL parsed parameters:**

```bash
# MANDATORY: Pass ALL parsed parameters to snapshot (even if default values)
# This ensures snapshot uses the SAME board/lane that ship command specified

# Build snapshot command with board parameter
snapshot_cmd="python3 .claude/skills/sl-iteration/snapshot_release.py \"$tag\" --board \"$board_name_or_id\""

# Add --lane if specified (either from command or preserved from existing release)
if [ -n "$lane_name" ]; then
    snapshot_cmd="$snapshot_cmd --lane \"$lane_name\""
fi

# Execute snapshot
eval $snapshot_cmd
```

**Example parameter flows:**

1. First-time ship (no existing release):
   - User runs: `/sl-iteration ship "MCSL 377" --board ph-wip`
   - Parse: `tag="MCSL 377"`, `board="ph-wip"`, `lane=None`
   - No existing release → lane stays None
   - Call: `python3 snapshot_release.py "MCSL 377" --board ph-wip`

2. Re-ship existing release (preserves lane):
   - Existing release has: `lane_filter: "SL MCSL 377: Iteration backlog"`
   - User runs: `/sl-iteration ship "MCSL 377" --board ph-wip`
   - Parse: `tag="MCSL 377"`, `board="ph-wip"`, `lane=None`
   - Reads existing release → preserves lane: `"SL MCSL 377: Iteration backlog"`
   - Call: `python3 snapshot_release.py "MCSL 377" --board ph-wip --lane "SL MCSL 377: Iteration backlog"`

3. Override with explicit lane:
   - User runs: `/sl-iteration ship "MCSL 377" --board ph-wip --lane "Different Lane"`
   - Parse: `tag="MCSL 377"`, `board="ph-wip"`, `lane="Different Lane"`
   - Explicit --lane in command overrides existing lane_filter
   - Call: `python3 snapshot_release.py "MCSL 377" --board ph-wip --lane "Different Lane"`

**DO NOT skip passing --board even if it's the default** - the snapshot script needs to know which board ship is targeting.

**DO NOT skip preserving lane_filter** - existing releases must maintain their lane scope on re-ship.

Ensures release.md reflects the SAME board state that ship will freeze.

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

# Mode 6: Sync Single Card (StoryLab → ph-WIP)

## Purpose

Refresh a ph-WIP card from StoryLab updates. Syncs name, description, and/or labels FROM StoryLab TO ph-WIP based on command-line flags. Preserves ph-WIP comments (PUT /cards only updates specified fields).

## Execution

### Step 1: Parse arguments

```python
import re

tokens = $ARGUMENTS.split()
# tokens[0] = "sync-single"
# tokens[1] = ZI-NNN
# tokens[2:] = optional flags

zi_pattern = re.compile(r'^ZI-\d+$')
zi_id = tokens[1] if len(tokens) > 1 and zi_pattern.match(tokens[1]) else None

if not zi_id:
    print("Error: ZI-NNN required")
    exit(1)

# Parse flags
flags = tokens[2:]
sync_name = '--name' in flags
sync_desc = '--desc' in flags
sync_labels = '--labels' in flags

# Default: if no flags, sync all
if not (sync_name or sync_desc or sync_labels):
    sync_name = sync_desc = sync_labels = True
```

### Step 2: Find ph-WIP card

Search all `SL *` lanes on ph-WIP for card with `{zi_id}` in name:

```python
GET /boards/63e1e0414b6026c45be1087c/lists?fields=name,id

# Filter lanes starting with "SL "
sl_lanes = [lane for lane in lanes if lane['name'].startswith('SL ')]

# Search each lane for the card
ph_wip_card = None
for lane in sl_lanes:
    GET /lists/{lane['id']}/cards?fields=name,desc,idLabels,shortUrl
    for card in cards:
        if zi_id.upper() in card['name'].upper():
            ph_wip_card = card
            break
    if ph_wip_card:
        break

if not ph_wip_card:
    print(f"Error: {zi_id} not found in any SL lane on ph-WIP")
    exit(1)
```

### Step 3: Extract StoryLab shortUrl from ph-WIP description

```python
# ph-WIP cards created by Mode 1/4 have StoryLab shortUrl as first line
desc_lines = ph_wip_card['desc'].split('\n')
storylab_url = desc_lines[0].strip() if desc_lines else None

if not storylab_url or 'trello.com/c/' not in storylab_url:
    print(f"Error: No StoryLab URL found in ph-WIP card description")
    exit(1)

# Extract shortId from URL (e.g., https://trello.com/c/abc12345 -> abc12345)
short_id = storylab_url.split('/c/')[-1].split('/')[0].split('?')[0]
```

### Step 4: Fetch StoryLab card

```python
GET /cards/{short_id}?fields=name,desc,idLabels
```

### Step 5: Fetch ph-WIP labels (for label mapping)

```python
GET /boards/63e1e0414b6026c45be1087c/labels?fields=name,color,id&limit=1000

# Build reverse map: StoryLab label name -> ph-WIP "SL: <name>" label ID
```

### Step 6: Fetch StoryLab labels (for label resolution)

```python
GET /boards/69dd9134576a26fcb79b670d/labels?fields=name,color,id&limit=1000

# Build map: label ID -> label object
```

### Step 7: Build update payload

```python
update_payload = {}

if sync_name:
    # Keep "From SL: " prefix on ph-WIP
    update_payload['name'] = f"From SL: {storylab_card['name']}"

if sync_desc:
    # Preserve StoryLab URL as first line, replace rest with StoryLab desc
    update_payload['desc'] = f"{storylab_url}\n\n{storylab_card['desc']}"

if sync_labels:
    # Map StoryLab labels to ph-WIP "SL: <name>" labels
    # Skip dev labels (DEV, DEV DONE, QA, PROD, BACKLOG)
    DEV_LABEL_IDS = ["69ddcada5e444b9157da951d", "69ddcadb130379d4cb79b4ef",
                     "69ddcadb1d2769d25b6a6f92", "69ddcadcd5d8f116d99db5f4",
                     "69ddcadcd2bfb5a850ffb2cc"]

    ph_wip_label_ids = []
    for label_id in storylab_card['idLabels']:
        if label_id in DEV_LABEL_IDS:
            continue

        # Get StoryLab label name
        sl_label = storylab_labels_by_id.get(label_id)
        if not sl_label:
            continue

        # Find matching "SL: <name>" label on ph-WIP
        sl_prefixed_name = f"SL: {sl_label['name']}"
        matching_ph_wip_labels = [l for l in ph_wip_labels
                                   if l['name'].lower() == sl_prefixed_name.lower()]

        if matching_ph_wip_labels:
            ph_wip_label_ids.append(matching_ph_wip_labels[0]['id'])
        else:
            # Create missing label on ph-WIP
            POST /boards/63e1e0414b6026c45be1087c/labels
            body = {"name": sl_prefixed_name, "color": sl_label['color']}
            ph_wip_label_ids.append(new_label['id'])

    # Preserve CONFIDENCE labels (don't overwrite with StoryLab labels)
    CONFIDENCE_LABEL_IDS = ["69dee0a642a39a86a39ca652", "69dee0a7a906af81b31a6831",
                            "69dee0a86d18af6f40e61d2f", "69dee0a8c0ebc650c9ddafaf"]
    existing_confidence = [lid for lid in ph_wip_card['idLabels']
                          if lid in CONFIDENCE_LABEL_IDS]

    update_payload['idLabels'] = ','.join(ph_wip_label_ids + existing_confidence)
```

### Step 8: Update ph-WIP card

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{ph_wip_card_id}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{update_payload_json}'
```

### Step 9: Report

```
## Sync Single Card — {zi_id}

✅ Synced StoryLab → ph-WIP

- StoryLab card: {storylab_card['name']}
- StoryLab URL: {storylab_url}
- ph-WIP card: {ph_wip_card['name']}
- ph-WIP URL: {ph_wip_card['shortUrl']}

**Updated:**
- Name: {✓ if sync_name else ✗}
- Description: {✓ if sync_desc else ✗}
- Labels: {✓ if sync_labels else (N labels synced)}

**Preserved:**
- ph-WIP comments: ✓ (not touched)
- CONFIDENCE labels: ✓ (preserved)
```

---

# Mode 7: Swap Cards in Release

## Purpose

Atomically swap two cards in a release — remove the old card's release tag and add the new card to the release. This combines Mode 5 (remove tag) and Mode 4 (copy single card) in a single operation.

## Execution

### Step 1: Parse arguments

```python
import re

tokens = $ARGUMENTS.split()
# tokens[0] = "swap"
# tokens[1] = ZI-OLD (card to remove from release)
# tokens[2] = ZI-NEW (card to add to release)
# tokens[3] = "--release"
# tokens[4:] = release tag (may be multi-word)

zi_pattern = re.compile(r'^ZI-\d+$')

if len(tokens) < 5:
    print("Error: Usage: swap ZI-OLD ZI-NEW --release <tag>")
    exit(1)

zi_old = tokens[1] if zi_pattern.match(tokens[1]) else None
zi_new = tokens[2] if zi_pattern.match(tokens[2]) else None

if not zi_old or not zi_new:
    print("Error: Both ZI-OLD and ZI-NEW must be valid ZI IDs")
    exit(1)

if tokens[3] != '--release':
    print("Error: Expected --release flag")
    exit(1)

tag = ' '.join(tokens[4:])

if not tag:
    print("Error: Release tag required")
    exit(1)
```

### Step 2: Execute Mode 5 (remove old card from release)

Run Mode 5 to remove the release tag from the old card:

```bash
# Internal execution of: /sl-iteration remove <tag> <zi_old>
```

Follow all Mode 5 steps:
1. Resolve release tag label on StoryLab board
2. Find ph-WIP card matching `zi_old`
3. Find matching "SL: <tag>" label on ph-WIP
4. Remove label from card via PUT /cards/{card_id}

If the card is not found or doesn't have the tag, log a warning but continue (idempotent).

### Step 3: Execute Mode 4 (add new card to release)

Run Mode 4 to copy the new card from StoryLab to ph-WIP:

```bash
# Internal execution of: /sl-iteration release-single <tag> <zi_new>
```

Follow all Mode 4 steps:
1. Resolve release tag label on StoryLab board
2. Search StoryLab for card matching `zi_new`
3. Find/create target lane `SL <tag>: Iteration backlog` on ph-WIP
4. Check for duplicates in target lane
5. Copy card (POST /cards)
6. Mirror labels with "SL: " prefix

If duplicate exists, abort with error.

### Step 4: Report

```markdown
## Swap Cards — {tag}

✅ Swap completed

**Removed from release:**
- Card: {zi_old}
- Release tag: {tag}
- Status: {"✓ Removed" or "⚠ Not found (already removed)"}

**Added to release:**
- Card: {zi_new}
- StoryLab URL: {storylab_url}
- ph-WIP URL: {ph_wip_url}
- Lane: SL {tag}: Iteration backlog
- Status: ✓ Copied

**Next steps:**
- Review ph-WIP card: {ph_wip_url}
- Consider running: `/sl-iteration analyze {tag} {zi_new}`
```

---

## Error Handling

- **No matching release tag** (copy mode): List all StoryLab labels, ask user to pick
- **No qualifying cards**: Report "0 cards found" and exit
- **Card not found** (analyze mode): Show available cards in the lane
- **API failure**: Show failed request URL and response, ask user how to proceed
- **Codebase search returns nothing**: Mark as CONFIDENCE:POOR with one-liner
