# Zendesk Issue Extraction Pipeline

**Pipeline**: `raw/zendesk/*.json` → `wiki/zendesk/summaries/*.md` → `wiki/zendesk/YYYY-MM-DD.md` → `product/backlog.md` → `product/roadmap-april-2026.html`

**Critical rule**: Downstream artifacts (backlog, roadmap, insights, metrics) MUST read from `wiki/zendesk/summaries/*.md` — NEVER go back to `raw/zendesk/*.json`. The summaries are the quality-gated source of truth.

## Commands

- `/zendesk-summarize [all|delta|<ticketId>] [shopify|other_platforms|all-products]` — full pipeline (Steps 1-6)
- `/zendesk-summarize-one <ticketId>` — single ticket only, skip daily index update

## Categorization

### Products (Zendesk `product_name` tag)
- `shopify_multi_carrier_shipping_label_app` → **shopify**
- Future products get their own category

### Feature Area Tags
See `CLAUDE.md` — Conventions → Feature Area Tags.

## Step 1: Sync Check

Check `raw/zendesk/` for:
- Staleness
- Truncation (flag files with exactly 100 comments — API pagination limit)
- Corrupt/empty files

## Step 2: Per-Ticket Summarization

For each ticket in `raw/zendesk/shopify/*.json`:

1. **Read full JSON in one pass** with python `json.load()`. Never use chunked `Read` with offset/limit — loses structure.
2. **Read comments in reverse** — start from latest to find current state, then work backwards for timeline.
3. **Write `wiki/zendesk/summaries/<ticketId>.md`**:

```markdown
---
title: "Ticket #<id> — <subject>"
ticket_id: <id>
status: <open|new|closed>
customer: <name> (<store>)
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# Ticket #<id> — <subject>

- **Customer**: <name> (<store>)
- **Duration**: <dates> (<ongoing|resolved>)

## Timeline & Key Phases

### Phase 1: <title> (<dates>)
- <key events>

## Open Issues

1. **<Title>** — <description>. Blocked: <who>. Severity: <signal>. Area: <feature-area-tag>. (Comment #N)

## Resolved Issues

1. **<Title>** — <how/when>. (Comment #N)

## Customer Context

- <details>
```

### Summarization rules

- **Open issues = latest state only** — L3 escalations, pending customer requests, unresolved blockers. Not a replay of every comment.
- **Lifecycle-only tickets** (install welcomes, uninstall win-backs with no substantive reply): "No open issues — lifecycle-only ticket."
- **Every issue MUST cite the comment number** that evidences it
- **Every open issue MUST include**: title, who's blocked, severity signal, feature area tag

### Parallelization

Spawn agents in batches of ~10 tickets. Each agent reads JSON via python and writes summary files.

## Step 3: Daily Index

Write `wiki/zendesk/YYYY-MM-DD.md`:

```markdown
# Zendesk Issue Extraction — YYYY-MM-DD

**Tickets with open issues**: NN
**Total open issues**: NNN

## Summary by Feature Area
| Feature Area | Issues | Tickets |
|---|---|---|

## Issue Index
| ID | Issue | Ticket | Area |
|---|---|---|---|
| ZI-001 | ... | [#NNNNNN](summaries/NNNNNN.md) | ... |

## Issues by Feature Area
### <area> (N issues)
| ID | Issue | Ticket |
```

## Step 4: Backlog Regeneration

**Input**: Open Issues sections of `wiki/zendesk/summaries/*.md`. Each has title, blocked-by, severity, feature area tag, comment citation. NEVER go back to raw JSON.

**Process**:
1. Parse all open issues from summaries
2. Read daily index `wiki/zendesk/YYYY-MM-DD.md` for canonical ZI IDs
3. Cluster ZI issues into backlog items by feature area / theme
4. Score each cluster: `(Impact × Confidence) / Effort`
   - **Impact** (1-5): based on issue count + severity signals
   - **Effort** (1-5): engineering complexity (1=toggle/config, 5=new carrier integration)
   - **Confidence** (1-5): higher when multiple summaries confirm same issue; lower for single-ticket requests
5. Sort by priority score

**Output**: Rewrite `wiki/product/backlog.md`:
- **Active Backlog table**: `# | Item | Issues | Tickets | Impact | Effort | Confidence | Score | Key Sources | Status`
- Key Sources column links to BOTH ZI IDs AND `wiki/zendesk/summaries/<ticketId>.md`
- **Cluster detail tables**: every ZI issue with title, ticket link, area
- **Parking Lot**: low-urgency feature requests
- **Stale / Back-log**: long-open items (2023-2024 vintage)
- **All issues must be accounted for** (active + parking lot + stale)
- **Scoring rationale table**: explain Impact/Effort/Confidence per backlog item

## Step 5: Roadmap Update

Read `wiki/product/backlog.md`. Update `ZEN_FEATURES` JS object in roadmap HTML. Preserve `SP_FEATURES` and `L3_ITEMS`.

## Step 6: Cross-link & Log

Update `wiki/index.md`, `wiki/log.md`, and cross-links from insights/metrics.

```markdown
## [YYYY-MM-DD HH:MM] zendesk-summarize | <scope>
- Processed: N tickets
- Created/updated: summaries, daily index, backlog, roadmap
- Git reference: <commit>
- Summary: <counts by feature area, notable changes>
```

## Delta Triage

When new tickets arrive (incremental sync):

1. Detect delta:
   ```bash
   git diff <last_git_reference>..HEAD --name-only -- raw/zendesk/
   ```
2. Run Steps 1-2 for only the new/changed tickets
3. Update daily index — add new ZI issues, increment counts
4. Re-cluster backlog if new issues change a cluster's scoring
5. Update `git_reference` in all modified pages
6. Log the triage
