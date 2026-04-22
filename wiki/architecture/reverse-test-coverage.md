---
title: Reverse Test Coverage Map
category: architecture
sources: [wiki/modules, wiki/features.md, coupling-data.json]
status: complete
last_updated: 2026-04-22
modules_scanned: 22
modules_with_coverage: 6
specs_indexed: 51
---

# Reverse Test Coverage Map

Inverts the forward coverage map (feature → test) into a reverse index: source file or module → test suites.
Indirect tests surface hidden dependencies via file co-change coupling — test suites that exercise files
that frequently co-change with your target, even when there's no direct import relationship.

**Built**: 2026-04-22 · **Modules**: 22 · **Specs indexed**: 51
**Direct coverage**: 6 modules · **Coupling source**: [coupling-map.md](coupling-map.md)

## How to Use

Before changing a source file or module, run:
```
/reverse-test-coverage query fedexShipmentHelper.js
/reverse-test-coverage query shipping/label-generation
/reverse-test-coverage query server/src/routes/orders.js
```

> Source file → test mapping is **module-level** (Playwright tests use POM, not direct imports).
> Indirect tests are found via [coupling-map.md](coupling-map.md) co-change partners.

---

## Coverage by Module

| Module | Wiki Page | Direct Tests | Source Refs Resolved | Notes |
|--------|-----------|:------------:|:--------------------:|-------|
| `automation/automation-actions` | [link](../modules/automation/automation-actions.md) | 11 | 0 | 0 ambiguous, 3 unresolved |
| `orders/order-bulk-actions` | [link](../modules/orders/order-bulk-actions.md) | 12 | 2 | 0 ambiguous, 2 unresolved |
| `shipping/carrier-configuration` | [link](../modules/shipping/carrier-configuration.md) | 3 | 3 | — |
| `shipping/label-generation` | [link](../modules/shipping/label-generation.md) | 20 | 4 | 0 ambiguous, 3 unresolved |
| `shipping/shipment-tracking` | [link](../modules/shipping/shipment-tracking.md) | 1 | 1 | 0 ambiguous, 18 unresolved |
| `stores/platform-connectors` | [link](../modules/stores/platform-connectors.md) | 5 | 2 | 0 ambiguous, 4 unresolved |

---

## Modules Without Test Coverage Section

These 16 module pages have no `## Test Coverage` section and are not in the reverse index.
Add the section to include them in future builds:

- `automation/automation-conditions` — [`wiki/modules/automation/automation-conditions.md`](../modules/automation/automation-conditions.md)
- `automation/automation-overview` — [`wiki/modules/automation/automation-overview.md`](../modules/automation/automation-overview.md)
- `integrations/store-platforms` — [`wiki/modules/integrations/store-platforms.md`](../modules/integrations/store-platforms.md)
- `orders/order-address-management` — [`wiki/modules/orders/order-address-management.md`](../modules/orders/order-address-management.md)
- `orders/order-lifecycle` — [`wiki/modules/orders/order-lifecycle.md`](../modules/orders/order-lifecycle.md)
- `orders/order-returns` — [`wiki/modules/orders/order-returns.md`](../modules/orders/order-returns.md)
- `products/product-import-export` — [`wiki/modules/products/product-import-export.md`](../modules/products/product-import-export.md)
- `products/product-management` — [`wiki/modules/products/product-management.md`](../modules/products/product-management.md)
- `shipping/batch-processing` — [`wiki/modules/shipping/batch-processing.md`](../modules/shipping/batch-processing.md)
- `shipping/carrier-integration` — [`wiki/modules/shipping/carrier-integration.md`](../modules/shipping/carrier-integration.md)
- `shipping/carrier-integrations` — [`wiki/modules/shipping/carrier-integrations.md`](../modules/shipping/carrier-integrations.md)
- `shipping/carrier-system-overview` — [`wiki/modules/shipping/carrier-system-overview.md`](../modules/shipping/carrier-system-overview.md)
- `shipping/rate-shopping` — [`wiki/modules/shipping/rate-shopping.md`](../modules/shipping/rate-shopping.md)
- `stores/store-integration-overview` — [`wiki/modules/stores/store-integration-overview.md`](../modules/stores/store-integration-overview.md)
- `warehouses/warehouse-selection` — [`wiki/modules/warehouses/warehouse-selection.md`](../modules/warehouses/warehouse-selection.md)
- `workflows/automation-rules` — [`wiki/modules/workflows/automation-rules.md`](../modules/workflows/automation-rules.md)

---

## Source File Resolution

Of 42 source file references extracted from module pages:

| Resolution | Count | Notes |
|------------|------:|-------|
| Resolved (1:1 match in coupling data) | 12 | Used for direct + indirect lookup |
| Ambiguous (multiple candidates) | 0 | All candidates included; flagged in query output |
| Unresolved (not in coupling data) | 30 | No coupling partners available |

---

## Top Source Files by Test Coverage

| Source File | Modules | Direct Tests | Indirect Tests |
|-------------|---------|:------------:|:--------------:|
| `fedexShipmentHelper.js` | `shipping/label-generation` | 20 | 20 |
| `fedexRequestBuilder.js` | `shipping/label-generation` | 20 | 20 |
| `batchProcessHelper.js` | `shipping/label-generation` | 20 | 0 |
| `orders.js` | `shipping/label-generation` | 20 | 0 |
| `ordersActions.js` | `orders/order-bulk-actions` | 12 | 0 |
| `bulkactionHelper.js` | `orders/order-bulk-actions` | 12 | 0 |
| `ShopifyStore.js` | `stores/platform-connectors` | 5 | 0 |
| `WooCommerceStore.js` | `stores/platform-connectors` | 5 | 0 |
| `carriers.js` | `shipping/carrier-configuration` | 3 | 0 |
| `storePepConstants.js` | `shipping/shipment-tracking` | 1 | 0 |

---

## Related

- [Features & Test Coverage](../features.md)
- [File Co-Change Coupling Map](coupling-map.md)
- [Backend Architecture](backend-architecture.md)
