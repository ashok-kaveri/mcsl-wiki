# Examples

Worked examples for the main workflows. Reference material — load when learning a workflow or when an edge case comes up.

## Example 1: Ingesting a Module with Test Coverage

**User request**: "Ingest the order bulk actions module"

**Workflow**:
1. **Read code**: Glob/Grep to find `bulkactionHelper.js` and related files
2. **Analyze tests**: Task tool with Explore agent for tests in `raw/mcsl-test-automation/tests/orderGrid/actionMenu/`
3. **Discuss findings**:
   - "Found 40+ bulk actions in `bulkactionHelper.js` (2500+ lines)"
   - "Found 12 Playwright tests covering cancel shipment, change carrier, create return label, etc."
   - "Coverage: 30% (12/40+ actions tested)"
4. **Create module page**: `modules/orders/order-bulk-actions.md` with Test Coverage section
5. **Update features.md**: add 12 tested features under "Order Management Actions"
6. **Cross-link**: from `order-lifecycle.md`, to `carrier-configuration.md`
7. **Update index**: add to Orders section
8. **Log**: ingestion entry with coverage stats

## Example 2: Comprehensive Test Coverage Analysis

**User request**: "Generate features.md from regression tests and Playwright automation"

**Workflow**:

1. **Read regression scenarios**:
   ```bash
   # Read raw/sheets/regression-scenarios.csv
   # Output: 150 total scenarios
   ```

2. **Discover Playwright tests**:
   ```bash
   find raw/mcsl-test-automation/tests -name "*.spec.ts" | wc -l
   # Output: 58 test files
   ```

3. **Analyze both sources** with Task / Explore agent:
   - 150 regression scenarios
   - 58 Playwright files
   - Extract user-facing descriptions, map regression → automation, assign confidence, flag gaps

4. **Create features.md**:
   - Organized by category (Automation, Orders, Shipping, etc.)
   - Table: Regression # | Feature | Manual | Automated | Confidence | Test File
   - Totals: 150 regression, 95 automated features, 63% coverage
   - 55 regression tests without automation
   - 12 orphan Playwright tests not mapped to regression

5. **Update module pages** (regression + automation sections):
   - `order-bulk-actions.md` — 18 regression, 12 automated (67%)
   - `label-generation.md` — 32 regression, 20 automated (63%)
   - `automation-actions.md` — 15 regression, 11 automated (73%)
   - `carrier-configuration.md` — 8 regression, 3 automated (38%)
   - `shipment-tracking.md` — 5 regression, 1 automated (20%)
   - `platform-connectors.md` — 10 regression, 5 automated (50%)

6. **Update index**: features.md link with coverage stats

7. **Log**: comprehensive activity entry

## Example 3: Feature Description Best Practices

**Test file**: `automationRules/automationCriteria/totalWeightRange.spec.ts`

**Code**:
```typescript
test('should create automation rule based on total weight range', async ({ page }) => {
  // Creates rule: if total weight is 5-10 lbs, use FedEx Ground
  await page.fill('[data-testid="min-weight"]', '5');
  await page.fill('[data-testid="max-weight"]', '10');
  await page.selectOption('[data-testid="carrier"]', 'FedEx Ground');
  await page.click('[data-testid="save-rule"]');
});
```

**Feature extraction**:
- ✅ Good: "Create automation rules based on total weight range"
- ✅ Good: "Automatically select carrier based on shipment weight thresholds"
- ❌ Bad: "Weight range automation test works" (not specific)
- ❌ Bad: "Test validates AutomationRulesManager.addWeightRangeCondition()" (implementation jargon)

## Example 4: Coverage Percentage Calculation

**Module**: Label Generation

**Code analysis**:
- 7 label generation flows
- 6 packaging types
- 3 special services
- 3 touchless SLGP workflows
- 1 document upload

Total features: **20**

**Test analysis**:
- Grid generation: 3
- Batch operations: 2
- Packaging: 6
- Special services: 3
- Touchless SLGP: 3
- Document upload: 1
- Summary generation: 1
- Return labels: 1

Total tests: **20**

**Coverage**: 20/20 = 100%

**Documentation**:
```markdown
**Test Coverage**: 20/20 label generation scenarios tested (100% coverage)
```
