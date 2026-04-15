---
name: sl-iteration
description: Copy release-tagged cards from StoryLab to ph-WIP as iteration backlog, and run AI code analysis on ph-WIP cards. Use when the user wants to plan an iteration, move story cards to ph-WIP, analyze cards, or says "sl-iteration".
argument-hint: <release-tag-label-name> | analyze <ZI-NNN|next|all> | reassess <ZI-NNN>
allowed-tools: Bash, Read, Write, Glob, Grep, Agent, WebFetch, TodoWrite, AskUserQuestion
disable-model-invocation: false
---

# StoryLab to ph-WIP Iteration Backlog

Two modes: **copy** (move cards from StoryLab to ph-WIP) and **analyze** (run AI code analysis on ph-WIP cards).

**Arguments**:
- `<release-tag-name>` — copy all StoryLab cards with that label to ph-WIP
- `analyze <ZI-NNN>` — run code analysis on a specific card
- `analyze next` — analyze the next unanalyzed card in the lane
- `analyze all` — analyze all unanalyzed cards, one at a time, waiting for user review
- `reassess <ZI-NNN>` — re-run analysis with updated context (comments, description edits)

---

## Pre-flight (MANDATORY — run before ANY operation)

### 1. Update All Sources

```bash
cd <wiki-root> && git submodule update --remote raw/storepep-react raw/mcsl-test-automation 2>&1
```

This ensures code analysis is based on the latest codebase, not a stale snapshot. **Do not skip this step.** If the submodule update fails, warn the user and ask whether to proceed with stale data.

Record the current commit hash after update:
```bash
cd raw/storepep-react && git rev-parse HEAD
```

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

| Board | ID |
|-------|-----|
| **StoryLab** (source) | `69dd9134576a26fcb79b670d` |
| **ph-WIP** (target) | `63e1e0414b6026c45be1087c` |

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

### Step 1: Find the release tag label on StoryLab

```
GET /boards/69dd9134576a26fcb79b670d/labels?fields=name,color,id
```

Find label matching user's argument (case-insensitive). If not found — show available labels and ask.

Record `RELEASE_LABEL_ID`, `RELEASE_LABEL_NAME`, `RELEASE_LABEL_COLOR`.

### Step 2: Collect qualifying cards in order

Fetch lanes (left → right):
```
GET /boards/69dd9134576a26fcb79b670d/lists?fields=name,id
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
- Skip dev label IDs
- For each remaining label: look up `SL: <original name>` in ph-WIP labels
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

---

## Error Handling

- **No matching release tag** (copy mode): List all StoryLab labels, ask user to pick
- **No qualifying cards**: Report "0 cards found" and exit
- **Card not found** (analyze mode): Show available cards in the lane
- **API failure**: Show failed request URL and response, ask user how to proceed
- **Codebase search returns nothing**: Mark as CONFIDENCE:POOR with one-liner
