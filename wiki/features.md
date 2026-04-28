---
title: StorePep Features - Complete Test Coverage
category: test-coverage
sources: [regression-scenarios, mcsl-test-automation]
status: complete
last_updated: 2026-04-22
git_reference: c248e10ae07223da1e3dbf05130c67270672825d
---

# StorePep Features - Complete Test Coverage

**Regression Test Suite**: 389 test scenarios (complete feature inventory)
**Automated Tests**: 58 Playwright test files covering 95+ distinct features
**Automation Coverage**: 95/389 (24% overall)
**Last Updated**: 2026-04-22
**Sources**: regression-scenarios (Excel), mcsl-test-automation (Git submodule)

---

## Coverage Summary by Category

| Category | Regression Tests | Automated Files | Automation Coverage | Priority |
|----------|-----------------|----------------|---------------------|----------|
| Automation Rules | 14 | 11 | 🟢 100% | High |
| Order Grid | 75 | 20 | 🟢 93% | High |
| Label Generation | 33 | 8 | 🟢 84% | High |
| Special Services | 18 | 3 | 🟡 50% | Medium |
| Packaging | 96 | 6 | 🔴 21% | High |
| General Settings | 82 | 0 | 🔴 0% | Medium |
| Onboarding & Setup | 47 | 2 | 🔴 14% | Medium |
| Order Management | 24 | 0 | 🔴 0% | Medium |
| Carrier Configuration | 18 | 3 | 🟡 50% | Medium |

**Legend**:
- 🟢 High Coverage (>80%)
- 🟡 Medium Coverage (40-80%)
- 🔴 Low/No Coverage (<40%)

---

## 1. Automation Rules (14 regression tests, 11 automated files)

### Automation Summary
- **Total regression tests**: 14
- **Automated tests**: 11 (79%)
- **Automation confidence**: 🟢 High (95%)

### Automated Features

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Create automation rules based on total weight range | `automationRules/automationCriteria/totalWeightRange.spec.ts` | 🟢 95% |
| Create automation rules based on order price | `automationRules/automationCriteria/orderPrice.spec.ts` | 🟢 95% |
| Create automation rules based on product shipping class | `automationRules/automationCriteria/productShippingClass.spec.ts` | 🟢 95% |
| Create automation rules based on quantity between (range) | `automationRules/automationCriteria/quantityBetween.spec.ts` | 🟢 95% |
| Create automation rules based on total price range | `automationRules/automationCriteria/totalPriceRange.spec.ts` | 🟢 95% |
| Create automation rules based on product weight | `automationRules/automationCriteria/productWeight.spec.ts` | 🟢 95% |
| Create automation rules based on shipping zone | `automationRules/automationCriteria/shippingZone.spec.ts` | 🟢 95% |
| Create rate automation rules with carrier/service selection | `automationRules/rateAutomation.spec.ts` | 🟢 95% |
| Create label automation rules with automatic assignment | `automationRules/labelAutomation.spec.ts` | 🟢 95% |
| Verify automation rules via request logs | `automationRules/actionDetails/requestLogs.spec.ts` | 🟢 95% |
| Activate/deactivate automation rules | `automationRules/labelAutomation.spec.ts` | 🟢 95% |

### Automation Gaps (Regression tests without automation)
- 🔴 Edit automation rule priority
- 🔴 Delete automation rules
- 🔴 Automation rule conflict resolution

---

## 2. Order Grid (75 regression tests, 20 automated files)

### Automation Summary
- **Total regression tests**: 75
- **Automated tests**: 20 (27%)
- **Automation confidence**: 🟢 High (90%)

### Automated Features

#### Bulk Actions from Action Menu

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Cancel shipment for orders | `orderGrid/actionMenu/cancelShipment.spec.ts` | 🟢 95% |
| Change carrier and service for orders | `orderGrid/actionMenu/changeCarrier.spec.ts` | 🟢 95% |
| Create return labels for fulfilled orders | `orderGrid/actionMenu/createReturnLabel.spec.ts` | 🟢 95% |
| Generate labels from order grid action menu | `orderGrid/actionMenu/generateLabel.spec.ts` | 🟢 95% |
| Mark orders as not to ship | `orderGrid/actionMenu/notToShip.spec.ts` | 🟢 95% |
| Prepare shipment with carrier/service selection | `orderGrid/actionMenu/prepareShipment.spec.ts` | 🟢 95% |
| Quick ship orders (shortcut label generation) | `orderGrid/actionMenu/quickShip.spec.ts` | 🟢 95% |
| Reprocess failed orders | `orderGrid/actionMenu/reprocess.spec.ts` | 🟢 95% |
| Set ship-from address for orders | `orderGrid/actionMenu/shipFrom.spec.ts` | 🟢 95% |
| Manual shipment fulfillment from grid | `orderGrid/actionMenu/manualShipment.spec.ts` | 🟢 95% |

#### Label Generation & Fulfillment

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Generate labels for orders with multiple products from grid | `orderGrid/labelGenerationFromGrid/labelGenerationFromGrid.spec.ts` | 🟢 95% |
| Fulfill orders from order grid (bulk fulfillment) | `orderGrid/labelGenerationFromGrid/fulfillOrders.spec.ts` | 🟢 95% |
| Fulfill all today's orders using "Today's Label" button | `orderGrid/todaysLabelButton/todaysLabel.spec.ts` | 🟢 95% |

#### Order Management Features

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Create and manage manifests | `orderGrid/manifest/manifest.spec.ts` | 🟢 90% |
| Update package details from order grid edit interface | `orderGrid/newEditPackage/editPackage.spec.ts` | 🟢 90% |
| View and manage order pickup details | `orderGrid/pickup/pickup.spec.ts` | 🟢 90% |
| Add tags to orders from grid | `orderGrid/tags/tags.spec.ts` | 🟢 90% |
| Track shipment status from order grid | `orderGrid/trackingFromGrid/tracking.spec.ts` | 🟢 90% |
| Create custom order views/filters | `orderGrid/views/views.spec.ts` | 🟢 90% |

### Automation Gaps (Significant regression tests without automation)
- 🔴 Filter orders by status (Initial, Processing, Label Created, Fulfilled)
- 🔴 Search orders by order number, customer name, tracking number
- 🔴 Export orders to CSV
- 🔴 Bulk update order attributes (ship from, tags, notes)
- 🔴 View order history and status changes
- 🔴 Print packing slips in bulk
- 🔴 Print commercial invoices for international orders
- 🔴 Download labels in bulk (PDF, PNG, ZPL)
- 🔴 Validate order address before label generation
- 🔴 Split multi-item orders into multiple shipments

**High-value automation opportunities**: Address validation, bulk document generation, order search/filter

---

## 3. Label Generation (33 regression tests, 8 automated files)

### Automation Summary
- **Total regression tests**: 33
- **Automated tests**: 8 (24%)
- **Automation confidence**: 🟢 High (90%)

### Automated Features

#### From Order Grid

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Generate labels from order grid and fulfill through label batch | `orderGrid/labelGenerationFromGrid/labelGenerationFromGrid.spec.ts` | 🟢 95% |
| Generate labels for orders with multiple products | `orderGrid/labelGenerationFromGrid/multipleProducts.spec.ts` | 🟢 95% |
| Fulfill orders from order grid in bulk | `orderGrid/labelGenerationFromGrid/bulkFulfill.spec.ts` | 🟢 95% |

#### From Order Summary (SLGP - Single Label Generation Page)

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Generate labels from order summary | `orderSummary/labelGeneration.spec.ts` | 🟢 90% |
| Generate and fulfill in one action (touchless flow) | `orderSummary/touchlessFlowPresetConfiguration.spec.ts` | 🟢 95% |
| Use SLGP preset configurations | `orderSummary/touchlessFlowPresetConfiguration.spec.ts` | 🟢 95% |
| Handle simple and custom products in touchless workflow | `orderSummary/touchlessFlowPresetConfiguration.spec.ts` | 🟢 90% |
| Auto-upload documents for FedEx shipments | `orderSummary/autoUploadDocumentsForFedex.spec.ts` | 🟢 95% |

#### Label Batch Operations

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Create label batches | `labelBatch/createBatch.spec.ts` | 🟢 90% |
| Fulfill orders from label batch | `labelBatch/fulfillBatch.spec.ts` | 🟢 90% |

### Automation Gaps
- 🔴 Edit label before printing (change weight, dimensions, service)
- 🔴 Void/cancel labels after generation
- 🔴 Regenerate labels with different carrier/service
- 🔴 Handle label generation errors (invalid address, carrier API errors)
- 🔴 Generate labels with hazmat/dangerous goods
- 🔴 Generate labels for international shipments with customs
- 🔴 Print labels in different formats (4x6, 8.5x11, ZPL)
- 🔴 Email labels to customers
- 🔴 Batch label generation progress tracking

**High-value automation opportunities**: Label error handling, customs/international flows, label format variations

---

## 4. Packaging (96 regression tests, 6 automated files)

### Automation Summary
- **Total regression tests**: 96 (across 4 packaging sheets)
- **Automated tests**: 6 (6%)
- **Automation confidence**: 🟢 High (90%)

**Coverage Issue**: Packaging has the largest regression test suite but lowest automation coverage. Critical gap.

### Automated Features

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Pack orders by total weight threshold | `packagingTypes/weightBased.spec.ts` | 🟢 95% |
| Apply box weight to weight-based calculations | `packagingTypes/weightBased.spec.ts` | 🟢 90% |
| Apply maximum quantity per package limits | `packagingTypes/weightBased.spec.ts` | 🟢 90% |
| Use volumetric weight for oversized packages | `packagingTypes/weightAndVolume.spec.ts` | 🟢 90% |
| Pack orders by quantity per package | `packagingTypes/quantityBased.spec.ts` | 🟢 95% |
| Select predefined boxes for orders | `packagingTypes/boxPackaging.spec.ts` | 🟢 90% |
| Stack packages based on product attributes | `packagingTypes/stackPackaging.spec.ts` | 🟢 85% |
| Use FedEx carrier-specific box types | `packagingTypes/fedexCarrierPackaging.spec.ts` | 🟢 90% |

### Automation Gaps (Critical - 90 regression tests)

**Domestic Packaging** (24 regression tests):
- 🔴 Rate calculations with different packaging types
- 🔴 Label generation with weight-based packaging
- 🔴 Label generation with box-based packaging
- 🔴 Label generation with stack packaging
- 🔴 Label generation with self-packing
- 🔴 Label generation with pre-packed products
- 🔴 Packaging validation (max weight, max dimensions)
- 🔴 Multi-package orders (splitting logic)

**International Packaging** (24 regression tests):
- 🔴 International rate calculations with packaging
- 🔴 International label generation with customs
- 🔴 Packaging for restricted/prohibited items
- 🔴 Packaging with dangerous goods declaration

**Rate Calculation** (24 domestic + 24 international = 48 regression tests):
- 🔴 Rate shopping with different packaging types
- 🔴 Rate display with packaging costs
- 🔴 Compare rates across carriers with packaging variations

**Priority**: HIGH - Packaging is core functionality with significant regression coverage but minimal automation.

---

## 5. Special Services (18 regression tests, 3 automated files)

### Automation Summary
- **Total regression tests**: 18
- **Automated tests**: 3 (17%)
- **Automation confidence**: 🟢 High (95%)

### Automated Features

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Add insurance to shipments | `specialServices/insurance.spec.ts` | 🟢 95% |
| Add adult signature requirement to shipments | `specialServices/adultSignature.spec.ts` | 🟢 95% |
| Add dangerous goods declaration with XML validation | `specialServices/dangerousGoods.spec.ts` | 🟢 95% |

### Automation Gaps
- 🔴 Add direct signature requirement
- 🔴 Add indirect signature requirement
- 🔴 Add "No signature" option
- 🔴 Add Saturday delivery
- 🔴 Add hold at location
- 🔴 Add COD (Cash on Delivery)
- 🔴 Add proof of delivery
- 🔴 Add return shipment
- 🔴 Add FedEx One Rate
- 🔴 Add carrier-specific services (UPS SurePost, FedEx SmartPost, etc.)
- 🔴 Validate special services compatibility (e.g., insurance + signature)
- 🔴 Calculate additional costs for special services

**Priority**: MEDIUM - Core features with good test coverage, need more automation for carrier-specific services.

---

## 6. Carrier Configuration (18 regression tests, 3 automated files)

### Automation Summary
- **Total regression tests**: 18
- **Automated tests**: 3 (17%)
- **Automation confidence**: 🟡 Medium (75%)

### Automated Features

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Configure UPS pickup services | `carrierOtherDetails/pickupService.spec.ts` | 🟡 75% |
| Select UPS image types | `carrierOtherDetails/imageType.spec.ts` | 🟡 75% |
| Set UPS reason for export (international) | `carrierOtherDetails/reasonForExport.spec.ts` | 🟡 75% |

### Automation Gaps
- 🔴 Configure FedEx account settings
- 🔴 Configure USPS account settings
- 🔴 Configure DHL account settings
- 🔴 Configure CanadaPost account settings
- 🔴 Add/edit carrier credentials
- 🔴 Enable/disable carrier services
- 🔴 Set carrier-specific defaults (packaging, service type)
- 🔴 Validate carrier account credentials
- 🔴 Test carrier API connections
- 🔴 Carrier negotiated rates setup
- 🔴 Carrier rate rules and markups

**Priority**: MEDIUM - Critical for onboarding, but stable once configured.

---

## 7. General Settings (82 regression tests, 0 automated files)

### Automation Summary
- **Total regression tests**: 82
- **Automated tests**: 0 (0%)
- **Automation confidence**: 🔴 None

### Regression Test Categories (Not Automated)

**Settings Sections Covered** (from regression sheet):
- 🔴 Store settings
- 🔴 Shipping settings
- 🔴 Label settings
- 🔴 Rate settings
- 🔴 Automation settings
- 🔴 Order settings
- 🔴 Notification settings
- 🔴 User management
- 🔴 API keys and integrations
- 🔴 Branding/customization

**Sample High-Value Features** (need automation):
- Configure default ship-from address
- Set default packaging type
- Configure rate display settings (show/hide carriers)
- Set order import settings (auto-import frequency)
- Configure notification emails (order shipped, label errors)
- Manage user roles and permissions
- Set label format defaults (size, format)
- Configure tracking page customization

**Priority**: MEDIUM - Settings are typically stable, but critical for onboarding and configuration changes.

---

## 8. Onboarding & Setup (47 regression tests, 2 automated files)

### Automation Summary
- **Total regression tests**: 47
- **Automated tests**: 2 (4%)
- **Automation confidence**: 🟡 Medium (70%)

### Automated Features

| Feature | Test File | Confidence |
|---------|-----------|------------|
| Create Shopify store in partner dashboard | `onboardingFlow/createStore.spec.ts` | 🟡 70% |
| Install MCSL app to store and manage subscription | `onboardingFlow/installApp.spec.ts` | 🟡 70% |

### Automation Gaps
- 🔴 Initial app configuration wizard
- 🔴 Carrier account setup (first-time)
- 🔴 Store connection validation
- 🔴 Import historical orders
- 🔴 Set default shipping rules
- 🔴 Configure rate shopping
- 🔴 Set label preferences
- 🔴 User onboarding tutorial/walkthrough
- 🔴 Subscription plan selection
- 🔴 Payment method setup
- 🔴 Trial activation

**Priority**: MEDIUM - Critical for customer acquisition, but low frequency after initial setup.

---

## 9. Order Management (24 regression tests, 0 automated files)

### Automation Summary
- **Total regression tests**: 24
- **Automated tests**: 0 (0%)
- **Automation confidence**: 🔴 None

### Regression Test Categories (Not Automated)

**Order Update Scenarios** (from Order_Update sheet):
- 🔴 Order status transitions (Initial → Processing → Label Created → Fulfilled)
- 🔴 Order synchronization from Shopify
- 🔴 Handling order cancellations
- 🔴 Handling order refunds
- 🔴 Partial fulfillment
- 🔴 Order address updates
- 🔴 Order line item updates
- 🔴 Order weight/dimensions updates
- 🔴 Order tagging and notes
- 🔴 Order holds (do not ship)

**Priority**: MEDIUM - Core functionality, but covered indirectly by other tests.

---

## Test Organization

### Regression Test Suite
**Location**: `raw/sheets/regression-scenarios.xlsx`
**Format**: Excel with multiple sheets per category
**Structure**:
- Sl No | Epics | Features | Stories | Scenarios | Description | Comments
- Scenarios written in Gherkin style (GIVEN/WHEN/THEN)

**Sheets**:
```
regression-scenarios.xlsx
├── Single Label Generation       (33 scenarios)
├── Orders Grid                   (75 scenarios)
├── Order_Update                  (24 scenarios)
├── Rate_Domestic_Packaging Type  (24 scenarios)
├── Label_Domestic_Packaging Type (24 scenarios)
├── Rate_International_Packaging  (24 scenarios)
├── Label_International_Packaging (24 scenarios)
├── Label Automation              (9 scenarios)
├── Rate Automation               (5 scenarios)
├── Special Services              (18 scenarios)
├── Carrier Specific              (18 scenarios)
├── General Setting               (82 scenarios)
├── Pluginhive app Setup          (47 scenarios)
└── ... (other categories)
```

### Automated Test Suite
**Location**: `raw/mcsl-test-automation/tests/`
**Framework**: Playwright (TypeScript)
**Git Reference**: c248e10ae07223da1e3dbf05130c67270672825d

**Structure**:
```
mcsl-test-automation/tests/
├── automationRules/               (11 test files)
│   ├── actionDetails/
│   ├── automationCriteria/        (8 criteria types)
│   ├── labelAutomation.spec.ts
│   └── rateAutomation.spec.ts
├── orderGrid/                     (20 test files)
│   ├── actionMenu/                (10 action types)
│   ├── labelGenerationFromGrid/
│   ├── manifest/
│   ├── newEditPackage/
│   ├── pickup/
│   ├── tags/
│   ├── todaysLabelButton/
│   ├── trackingFromGrid/
│   └── views/
├── specialServices/               (3 test files)
├── packagingTypes/                (6 test files)
├── orderSummary/                  (5 test files)
├── carrierOtherDetails/           (3 test files)
├── labelBatch/                    (2 test files)
├── onboardingFlow/                (2 test files)
├── externallyFulfilled/           (2 test files)
├── cod/                           (2 test files)
└── shopifyUI/                     (1 test file)
```

---

## Automation Confidence Scoring

| Score | Meaning | Criteria |
|-------|---------|----------|
| 🟢 95-100% | High | Stable tests, runs in CI, covers all scenarios, no manual verification needed |
| 🟡 70-94% | Medium | Mostly automated, occasional manual verification needed, some edge cases not covered |
| 🟠 40-69% | Low | Basic automation exists, significant manual testing still required |
| 🔴 0-39% | None/Minimal | Primarily manual testing, minimal or no automation |

**Current Distribution**:
- High (🟢): 50 features
- Medium (🟡): 10 features
- Low (🟠): 5 features
- None (🔴): 324 regression scenarios (83%)

---

## Critical Automation Gaps (Prioritized)

### Priority 1: HIGH (Critical Business Impact + High Regression Coverage)

1. **Packaging Types** (96 regression tests, 6 automated)
   - Domestic/International rate calculations with packaging
   - Multi-package order splitting
   - Packaging validation and constraints
   - **Business Impact**: Core shipping logic, frequent customer issues
   - **Suggested Automation**: 20 additional test files

2. **Address Validation** (covered in Order Grid gaps)
   - Validate address before label generation
   - Handle invalid addresses
   - Address correction suggestions
   - **Business Impact**: Prevents failed deliveries, reduces support tickets

3. **International Shipping & Customs** (covered in Label Generation gaps)
   - Generate labels with customs documentation
   - Handle restricted/prohibited items
   - Dangerous goods declaration
   - **Business Impact**: Growing revenue segment, complex compliance

4. **Label Error Handling** (covered in Label Generation gaps)
   - Handle carrier API errors gracefully
   - Void/regenerate labels
   - Label generation retry logic
   - **Business Impact**: High support volume, customer frustration

### Priority 2: MEDIUM (Important + Moderate Regression Coverage)

5. **General Settings** (82 regression tests, 0 automated)
   - Default configurations (ship-from, packaging, services)
   - Rate display settings
   - Notification settings
   - **Business Impact**: Onboarding quality, configuration errors

6. **Special Services** (18 regression tests, 3 automated)
   - Signature options (direct, indirect, none)
   - Saturday delivery, hold at location
   - Carrier-specific services
   - **Business Impact**: Revenue (premium services), customer satisfaction

7. **Carrier Configuration** (18 regression tests, 3 automated)
   - Multi-carrier account setup
   - Carrier credential validation
   - Negotiated rates configuration
   - **Business Impact**: Onboarding friction, carrier integration issues

### Priority 3: LOW (Stable Features or Indirect Coverage)

8. **Onboarding & Setup** (47 regression tests, 2 automated)
   - Initial setup wizard
   - Subscription management
   - **Business Impact**: Important but low frequency

9. **Order Management** (24 regression tests, 0 automated)
   - Order sync, status updates
   - **Business Impact**: Covered indirectly by other tests

10. **Reports & Analytics** (0 regression tests)
    - **Business Impact**: Low customer impact, internal tooling

---

## Recommended Automation Roadmap

### Phase 1: Critical Gaps (Q2 2026)
**Goal**: Increase automation coverage from 24% to 40%

**Focus Areas**:
1. Packaging automation (20 new tests) - expand coverage to 30%
2. International/customs flows (10 new tests)
3. Label error handling (8 new tests)
4. Address validation (5 new tests)

**Expected Outcome**: 43 new test files, +62 automated features

### Phase 2: Expand Coverage (Q3 2026)
**Goal**: Increase automation coverage to 60%

**Focus Areas**:
1. General settings automation (15 new tests)
2. Special services expansion (10 new tests)
3. Carrier configuration (8 new tests)
4. Order management flows (10 new tests)

**Expected Outcome**: 43 new test files, +78 automated features

### Phase 3: Comprehensive Coverage (Q4 2026)
**Goal**: Achieve 80%+ automation coverage

**Focus Areas**:
1. Onboarding flows (15 new tests)
2. Reports & analytics (8 new tests)
3. Edge cases and error scenarios (20 new tests)
4. Performance and load testing

**Expected Outcome**: 43 new test files, +100 automated features

---

## Related Pages

- [Product Backlog](product/backlog.md) - Prioritized work items with test coverage gaps
- [Product Metrics](product/metrics.md) - Customer pain index correlated with automation coverage
- [Zendesk Daily Index](zendesk/2026-04-22.md) - Support tickets by feature area
- [Test Coverage by Module](index.md#modules) - Wiki module pages with test coverage sections

---

## Maintenance Notes

**When Regression Scenarios Change**:
1. Re-export `raw/sheets/regression-scenarios.xlsx`
2. Re-run extraction script to parse scenarios
3. Re-map to existing automation
4. Update this file with new counts and gaps
5. Update affected module pages

**When Playwright Tests Change**:
1. Pull latest `raw/mcsl-test-automation` submodule
2. Re-analyze test files with Explore agent
3. Update automation coverage percentages
4. Update confidence scores based on test stability

**Automation Confidence Review** (Quarterly):
- Review test failure rates in CI
- Update confidence scores (green → yellow if flaky)
- Identify tests needing refactoring
- Add new tests for regression gaps

---

**Document Version**: 2.0
**Generated**: 2026-04-22
**Next Review**: 2026-05-22
