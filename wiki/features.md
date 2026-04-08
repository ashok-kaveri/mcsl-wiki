---
title: StorePep Features & Test Coverage
category: test-coverage
status: complete
last_updated: 2026-04-08
git_reference: current
sources: [storepep-react, mcsl-test-automation]
---

# StorePep Features & Test Coverage

**Last Updated**: 2026-04-08
**Regression Test Suite**: MCSL Regression Master Sheet
**Automated Test Suite**: mcsl-test-automation (Playwright)

---

## Overview

This document maps StorePep's regression test matrix to automated test coverage. The regression suite defines feature areas and product types that must be tested, while automation status shows which tests have Playwright implementations.

### Legend

**Test Status**:
- ✅ Automated (Playwright test exists and passing)
- 🔴 Manual Only (no automation)
- ⚠️ Automated but Flaky
- ❌ Automated but Failing
- 🚧 Automation In Progress

**Automation Confidence**:
- 🟢 High (95-100%) - Stable, comprehensive automation
- 🟡 Medium (70-94%) - Mostly automated, some manual verification
- 🟠 Low (40-69%) - Partial automation, significant manual testing
- 🔴 None (0-39%) - Primarily manual testing

**Product Types** (tested across all features):
- Simple Product
- Digital Product
- Custom Product
- High Value (Insurance)
- Dangerous Goods
- Prepackaged & Self Packing
- Multi Product
- Variable Products

---

## Automation Summary

| Feature Area | Owner | Total Tests | Automated | Manual | Automation % | Avg Confidence | Wiki |
|--------------|-------|-------------|-----------|--------|--------------|----------------|------|
| **Single Label Gen** | Ashok + Shahitha | 16 | 16 | 0 | 100% | 🟢 90% | [Label Generation](modules/shipping/label-generation.md) |
| **Orders Grid** | Ashok + Shahitha | 24 | 14 | 10+ | 58% | 🟡 83% | [Order Lifecycle](modules/orders/order-lifecycle.md), [Bulk Actions](modules/orders/order-bulk-actions.md) |
| **Packaging** | Basava | 6 | 6 | 0 | 100% | 🟢 95% | [Label Generation](modules/shipping/label-generation.md) |
| **SLGP (Touchless)** | Basava | 3 | 3 | 0 | 100% | 🟡 85% | [Label Generation](modules/shipping/label-generation.md) |
| **Quick Ship** | Basava | 1 | 1 | 0 | 100% | 🟡 85% | [Order Bulk Actions](modules/orders/order-bulk-actions.md) |
| **General Settings** | Preethi + Anuja | 1 | 1 | TBD | ~50% | 🟡 80% | [Label Generation](modules/shipping/label-generation.md) |
| **Views** | Preethi | 1 | 1 | 0 | 100% | 🟡 80% | [Order Lifecycle](modules/orders/order-lifecycle.md) |
| **Rules (Label + Rate)** | TBD | 11 | 11 | 0 | 100% | 🟢 95% | [Automation Actions](modules/automation/automation-actions.md) |
| **Platform Setup** | - | 2 | 2 | TBD | ~40% | 🟡 82% | [Platform Connectors](modules/stores/platform-connectors.md) |
| **Adding Products** | - | TBD | 0 | TBD | 0% | 🔴 0% | [Product Management](modules/products/product-management.md) |
| **Tracking Page** | - | 1 | 1 | TBD | ~20% | 🟠 60% | [Shipment Tracking](modules/shipping/shipment-tracking.md) |
| **Products Page** | - | TBD | 0 | TBD | 0% | 🔴 0% | [Product Management](modules/products/product-management.md) |
| **Account** | - | TBD | 0 | TBD | 0% | 🔴 0% | - |
| **Reports** | Ashok + Shahitha | TBD | 0 | TBD | 0% | 🔴 0% | - |
| **Auto Import** | - | TBD | 0 | TBD | 0% | 🔴 0% | [Store Integration](modules/stores/store-integration-overview.md) |
| **TOTAL** | - | **58+** | **58** | **10+** | **61%** | 🟡 **Medium** | - |

---

## Feature Areas

### 1. Single Label Gen (Order Summary)

**Owner**: Ashok + Shahitha
**Purpose**: Generate shipping labels from individual order summary page
**Wiki**: [Label Generation](modules/shipping/label-generation.md)

#### Automation Status

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Generate label and fulfill order from summary | Simple, Digital, Custom | 🔴 | ✅ | 🟢 92% | `orderSummary/labelGenerationFromSummary/labelGenerationAndFulfillment.spec.ts` |
| Box-based packing | Simple, Multi Product | 🔴 | ✅ | 🟢 95% | `packagingTypes/boxPackaging.spec.ts` |
| Quantity-based packing | Multi Product | 🔴 | ✅ | 🟢 95% | `packagingTypes/quantityPackaging.spec.ts` |
| Stack-based packing | Multi Product | 🔴 | ✅ | 🟢 95% | `packagingTypes/stackPackaging.spec.ts` |
| Weight-based automatic packing | Simple, Multi Product | 🔴 | ✅ | 🟢 95% | `packagingTypes/weightBasedPackaging.spec.ts` |
| Weight and volume combined packing | Multi Product | 🔴 | ✅ | 🟢 95% | `packagingTypes/weightAndVolume.spec.ts` |
| FedEx carrier box selection | Simple | 🔴 | ✅ | 🟢 95% | `packagingTypes/fedExCarrierBoxPackaging.spec.ts` |
| Auto-upload custom documents (FedEx) | Simple | 🔴 | ✅ | 🟡 80% | `orderSummary/documentAutoUploadForFedex.spec.ts` |
| Insurance coverage | High Value | 🔴 | ✅ | 🟢 90% | `specialServices/insurance.spec.ts` |
| Dangerous goods classification | Dangerous Goods | 🔴 | ✅ | 🟢 90% | `specialServices/dangerousgoods.spec.ts` |
| Adult signature requirement | Simple | 🔴 | ✅ | 🟢 90% | `specialServices/adultsignature.spec.ts` |
| Complete COD orders | Simple | 🔴 | ✅ | 🟡 85% | `cod/completeCOD.spec.ts` |
| Partial COD orders | Simple | 🔴 | ✅ | 🟡 80% | `cod/partialCOD.spec.ts` |
| UPS label image type (PNG/ZPL) | Simple | 🔴 | ✅ | 🟡 85% | `carrierOtherDetails/UPS/imageType.spec.ts` |
| UPS pickup service selection | Simple | 🔴 | ✅ | 🟡 85% | `carrierOtherDetails/UPS/pickupService.spec.ts` |
| UPS reason for export (international) | Simple | 🔴 | ✅ | 🟡 85% | `carrierOtherDetails/UPS/reasonForExport.spec.ts` |

**Summary**: 16 automated tests, 0 manual, 100% automation coverage
**Average Confidence**: 🟢 90%
**Gaps**: Need tests for other carriers (FedEx, DHL, USPS, Canada Post)

---

### 2. Orders Grid

**Owner**: Ashok + Shahitha
**Purpose**: Manage orders in bulk from grid view
**Wiki**: [Order Lifecycle](modules/orders/order-lifecycle.md), [Order Bulk Actions](modules/orders/order-bulk-actions.md)

#### Sub-Components

##### 2.1 Filters
**Status**: 🔴 Manual Only
**Gaps**: No automated tests for grid filters (status, date range, carrier, tags, etc.)

##### 2.2 Saved Views
**Status**: ✅ Automated (partial)

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Create, duplicate, and delete custom views | All | 🔴 | ✅ | 🟡 80% | `orderGrid/views/creatingview.spec.ts` |

**Gaps**: Need tests for view filters, sorting, column customization

##### 2.3 Imports
**Status**: 🔴 Manual Only
**Gaps**: No automated tests for CSV order imports

##### 2.4 Action Menu Items
**Status**: ✅ Automated (partial - 12/40+ actions)

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Cancel shipments | Simple | 🔴 | ✅ | 🟡 85% | `orderGrid/actionMenu/cancelShipment.spec.ts` |
| Change carrier and service | Simple | 🔴 | ✅ | 🟡 85% | `orderGrid/actionMenu/changeCarrierAndService.spec.ts` |
| Create return labels | Simple | 🔴 | ✅ | 🟡 80% | `orderGrid/actionMenu/createReturnLabel.spec.ts` |
| Generate labels from actions menu | Simple | 🔴 | ✅ | 🟢 90% | `orderGrid/actionMenu/generateLabelFromActionsMenu.spec.ts` |
| Change order status (Initial/Processing) | Simple | 🔴 | ✅ | 🟢 90% | `orderGrid/actionMenu/initialAndReprocessOrder.spec.ts` |
| Manual fulfillment with tracking | Simple | 🔴 | ✅ | 🟡 80% | `orderGrid/actionMenu/manualFulfillment.spec.ts` |
| Mark as not to ship | Simple | 🔴 | ✅ | 🟢 90% | `orderGrid/actionMenu/markAsNotToShip.spec.ts` |
| Prepare shipments | Simple | 🔴 | ✅ | 🟡 85% | `orderGrid/actionMenu/prepareShipment.spec.ts` |
| Quick ship with default/custom values | Simple | 🔴 | ✅ | 🟡 85% | `orderGrid/actionMenu/quickShip.spec.ts` |
| Set ship from address | Simple | 🔴 | ✅ | 🟢 90% | `orderGrid/actionMenu/setShipFromAddress.spec.ts` |
| Add and manage tags | Simple | 🔴 | ✅ | 🟡 80% | `orderGrid/tags/addTags.spec.ts` |
| Edit package details (pencil icon) | Simple | 🔴 | ✅ | 🟡 80% | `orderGrid/newEditPackage/newEditPackageFromPencilIconInOrdersGrid.spec.ts` |

**Gaps**: 28+ bulk actions untested (see [Order Bulk Actions](modules/orders/order-bulk-actions.md#untested-actions))

##### 2.5 Label Generation from Grid

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Generate labels and fulfill from grid | Simple | 🔴 | ✅ | 🟢 95% | `orderGrid/labelGenerationFromGrid/generateLabelFromGridAndFulfillFromLabelBatch.spec.ts` |
| Generate labels with multiple products | Multi Product | 🔴 | ✅ | 🟢 95% | `orderGrid/labelGenerationFromGrid/generateLabelWithMultipleProducts.spec.ts` |
| Order fulfillment from grid | Simple | 🔴 | ✅ | 🟢 95% | `orderGrid/labelGenerationFromGrid/orderFulfillmentFromOrderGrid.spec.ts` |

##### 2.6 Additional Grid Features

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Bulk fulfill today's orders (Today's Label button) | Simple | 🔴 | ✅ | 🟡 85% | `orderGrid/todaysLabelButton/fulfillTodaysOrders.spec.ts` |
| Track orders from grid | Simple | 🔴 | ✅ | 🟠 60% | `orderGrid/trackingFromGrid/trackOrderFromOrderGrid.spec.ts` |
| View manifest details | Simple | 🔴 | ✅ | 🟡 75% | `orderGrid/manifest/manifestDetails.spec.ts` |
| Request pickups | Simple | 🔴 | ✅ | 🟡 75% | `orderGrid/pickup/pickupDetails.spec.ts` |

**Summary**: 14 automated tests, 10+ manual gaps, 58% automation coverage
**Average Confidence**: 🟡 83%

---

### 3. Packaging

**Owner**: Basava
**Purpose**: Define how products are packed into boxes
**Wiki**: [Label Generation](modules/shipping/label-generation.md)

#### Automation Status

| Packaging Type | Carrier Specific | Manual | Automated | Confidence | Test File |
|----------------|------------------|--------|-----------|------------|-----------|
| Box-based (weight/dimension constraints) | No | 🔴 | ✅ | 🟢 95% | `packagingTypes/boxPackaging.spec.ts` |
| Quantity-based (items per box) | No | 🔴 | ✅ | 🟢 95% | `packagingTypes/quantityPackaging.spec.ts` |
| Stack-based | No | 🔴 | ✅ | 🟢 95% | `packagingTypes/stackPackaging.spec.ts` |
| Weight-based automatic | No | 🔴 | ✅ | 🟢 95% | `packagingTypes/weightBasedPackaging.spec.ts` |
| Weight and volume combined | No | 🔴 | ✅ | 🟢 95% | `packagingTypes/weightAndVolume.spec.ts` |
| FedEx carrier boxes | Yes (FedEx) | 🔴 | ✅ | 🟢 95% | `packagingTypes/fedExCarrierBoxPackaging.spec.ts` |

**Summary**: 6 automated tests, 0 manual, 100% automation coverage
**Average Confidence**: 🟢 95%
**Gaps**: Need carrier-specific packaging for UPS, USPS, DHL

---

### 4. SLGP (Touchless Single Label Generation)

**Owner**: Basava
**Purpose**: Generate labels with preset configurations without manual intervention
**Wiki**: [Label Generation](modules/shipping/label-generation.md)

#### Automation Status

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Touchless label generation with presets | Simple | 🔴 | ✅ | 🟡 85% | `orderSummary/touchlessSLGPFlow/touchLessSLGPFlow.spec.ts` |
| Create, apply, and manage SLGP presets | Simple | 🔴 | ✅ | 🟡 85% | `orderSummary/touchlessSLGPFlow/slgpPreset.spec.ts` |
| Process simple and custom products | Simple, Custom | 🔴 | ✅ | 🟡 85% | `orderSummary/touchlessSLGPFlow/simpleAndcustomproduct.spec.ts` |

**Summary**: 3 automated tests, 0 manual, 100% automation coverage
**Average Confidence**: 🟡 85%

---

### 5. Quick Ship

**Owner**: Basava
**Purpose**: Rapid order fulfillment with minimal clicks
**Wiki**: [Order Bulk Actions](modules/orders/order-bulk-actions.md)

#### Automation Status

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Quick ship with default or custom values | Simple | 🔴 | ✅ | 🟡 85% | `orderGrid/actionMenu/quickShip.spec.ts` |

**Summary**: 1 automated test, 0 manual, 100% automation coverage
**Average Confidence**: 🟡 85%

---

### 6. General Settings

**Owner**: Preethi + Anuja
**Purpose**: Configure packing slips, tax invoices, and other documents
**Wiki**: [Label Generation](modules/shipping/label-generation.md)

#### Automation Status

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Auto-upload custom documents for FedEx | Simple | 🔴 | ✅ | 🟡 80% | `orderSummary/documentAutoUploadForFedex.spec.ts` |
| Packing slip configuration | All | 🔴 | 🔴 | 🔴 0% | - |
| Tax invoice configuration | All | 🔴 | 🔴 | 🔴 0% | - |

**Summary**: 1 automated test, TBD manual tests, ~50% automation coverage
**Average Confidence**: 🟡 80% (automated), 🔴 0% (manual)

---

### 7. Views

**Owner**: Preethi
**Purpose**: Custom grid views with filters and saved configurations
**Wiki**: [Order Lifecycle](modules/orders/order-lifecycle.md)

#### Automation Status

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Create, duplicate, and delete custom views | All | 🔴 | ✅ | 🟡 80% | `orderGrid/views/creatingview.spec.ts` |

**Summary**: 1 automated test, 0 manual, 100% automation coverage
**Average Confidence**: 🟡 80%
**Gaps**: Need tests for view filters, column customization, sharing

---

### 8. Rules (Label Automation + Rate Automation)

**Owner**: TBD (Later)
**Purpose**: Automated business logic for order processing
**Wiki**: [Automation Actions](modules/automation/automation-actions.md)

#### Automation Status

| Feature Category | Tests | Manual | Automated | Confidence | Test Files |
|------------------|-------|--------|-----------|------------|------------|
| Automation Criteria | 7 | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/*.spec.ts` |
| Action Details (Carrier/Service) | 1 | 🔴 | ✅ | 🟢 98% | `automationRules/actionDetails/setCarrierService.spec.ts` |
| Label Automation | 1 | 🔴 | ✅ | 🟢 95% | `automationRules/labelAutomation.spec.ts` |
| Rate Automation | 1 | 🔴 | ✅ | 🟢 95% | `automationRules/rateAutomation.spec.ts` |
| General Rules Management | 1 | 🔴 | ✅ | 🟢 95% | `automationRules/automationRules.spec.ts` |

**Detailed Tests**:

| Feature | Product Types | Manual | Automated | Confidence | Test File |
|---------|---------------|--------|-----------|------------|-----------|
| Quantity between threshold | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/quantityBetween.spec.ts` |
| Product price conditions | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/price.spec.ts` |
| Product shipping class | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/productShippingClass.spec.ts` |
| Total price range | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/totalPriceRange.spec.ts` |
| Total weight range | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/totalWeightRange.spec.ts` |
| Total weight conditions | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/totalWeightRule.spec.ts` |
| Shipping zone criteria | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationCriteria/zone.spec.ts` |
| Set carrier and service automatically | All | 🔴 | ✅ | 🟢 98% | `automationRules/actionDetails/setCarrierService.spec.ts` |
| Auto-generate labels | All | 🔴 | ✅ | 🟢 95% | `automationRules/labelAutomation.spec.ts` |
| Auto-set shipping rates | All | 🔴 | ✅ | 🟢 95% | `automationRules/rateAutomation.spec.ts` |
| Create and manage multiple rules | All | 🔴 | ✅ | 🟢 95% | `automationRules/automationRules.spec.ts` |

**Summary**: 11 automated tests, 0 manual, 100% automation coverage
**Average Confidence**: 🟢 95%
**Gaps**: Need tests for 13 untested actions (see [Automation Actions](modules/automation/automation-actions.md#untested-actions))

---

### 9. Platform Setup (Carrier Registration)

**Owner**: Not assigned
**Purpose**: Onboard new stores and manage subscriptions
**Wiki**: [Platform Connectors](modules/stores/platform-connectors.md)

#### Automation Status

| Feature | Platform | Manual | Automated | Confidence | Test File |
|---------|----------|--------|-----------|------------|-----------|
| Create development stores and install app | Shopify | 🔴 | ✅ | 🟡 80% | `onboardingFlow/createStoreAndInstallApp.spec.ts` |
| Manage subscription plans (upgrade/downgrade) | Shopify | 🔴 | ✅ | 🟡 80% | `onboardingFlow/manageSubscription.spec.ts` |
| Carrier registration | All Carriers | 🔴 | 🔴 | 🔴 0% | - |
| Carrier credentials configuration | All Carriers | Manual | Partial | 🟠 40% | Via carrier-specific tests |

**Summary**: 2 automated tests, TBD manual tests, ~40% automation coverage
**Average Confidence**: 🟡 82% (onboarding), 🔴 0% (carrier registration)
**Gaps**: No tests for carrier registration flow, WooCommerce/Magento onboarding

---

### 10. Adding Products

**Owner**: Not assigned
**Purpose**: Add products to StorePep catalog
**Wiki**: [Product Management](modules/products/product-management.md), [Product Import/Export](modules/products/product-import-export.md)

#### Feature Areas

| Feature | Manual | Automated | Confidence | Test File |
|---------|--------|-----------|------------|-----------|
| Single product add | 🔴 | 🔴 | 🔴 0% | - |
| Bulk upload (CSV) | 🔴 | 🔴 | 🔴 0% | - |

**Summary**: 0 automated tests, TBD manual tests, 0% automation coverage
**Average Confidence**: 🔴 0%
**Status**: 🔴 Critical Gap - No automation

---

### 11. Tracking Page

**Owner**: Not assigned
**Purpose**: View shipment tracking information
**Wiki**: [Shipment Tracking](modules/shipping/shipment-tracking.md)

#### Automation Status

| Feature | Manual | Automated | Confidence | Test File |
|---------|--------|-----------|------------|-----------|
| Track orders from grid | 🔴 | ✅ | 🟠 60% | `orderGrid/trackingFromGrid/trackOrderFromOrderGrid.spec.ts` |
| Retrack shipments | 🔴 | 🔴 | 🔴 0% | - |
| Date filter | 🔴 | 🔴 | 🔴 0% | - |
| Status filter | 🔴 | 🔴 | 🔴 0% | - |

**Summary**: 1 automated test (UI only), TBD manual tests, ~20% automation coverage
**Average Confidence**: 🟠 60% (UI test only)
**Gaps**: No tests for tracking engine, cron jobs, carrier API integration, email notifications

---

### 12. Products Page

**Owner**: Not assigned
**Purpose**: Manage product catalog
**Wiki**: [Product Management](modules/products/product-management.md)

#### Feature Areas

| Feature | Manual | Automated | Confidence | Test File |
|---------|--------|-----------|------------|-----------|
| Import CSV | 🔴 | 🔴 | 🔴 0% | - |
| Export CSV | 🔴 | 🔴 | 🔴 0% | - |
| Import products from stores | 🔴 | 🔴 | 🔴 0% | - |
| Search products | 🔴 | 🔴 | 🔴 0% | - |
| Filter products | 🔴 | 🔴 | 🔴 0% | - |
| Edit products | 🔴 | 🔴 | 🔴 0% | - |
| Force import | 🔴 | 🔴 | 🔴 0% | - |
| Delete products | 🔴 | 🔴 | 🔴 0% | - |

**Summary**: 0 automated tests, TBD manual tests, 0% automation coverage
**Average Confidence**: 🔴 0%
**Status**: 🔴 Critical Gap - No automation

---

### 13. Account

**Owner**: Not assigned
**Purpose**: Manage account settings and billing
**Wiki**: None

#### Feature Areas

| Feature | Manual | Automated | Confidence | Test File |
|---------|--------|-----------|------------|-----------|
| Billing address management | 🔴 | 🔴 | 🔴 0% | - |
| Manage subscription | 🔴 | Partial | 🟡 80% | `onboardingFlow/manageSubscription.spec.ts` (covered in Platform Setup) |

**Summary**: 0 standalone tests (1 covered in Platform Setup), TBD manual tests, 0% automation coverage
**Average Confidence**: 🔴 0%

---

### 14. Reports

**Owner**: Ashok + Shahitha
**Purpose**: Analytics and reporting
**Wiki**: None

#### Feature Areas

| Feature | Manual | Automated | Confidence | Test File |
|---------|--------|-----------|------------|-----------|
| Analytics reports | 🔴 | 🔴 | 🔴 0% | - |

**Summary**: 0 automated tests, TBD manual tests, 0% automation coverage
**Average Confidence**: 🔴 0%
**Status**: 🔴 Critical Gap - No automation

---

### 15. Auto Import

**Owner**: Not assigned
**Purpose**: Automatic order import from connected stores
**Wiki**: [Store Integration Overview](modules/stores/store-integration-overview.md)

#### Feature Areas

| Feature | Platform | Manual | Automated | Confidence | Test File |
|---------|----------|--------|-----------|------------|-----------|
| Initial processing | All | 🔴 | 🔴 | 🔴 0% | - |
| Partial fulfillment | All | 🔴 | 🔴 | 🔴 0% | - |
| Order update ring (webhooks) | All | 🔴 | 🔴 | 🔴 0% | - |

**Summary**: 0 automated tests, TBD manual tests, 0% automation coverage
**Average Confidence**: 🔴 0%
**Status**: 🔴 Critical Gap - No automation for core import flow

---

### 16. Store Integration (Additional)

**Purpose**: E-commerce platform integrations
**Wiki**: [Platform Connectors](modules/stores/platform-connectors.md)

#### Automation Status

| Feature | Platform | Manual | Automated | Confidence | Test File |
|---------|----------|--------|-----------|------------|-----------|
| Order products from store checkout | Shopify | 🔴 | ✅ | 🟡 75% | `shopifyUI/shopifyCheckout.spec.ts` |
| Mark orders as externally fulfilled | Shopify | 🔴 | ✅ | 🟡 80% | `externallyFulfilled/fulfillOrderFromShopify.spec.ts` |
| Handle partially externally fulfilled orders | Shopify | 🔴 | ✅ | 🟡 75% | `externallyFulfilled/partiallyExternallyFulfilled.spec.ts` |

**Summary**: 3 automated tests (Shopify only), TBD manual tests
**Gaps**: WooCommerce, Magento, BigCommerce, PrestaShop, Amazon India untested

---

### 17. Label Batching

**Purpose**: Batch label generation and printing
**Wiki**: [Label Generation](modules/shipping/label-generation.md)

#### Automation Status

| Feature | Manual | Automated | Confidence | Test File |
|---------|--------|-----------|------------|-----------|
| Create label batches | 🔴 | ✅ | 🟢 90% | `labelBatch/createBatch.spec.ts` |
| Generate and manage label batches with printing | 🔴 | ✅ | 🟢 90% | `labelBatch/generateLabelBatch.spec.ts` |

**Summary**: 2 automated tests, 0 manual, 100% automation coverage
**Average Confidence**: 🟢 90%

---

## Automated Test Suite Details

**Location**: `mcsl-test-automation/tests/`
**Total Test Files**: 58

### Test Organization

```
mcsl-test-automation/tests/
├── automationRules/          (11 tests) ✅ 100% automated
│   ├── automationCriteria/   (7 tests - quantity, price, shipping class, weight, zone)
│   ├── actionDetails/        (1 test - set carrier/service)
│   ├── labelAutomation.spec.ts
│   ├── rateAutomation.spec.ts
│   └── automationRules.spec.ts
├── carrierOtherDetails/      (3 tests) ✅ 100% automated (UPS only)
│   └── UPS/                  (imageType, pickupService, reasonForExport)
├── cod/                      (2 tests) ✅ 100% automated
│   ├── completeCOD.spec.ts
│   └── partialCOD.spec.ts
├── externallyFulfilled/      (2 tests) ✅ 100% automated (Shopify only)
│   ├── fulfillOrderFromShopify.spec.ts
│   └── partiallyExternallyFulfilled.spec.ts
├── labelBatch/               (2 tests) ✅ 100% automated
│   ├── createBatch.spec.ts
│   └── generateLabelBatch.spec.ts
├── onboardingFlow/           (2 tests) ✅ 100% automated
│   ├── createStoreAndInstallApp.spec.ts
│   └── manageSubscription.spec.ts
├── orderGrid/                (17 tests) 🟡 Partial coverage
│   ├── actionMenu/           (10 tests - bulk actions)
│   ├── labelGenerationFromGrid/ (3 tests)
│   ├── manifest/             (1 test)
│   ├── newEditPackage/       (1 test)
│   ├── pickup/               (1 test)
│   ├── tags/                 (1 test)
│   ├── todaysLabelButton/    (1 test)
│   ├── trackingFromGrid/     (1 test - UI only)
│   └── views/                (1 test)
├── orderSummary/             (5 tests) ✅ 100% automated
│   ├── documentAutoUploadForFedex/
│   ├── labelGenerationFromSummary/
│   └── touchlessSLGPFlow/    (3 tests - SLGP presets, touchless flow, products)
├── packagingTypes/           (6 tests) ✅ 100% automated
│   ├── boxPackaging.spec.ts
│   ├── quantityPackaging.spec.ts
│   ├── stackPackaging.spec.ts
│   ├── weightBasedPackaging.spec.ts
│   ├── weightAndVolume.spec.ts
│   └── fedExCarrierBoxPackaging.spec.ts
├── shopifyUI/                (1 test) ✅ 100% automated
│   └── shopifyCheckout.spec.ts
└── specialServices/          (3 tests) ✅ 100% automated
    ├── insurance.spec.ts
    ├── dangerousgoods.spec.ts
    └── adultsignature.spec.ts
```

---

## Product Type Coverage

| Product Type | Feature Areas Covered | Automation Status |
|--------------|----------------------|-------------------|
| **Simple Product** | All label gen, order grid, SLGP, COD, carrier config | ✅ Well covered |
| **Digital Product** | Label generation only | 🟡 Limited |
| **Custom Product** | Label generation, SLGP | 🟡 Limited |
| **Multi Product** | Packaging (all types), label generation | ✅ Well covered |
| **High Value (Insurance)** | Insurance special service | 🟡 Limited to insurance |
| **Dangerous Goods** | Dangerous goods special service | 🟡 Limited to DG classification |
| **Variable Products** | None | 🔴 Not tested |
| **Prepackaged & Self Packing** | None explicitly | 🔴 Not tested |

---

## Critical Gaps

### 🔴 High Priority (No Automation)

1. **Auto Import Flow** - Core order import from stores (Initial Processing, Partial FF, Order Update)
2. **Products Page** - Complete product management (Import/Export CSV, Search, Filter, Edit, Delete)
3. **Adding Products** - Single add, Bulk upload
4. **Reports** - Analytics and reporting
5. **Account** - Billing address management
6. **Carrier Registration** - Onboarding carriers
7. **Order Grid Filters** - Critical for order management
8. **Order Grid Imports** - CSV order imports

### 🟡 Medium Priority (Partial Automation)

1. **Tracking System** - Only UI tested, missing: Cron jobs, Carrier API integration, Email notifications
2. **Order Bulk Actions** - 12/40+ actions automated (30% coverage)
3. **Platform Integration** - Only Shopify tested (WooCommerce, Magento, BigCommerce, PrestaShop, Amazon India untested)
4. **Carrier Configuration** - Only UPS tested (42+ carriers untested)
5. **General Settings** - Packing slip and tax invoice configuration untested
6. **Grid Views** - View filters, column customization, sharing untested

### 🟠 Low Confidence Areas

1. **Tracking from Grid** (60% confidence) - Only tests UI, doesn't verify carrier data
2. **External Fulfillment** (75-80% confidence) - Dependent on Shopify API stability
3. **Document Auto-Upload** (80% confidence) - Limited to FedEx only

---

## Recommendations

### Immediate Actions

1. **Automate Auto Import Flow** - Most critical gap affecting core functionality
2. **Add Product Management Tests** - Import/Export CSV, CRUD operations
3. **Expand Carrier Coverage** - Add FedEx, DHL, USPS tests (3 tests per carrier minimum)
4. **Tracking System Integration Tests** - Test cron jobs, carrier APIs, email triggers
5. **Add Order Grid Filter Tests** - Critical for usability

### Short-term Actions

1. **Platform Integration Expansion** - WooCommerce and Magento tests
2. **Order Bulk Actions Coverage** - Increase from 30% to 60% (add 12 more actions)
3. **Product Type Coverage** - Variable products, prepackaged, self-packing scenarios
4. **General Settings Tests** - Packing slip, tax invoice configuration
5. **Grid Views Enhancement** - Filter tests, column customization

### Long-term Actions

1. **Reports Automation** - Analytics and reporting tests
2. **Account Management** - Billing address, subscription management (beyond onboarding)
3. **Carrier Registration Flow** - End-to-end carrier onboarding
4. **Multi-product Scenarios** - Complex order combinations across all features
5. **Performance Testing** - Load tests for batch operations

---

## Maintenance

**Updating This Document**:

1. **When adding new automated tests**:
   - Add row to relevant feature area table
   - Update automation summary at top
   - Recalculate automation percentage and confidence scores
   - Update test organization tree

2. **When regression suite changes**:
   - User provides updated spreadsheet
   - Map new feature areas to wiki modules
   - Update feature area tables
   - Adjust gaps and recommendations

3. **When test stability changes**:
   - Update confidence scores with explanation
   - Move between confidence tiers if significant change
   - Document issues in test file or wiki page

4. **When manual tests are performed**:
   - Note manual test results in relevant feature area
   - Adjust automation priority based on manual effort required

---

## Related Documentation

- [Order Lifecycle](modules/orders/order-lifecycle.md) - Order processing flow
- [Order Bulk Actions](modules/orders/order-bulk-actions.md) - Bulk operations (40+ actions)
- [Label Generation](modules/shipping/label-generation.md) - Label creation workflows
- [Automation Actions](modules/automation/automation-actions.md) - Automation engine (24 actions)
- [Carrier Configuration](modules/shipping/carrier-configuration.md) - Carrier settings
- [Carrier System Overview](modules/shipping/carrier-system-overview.md) - Multi-carrier architecture
- [Platform Connectors](modules/stores/platform-connectors.md) - Store integrations (7 platforms)
- [Shipment Tracking](modules/shipping/shipment-tracking.md) - Tracking system (45+ carriers)
- [Product Management](modules/products/product-management.md) - Product catalog
- [Product Import/Export](modules/products/product-import-export.md) - Product data sync
