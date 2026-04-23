# Test Coverage Workflow

**Trigger**: "Generate features.md", "update test coverage", "map regression to automation"

**Goal**: Integrate two sources — regression scenarios (what SHOULD be tested) and Playwright tests (what IS tested) — to give complete coverage visibility and identify automation gaps.

## Sources

| Source | Path | Contains |
|--------|------|----------|
| Regression | `raw/sheets/regression-scenarios.csv` | Complete feature inventory (manual + automated) |
| Automated | `raw/mcsl-test-automation/tests/**/*.spec.ts` | Playwright E2E tests |

## Steps

### 1. Analyze regression scenarios
Read the CSV. For each row extract: test ID, feature description, category/domain, manual status. Group by category.

### 2. Analyze Playwright tests
```bash
find raw/mcsl-test-automation/tests -name "*.spec.ts"
```
For each file: read content, understand what's tested, extract a user-facing description (one line, plain English), note path, identify corresponding wiki module.

Use Task tool with Explore agent for comprehensive analysis across all files.

### 3. Map regression → automation
For each regression test:
- Is there a Playwright test covering it? Match by description/intent/ID.
- Assign an automation confidence score (see `CLAUDE.md` — Conventions → Test Coverage Badges)
- Flag regression gaps (regression without automation)
- Flag orphan automation (Playwright tests not in regression)

### 4. Create/update `wiki/features.md`

Canonical structure:

```markdown
# StorePep Features

**Regression Test Suite**: X total scenarios
**Automated Tests**: Y Playwright tests
**Automation Coverage**: Y/X (Z%)
**Last Updated**: YYYY-MM-DD
**Sources**: regression-scenarios, mcsl-test-automation

---

## <Category> (e.g., Automation Rules)

### Regression Test Suite

| # | Feature | Manual | Automated | Confidence | Test File | Wiki Reference |
|---|---------|--------|-----------|------------|-----------|----------------|
| 1 | Feature from sheet | 🔴 | ✅ | 🟢 95% | `path/to/test.spec.ts` | [Module](modules/path.md) |
| 2 | Another feature | ✅ | 🔴 | 🔴 0% | — | [Module](modules/path.md) |

**Automation Summary**:
- Total regression tests: X
- Automated: Y (Z%)
- High confidence: N  |  Medium: M  |  Low/none: L

**Automated Test Files**:
- `automationRules/totalWeightRange.spec.ts` — covers regression #1, #3, #5

**Automation Gaps** (regression without automation):
- 🔴 Regression #X: description — [Module](modules/path.md)

---

## Test Coverage by Module

| Module | Total Features | Automated | Manual Only | Automation % |
|--------|---------------|-----------|-------------|--------------|
| Automation Rules | X | Y | Z | W% |

## Test Organization

**Regression**: `raw/sheets/regression-scenarios.csv`
**Automated**: `raw/mcsl-test-automation/tests/`

[tree of test directory]

## Related Pages
- [Module](modules/<domain>/<module>.md)
- [Product Backlog](product/backlog.md)
```

### 5. Add "Test Coverage" section to each affected module page

Insert before "Known Issues / Tech Debt":

```markdown
## Test Coverage

**Automated E2E Tests**: X Playwright tests covering <module name>

### Tested Features
| Feature | Test File | Status |
|---------|-----------|--------|
| Feature Name | `category/subcategory/testName.spec.ts` | ✅ Passing |

**Coverage**: X/Y features tested (Z%)

**Tested Scenarios**:
- ✅ Scenario 1
- ✅ Scenario 2

**Untested Scenarios**:
- ❌ Scenario 3

**Test Suite Location**: `raw/mcsl-test-automation/tests/<category>/`
**Documentation**: See [Features List](../../features.md)
```

### 6. Map tests → wiki modules

| Test Path | Wiki Module |
|-----------|-------------|
| `automationRules/` | `modules/automation/` |
| `carrierOtherDetails/` | `modules/shipping/carrier-configuration.md` |
| `orderGrid/actionMenu/` | `modules/orders/order-bulk-actions.md` |
| `orderGrid/labelGenerationFromGrid/` | `modules/shipping/label-generation.md` |
| `orderSummary/` | `modules/orders/order-lifecycle.md` |
| `packagingTypes/` | `modules/shipping/label-generation.md` (packaging) |
| `shopifyUI/` | `modules/stores/platform-connectors.md` |
| `specialServices/` | `modules/shipping/label-generation.md` or `carrier-configuration.md` |
| `trackingFromGrid/` | `modules/shipping/shipment-tracking.md` |

### 7. Update index & log

Index:
```markdown
## Features & Testing
- [Features](features.md) — Complete list of X features with test coverage
**Test Coverage**: Y automated Playwright tests covering Z features
```

Log:
```markdown
## [YYYY-MM-DD HH:MM] test-coverage | <Scope>
- Created/Updated: `features.md`
- Updated: `modules/<domain>/<module>.md` (test coverage section)
- Updated: `index.md`, `log.md`
- Git reference: <commit-hash>
- Summary: Analyzed X test files, Y features extracted, Z% coverage
```

## Feature Description Guidelines

- **User-facing** — what the user can do, not implementation
- **Plain English** — minimal jargon
- **Action-oriented** — start with verbs (Create, Generate, Configure, Process)
- **Specific** — "Generate labels for orders with multiple products," not "Label generation works"
- **One line**

Good: "Create automation rules based on total weight range"
Bad: "Test automation rules" | "OrderProcessingService handles weight-based routing"

## Maintenance

**Regression CSV updated** → re-read CSV, identify new/changed/removed rows, re-map to automation, update features.md and module pages.

**Playwright tests updated** → re-analyze affected files, map new tests to regression, update confidence scores.

**Both changed** → full resync: re-read both, rebuild mapping, regenerate features.md and all module pages.

## Health Checks

- Flag modules with <50% automation
- Identify critical workflows without automation
- Suggest high-value regression tests to automate
- Flag low-confidence automation (<70%) for review
- Identify orphan automation (not mapped to regression)

## Coverage Calculation

- Count distinct features tested
- Count total features in module (from code analysis)
- Percentage: `(tested / total) * 100`, rounded to nearest whole number

## Examples

See @workflows/examples.md — "Comprehensive Test Coverage Analysis", "Feature Description Best Practices", "Coverage Percentage Calculation".
