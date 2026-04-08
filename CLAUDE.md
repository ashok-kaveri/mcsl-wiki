# StorePep React Knowledge Base - Schema & Workflows

## Purpose

This is an **LLM-maintained knowledge base** for the StorePep React codebase (`../storepep-react/storepepSAAS`). The goal is to create a living, evolving wiki that serves as an active development companion - documentation that stays current as the code evolves, tracks architectural decisions, and maintains dependency maps.

**Key Principle**: The wiki is a persistent, compounding artifact. You (Claude) write and maintain all wiki pages. The user curates what to ingest, asks questions, and directs the analysis. The wiki keeps getting richer with every source ingested and every question asked.

## Architecture

There are three layers:

1. **Raw Source** (`../storepep-react/storepepSAAS`) - The actual codebase. Immutable from the wiki's perspective. You read from it but never modify it.

2. **The Wiki** (`wiki/`) - LLM-generated markdown files. You own this layer entirely. You create pages, update them when ingesting new code, maintain cross-references, and keep everything consistent.

3. **This Schema** (`CLAUDE.md`) - Instructions for how to maintain the wiki. Workflows, templates, conventions.

## Directory Structure

```
mcsl-wiki/
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

**Test Suite Location**: `mcsl-test-automation/tests/<domain>/`

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

When the user asks to document test coverage (e.g., "Extract features from Playwright tests and update wiki"):

### 1. **Analyze Test Files**

**Test Suite Location**: `../mcsl-test-automation/tests/`

**Discovery**:
```bash
find ../mcsl-test-automation/tests -name "*.spec.ts" -o -name "*.spec.js"
```

**For each test file**:
- Read the test file content
- Understand what feature/functionality is being tested
- Extract user-facing feature description (plain English, one line)
- Note the test file path
- Identify which wiki module it relates to

**Use Task tool with Explore agent** for comprehensive test analysis across all files.

### 2. **Create/Update features.md**

**Location**: `wiki/features.md`

**Structure**:
```markdown
# StorePep Features

**Test Coverage**: X automated Playwright tests covering Y distinct features
**Last Updated**: YYYY-MM-DD
**Test Suite**: mcsl-test-automation

## <Category Name> (e.g., Automation Rules)

- Feature description in plain English
- Another feature description

**Test Coverage**: X/Y tests passing
**Documentation**: [Module Page](modules/<domain>/<module>.md)

---

## Test Coverage by Module

| Module | Features Tested | Test Files | Coverage |
|--------|----------------|------------|----------|
| Module Name | X | Y | Z% |

---

## Test Organization

Tests are organized in:
```
mcsl-test-automation/tests/
├── <category>/           (X tests)
│   └── <subcategory>/
└── ...
```

---

## Related Pages

- [Module Page](modules/<domain>/<module>.md)
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

**Test Suite Location**: `mcsl-test-automation/tests/<category>/`

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

**When tests change**:
1. User notifies of new/changed tests
2. Re-analyze affected test files
3. Update features.md with new features
4. Update affected module pages
5. Update coverage statistics
6. Log the update

**Coverage Health Checks**:
- Flag modules with <50% test coverage
- Identify critical workflows without tests
- Suggest high-value tests to write

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
- When ingesting, check current commit: `cd ../storepep-react/storepepSAAS && git rev-parse HEAD`
- Store in page frontmatter: `git_reference: abc123def`
- If repo is not in git or user specifies a snapshot, use `git_reference: "current"`

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
- **Test coverage**: Playwright E2E tests from `mcsl-test-automation`

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
2. **Analyze tests**: Use Task tool with Explore agent to find tests in `mcsl-test-automation/tests/orderGrid/actionMenu/`
3. **Discuss findings**:
   - "Found 40+ bulk actions in `bulkactionHelper.js` (2500+ lines)"
   - "Found 12 Playwright tests covering actions: cancel shipment, change carrier, create return label, etc."
   - "Coverage: 30% (12/40+ actions tested)"
4. **Create module page**: `modules/orders/order-bulk-actions.md` with Test Coverage section
5. **Update features.md**: Add 12 tested features under "Order Management Actions"
6. **Cross-link**: Link from order-lifecycle.md, link to carrier-configuration.md
7. **Update index**: Add to Orders section
8. **Log**: Document ingestion with test coverage stats

### Example 2: Test Coverage Analysis Request

**User Request**: "Extract features from Playwright tests and update wiki"

**Workflow**:
1. **Discover tests**:
   ```bash
   find ../mcsl-test-automation/tests -name "*.spec.ts" | wc -l
   # Output: 58 test files
   ```

2. **Analyze all tests**: Use Task tool with Explore agent:
   ```
   Analyze all 58 test files and extract:
   - User-facing feature descriptions
   - Test file paths
   - Module mappings
   ```

3. **Create features.md**:
   - Organize by category (Automation, Orders, Shipping, etc.)
   - List 95 distinct features
   - Add test coverage summary table

4. **Update module pages**: Add Test Coverage sections to:
   - `order-bulk-actions.md` - 12 tests
   - `label-generation.md` - 20 tests
   - `automation-actions.md` - 11 tests
   - `carrier-configuration.md` - 3 tests
   - `shipment-tracking.md` - 1 test
   - `platform-connectors.md` - 5 tests

5. **Update index**: Add features.md link, update stats

6. **Log**: Comprehensive test coverage activity entry

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
2. If yes, find relevant tests in `mcsl-test-automation/tests/`
3. Extract features from tests
4. Add Test Coverage section to module page
5. Update or create features.md with tested features
6. Update index with test stats
