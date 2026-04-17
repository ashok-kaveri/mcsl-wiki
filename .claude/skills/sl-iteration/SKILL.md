---
name: sl-iteration
description: Copy release-tagged cards from StoryLab to ph-WIP as iteration backlog, run AI code analysis on ph-WIP cards, and run the release closure workflow (sync / snapshot / ship) for a release tag. Use when the user wants to plan an iteration, move story cards to ph-WIP, analyze cards, sync Zendesk deltas to a release, snapshot a release's Trello state into the wiki, ship/close a release, or says "sl-iteration".
argument-hint: <release-tag> | analyze <tag> <ZI-NNN|next|all|@name> | reassess <ZI-NNN> | sync <tag> [board] | snapshot <tag> [board] | ship <tag> [board] [--force]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, WebFetch, TodoWrite, AskUserQuestion
disable-model-invocation: false
---

# StoryLab to ph-WIP Iteration Backlog, plus Release Closure

Three modes:
- **copy** (Mode 1): move StoryLab cards tagged with a release label into a ph-WIP `SL <tag>: Iteration backlog` lane.
- **analyze** (Mode 2): run AI code analysis on ph-WIP cards; classify confidence; update StoryLab dev-status labels.
- **release** (Mode 3): close the loop between Trello + Zendesk and the wiki via three read-leaning subcommands — `sync`, `snapshot`, `ship`.

**Arguments**:
- `<release-tag-name>` — Mode 1 copy
- `analyze <release-tag> <ZI-NNN>` — Mode 2 analyze a specific card
- `analyze <release-tag> next` — Mode 2 analyze the next unanalyzed card in the named ph-WIP lane
- `analyze <release-tag> all` — Mode 2 analyze all unanalyzed cards in the named ph-WIP lane
- `analyze <release-tag> @<name>` — Mode 2 analyze only cards assigned to a member (matches by username or full name)
- `reassess <ZI-NNN>` — Mode 2 re-run analysis (ph-WIP lane auto-detected)
- `sync <release-tag> [board]` — Mode 3a: diff Zendesk JSONs vs the release's last `git_reference`, regen summaries, post compact delta comments on tagged StoryLab cards
- `snapshot <release-tag> [board]` — Mode 3b: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current StoryLab + ph-WIP state
- `ship <release-tag> [board] [--force]` — Mode 3c: freeze the release in wiki (status=shipped, backlog + log updates); no Trello writes

**Lane resolution (Mode 2 only)**: The `<release-tag>` in analyze commands identifies the ph-WIP lane `SL <release-tag>: Iteration backlog`. If the lane doesn't exist, list all `SL *` lanes and ask user to pick.

**Board default (Mode 3)**: StoryLab (`69dd9134576a26fcb79b670d`) when `[board]` is omitted.

**Examples**:
- `/sl-iteration MCSL 377` — Mode 1 copy release-tagged cards
- `/sl-iteration analyze MCSL 377 all` — Mode 2 analyze all cards in `SL MCSL 377: Iteration backlog`
- `/sl-iteration analyze MCSL 377 @ajeesh` — Mode 2 analyze cards assigned to Ajeesh
- `/sl-iteration analyze MCSL 377 ZI-035` — Mode 2 analyze ZI-035
- `/sl-iteration snapshot MCSL 377` — Mode 3b first-time snapshot (creates release.md baseline)
- `/sl-iteration sync MCSL 377` — Mode 3a delta sync (snapshot must have run first)
- `/sl-iteration ship MCSL 377 --force` — Mode 3c ship even with non-terminal cards

## Dispatch

Parse `$ARGUMENTS` as a token list. Match the **first token**:

| First token | Mode |
|-------------|------|
| `analyze` | Mode 2 analyze |
| `reassess` | Mode 2 reassess |
| `sync` | Mode 3a |
| `snapshot` | Mode 3b |
| `ship` | Mode 3c |
| anything else | Mode 1 copy (all tokens = tag name, may be multi-word like `MCSL 377`) |

For Mode 3 commands: everything after the subcommand, minus any trailing `--force` flag and any trailing token matching a Trello board URL (`^https://trello\.com/b/`) or bare shortLink (alphanumeric, ≥8 chars), is the tag. Tags may be multi-word.

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

# Mode 3: Release Workflow

Three subcommands that close the loop between Trello + Zendesk and the wiki, **per release tag** (e.g., `MCSL 377`):

- **sync**: delta-based pull of Zendesk JSONs → regen wiki summaries → post compact delta comments on tagged StoryLab cards.
- **snapshot**: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current Trello state.
- **ship**: freeze the release in wiki state; update backlog + log. **No Trello writes.**

**Design principle (read-leaning)**: Trello (StoryLab tags, ph-WIP lanes) and Zendesk raw JSONs are upstream sources. Wiki files (release.md, backlog.md, Zendesk summaries) are the downstream derivatives this workflow maintains. The **only** Trello write is sync posting comments on tagged StoryLab cards. Ship never moves cards, never changes labels, never creates lanes.

**Delta anchor**: per-release `git_reference` in `wiki/product/releases/<TAG-slug>.md` frontmatter. snapshot sets it on first creation; sync advances it every run. No separate state file.

## 4-State Legend (coarsening for release reports)

Release views classify each tagged StoryLab card by the HIGHEST-precedence **label** found on ANY matching ph-WIP card (matched by Zendesk ticket ID in the card name/desc/attachments/comments). Lane membership is NOT used for state — labels are the authoritative delivery signal.

**Do NOT read StoryLab dev labels** (`🛠️ DEV`, `✅ DEV DONE`, `🧪 QA`, `🚀 PROD`, `📋 BACKLOG`). Those are cached projections from Mode 2 analyze and may be stale. Always read ph-WIP labels live.

**ph-WIP label precedence** (high → low, match by NAME not ID — ph-WIP has multiple labels with the same name and varying colors):

```
SHIPPED  >  PROD  >  QA_VERIFIED  >  QA Reported  >  Ready for QA  >  Dev Done  >  DEV
```

**Coarsening to 4-state legend**:

| Legend state | ph-WIP label name(s) |
|--------------|----------------------|
| `PROD` | `SHIPPED`, `PROD` (same terminal state) |
| `QA READY` | `QA_VERIFIED`, `QA Reported`, `Ready for QA`, `Dev Done` |
| `DEV` | `DEV` |
| `Open (not started)` | NO state label on any matching ph-WIP card |
| `Support Closed` | StoryLab card carries `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label (precedence — overrides any ph-WIP state) |

**Do NOT exclude SL-copy cards** (cards named `From SL: ...` in `SL <tag>: Iteration backlog` lanes). Devs often apply state labels directly to the SL-copy rather than creating separate dev cards. Search ALL ph-WIP matches for state labels.

**Closed** = {PROD, Support Closed}. **Open** = {Open, DEV, QA READY}. Ship refuses non-terminal cards unless `--force`.

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

**Trello API pagination gotcha**: `GET /boards/{id}/labels` defaults to 50 items. ph-WIP currently has 162+ labels; StoryLab has 60+. ALWAYS pass `limit=1000` when fetching labels or you will silently miss state labels like `SHIPPED`, `DEV`, `PROD`. For `/boards/{id}/cards`, DO NOT pass `limit` (its default returns all cards; passing `limit=1000` actively caps it).

### `resolve_tag_label(storylab_board_id, tag)`
`GET /boards/{id}/labels?fields=name,color,id`; case-insensitive match on `name`. If missing, list available labels and ask user to pick (same pattern as Mode 1 Step 1).

### `resolve_support_closed_label_ids(storylab_board_id)`
Look up labels on StoryLab whose name (case-insensitive, trimmed) equals either `Closed by Support` OR `SL: Closed By Support`. Return the **set** of matching label IDs (can be empty, one, or more than one — both names might exist, and each could have multiple color-variants). A card is "Support Closed" if ANY of its label IDs is in this set. **Do NOT auto-create** — user controls board structure. If the set is empty, warn once and treat all cards as not-Support-Closed.

### `resolve_ph_wip_state_labels(ph_wip_board_id)`
Fetch all ph-WIP labels with `limit=1000` (the default limit is 50 — missing this causes silent truncation). Build a map of `{state_name: set(label_ids)}` for each of the 7 state-label names: `SHIPPED`, `PROD`, `QA_VERIFIED`, `QA Reported`, `Ready for QA`, `Dev Done`, `DEV`. ph-WIP has multiple labels with the same name (different colors) — treat them as equivalent.

### `fetch_tagged_storylab_cards(tag_label_id)`
Single bulk `GET /boards/<STORYLAB>/cards?attachments=true&fields=name,desc,idList,idLabels,shortUrl`. Filter in-memory where `idLabels` contains `tag_label_id`.

### `fetch_ph_wip_snapshot()`
2 calls:
- `GET /boards/<PH_WIP>/cards?fields=name,desc,idList,shortUrl&attachments=true`
- `GET /boards/<PH_WIP>/lists?fields=name,id`

Build `{ph_wip_cardId: lane_name}` map. Cache for the run.

### `fetch_all_card_comments(board_id)`
Single `GET /boards/{id}/actions?filter=commentCard&limit=1000`. Index by cardId. Used for: (a) StoryLab card close-reason parsing; (b) ph-WIP card correlation fallback when name/desc/attachments miss.

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

### `best_ph_wip_state_label(ph_matches, state_label_ids)`
Walks the 7 state-label names in precedence order (`SHIPPED`, `PROD`, `QA_VERIFIED`, `QA Reported`, `Ready for QA`, `Dev Done`, `DEV`). For each, scans ALL `ph_matches` and returns the first name whose label id appears on any matching card. Returns `(label_name, chosen_card)` or `(None, None)` if no state label is present on any match.

**Important**: do NOT filter out SL-copy cards (named `From SL: ...` in `SL <tag>: Iteration backlog` lane). Devs often apply state labels directly to the SL-copy — excluding them causes false "Open" classifications.

### `coarsen_state(storylab_card, ph_wip_label_name_or_none)`
Decision order:
1. If `support_closed_label_id` is set AND `storylab_card.idLabels` contains it → return `Support Closed`.
2. If `ph_wip_label_name_or_none is None` → return `Open (not started)`.
3. Map the ph-WIP label name:
   - `SHIPPED` or `PROD` → `PROD`
   - `QA_VERIFIED`, `QA Reported`, `Ready for QA`, or `Dev Done` → `QA READY`
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

## Mode 3a: `/sl-iteration sync <tag> [board]`

**Purpose**: pull Zendesk deltas since the release's last sync point; regen summaries; post compact delta comments on tagged StoryLab cards.

### Flow

**Step 1 — Precondition check**: Require `wiki/product/releases/<TAG-slug>.md` to exist.
- If missing → hard error:
  ```
  No release file for MCSL 377. Run /sl-iteration snapshot MCSL 377 first to establish the release baseline.
  ```
  Never create it from sync; snapshot owns creation.

**Step 2 — Read anchor**: Parse release.md frontmatter.
- `PRIOR_REF = frontmatter['git_reference']`
- `IS_SHIPPED = (frontmatter['status'] == 'shipped')`
- `CURRENT_REF = git rev-parse HEAD`

**Step 3 — Compute delta**: Run `git_diff_tickets(PRIOR_REF, CURRENT_REF)`.
- If empty AND `PRIOR_REF == CURRENT_REF`: report `0 tickets changed since <ref>`. Still bump `last_synced` on release.md. Exit with no Trello writes.
- If `PRIOR_REF` not in git history: fallback to `HEAD~1..HEAD` (handled by helper); warn the user.

**Step 4 — Fetch tagged cards**: `resolve_tag_label`, `fetch_tagged_storylab_cards(tag_label_id)`. Only cards with `<tag>` label will get delta comments.

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

## Mode 3b: `/sl-iteration snapshot <tag> [board]`

**Purpose**: idempotent rewrite of `wiki/product/releases/<TAG-slug>.md` from current StoryLab + ph-WIP live state.

### Flow

**Step 1 — File existence check**: Does `wiki/product/releases/<TAG-slug>.md` exist?
- If NO: this is the first snapshot. Mark `is_first_snapshot = true`. The new frontmatter will set `git_reference = HEAD` (establishes sync baseline).
- If YES: read existing frontmatter. Preserve `git_reference` (snapshot NEVER bumps it — sync owns it), preserve `status` and `shipped_at` if `status == "shipped"`.

**Step 2 — Fetch Trello state**:
- `resolve_tag_label` → `tag_label_id`
- `resolve_support_closed_label_id` → `support_closed_label_id` (or None, with warning)
- `fetch_tagged_storylab_cards(tag_label_id)` → tagged StoryLab cards
- `fetch_all_card_comments(<STORYLAB>)` → StoryLab comments by cardId (for close-reason parsing)
- `fetch_ph_wip_snapshot()` → ph-WIP cards + lane map
- `fetch_all_card_comments(<PH_WIP>)` → ph-WIP comments (only used by correlation fallback)

**Step 3 — Correlate & coarsen**: For each tagged StoryLab card:
- `ph_wip_matches = match_storylab_card_to_ph_wip(storylab_card, ph_wip_cards, ph_wip_comments_by_card)`
- `ph_wip_lane = lane_map[ph_wip_matches[0].id] if ph_wip_matches else None`
- `state = coarsen_state(storylab_card, ph_wip_lane)`
- Extract: `zi_id` (from card name `ZI-NNN — ...`), `ticket_id` (from `[#<ticketId>]`), `theme` / `carrier` / `product` labels

**Step 4 — Parse close reasons**: For cards where `state == "Support Closed"`:
- `close_reason = parse_close_reason(storylab_comments[card.id])`
- If `None`: flag the card in "cards missing close-reason" count

**Step 5 — Sort & group**:
Sort buckets: PROD → Support Closed → QA READY → DEV → Open (not started).

**Step 6 — Rewrite release.md body** (preserving protected frontmatter fields from Step 1):

```markdown
---
title: "Release <TAG>"
category: product-release
tag: "<TAG>"
tag_slug: <TAG-slug>
board_id: 69dd9134576a26fcb79b670d
status: <preserved, or "draft" if first snapshot>
last_synced: <now>
shipped_at: <preserved, or null>
git_reference: <preserved, or HEAD on first snapshot>
tickets_delta_on_last_sync: <preserved, or 0 on first snapshot>
cards_total: <N>
cards_shipped: <N>
cards_support_closed: <N>
cards_open: <N>
---

# Release <TAG>

> **Status**: <status> · **Last synced**: <YYYY-MM-DD HH:MM UTC> · **Board**: [StoryLab](https://trello.com/b/d1xk25XH/storylab)

## Summary

| State | Count |
|-------|-------|
| PROD (shipped) | <N> |
| Support Closed | <N> |
| QA READY | <N> |
| DEV | <N> |
| Open (not started) | <N> |
| **Total** | **<N>** |

## Legend

- **PROD** — shipped to production (ph-WIP PROD-class lane)
- **Support Closed** — StoryLab card has `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label; closed without code via support action
- **QA READY** — code complete, in QA (ph-WIP Dev Done + QA-class lanes — NOT yet shipped)
- **DEV** — active development (ph-WIP DEV-class lanes)
- **Open (not started)** — in product backlog but dev hasn't started (ph-WIP BACKLOG-class lane, or no ph-WIP card found)

## Shipped (<N>)

| ZI | Ticket | Theme | Carriers | Card |
|----|--------|-------|----------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | ... | ... | [SL](shortUrl) |

## Support Closed (<N>)

| ZI | Ticket | Reason | Detail | Card |
|----|--------|--------|--------|------|
| ZI-NNN | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) | <kind> | <detail or ZI-ref> | [SL](shortUrl) |

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

**Step 7 — Report**:
```
## Snapshot <TAG>
- File: wiki/product/releases/<TAG-slug>.md (created | refreshed)
- Cards total: N  (Shipped: N, Support Closed: N, QA READY: N, DEV: N, Open: N)
- git_reference: <unchanged | set to HEAD on first snapshot>
- Cards missing close-reason: N
- Cards without ph-WIP match: N
- Drift: N cards dropped since last snapshot  (if any)
- Warnings: <list>
```

### Idempotency guarantees

Running snapshot twice in sequence produces byte-identical body except for `last_synced`. If ph-WIP lanes changed in between, the body may differ in state rows — but the structure is deterministic.

---

## Mode 3c: `/sl-iteration ship <tag> [board] [--force]`

**Purpose**: freeze the release in wiki state. Propagate shipped work to `wiki/product/backlog.md` and append an entry to `wiki/log.md`. **No Trello writes** at all (no comments, no label changes, no moves, no new lanes).

### Flow

**Step 1 — Run snapshot**: Execute full Mode 3b logic. Ensures release.md is current.

**Step 2 — Parse latest snapshot**: Re-read the freshly written release.md. Count cards by state.

**Step 3 — Safety gate**:
- If any card is in `{Open, DEV, QA READY}`:
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
BOARD = '69dd9134576a26fcb79b670d'
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
/sl-iteration snapshot <tag>
/sl-iteration ship <tag> --force
```

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
