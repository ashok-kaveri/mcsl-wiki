# StorePep Knowledge Base

## Purpose

LLM-maintained knowledge base for the StorePep product ecosystem. A living wiki that stays current with the code, tracks architectural decisions, and aggregates signals from multiple sources (code, tests, support tickets, regression plans, Slack).

**Key principle**: The wiki is persistent and compounding. You (Claude) write and maintain all wiki pages. The user curates what to ingest, asks questions, and directs analysis. Every ingested source and answered question enriches the wiki.

## Architecture

Four layers:

1. **Raw** (`raw/`) — All input sources. Immutable from the wiki's perspective. Read from, never modify. Declared in `raw/sources.yaml`.
2. **Wiki** (`wiki/`) — LLM-generated markdown. You own it entirely.
3. **Schema** (`CLAUDE.md` + `workflows/` + `templates/`) — Instructions for maintaining the wiki.
4. **Source registry** (`raw/sources.yaml`) — Single source of truth for where raw data lives. Always read this when resolving paths.

**Immutability rule**: Never modify anything in `raw/`. Writes to `raw/` come only from external processes (git pulls, webhooks, manual exports).

## Source Registry (`raw/sources.yaml`)

### Source Types

| Type | How it gets into `raw/` | Example |
|------|------------------------|---------|
| `git-submodule` | `git submodule add <repo> raw/<name>` | Codebase, test suite |
| `webhook-json` | External webhook writes `{id}.json` files | Zendesk tickets |
| `google-sheet` | Manual CSV export or sync script | Regression scenarios |
| `manual` | User places files directly | Slack conversations, specs |

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

  zendesk:
    type: webhook-json
    path: raw/zendesk
    pattern: "{ticketId}.json"
    description: "Customer support tickets"
    workflow: workflows/zendesk-pipeline.md

  regression-scenarios:
    type: google-sheet
    path: raw/sheets/regression-scenarios.csv
    sync: manual
    description: "Master regression test plan"

  slack:
    type: manual
    path: raw/slack
    pattern: "YYYY-MM-DD-<slug>.md"
    description: "Internal Slack conversations"
    workflow: workflows/slack-ingestion.md
```

### Adding a New Source

1. Choose a type from the table above
2. Place source in `raw/` (submodule, webhook, files)
3. Register in `raw/sources.yaml` with type, path, description
4. If it needs an ingestion workflow, add one under `workflows/`
5. Commit to the wiki repo

## Directory Structure

```
mcsl-wiki/
├── CLAUDE.md                      # This file (always loaded)
├── workflows/                     # Workflow files (loaded on demand)
├── templates/                     # Page templates (loaded when creating pages)
├── raw/                           # ALL input sources (immutable)
│   ├── sources.yaml
│   ├── storepep-react/            # git submodule → main codebase
│   ├── mcsl-test-automation/      # git submodule → Playwright tests
│   ├── zendesk/shopify/           # Zendesk tickets by product
│   ├── sheets/                    # CSV exports
│   └── slack/                     # Slack conversations
└── wiki/
    ├── architecture/              # System-level docs
    ├── modules/<domain>/          # Feature/domain pages
    ├── patterns/                  # Cross-cutting concepts
    ├── operations/                # Dev/ops guides
    ├── product/                   # Product management layer
    │   ├── backlog.md
    │   ├── insights.md
    │   ├── metrics.md
    │   ├── features/<slug>.md
    │   ├── decisions/YYYY-MM-DD-<slug>.md
    │   └── releases/YYYY-MM-DD.md
    ├── zendesk/
    │   ├── summaries/<ticketId>.md
    │   └── YYYY-MM-DD.md          # Daily issue index
    ├── features.md                # User-facing features + test coverage
    ├── index.md                   # Catalog of all pages
    └── log.md                     # Chronological activity log
```

## Conventions

### Code References
- Use `file:line` format: `server/src/routes/orders.js:1234`
- Ranges: `server/src/routes/orders.js:100-150`
- Include git commit hash when available

### Git Integration
- Ingesting from a git-submodule: record its commit with `cd raw/<source> && git rev-parse HEAD`
- Store in page frontmatter: `git_reference: abc123def`
- Non-git sources: use `git_reference: "current"` or the wiki repo's commit hash
- Always record sources in the `sources:` frontmatter field (keys from `sources.yaml`)

### Status Tags
- `complete` — comprehensive, up-to-date
- `partial` — basic info, needs expansion
- `needs-update` — known stale/incomplete

### Naming
- Files: `lowercase-with-hyphens.md`
- Titles: Proper Case With Spaces
- Domains: lowercase single words (orders, shipping, products)

### Cross-references
- Link liberally between pages
- Maintain bidirectional links (Dependencies ↔ Referenced By)
- Link module pages to pattern/architecture pages

### Test Coverage Badges
Status:
- ✅ Automated & Passing
- 🔴 Manual Only
- ⚠️ Automated but Flaky
- ❌ Automated but Failing
- 🚧 Automation In Progress

Automation confidence:
- 🟢 High (95-100%) — Stable, comprehensive, CI
- 🟡 Medium (70-94%) — Automated, some manual verification
- 🟠 Low (40-69%) — Partial automation
- 🔴 None (0-39%) — Primarily manual

### Feature Area Tags (Zendesk + product pages)
`onboarding`, `carrier-config`, `carrier-migration`, `label-generation`, `rate-shopping`, `tracking`, `returns`, `international`, `order-management`, `product-management`, `feature-request`, `other`

### Page Categories (frontmatter)
`architecture`, `module`, `pattern`, `operation`, `product`, `product-feature`, `product-decision`, `product-release`

## StorePep Domain Notes

### Primary Domains
- **orders** — order processing, batch operations, automation
- **shipping** — labels, manifests, carriers, pickups
- **products** — product management, imports, sync
- **integrations** — external APIs (stores, carriers, payments)
- **subscriptions** — payment, subscription management
- **workflows** — automation rules, workflow engine
- **tracking** — shipment tracking
- **admin** — StorePep team features, support tools

### Key Areas to Document
- Multi-carrier integration patterns (15+ carriers)
- Store integration architecture (Shopify, WooCommerce, Magento, etc.)
- Redux state management (87 actions, 26 reducers)
- Feature toggle system
- Access control (ACL) system
- Database migrations (106+)
- Real-time updates (Socket.io)
- Test coverage from `raw/mcsl-test-automation`

### Complexity Markers
Flag when documenting:
- Large files (>1000 lines): `orders.js` is 2139 lines
- Complex service classes: OrderProcessingService, ProductImportService
- Multi-file features spanning client/server
- External API integration points

## Cross-Linking Rules

Every product page must link in three directions:
- **Upstream** (raw): Zendesk tickets, regression rows, code paths, Slack files
- **Lateral** (wiki): related features, decisions, modules, features.md sections
- **Downstream** (outputs): backlog items, releases, affected metrics

## Delta-Aware Resync

All product pages use git-based delta detection. Each page's frontmatter records `git_reference` — the wiki repo commit at last sync.

```bash
# What changed since last sync for a given page:
git diff <git_reference>..HEAD --name-only -- raw/zendesk/shopify/
git diff <git_reference>..HEAD --name-only -- raw/sheets/
git diff <git_reference>..HEAD --name-only -- raw/slack/
git diff <git_reference>..HEAD -- raw/storepep-react raw/mcsl-test-automation
```

Process only the delta. Update `git_reference` to current HEAD after processing.

## User Interaction Principles

- **Discuss before creating pages** — share findings, ask what to emphasize
- **Ask clarifying questions** when structure or priority is unclear
- **Offer choices** — "Separate pages per carrier, or one unified page?"
- **File valuable queries** — after a substantive answer, ask whether to file as a wiki page

## Workflows

Load the relevant workflow file when a trigger matches:

- @workflows/ingestion.md — "Ingest X", "document this module"
- @workflows/query.md — Questions about the codebase
- @workflows/lint.md — "Lint the wiki", "health-check"
- @workflows/test-coverage.md — "Generate features.md", test coverage updates
- @workflows/zendesk-pipeline.md — `/zendesk-summarize`, ticket triage
- @workflows/slack-ingestion.md — New files in `raw/slack/`
- @workflows/product-management.md — Feature stories, metrics refresh, releases, delta resync
- @workflows/examples.md — Worked examples (ingestion, test coverage, feature extraction)

## Templates

Load when creating that page type:

- @templates/page.md — Standard wiki page (module, architecture, pattern, operation)
- @templates/feature-story.md — Product feature story
- @templates/decision-record.md — Product decision record
- @templates/release-notes.md — Release notes

## Index & Log Formats

`wiki/index.md` is organized by category (Architecture, Modules by domain, Patterns, Operations, Product, Features & Testing). Each entry is one line with a brief summary. Footer shows total page count and test coverage stats.

`wiki/log.md` is append-only, chronological. Entry format:

```markdown
## [YYYY-MM-DD HH:MM] <action> | <Topic>
- Created: `path/to/page.md`
- Updated: `path/to/other.md`
- Git reference: <commit-hash>
- Summary: Brief description
```

Actions: `ingest`, `query`, `lint`, `test-coverage`, `zendesk-summarize`, `slack-ingest`, `triage`, `feature-story`, `metrics-refresh`, `release`.

## Getting Started

On first use:
1. Bootstrap architecture docs (overview, frontend, backend, tech stack)
2. Create `wiki/index.md` and `wiki/log.md`
3. Ask user which domain to ingest first
4. Iterate: ingest → discuss → document → cross-link → log
