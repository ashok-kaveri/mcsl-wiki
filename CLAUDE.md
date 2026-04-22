# StorePep Knowledge Base - Schema & Workflows

## Purpose

This is an **LLM-maintained knowledge base** for the StorePep product ecosystem. The goal is to create a living, evolving wiki that serves as an active development companion - documentation that stays current as the code evolves, tracks architectural decisions, maintains dependency maps, and aggregates insights from multiple sources (code, tests, support tickets, regression plans, etc.).

**Key Principle**: The wiki is a persistent, compounding artifact. You (Claude) write and maintain all wiki pages. The user curates what to ingest, asks questions, and directs the analysis. The wiki keeps getting richer with every source ingested and every question asked.

## Architecture

There are four layers:

1. **Raw** (`raw/`) - All input sources. Immutable from the wiki's perspective. You read from `raw/` but **never modify it**. Contains multiple source types (git submodules, webhook-populated data, exported sheets, etc.) registered in `raw/sources.yaml`.

2. **The Wiki** (`wiki/`) - LLM-generated markdown files. You own this layer entirely. You create pages, update them when ingesting new material, maintain cross-references, and keep everything consistent.

3. **This Schema** (`CLAUDE.md`) - Instructions for how to maintain the wiki. Workflows, templates, conventions.

4. **Source Registry** (`raw/sources.yaml`) - Declares every raw source: its type, local path, sync method, and description. This is the single source of truth for where raw data lives. When resolving a source, always read `raw/sources.yaml` first.

## Source Registry (`raw/sources.yaml`)

The registry declares every raw source. When resolving paths, always read this file first rather than hardcoding paths.

### Source Types

| Type | How it gets into `raw/` | Git-trackable? | Example |
|------|------------------------|----------------|---------|
| `git-submodule` | `git submodule add <repo> raw/<name>` | Yes (pinned commit) | Codebase, test suite |
| `webhook-json` | External webhook writes `{id}.json` files | Yes (commit on receive) | Zendesk tickets |
| `google-sheet` | Manual CSV export or automated sync script | Yes (commit after export) | Regression scenarios |
| `manual` | User places files directly | Yes | Ad-hoc documents, specs, Slack conversations |

### `sources.yaml` Format

```yaml
sources:
  storepep-react:
    type: git-submodule
    path: raw/storepep-react
    description: "Main StorePep SaaS codebase"
    repo: <git-url>

  mcsl-test-automation:
    type: git-submodule
    path: raw/mcsl-test-automation
    description: "Playwright E2E test suite"
    repo: <git-url>

  zendesk:
    type: webhook-json
    path: raw/zendesk
    pattern: "{ticketId}.json"
    description: "Customer support tickets via webhook"
    workflow: "Zendesk Issue Extraction Pipeline (see below)"
    # Pipeline: raw/zendesk/*.json → wiki/zendesk/summaries/*.md → wiki/zendesk/YYYY-MM-DD.md → backlog → roadmap

  regression-scenarios:
    type: google-sheet
    path: raw/sheets/regression-scenarios.csv
    url: "https://docs.google.com/spreadsheets/d/1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY"
    sync: manual
    description: "Master regression test plan"

  slack:
    type: manual
    path: raw/slack
    pattern: "YYYY-MM-DD-<slug>.md"
    description: "Internal Slack conversations with product/engineering context"
    workflow: "Slack Ingestion Workflow (see below)"
    # Pipeline: raw/slack/*.md → extract decisions/constraints/action items → wiki/product/decisions/, wiki/modules/, wiki/product/backlog.md
```

### Adding a New Source

1. Choose the appropriate type from the table above
2. Add the source to `raw/` (e.g., `git submodule add`, place files, configure webhook)
3. Register it in `raw/sources.yaml` with type, path, and description
4. If the source needs an ingestion workflow, define it in the Ingestion Workflows section below
5. Commit the changes to the wiki repo

### Immutability Rule

Everything under `raw/` is **read-only from the wiki's perspective**. Claude reads from `raw/` but never modifies files there. The only writes to `raw/` come from external processes (git pulls, webhooks, manual exports).

## Directory Structure

```
mcsl-wiki/
├── raw/                               # ALL input sources (immutable)
│   ├── sources.yaml                   # Source registry — single source of truth
│   ├── storepep-react/                # git submodule → main codebase
│   ├── mcsl-test-automation/          # git submodule → Playwright E2E tests
│   ├── zendesk/                       # Zendesk tickets, categorized by product
│   │   ├── shopify/                   # Shopify MCSL tickets (status<pending, agent)
│   │   │   ├── <ticketId>.json
│   │   │   └── ...
│   │   └── <future-product>/          # Extensible — add new products here
│   ├── sheets/                        # Google Sheets exported as CSV
│   │   └── regression-scenarios.csv
│   ├── slack/                         # Slack conversations saved as markdown
│   │   └── YYYY-MM-DD-<slug>.md
│   └── <future-source>/               # Extensible — add new sources here
├── wiki/
│   ├── architecture/          # System-level documentation
│   │   ├── overview.md
│   │   ├── frontend-architecture.md
│   │   ├── backend-architecture.md
│   │   ├── data-flow.md
│   │   ├── authentication-flow.md
│   │   ├── deployment-pipeline.md
│   │   └── technology-stack.md
│   ├── modules/               # Feature/domain pages
│   │   ├── <domain>/          # Group by domain (orders, shipping, products, etc.)
│   │   │   ├── <module>.md    # One page per logical unit
│   │   │   └── ...
│   ├── patterns/              # Cross-cutting concepts
│   │   ├── redux-patterns.md
│   │   ├── api-conventions.md
│   │   ├── error-handling.md
│   │   ├── feature-toggles.md
│   │   └── access-control.md
│   ├── operations/            # Dev/ops guides
│   │   ├── local-setup.md
│   │   ├── database-migrations.md
│   │   ├── deployment.md
│   │   └── monitoring.md
│   ├── product/               # Product management layer
│   │   ├── backlog.md         # Scored, prioritized work items
│   │   ├── insights.md        # Aggregated signals from all sources
│   │   ├── metrics.md         # Customer metrics dashboard
│   │   ├── features/          # Feature stories with acceptance criteria
│   │   │   └── <slug>.md
│   │   ├── decisions/         # Product decision records
│   │   │   └── YYYY-MM-DD-<slug>.md
│   │   └── releases/          # Release notes with metrics delta
│   │       └── YYYY-MM-DD.md
│   ├── zendesk/               # Zendesk issue extraction pipeline output
│   │   ├── summaries/         # One structured summary per ticket
│   │   │   └── <ticketId>.md  # Timeline, open/resolved issues, customer context
│   │   └── YYYY-MM-DD.md     # Daily index: all issues with ZI IDs, area counts
│   ├── features.md            # User-facing features with test coverage
│   ├── index.md               # Catalog of all pages
│   └── log.md                 # Chronological activity log
├── CLAUDE.md                  # This file
└── README.md                  # Human-readable intro
```

## Page Template

Every wiki page should follow this structure:

```markdown
---
title: <Page Title>
category: <architecture|module|pattern|operation>
domain: <orders|shipping|products|etc.> # if category=module
sources: [storepep-react, mcsl-test-automation] # which raw sources this page draws from (keys from sources.yaml)
status: <complete|partial|needs-update>
last_updated: <YYYY-MM-DD>
git_reference: <commit hash or "current">
---

# <Page Title>

## Overview

Brief description of what this is and why it exists.

## Key Components

### Component/File 1
- **Location**: `path/to/file.js:123-456`
- **Purpose**: What it does
- **Key exports/APIs**: List main functions, classes, components

### Component/File 2
...

## Data Flow

How data moves through this module. Diagrams welcome (mermaid, ascii).

## Dependencies

This module depends on:
- [Module Name](../path/to/module.md) - why/how
- [External Package](link) - version, purpose

## Referenced By

This module is used by:
- [Module Name](../path/to/module.md) - how it's used
- [Another Module](../path/to/another.md)

## Configuration

Environment variables, feature toggles, settings relevant to this module.

## Common Patterns

Typical usage patterns, code examples if useful.

## Test Coverage

**Automated E2E Tests**: X Playwright tests covering this module

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| Feature Name | `path/to/test.spec.ts` | ✅ Passing |
| Another Feature | `path/to/another.spec.ts` | ✅ Passing |

**Test Coverage**: X/Y features tested (Z% coverage)

**Tested Scenarios**:
- ✅ Scenario 1
- ✅ Scenario 2

**Untested Scenarios**:
- ❌ Scenario 3
- ❌ Scenario 4

**Test Suite Location**: `raw/mcsl-test-automation/tests/<domain>/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Known Issues / Tech Debt

Areas for improvement, known bugs, planned refactoring.

## Related Pages

- [Related Topic](../path/to/topic.md)
- [Another Topic](../path/to/another.md)
- [Features List](../../features.md) - User-facing features and test coverage
```

## Ingestion Workflow

When the user asks to ingest code (e.g., "Ingest the order management system"):

1. **Read**: Use Glob/Grep/Read to explore the specified files/directories
   - For a feature domain, read: routes, models, services, actions, reducers, components
   - Look for the main files first, then dependencies

2. **Discuss**: Share key findings with the user
   - What's the core functionality?
   - How complex is it? (lines of code, number of files)
   - What are the main dependencies?
   - Any surprises or interesting patterns?
   - Ask clarifying questions if needed

3. **Create/Update Pages**:
   - Create new module pages or update existing ones
   - Update architecture/pattern pages if they're affected
   - Follow the page template
   - Include file:line references for key code locations
   - Note the git commit hash (use `git rev-parse HEAD` in the source repo)

4. **Cross-link**:
   - Add "Dependencies" section linking to other modules
   - Update "Referenced By" sections in dependent pages
   - Add links to relevant pattern/architecture pages

5. **Update Index**: Add new pages to `wiki/index.md` with one-line summaries

6. **Log**: Append an entry to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD HH:MM] ingest | <Feature/Module Name>
   - Created: `path/to/new/page.md`
   - Updated: `path/to/existing/page.md`
   - Git reference: <commit-hash>
   - Summary: Brief description of what was ingested
   ```

## Query Workflow

When the user asks a question about the codebase:

1. **Search Index**: Read `wiki/index.md` to find relevant pages
2. **Read Pages**: Read the relevant wiki pages
3. **Check Source**: If wiki info is insufficient or potentially stale, read the actual source files
4. **Answer**: Provide answer with citations (link to wiki pages and source files)
5. **File (Optional)**: If the answer is substantial and reusable, ask user if you should create a new wiki page for it

## Lint Workflow

When the user asks to "lint the wiki" or "health-check the KB":

1. **Staleness Check**:
   - Compare page metadata (last_updated, git_reference) with current git state
   - Flag pages that reference old commits or are outdated

2. **Completeness Check**:
   - Look for pages marked `status: partial` or `status: needs-update`
   - Identify major features/modules in the codebase not yet documented

3. **Consistency Check**:
   - Find orphan pages (no inbound links)
   - Find broken links
   - Check for contradictions between pages

4. **Coverage Suggestions**:
   - Suggest important concepts that lack dedicated pages
   - Identify missing cross-references

5. **Report**: Provide a summary with actionable items

## Test Coverage Workflow

When the user asks to document test coverage (e.g., "Generate features.md from regression tests and Playwright automation"):

**Two-Source Strategy**: `features.md` integrates both regression scenarios (what SHOULD be tested) and automated tests (what IS tested) to provide complete coverage visibility and identify automation gaps.

### 1. **Analyze Both Test Sources**

#### A. Regression Test Scenarios (Manual Test Plan)

**Source**: `raw/sheets/regression-scenarios.csv`

**Steps**:
1. Read the regression CSV to understand complete feature inventory
2. Extract each test scenario with:
   - Test ID/number (if available)
   - Feature description (user-facing)
   - Category/domain (orders, shipping, automation, etc.)
   - Manual test status
3. Group scenarios by feature category

#### B. Playwright Automated Tests

**Test Suite Location**: `raw/mcsl-test-automation/tests/`

**Discovery**:
```bash
find raw/mcsl-test-automation/tests -name "*.spec.ts" -o -name "*.spec.js"
```

**For each test file**:
- Read the test file content
- Understand what feature/functionality is being tested
- Extract user-facing feature description (plain English, one line)
- Note the test file path
- Identify which wiki module it relates to

**Use Task tool with Explore agent** for comprehensive test analysis across all files.

#### C. Map Regression to Automation

**Mapping Process**:
1. For each regression test, determine if a Playwright test covers it
2. Match by feature description, test intent, or explicit test ID references
3. Calculate automation confidence score (see Section 7)
4. Flag regression gaps (tests without automation)
5. Flag orphan automation (automated tests not in regression suite)

### 2. **Create/Update features.md**

**Location**: `wiki/features.md`

**Structure** (integrating both regression and automation):

```markdown
# StorePep Features

**Regression Test Suite**: X total test scenarios (complete feature inventory)
**Automated Tests**: Y Playwright tests
**Automation Coverage**: Y/X (Z%)
**Last Updated**: YYYY-MM-DD
**Sources**: regression-scenarios, mcsl-test-automation

---

## <Category Name> (e.g., Automation Rules)

### Regression Test Suite

| # | Feature | Manual | Automated | Confidence | Test File | Wiki Reference |
|---|---------|--------|-----------|------------|-----------|----------------|
| 1 | Feature from regression sheet | 🔴 | ✅ | 🟢 95% | `path/to/test.spec.ts` | [Module](modules/path.md) |
| 2 | Another feature from sheet | ✅ | 🔴 | 🔴 0% | — | [Module](modules/path.md) |
| 3 | Feature with partial automation | 🔴 | ⚠️ | 🟡 75% | `path/to/partial.spec.ts` | [Module](modules/path.md) |

**Automation Summary**:
- Total regression tests: X
- Automated tests: Y (Z%)
- High confidence automation: N (>95%)
- Medium confidence automation: M (70-94%)
- Low/no automation: L (<70%)

**Automated Test Files**:
- `automationRules/totalWeightRange.spec.ts` - Covers regression #1, #3, #5
- `automationRules/carrierSelection.spec.ts` - Covers regression #2, #4

**Automation Gaps** (regression tests without automation):
- 🔴 Regression #X: Feature description - [Module](modules/path.md)

---

## Test Coverage by Module

| Module | Total Features | Automated | Manual Only | Automation % |
|--------|---------------|-----------|-------------|--------------|
| Automation Rules | X | Y | Z | W% |
| Label Generation | X | Y | Z | W% |

---

## Test Organization

**Regression Test Suite**: `raw/sheets/regression-scenarios.csv`
**Automated Tests**: `raw/mcsl-test-automation/tests/`
```
mcsl-test-automation/tests/
├── automationRules/     (X tests)
│   ├── automationCriteria/
│   └── automationActions/
├── orderGrid/           (Y tests)
│   ├── actionMenu/
│   └── labelGenerationFromGrid/
└── ...
```

---

## Related Pages

- [Module Page](modules/<domain>/<module>.md)
- [Product Backlog](product/backlog.md) - Prioritized work items
```

**Feature Description Guidelines**:
- **User-facing**: Describe what the user can do, not implementation details
- **Plain English**: No technical jargon unless necessary
- **Action-oriented**: Start with verbs (Create, Generate, Configure, Process)
- **Specific**: "Generate labels for orders with multiple products" not "Label generation works"
- **One line**: Keep it concise

**Examples**:
- ✅ Good: "Create automation rules based on total weight range"
- ✅ Good: "Generate labels and fulfill orders from order grid"
- ❌ Bad: "Test automation rules" (not specific)
- ❌ Bad: "OrderProcessingService handles weight-based routing" (technical)

**Why This Comprehensive Approach Matters**:

This two-source integration provides critical insights:

1. **Automation Coverage** - What percentage of regression tests have automation
2. **Automation Gaps** - Which critical features lack automated tests
3. **Orphan Tests** - Automated tests not mapped to regression scenarios (may indicate missing documentation)
4. **Confidence Scoring** - Quality/stability of automation per feature
5. **Prioritization Data** - For product/backlog decisions: automate high-impact manual tests first
6. **Feature Inventory** - Complete catalog of what the product should do (regression) vs what's verified (automation)

### 3. **Update Module Pages with Test Coverage**

**For each relevant module page**, add a "Test Coverage" section before "Known Issues / Tech Debt":

**Template**:
```markdown
## Test Coverage

**Automated E2E Tests**: X Playwright tests covering <module name>

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| Feature Name | `category/subcategory/testName.spec.ts` | ✅ Passing |

**Test Coverage**: X/Y features tested (Z% coverage)

**Tested Scenarios**:
- ✅ Scenario 1 description
- ✅ Scenario 2 description

**Untested Scenarios**:
- ❌ Untested scenario 1
- ❌ Untested scenario 2

**Test Suite Location**: `raw/mcsl-test-automation/tests/<category>/`

**Documentation**: See [Features List](../../features.md) for complete test coverage
```

**Coverage Calculation**:
- Count distinct features tested
- Count total features in module (from code analysis)
- Calculate percentage: (tested / total) * 100

**Status Indicators**:
- ✅ Test passing
- ⚠️ Test flaky/intermittent
- ❌ Test failing
- 🚧 Test in development

### 4. **Map Tests to Modules**

**Mapping Guidelines**:

| Test Category | Wiki Module |
|---------------|-------------|
| `automationRules/` | `modules/automation/` |
| `carrierOtherDetails/` | `modules/shipping/carrier-configuration.md` |
| `orderGrid/actionMenu/` | `modules/orders/order-bulk-actions.md` |
| `orderGrid/labelGenerationFromGrid/` | `modules/shipping/label-generation.md` |
| `orderSummary/` | `modules/orders/order-lifecycle.md` |
| `packagingTypes/` | `modules/shipping/label-generation.md` (packaging section) |
| `shopifyUI/` | `modules/stores/platform-connectors.md` |
| `specialServices/` | `modules/shipping/label-generation.md` or `carrier-configuration.md` |
| `trackingFromGrid/` | `modules/shipping/shipment-tracking.md` |

### 5. **Update Index and Log**

**Index Updates**:
```markdown
## Features & Testing

- [Features](features.md) - Complete list of X user-facing features with test coverage status

**Total pages**: X
**Test Coverage**: Y automated Playwright tests covering Z features
```

**Log Entry Format**:
```markdown
## [YYYY-MM-DD HH:MM] test-coverage | Complete Test Coverage Documentation
- Created: `features.md`
- Updated: `modules/<domain>/<module>.md` (added test coverage section)
- Updated: `index.md`
- Updated: `log.md`
- Git reference: <commit-hash>
- Summary: Comprehensive analysis of X Playwright test files, extracting Y distinct user-facing features. Added test coverage sections to Z module pages with tested/untested scenario breakdowns. Test organization: <brief summary of test structure>. Coverage highlights: <key stats>.
```

### 6. **Maintain Test Coverage**

**When regression scenarios change** (re-exported CSV):
1. User notifies of regression sheet update
2. Re-read `raw/sheets/regression-scenarios.csv`
3. Identify new/changed/removed regression tests
4. Re-map to existing automation
5. Update features.md with new regression rows
6. Update coverage percentages
7. Update module pages with new scenarios
8. Log the update

**When Playwright tests change** (new/modified .spec.ts files):
1. User notifies of new/changed tests
2. Re-analyze affected test files
3. Map new tests to regression scenarios (if applicable)
4. Update features.md with new automation
5. Update automation confidence scores
6. Update affected module pages
7. Update coverage statistics
8. Log the update

**When both change** (full resync):
1. Re-read regression CSV
2. Re-analyze all Playwright tests
3. Rebuild complete mapping
4. Regenerate features.md
5. Update all module pages
6. Log comprehensive resync

**Coverage Health Checks**:
- Flag modules with <50% automation coverage
- Identify critical workflows without automation
- Suggest high-value tests to automate (regression tests with high impact, no automation)
- Flag low-confidence automation (<70%) for review
- Identify orphan automation (not mapped to regression)

### 7. **Integrate Regression Test Suite**

**Master Test Plan**: User maintains a comprehensive regression test spreadsheet

**Structure**:
- **Regression Tests**: Complete test suite (manual + automated)
- **Automated Tests**: Subset that's been automated via Playwright
- **Automation Status**: Which regression tests have automation
- **Confidence Score**: Quality/stability of automation

**features.md Structure**:

```markdown
# StorePep Features

## Feature Category

### Regression Test Suite

| # | Feature | Manual | Automated | Confidence | Wiki Reference |
|---|---------|--------|-----------|------------|----------------|
| 1 | Feature description | 🔴 | ✅ | 🟢 95% | [Module](modules/path.md) |
| 2 | Another feature | ✅ | 🔴 | 🔴 0% | [Module](modules/path.md) |

**Automation Summary**:
- Total regression tests: X
- Automated tests: Y (Z%)
- Automation confidence: 🟢 High / 🟡 Medium / 🟠 Low

**Automated Test Files**:
- `path/to/test1.spec.ts` - Covers regression tests #1, #3, #5
- `path/to/test2.spec.ts` - Covers regression tests #2, #4
```

**Mapping Process**:
1. User provides regression test spreadsheet (CSV export or data)
2. For each regression test, identify:
   - Is it automated? (Playwright test exists)
   - Which test file covers it?
   - Automation confidence score (based on test stability)
3. Link regression test to wiki module
4. Calculate automation percentage per category
5. Update features.md with complete mapping

**Confidence Score Calculation**:
- **High (🟢 95-100%)**: Test is stable, runs in CI, covers all scenarios, no manual verification needed
- **Medium (🟡 70-94%)**: Test automated but requires occasional manual verification, some edge cases not covered
- **Low (🟠 40-69%)**: Basic automation exists but significant manual testing still required
- **None (🔴 0-39%)**: Primarily manual testing, minimal or no automation

## Product Management

The wiki includes a **product management layer** under `wiki/product/` that synthesizes signals from all raw sources (Zendesk tickets, Slack conversations, test coverage, code complexity, regression matrix) into actionable product intelligence.

### Product Directory Structure

```
wiki/product/
├── backlog.md                    # Scored, prioritized work items
├── insights.md                   # Aggregated signals from all sources
├── metrics.md                    # Customer metrics dashboard (ticket trends, feature health)
├── features/
│   └── <feature-slug>.md         # Feature story: problem, user stories, acceptance criteria, metrics
├── decisions/
│   └── YYYY-MM-DD-<slug>.md      # Product decision records
└── releases/
    └── YYYY-MM-DD.md             # Release notes with metrics delta
```

### Product Page Categories

Add these to the existing `category` frontmatter options:

- `product` — backlog, insights, metrics
- `product-feature` — feature stories
- `product-decision` — decision records
- `product-release` — release notes

### Ticket Categorization

Zendesk tickets are categorized by **product** and **feature area**:

**Products** (from Zendesk `product_name` tag):
- `shopify_multi_carrier_shipping_label_app` → categorized under **shopify**
- Future products get their own category

**Feature Areas** (derived from ticket subject + tags):
- `onboarding` — installation, setup, welcome tickets, uninstalls
- `carrier-config` — carrier-specific setup, credentials, account issues
- `carrier-migration` — API migrations (e.g., FedEx SOAP→REST)
- `label-generation` — label creation, manifests, label errors
- `rate-shopping` — rate fetch, rate display, rate rules
- `tracking` — shipment tracking, status updates
- `returns` — return label generation, return tracking
- `international` — customs, dangerous goods, country of manufacture, commercial invoices
- `order-management` — order data, line items, order errors
- `product-management` — product import, product data
- `feature-request` — customer feature suggestions
- `other` — uncategorized / multi-issue

### Delta-Aware Resync Workflow

All product pages use **git-based delta detection**. Each page records `git_reference` in its frontmatter — the wiki repo commit at which the page was last synced.

#### How Delta Detection Works

1. **On resync**, read `git_reference` from the product page's frontmatter
2. **Diff raw/ against that commit**:
   ```bash
   # New/changed Zendesk tickets since last sync
   git diff <git_reference>..HEAD --name-only -- raw/zendesk/shopify/
   
   # Changed regression sheet
   git diff <git_reference>..HEAD --name-only -- raw/sheets/
   
   # New Slack conversations since last sync
   git diff <git_reference>..HEAD --name-only -- raw/slack/
   
   # Updated submodules
   git diff <git_reference>..HEAD -- raw/storepep-react raw/mcsl-test-automation
   ```
3. **Process only the delta** — new tickets, changed test files, updated sheet
4. **Update page frontmatter** with current commit hash after processing

#### What Triggers a Resync

Any change in `raw/` can trigger an update:
- **New Zendesk tickets** → update insights.md, metrics.md, potentially create backlog items
- **Updated git submodules** → update test coverage in metrics.md, feature stories
- **Re-exported regression sheet** → update regression coverage in features, metrics
- **New Slack conversations** → extract decisions/constraints/action items, update decisions/, modules/, backlog
- **User command** — "resync PM", "triage new tickets", "refresh metrics"

### Zendesk Issue Extraction Pipeline

**Pipeline**: `raw/zendesk/*.json` → `wiki/zendesk/summaries/*.md` → `wiki/zendesk/YYYY-MM-DD.md` → `product/backlog.md` → `product/roadmap-april-2026.html`

**Critical rule**: Downstream artifacts (backlog, roadmap, insights, metrics) MUST read from `wiki/zendesk/summaries/*.md` — NEVER go back to `raw/zendesk/*.json`. The summaries are the processed, quality-gated source of truth.

**Skills**:
- `/zendesk-summarize [all|delta|<ticketId>] [shopify|other_platforms|all-products]` — Full pipeline (Steps 1-6)
- `/zendesk-summarize-one <ticketId>` — Summarize a single ticket only, skip daily index update

#### Step 1: Sync Check

```bash
# Check for staleness, truncation, corruption
# Flag files with exactly 100 comments (API pagination limit)
# Flag corrupt/empty files
```

#### Step 2: Per-Ticket Summarization

For each ticket in `raw/zendesk/shopify/*.json`:

1. **Read the full JSON** in one pass using python `json.load()` — never use chunked `Read` with offset/limit on JSON files (loses structure)
2. **Read comments in reverse** — start from the LATEST to find current state, then work backwards for timeline
3. **Write `wiki/zendesk/summaries/<ticketId>.md`** with this structure:

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

**Summarization rules**:
- **Open issues = latest state only** — L3 escalations, pending customer requests, unresolved blockers. NOT a replay of every comment interaction.
- **Lifecycle-only tickets** (installation welcomes, uninstall win-backs with no substantive customer reply) get: "No open issues — lifecycle-only ticket."
- **Each issue MUST cite** the comment number that evidences it
- **Each open issue MUST include**: title, who's blocked, severity signal, feature area tag
- **Feature area tags**: onboarding, carrier-config, carrier-migration, label-generation, rate-shopping, tracking, returns, international, order-management, product-management, feature-request, other

**Parallelization**: Spawn agents in batches of ~10 tickets each. Each agent reads JSON via python and writes summary files.

#### Step 3: Daily Index

Write `wiki/zendesk/YYYY-MM-DD.md` — aggregates all open issues with ZI IDs:

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

#### Step 4: Backlog Regeneration

Read `wiki/zendesk/summaries/*.md` (NOT raw JSON). NEVER go back to `raw/zendesk/*.json` for backlog generation.

**Input**: The Open Issues section of each summary file. Each issue has: title, blocked-by, severity, feature area tag, comment citation.

**Process**:
1. Parse all open issues from `wiki/zendesk/summaries/*.md`
2. Read the daily index `wiki/zendesk/YYYY-MM-DD.md` for canonical ZI IDs
3. Cluster ZI issues into backlog items by feature area / theme
4. Score each cluster: `(Impact × Confidence) / Effort`
   - Impact (1-5): Based on issue count in cluster + severity signals from summaries
   - Effort (1-5): Engineering complexity (1=toggle/config, 5=new carrier integration)
   - Confidence (1-5): Higher when multiple summaries confirm same issue; lower for single-ticket requests
5. Sort by priority score (highest first)

**Output**: Rewrite `wiki/product/backlog.md` with:
- Active Backlog table: `# | Item | Issues | Tickets | Impact | Effort | Confidence | Score | Key Sources | Status`
- Key Sources column links to BOTH ZI issue IDs AND `wiki/zendesk/summaries/<ticketId>.md`
- Cluster detail tables: every ZI issue within each cluster with title, ticket link, area
- Parking Lot: low-urgency feature requests
- Stale / Back-log: long-open items (2023-2024 vintage)
- All 93 ZI issues must be accounted for (active + parking lot + stale)

**Scoring rationale table**: Include a table explaining Impact/Effort/Confidence choices per backlog item.

#### Step 5: Roadmap Update

Read `wiki/product/backlog.md`. Update `ZEN_FEATURES` JS object in roadmap HTML. Preserve `SP_FEATURES` and `L3_ITEMS`.

#### Step 6: Cross-link & Log

Update `wiki/index.md`, `wiki/log.md`, cross-links from insights/metrics.

### Slack Ingestion Workflow

**Pipeline**: `raw/slack/*.md` → extract decisions, constraints, action items → `wiki/product/decisions/`, `wiki/modules/`, `wiki/product/backlog.md`

Slack conversations are saved manually as structured markdown with frontmatter. Unlike Zendesk (JSON requiring parsing), Slack files are already human-readable markdown with timestamped dialogue.

**Critical rule**: `raw/slack/` is immutable — read only, never modify.

#### Step 1: Read & Parse Frontmatter

For each file in `raw/slack/`:

1. **Read frontmatter**: Extract `date`, `channel`, `participants`, `related`, `topic`
2. **Resolve cross-references** from the `related` field:
   - `zendesk: <ticketId>` → check if `wiki/zendesk/summaries/<ticketId>.md` exists
   - `zi: <ZI-ID>` → locate in daily index `wiki/zendesk/YYYY-MM-DD.md`
   - `trello: <url>` → note for cross-linking in output pages
3. **Read conversation body**: Identify speakers, timestamps, and message content

#### Step 2: Extract Artifacts

Scan the conversation for three artifact types:

**Decisions** — statements where the team commits to an approach:
- Look for: definitive statements, "we will", "let's go with", "the plan is", conclusions after debate
- Each decision becomes a candidate for `wiki/product/decisions/YYYY-MM-DD-<slug>.md`

**Constraints** — external limitations or dependencies discovered:
- Look for: "we cannot", "requires", "blocked by", third-party requirements, API limitations, partnership dependencies
- Constraints update the relevant `wiki/modules/` page (add to Known Issues / Tech Debt or a new Constraints section)

**Action items** — tasks assigned to specific people:
- Look for: "@person will", "next step is", "I will", explicit commitments with owners
- Action items become candidates for `wiki/product/backlog.md` entries

#### Step 3: Create/Update Wiki Pages

**Decision records** (if decisions were extracted):
- Create `wiki/product/decisions/YYYY-MM-DD-<slug>.md` using the Decision Record Template
- In the `## Signals` section, link to the Slack source: `Slack: raw/slack/YYYY-MM-DD-<slug>.md`
- Cross-link any referenced Zendesk tickets: `Zendesk: [#<ticketId>](../../zendesk/summaries/<ticketId>.md)` (ZI-XXX)
- Cross-link any referenced Trello cards

**Module page updates** (if constraints were extracted):
- Identify the relevant module page under `wiki/modules/`
- Add constraints to the "Known Issues / Tech Debt" section with source citation
- Add to Dependencies section if new external dependencies were discovered

**Backlog updates** (if action items were extracted):
- Add new items to `wiki/product/backlog.md`
- Score using the existing formula: `(Impact × Confidence) / Effort`
- Link back to the Slack source file in the Key Sources column

#### Step 4: Cross-link & Log

1. **Update `wiki/index.md`** if new decision records were created
2. **Update cross-references**:
   - From new decision records → referenced Zendesk summaries, module pages, Trello cards
   - From updated module pages → the Slack source and any referenced tickets
   - From backlog items → the Slack source
3. **Log** in `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD HH:MM] slack-ingest | <Topic from frontmatter>
   - Source: `raw/slack/YYYY-MM-DD-<slug>.md`
   - Created: `product/decisions/YYYY-MM-DD-<slug>.md` (if applicable)
   - Updated: `modules/<domain>/<module>.md` (if applicable)
   - Updated: `product/backlog.md` (if applicable)
   - Cross-refs: Zendesk #<ticketId>, ZI-<id>, Trello <card>
   - Summary: <what was extracted — N decisions, N constraints, N action items>
   ```

### Triage Workflow (Delta)

When new tickets arrive in `raw/zendesk/` (incremental sync):

1. **Detect delta**:
   ```bash
   git diff <last_git_reference>..HEAD --name-only -- raw/zendesk/
   ```
2. **Run Steps 1-2 of the pipeline** for only the new/changed tickets
3. **Update the daily index** — add new ZI issues, increment counts
4. **Re-cluster backlog** if new issues change a cluster's scoring
5. **Update `git_reference`** in all modified pages
6. **Log** the triage in `wiki/log.md`

### Feature Story Workflow

When the user says "create feature story for X":

1. **Gather signals**:
   - Read relevant wiki module pages
   - Read related Zendesk **summaries** from `wiki/zendesk/summaries/*.md` (search by feature area tag in Open Issues sections)
   - Read the daily index `wiki/zendesk/YYYY-MM-DD.md` for ZI issue IDs in the relevant feature area
   - Read related Slack conversations from `raw/slack/` (search by `related` frontmatter matching the feature area's Zendesk tickets or ZI IDs, or by `topic` keyword)
   - Read test coverage from features.md
   - Read regression scenarios from the sheet (if applicable)
2. **Create `product/features/<slug>.md`** using the Feature Story Template
3. **Write user stories** with acceptance criteria:
   - Map regression scenarios from the spreadsheet to stories
   - Link ZI issues and ticket summaries as evidence
4. **Cross-link**:
   - Link to wiki module pages (implementation details)
   - Link to Zendesk summaries (customer evidence): `wiki/zendesk/summaries/<ticketId>.md`
   - Link to regression test rows (manual test scenarios)
   - Link to features.md (automation status)
   - Add to backlog.md if not already there
5. **Update `git_reference`** to current HEAD

### Metrics Refresh Workflow

When the user says "refresh metrics":

1. **Detect delta** via git diff on `wiki/zendesk/summaries/` (NOT raw/zendesk/)
2. **Read new/changed ticket summaries**, group by product and feature area
3. **Check for new Slack conversations** via `git diff` on `raw/slack/`:
   - Extract any decisions or constraints that affect feature health
   - Note action items that may indicate upcoming work
4. **Calculate per-feature metrics**:
   - Ticket volume (total, open, pending, solved)
   - Trend (↑ increasing, → stable, ↓ decreasing) — compare to previous count
   - Top issue (most common subject theme)
5. **Cross-reference with automation data** from `features.md`:
   - Automation confidence per feature
   - Regression coverage per feature
6. **Compute Customer Pain Index**: `(ticket_volume × severity_weight) / automation_confidence`
7. **Compute Feature Health**: 🟢 Healthy / 🟡 Watch / 🔴 At Risk based on composite score
8. **Update `product/metrics.md`** with refreshed data
9. **Update `git_reference`** to current HEAD

### Release Workflow

When the user says "draft release notes for X":

1. Check which backlog items moved to "shipped"
2. Pull metrics before/after from metrics.md history (git blame or previous values)
3. Link to feature stories and decisions that drove the release
4. Create `product/releases/YYYY-MM-DD.md`

### Cross-Linking Rules

Every product page must link in three directions:

- **Upstream** (raw sources): Zendesk ticket IDs, regression matrix rows, code file paths, Slack conversation files
- **Lateral** (wiki): Related features, decisions, module pages, features.md sections
- **Downstream** (outputs): Backlog items, releases, metrics affected

### Feature Story Template

```markdown
---
title: <Feature Name>
category: product-feature
domain: <orders|shipping|etc.>
sources: [zendesk, regression-scenarios, storepep-react, mcsl-test-automation]
status: <proposed|accepted|in-progress|shipped>
last_updated: YYYY-MM-DD
git_reference: <commit hash>
---

# <Feature Name>

## Problem Statement

What problem does this solve? Who experiences it? How do we know?
- **Evidence**: [Ticket #XXXXX](../../zendesk/summaries/XXXXX.md) (ZI-001, ZI-002), ...
- **Affected users**: X customers reported this
- **Impact**: Revenue / reliability / UX

## User Stories

### Story 1: As a [role], I want [goal], so that [benefit]

**Acceptance Criteria**:
- [ ] Given [context], when [action], then [outcome]

**Regression Scenarios** (from regression matrix):
- Sheet row/scenario → maps to this story

### Story 2: ...

## Cross-Links

| Type | Link | Relationship |
|------|------|-------------|
| Wiki Module | [Module](../../modules/...) | Implementation details |
| Test Coverage | [Features](../../features.md#section) | Automation status |
| Zendesk Summary | [#XXXXX](../../zendesk/summaries/XXXXX.md) | Customer report (structured) |
| ZI Issues | ZI-001, ZI-002 | Open issues from daily index |
| Regression | Sheet rows | Manual test scenarios |
| Backlog | [Item](../backlog.md) | Prioritization |
| Decision | [Record](../decisions/...) | Why this approach |

## Customer Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| Related tickets (30d) | X | ↑/→/↓ |
| Automation confidence | 🟠 X% | |
| Regression coverage | X% | |

## Acceptance Sign-off

| Criteria | Status | Verified By |
|----------|--------|------------|
| All stories implemented | ⬜ | |
| Regression scenarios pass | ⬜ | |
| No open P1/P2 tickets | ⬜ | |
| Automation confidence >= 70% | ⬜ | |
```

### Decision Record Template

```markdown
---
title: "<Decision Title>"
category: product-decision
status: <proposed|accepted|superseded>
date: YYYY-MM-DD
git_reference: <commit hash>
---

# <Decision Title>

## Context
What prompted this decision?

## Decision
What did we decide?

## Alternatives Considered
What else was on the table?

## Signals
- Zendesk: [ticket links]
- Test gaps: [coverage data]
- Code complexity: [hotspot data]

## Consequences
What changes as a result?

## Related
- Feature: [link]
- Backlog: [link]
- Module: [link]
```

### Release Notes Template

```markdown
---
title: "Release YYYY-MM-DD"
category: product-release
git_reference: <commit hash>
---

# Release YYYY-MM-DD

## Features Shipped
| Feature | Stories Completed | Acceptance Met |
|---------|-----------------|----------------|

## Metrics Delta
| Feature | Tickets Before | Tickets After | Automation Before | Automation After |
|---------|---------------|---------------|------------------|-----------------|

## Decisions Referenced
- [Decision](../decisions/...)
```

## Index Format

`wiki/index.md` is organized by category:

```markdown
# StorePep KB Index

Last updated: YYYY-MM-DD

## Architecture
- [Overview](architecture/overview.md) - High-level system architecture and component interaction
- [Frontend Architecture](architecture/frontend-architecture.md) - React, Redux, Material-UI setup
- ...

## Modules

### Orders
- [Order Processing Service](modules/orders/order-processing-service.md) - Core order lifecycle management
- ...

### Shipping
- [Label Generation](modules/shipping/label-generation.md) - Multi-carrier label creation
- ...

## Patterns
- [Redux Patterns](patterns/redux-patterns.md) - Action/reducer conventions used throughout
- ...

## Operations
- [Local Setup](operations/local-setup.md) - Development environment configuration
- ...

---
Total pages: <count>
```

## Log Format

`wiki/log.md` is append-only, chronological:

```markdown
# StorePep KB Activity Log

## [2026-04-07 14:30] ingest | Architecture Bootstrap
- Created: `architecture/overview.md`
- Created: `architecture/frontend-architecture.md`
- Created: `architecture/backend-architecture.md`
- Created: `architecture/technology-stack.md`
- Git reference: abc123def
- Summary: Initial architecture documentation covering system overview, frontend/backend structure, and tech stack

## [2026-04-07 15:45] ingest | Order Management System
- Created: `modules/orders/order-processing-service.md`
- Created: `modules/orders/order-api.md`
- Created: `modules/orders/order-model.md`
- Updated: `architecture/data-flow.md`
- Git reference: abc123def
- Summary: Comprehensive documentation of order management - routes (82 endpoints), models, service layer, and frontend components

## [2026-04-07 16:00] query | How does subscription validation work?
- Read: `modules/subscriptions/subscription-validation.md`
- Result: Answered with citation to middleware stack
- No pages created

## [2026-04-08 10:00] lint | Wiki health check
- Flagged 3 pages as potentially stale
- Identified 2 orphan pages
- Suggested 5 new topics to document
```

## Conventions

### Code References
- Always use `file:line` format: `server/src/routes/orders.js:1234`
- For ranges: `server/src/routes/orders.js:100-150`
- Include git commit hash when available

### Git Integration
- When ingesting from a git-submodule source, check its current commit: `cd raw/<source-name> && git rev-parse HEAD`
- Store in page frontmatter: `git_reference: abc123def`
- For non-git sources (sheets, webhook JSON), use `git_reference: "current"` or the wiki repo's own commit hash
- Always record which source(s) a page draws from in the `sources:` frontmatter field

### Status Tags
- `complete`: Comprehensive documentation, up-to-date
- `partial`: Basic info present, needs expansion
- `needs-update`: Known to be stale or incomplete

### Cross-references
- Link liberally between pages
- Maintain bidirectional links (Dependencies ↔ Referenced By)
- Link to pattern/architecture pages from module pages

### Naming Conventions
- Files: lowercase-with-hyphens.md
- Titles: Proper Case With Spaces
- Domains: lowercase single words (orders, shipping, products)

### Test Coverage Conventions
- **Test file references**: Use relative path from test root: `orderGrid/actionMenu/cancelShipment.spec.ts`
- **Feature descriptions**: User-facing, action-oriented, plain English, one line
- **Status badges**:
  - ✅ Automated & Passing
  - 🔴 Manual Test Only
  - ⚠️ Automated but Flaky
  - ❌ Automated but Failing
  - 🚧 Automation In Progress
- **Automation confidence scores**:
  - 🟢 High (95-100%) - Stable, comprehensive automation
  - 🟡 Medium (70-94%) - Mostly automated, some manual verification needed
  - 🟠 Low (40-69%) - Partial automation, significant manual testing required
  - 🔴 None (0-39%) - Primarily manual testing
- **Coverage percentages**: Round to nearest whole number
- **Test suite location**: Always provide path to test directory
- **Regression vs Automated**: Separate sections for regression test suite vs automated Playwright tests
- **Link to features.md**: Always include in Test Coverage section

## Special Considerations for StorePep

### Domain Organization
Organize modules by these primary domains:
- **orders**: Order processing, batch operations, automation
- **shipping**: Labels, manifests, carriers, pickups
- **products**: Product management, imports, sync
- **integrations**: External APIs (stores, carriers, payments)
- **subscriptions**: Payment, subscription management
- **workflows**: Automation rules, workflow engine
- **tracking**: Shipment tracking
- **admin**: StorePep team features, support tools

### Key Areas to Document
- Multi-carrier integration patterns (15+ carriers)
- Store integration architecture (Shopify, WooCommerce, Magento, etc.)
- Redux state management patterns (87 actions, 26 reducers)
- Feature toggle system
- Access control (ACL) system
- Database migration strategy (106+ migrations)
- Real-time updates (Socket.io)
- **Test coverage**: Playwright E2E tests from `raw/mcsl-test-automation`

### Complexity Markers
Note when documenting:
- Large files (>1000 lines): `orders.js` is 2139 lines
- Complex service classes: OrderProcessingService, ProductImportService
- Multi-file features that span client/server
- External API integration points

## User Interaction

- **Always discuss before creating pages**: Show the user key findings, ask what to emphasize
- **Ask clarifying questions**: If unclear what to prioritize or how to structure
- **Offer choices**: "Should I create separate pages for each carrier integration, or one unified page?"
- **File valuable queries**: After answering a complex question, ask: "Should I file this as a wiki page?"

## Tools & Workflows

### Search
At small scale (<100 pages), the index.md file is sufficient for finding relevant pages. As the wiki grows, consider:
- Using Grep to search across wiki markdown files
- Building a simple search script if needed
- The user may later add tools like `qmd` for advanced search

### Visualization
- Obsidian graph view (user's tool) shows page connections
- Consider generating a dependencies graph page if the wiki gets large

### Version Control
- The wiki is just markdown files - can be committed to git
- User may want to track wiki evolution alongside codebase evolution

---

## Examples

### Example 1: Ingesting a Module with Test Coverage

**User Request**: "Ingest the order bulk actions module"

**Workflow**:
1. **Read code**: Use Glob/Grep to find `bulkactionHelper.js` and related files
2. **Analyze tests**: Use Task tool with Explore agent to find tests in `raw/mcsl-test-automation/tests/orderGrid/actionMenu/`
3. **Discuss findings**:
   - "Found 40+ bulk actions in `bulkactionHelper.js` (2500+ lines)"
   - "Found 12 Playwright tests covering actions: cancel shipment, change carrier, create return label, etc."
   - "Coverage: 30% (12/40+ actions tested)"
4. **Create module page**: `modules/orders/order-bulk-actions.md` with Test Coverage section
5. **Update features.md**: Add 12 tested features under "Order Management Actions"
6. **Cross-link**: Link from order-lifecycle.md, link to carrier-configuration.md
7. **Update index**: Add to Orders section
8. **Log**: Document ingestion with test coverage stats

### Example 2: Comprehensive Test Coverage Analysis

**User Request**: "Generate features.md from regression tests and Playwright automation"

**Workflow**:
1. **Read regression scenarios**:
   ```bash
   # Read raw/sheets/regression-scenarios.csv
   # Output: 150 total regression test scenarios
   ```

2. **Discover Playwright tests**:
   ```bash
   find raw/mcsl-test-automation/tests -name "*.spec.ts" | wc -l
   # Output: 58 automated test files
   ```

3. **Analyze both sources**: Use Task tool with Explore agent:
   ```
   Analyze:
   - 150 regression scenarios from CSV
   - 58 Playwright test files
   Extract and map:
   - User-facing feature descriptions
   - Which regression tests have automation
   - Automation confidence scores
   - Gaps (regression without automation, automation without regression)
   ```

4. **Create features.md**:
   - Organize by category (Automation, Orders, Shipping, etc.)
   - Table format: Regression # | Feature | Manual | Automated | Confidence | Test File
   - Total: 150 regression tests, 95 distinct automated features
   - Automation coverage: 63% (95/150)
   - Automation gaps: 55 regression tests without automation
   - Orphan automation: 12 Playwright tests not mapped to regression

5. **Update module pages**: Add Test Coverage sections showing both regression and automation:
   - `order-bulk-actions.md` - 18 regression tests, 12 automated (67%)
   - `label-generation.md` - 32 regression tests, 20 automated (63%)
   - `automation-actions.md` - 15 regression tests, 11 automated (73%)
   - `carrier-configuration.md` - 8 regression tests, 3 automated (38%)
   - `shipment-tracking.md` - 5 regression tests, 1 automated (20%)
   - `platform-connectors.md` - 10 regression tests, 5 automated (50%)

6. **Update index**: Add features.md link with coverage stats

7. **Log**: Comprehensive test coverage activity entry with regression + automation mapping

### Example 3: Feature Description Best Practices

**Test File**: `automationRules/automationCriteria/totalWeightRange.spec.ts`

**Code Analysis**:
```typescript
test('should create automation rule based on total weight range', async ({ page }) => {
  // Test creates rule: if total weight is 5-10 lbs, use FedEx Ground
  await page.fill('[data-testid="min-weight"]', '5');
  await page.fill('[data-testid="max-weight"]', '10');
  await page.selectOption('[data-testid="carrier"]', 'FedEx Ground');
  await page.click('[data-testid="save-rule"]');
});
```

**Feature Extraction**:
- ✅ **Good**: "Create automation rules based on total weight range"
- ✅ **Good**: "Automatically select carrier based on shipment weight thresholds"
- ❌ **Bad**: "Weight range automation test works"
- ❌ **Bad**: "Test validates AutomationRulesManager.addWeightRangeCondition()"

**Rationale**: Good descriptions focus on user value, not implementation

### Example 4: Coverage Percentage Calculation

**Module**: Label Generation

**Code Analysis**:
- 7 label generation flows identified in code
- 6 packaging types supported
- 3 special services available
- 3 touchless SLGP workflows
- 1 document upload feature

**Total features**: 20

**Test Analysis**:
- Grid generation: 3 tests ✅
- Batch operations: 2 tests ✅
- Packaging: 6 tests ✅
- Special services: 3 tests ✅
- Touchless SLGP: 3 tests ✅
- Document upload: 1 test ✅
- Summary generation: 1 test ✅
- Return labels: 1 test ✅

**Total tests**: 20

**Coverage**: 20/20 = 100%

**Documentation**:
```markdown
**Test Coverage**: 20/20 label generation scenarios tested (100% coverage)
```

## Getting Started

On first use:
1. Bootstrap the architecture documentation (overview, frontend, backend, tech stack)
2. Create index.md and log.md
3. Ask user which domain to ingest first (orders, shipping, products, etc.)
4. Iterate: ingest → discuss → document → cross-link → log

**With test coverage**:
1. After initial ingestion, ask: "Should I analyze test coverage for this module?"
2. If yes, find relevant tests in `raw/mcsl-test-automation/tests/`
3. Extract features from tests
4. Add Test Coverage section to module page
5. Update or create features.md with tested features
6. Update index with test stats
