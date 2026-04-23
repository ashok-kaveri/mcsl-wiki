# Product Management Workflow

Covers feature stories, metrics refresh, release notes, and delta-aware resyncs.

## Overview

The `wiki/product/` layer synthesizes signals from all raw sources (Zendesk, Slack, test coverage, code complexity, regression matrix) into actionable product intelligence.

```
wiki/product/
├── backlog.md          # Scored, prioritized work items
├── insights.md         # Aggregated signals from all sources
├── metrics.md          # Customer metrics dashboard
├── features/<slug>.md  # Feature stories
├── decisions/YYYY-MM-DD-<slug>.md
└── releases/YYYY-MM-DD.md
```

See `CLAUDE.md` for frontmatter categories and delta detection fundamentals.

## Feature Story Workflow

**Trigger**: "Create feature story for X"

### 1. Gather signals
- Wiki module pages
- Zendesk summaries matching the feature area (from `wiki/zendesk/summaries/*.md` Open Issues tags)
- Daily index `wiki/zendesk/YYYY-MM-DD.md` for ZI IDs in the feature area
- Slack conversations from `raw/slack/` (filter by `related` matching feature area tickets/ZI IDs, or by `topic`)
- Test coverage from `features.md`
- Regression rows from the sheet (if applicable)

### 2. Create the story
Use `@templates/feature-story.md`. Place at `wiki/product/features/<slug>.md`.

### 3. Write user stories with acceptance criteria
- Map regression scenarios from the spreadsheet to stories
- Link ZI issues and ticket summaries as evidence

### 4. Cross-link
- Module pages (implementation)
- Zendesk summaries (customer evidence): `wiki/zendesk/summaries/<ticketId>.md`
- Regression rows (manual test scenarios)
- `features.md` (automation status)
- Add to `backlog.md` if not already there

### 5. Update `git_reference` to current HEAD

## Metrics Refresh Workflow

**Trigger**: "Refresh metrics"

### 1. Detect delta
`git diff` on `wiki/zendesk/summaries/` (NOT raw/zendesk/).

### 2. Read new/changed ticket summaries
Group by product and feature area.

### 3. Check new Slack conversations
`git diff` on `raw/slack/`:
- Extract decisions/constraints affecting feature health
- Note action items indicating upcoming work

### 4. Compute per-feature metrics
- Ticket volume (total, open, pending, solved)
- Trend vs previous count: ↑ increasing, → stable, ↓ decreasing
- Top issue (most common subject theme)

### 5. Cross-reference automation data from `features.md`
- Automation confidence per feature
- Regression coverage per feature

### 6. Derived metrics
- **Customer Pain Index**: `(ticket_volume × severity_weight) / automation_confidence`
- **Feature Health**: 🟢 Healthy / 🟡 Watch / 🔴 At Risk (composite score)

### 7. Update `product/metrics.md` and set `git_reference` to current HEAD

## Release Workflow

**Trigger**: "Draft release notes for X"

1. Check which backlog items moved to "shipped"
2. Pull before/after metrics from `metrics.md` history (git blame or previous values)
3. Link to feature stories and decisions that drove the release
4. Create `product/releases/YYYY-MM-DD.md` using `@templates/release-notes.md`

## Delta-Aware Resync

Every page records `git_reference` — the wiki repo commit at last sync.

### Delta detection

```bash
# New/changed Zendesk tickets since last sync
git diff <git_reference>..HEAD --name-only -- raw/zendesk/shopify/

# Changed regression sheet
git diff <git_reference>..HEAD --name-only -- raw/sheets/

# New Slack conversations
git diff <git_reference>..HEAD --name-only -- raw/slack/

# Updated submodules
git diff <git_reference>..HEAD -- raw/storepep-react raw/mcsl-test-automation
```

Process only the delta. Update `git_reference` to current HEAD.

### Triggers
- New Zendesk tickets → update insights.md, metrics.md, potentially create backlog items
- Updated submodules → update test coverage in metrics.md and feature stories
- Re-exported regression sheet → update regression coverage
- New Slack conversations → extract decisions/constraints/action items (see @workflows/slack-ingestion.md)
- User command — "resync PM", "triage new tickets", "refresh metrics"

## Cross-Linking Rules

Every product page links in three directions:
- **Upstream** (raw): Zendesk ticket IDs, regression rows, code paths, Slack files
- **Lateral** (wiki): related features, decisions, modules, features.md sections
- **Downstream** (outputs): backlog items, releases, affected metrics
