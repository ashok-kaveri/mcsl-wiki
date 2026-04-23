# Slack Ingestion Workflow

**Pipeline**: `raw/slack/*.md` → extract decisions, constraints, action items → `wiki/product/decisions/`, `wiki/modules/`, `wiki/product/backlog.md`

Slack conversations are saved manually as structured markdown with frontmatter. Unlike Zendesk JSON, they're already human-readable with timestamped dialogue.

**Critical rule**: `raw/slack/` is immutable — read only, never modify.

## Step 1: Read & Parse Frontmatter

For each file in `raw/slack/`:

1. **Read frontmatter**: `date`, `channel`, `participants`, `related`, `topic`
2. **Resolve cross-references** from `related`:
   - `zendesk: <ticketId>` → check `wiki/zendesk/summaries/<ticketId>.md` exists
   - `zi: <ZI-ID>` → locate in `wiki/zendesk/YYYY-MM-DD.md`
   - `trello: <url>` → note for cross-linking
3. **Read conversation body**: speakers, timestamps, message content

## Step 2: Extract Artifacts

Scan for three types:

### Decisions
Team commitments to an approach.
- Signals: definitive statements, "we will", "let's go with", "the plan is", conclusions after debate
- Each becomes a candidate for `wiki/product/decisions/YYYY-MM-DD-<slug>.md`

### Constraints
External limitations or dependencies.
- Signals: "we cannot", "requires", "blocked by", third-party requirements, API limitations
- Update relevant `wiki/modules/` page (Known Issues / Tech Debt, or new Constraints section)

### Action items
Tasks assigned to specific people.
- Signals: "@person will", "next step is", "I will", explicit owner commitments
- Candidates for `wiki/product/backlog.md`

## Step 3: Create/Update Wiki Pages

### Decision records (if any)
- Create `wiki/product/decisions/YYYY-MM-DD-<slug>.md` using `@templates/decision-record.md`
- In `## Signals`, link Slack source: `Slack: raw/slack/YYYY-MM-DD-<slug>.md`
- Cross-link referenced Zendesk: `Zendesk: [#<ticketId>](../../zendesk/summaries/<ticketId>.md)` (ZI-XXX)
- Cross-link any referenced Trello cards

### Module page updates (if constraints found)
- Identify the relevant module page under `wiki/modules/`
- Add constraints to "Known Issues / Tech Debt" section with source citation
- Add to Dependencies if new external dependencies were discovered

### Backlog updates (if action items found)
- Add to `wiki/product/backlog.md`
- Score using `(Impact × Confidence) / Effort`
- Link to Slack source in Key Sources column

## Step 4: Cross-link & Log

1. Update `wiki/index.md` if new decision records were created
2. Update cross-references:
   - New decision records → Zendesk summaries, module pages, Trello cards
   - Updated module pages → Slack source and referenced tickets
   - Backlog items → Slack source
3. Log in `wiki/log.md`:

```markdown
## [YYYY-MM-DD HH:MM] slack-ingest | <Topic from frontmatter>
- Source: `raw/slack/YYYY-MM-DD-<slug>.md`
- Created: `product/decisions/YYYY-MM-DD-<slug>.md` (if applicable)
- Updated: `modules/<domain>/<module>.md` (if applicable)
- Updated: `product/backlog.md` (if applicable)
- Cross-refs: Zendesk #<ticketId>, ZI-<id>, Trello <card>
- Summary: N decisions, N constraints, N action items
```
