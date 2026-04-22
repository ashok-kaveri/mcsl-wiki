---
title: File Co-Change Coupling Map
category: architecture
sources: [storepep-react]
status: complete
last_updated: 2026-04-22
git_reference: a5405aed2fe8a3b54b91b28c9a0d5f8396b890c0
since_window: "1 year ago"
commits_analyzed: 599
pairs_above_threshold: 5233
threshold: 3
---

# File Co-Change Coupling Map

Files that frequently appear in the same commit are likely coupled — changing one
probably requires reviewing the others. Generated from `raw/storepep-react` git history.

**Window**: last 1 year ago · **Commits**: 599 · **Threshold**: ≥3 · **Pairs**: 5233
**Last updated**: 2026-04-22 @ `a5405aed`

## How to Use

To find blast-radius partners for a specific file before making a change:
```
/git-co-change-graph query server/src/routes/orders.js
```

> Commits touching >30 files are excluded (mass reformats). Test files, lock files, and migrations are also excluded.

---

## Top Coupled Pairs

| # | Co-changes | File A | File B | Domain |
|---|------------|--------|--------|--------|
| 1 | 133 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 2 | 105 | `storepepSAAS/server/config.json` | `storepepSAAS/server/featureToggles.json` | server |
| 3 | 68 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/storePepConstants.js` | server |
| 4 | 50 | `storepepSAAS/client/src/components/form/settings/carriers/getDefaultValues.js` | `storepepSAAS/server/src/shared/settings/carrierRequiredFields.js` | cross-domain |
| 5 | 45 | `storepepSAAS/server/src/models/carriers.js` | `storepepSAAS/server/src/shared/settings/carrierRequiredFields.js` | cross-domain |
| 6 | 45 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/shared/listeners/index.js` | cross-domain |
| 7 | 44 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/listeners/index.js` | cross-domain |
| 8 | 44 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/routes/orders.js` | cross-domain |
| 9 | 44 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 10 | 43 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 11 | 40 | `storepepSAAS/client/src/components/form/settings/carriers/getDefaultValues.js` | `storepepSAAS/server/src/models/carriers.js` | cross-domain |
| 12 | 38 | `storepepSAAS/client/src/utils/constants.js` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 13 | 37 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 14 | 36 | `storepepSAAS/server/src/models/orders.js` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` | cross-domain |
| 15 | 35 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/storePepConstants.js` | server |
| 16 | 35 | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 17 | 34 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/models/orders.js` | cross-domain |
| 18 | 34 | `storepepSAAS/client/src/utils/constants.js` | `storepepSAAS/server/src/storePepConstants.js` | cross-domain |
| 19 | 33 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` | cross-domain |
| 20 | 33 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/server/src/routes/orders.js` | cross-domain |
| 21 | 32 | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | `storepepSAAS/server/src/storePepConstants.js` | cross-domain |
| 22 | 32 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/customLabels/customLabel.js` | cross-domain |
| 23 | 30 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | cross-domain |
| 24 | 29 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/storePepBatch.js` | cross-domain |
| 25 | 29 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/shared/storePepBatch.js` | cross-domain |
| 26 | 28 | `storepepSAAS/server/src/shared/listeners/index.js` | `storepepSAAS/server/src/shared/storePepBatch.js` | shared |
| 27 | 28 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/API/stores/common/processOrders.js` | cross-domain |
| 28 | 28 | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 29 | 28 | `storepepSAAS/client/src/components/form/views/common/batchProcess.js` | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` | ui-components |
| 30 | 27 | `storepepSAAS/server/src/routes/orders.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 31 | 27 | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 32 | 27 | `storepepSAAS/client/src/components/form/views/common/moreFilters/filterMenu.js` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 33 | 27 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/client/src/components/form/views/common/moreFilters/filterMenu.js` | ui-components |
| 34 | 26 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/routes/products.js` | cross-domain |
| 35 | 26 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/shared/customLabels/customLabel.js` | cross-domain |
| 36 | 26 | `storepepSAAS/client/public/css/style.css` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 37 | 26 | `storepepSAAS/client/public/css/style.css` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 38 | 25 | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` | `storepepSAAS/server/src/storePepConstants.js` | cross-domain |
| 39 | 25 | `storepepSAAS/server/src/shared/listeners/index.js` | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | cross-domain |
| 40 | 25 | `storepepSAAS/server/src/shared/API/stores/common/processOrders.js` | `storepepSAAS/server/src/storePepConstants.js` | cross-domain |
| 41 | 25 | `storepepSAAS/server/src/models/orders.js` | `storepepSAAS/server/src/storePepConstants.js` | cross-domain |
| 42 | 25 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/listeners/socketEventPublishingListener.js` | cross-domain |
| 43 | 25 | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | cross-domain |
| 44 | 25 | `storepepSAAS/client/src/components/form/views/common/batchProcess.js` | `storepepSAAS/server/src/routes/batchProcess.js` | cross-domain |
| 45 | 25 | `storepepSAAS/client/src/components/form/views/common/batchProcess.js` | `storepepSAAS/server/featureToggles.json` | cross-domain |
| 46 | 24 | `storepepSAAS/server/src/shared/listeners/index.js` | `storepepSAAS/server/src/storePepConstants.js` | cross-domain |
| 47 | 24 | `storepepSAAS/server/src/models/orders.js` | `storepepSAAS/server/src/models/ordersMaster.js` | models |
| 48 | 24 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/batchProcessHelper.js` | cross-domain |
| 49 | 24 | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` | `storepepSAAS/server/src/routes/batchProcess.js` | cross-domain |
| 50 | 24 | `storepepSAAS/client/src/components/form/views/common/batchProcessTable.js` | `storepepSAAS/server/src/routes/batchProcess.js` | cross-domain |

---

## By Domain

> **Cross-domain** pairs have the largest blast radius.

### Cross-Domain (3720 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 133 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 50 | `storepepSAAS/client/src/components/form/settings/carriers/getDefaultValues.js` | `storepepSAAS/server/src/shared/settings/carrierRequiredFields.js` |
| 45 | `storepepSAAS/server/src/models/carriers.js` | `storepepSAAS/server/src/shared/settings/carrierRequiredFields.js` |
| 45 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/shared/listeners/index.js` |
| 44 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/listeners/index.js` |
| 44 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/routes/orders.js` |
| 44 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 43 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/server/featureToggles.json` |
| 40 | `storepepSAAS/client/src/components/form/settings/carriers/getDefaultValues.js` | `storepepSAAS/server/src/models/carriers.js` |
| 38 | `storepepSAAS/client/src/utils/constants.js` | `storepepSAAS/server/featureToggles.json` |
| 37 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 36 | `storepepSAAS/server/src/models/orders.js` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` |
| 35 | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` | `storepepSAAS/server/featureToggles.json` |
| 34 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/models/orders.js` |
| 34 | `storepepSAAS/client/src/utils/constants.js` | `storepepSAAS/server/src/storePepConstants.js` |
| 33 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` |
| 33 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/server/src/routes/orders.js` |
| 32 | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | `storepepSAAS/server/src/storePepConstants.js` |
| 32 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/customLabels/customLabel.js` |
| 30 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` |

_...and 3700 more. Run `query` for the full list._

### Carriers (75 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 9 | `storepepSAAS/server/src/shared/API/carriers/fedExRest/requestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/fedExRest/shipmentHelper.js` |
| 9 | `storepepSAAS/server/src/shared/API/carriers/delhivery/featureLoader.js` | `storepepSAAS/server/src/shared/API/carriers/delhivery/labelBuilder.js` |
| 9 | `storepepSAAS/server/src/shared/API/carriers/blueDart/blueDartRequestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/blueDart/labelBuilder.js` |
| 8 | `storepepSAAS/server/src/shared/API/carriers/uspsRest/remoteApi.js` | `storepepSAAS/server/src/shared/API/carriers/uspsRest/shipmentHelper.js` |
| 8 | `storepepSAAS/server/src/shared/API/carriers/auPostMyPostBusiness/requestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/australiaPost/australiaPostRequestBuilder.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/delhivery/helperFunctions.js` | `storepepSAAS/server/src/shared/API/carriers/delhivery/labelBuilder.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryShipmentHelper.js` | `storepepSAAS/server/src/shared/API/carriers/xpressbees/shipmentHelper.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryRequestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/xpressbees/shipmentHelper.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryRequestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryShipmentHelper.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/blueDart/helperFunctions.js` | `storepepSAAS/server/src/shared/API/carriers/xpressbees/shipmentHelper.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/blueDart/helperFunctions.js` | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryShipmentHelper.js` |
| 7 | `storepepSAAS/server/src/shared/API/carriers/blueDart/helperFunctions.js` | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryRequestBuilder.js` |
| 6 | `storepepSAAS/server/src/shared/API/carriers/fedex/fedexRequestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/fedex/fedexShipmentHelper.js` |
| 6 | `storepepSAAS/server/src/shared/API/carriers/fedExRest/remoteApi.js` | `storepepSAAS/server/src/shared/API/carriers/fedExRest/requestBuilder.js` |
| 6 | `storepepSAAS/server/src/shared/API/carriers/blueDart/blueDartRequestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/blueDart/helperFunctions.js` |
| 5 | `storepepSAAS/server/src/shared/API/carriers/xpressbees/requestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/xpressbees/shipmentHelper.js` |
| 5 | `storepepSAAS/server/src/shared/API/carriers/fedex/featureLoader.js` | `storepepSAAS/server/src/shared/API/carriers/fedex/fedexRequestBuilder.js` |
| 5 | `storepepSAAS/server/src/shared/API/carriers/fedExRest/servicesAndBoxesHelper.js` | `storepepSAAS/server/src/shared/API/carriers/fedExRest/shipmentHelper.js` |
| 5 | `storepepSAAS/server/src/shared/API/carriers/fedExRest/requestBuilder.js` | `storepepSAAS/server/src/shared/API/carriers/fedExRest/servicesAndBoxesHelper.js` |
| 5 | `storepepSAAS/server/src/shared/API/carriers/delhivery/delhiveryShipmentHelper.js` | `storepepSAAS/server/src/shared/API/carriers/xpressbees/requestBuilder.js` |

_...and 55 more. Run `query` for the full list._

### Orders (73 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 21 | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/app/orderDiffsServices.js` |
| 11 | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | `storepepSAAS/server/src/shared/orders/processOrderHelper.js` |
| 10 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/orderDiffsServices.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/app/parse.js` |
| 9 | `storepepSAAS/server/src/shared/orders/orderUpdates/notifier/index.js` | `storepepSAAS/server/src/shared/orders/orderUpdates/notifier/notifySubOrderUUIDUpdated.js` |
| 9 | `storepepSAAS/server/src/shared/orders/orderMessages/app/orderMessagesTranslator.js` | `storepepSAAS/server/src/shared/orders/orderMessages/app/translators/ShippingErrorTranslator.js` |
| 9 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/parse.js` | `storepepSAAS/server/src/shared/orders/processOrderHelper.js` |
| 9 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/orderDiffsServices.js` | `storepepSAAS/server/src/shared/orders/processOrderHelper.js` |
| 9 | `storepepSAAS/server/src/shared/orders/events/index.js` | `storepepSAAS/server/src/shared/orders/orderUpdates/notifier/notifySubOrderUUIDUpdated.js` |
| 9 | `storepepSAAS/server/src/shared/orders/events/index.js` | `storepepSAAS/server/src/shared/orders/orderUpdates/notifier/index.js` |
| 9 | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/app/parse.js` |
| 9 | `storepepSAAS/server/src/shared/orders/CustomsDataTransformer.js` | `storepepSAAS/server/src/shared/orders/orderDataEnhancer.js` |
| 8 | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | `storepepSAAS/server/src/shared/orders/processCanceledOrders.js` |
| 8 | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | `storepepSAAS/server/src/shared/orders/events/index.js` |
| 7 | `storepepSAAS/server/src/shared/orders/events/index.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/fetauresLoader.js` |
| 7 | `storepepSAAS/server/src/shared/orders/bulkactionHelper.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/fetauresLoader.js` |
| 6 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/orderDiffsServices.js` | `storepepSAAS/server/src/shared/orders/orderUpdateService.js` |
| 6 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/index.js` | `storepepSAAS/server/src/shared/orders/orderUpdateService.js` |
| 6 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/index.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/app/orderDiffsServices.js` |
| 6 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/batch/notifier/orderDiffsBatchItemConcludedProxy.js` | `storepepSAAS/server/src/shared/orders/orderUpdateService.js` |
| 6 | `storepepSAAS/server/src/shared/orders/orderDiffs/app/batch/notifier/orderDiffsBatchItemConcludedProxy.js` | `storepepSAAS/server/src/shared/orders/orderDiffs/app/orderDiffsServices.js` |

_...and 53 more. Run `query` for the full list._

### Shared (658 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 28 | `storepepSAAS/server/src/shared/listeners/index.js` | `storepepSAAS/server/src/shared/storePepBatch.js` |
| 22 | `storepepSAAS/server/src/shared/listeners/index.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 21 | `storepepSAAS/server/src/shared/API/stores/common/processOrders.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 20 | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` |
| 20 | `storepepSAAS/server/src/shared/listeners/socketEventPublishingListener.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 20 | `storepepSAAS/server/src/shared/API/stores/common/processOrders.js` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` |
| 16 | `storepepSAAS/server/src/shared/batchProcessHelper.js` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` |
| 16 | `storepepSAAS/server/src/shared/batchProcessHelper.js` | `storepepSAAS/server/src/shared/listeners/index.js` |
| 15 | `storepepSAAS/server/src/shared/API/stores/shopify/featureLoader.js` | `storepepSAAS/server/src/shared/API/stores/shopify/mapper/shopifyToStorepepOrderMapper.js` |
| 14 | `storepepSAAS/server/src/shared/batchProcessHelper.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 14 | `storepepSAAS/server/src/shared/batch/featureLoader.js` | `storepepSAAS/server/src/shared/storePepBatch.js` |
| 14 | `storepepSAAS/server/src/shared/batch/featureLoader.js` | `storepepSAAS/server/src/shared/listeners/index.js` |
| 14 | `storepepSAAS/server/src/shared/API/stores/woocommerce/WooCommerceStore.js` | `storepepSAAS/server/src/shared/API/stores/woocommerce/batch/WoocommerceProductImport.js` |
| 14 | `storepepSAAS/server/src/shared/API/stores/shopify/ShopifyStore.js` | `storepepSAAS/server/src/shared/API/stores/shopify/products/ShopifyProductService.js` |
| 14 | `storepepSAAS/server/src/shared/API/stores/common/processOrders.js` | `storepepSAAS/server/src/shared/listeners/socketEventPublishingListener.js` |
| 14 | `storepepSAAS/server/src/shared/API/stores/common/processOrders.js` | `storepepSAAS/server/src/shared/listeners/index.js` |
| 13 | `storepepSAAS/server/src/shared/listeners/socketEventPublishingListener.js` | `storepepSAAS/server/src/shared/storepepOrderSplitter/orderSplitEngine.js` |
| 12 | `storepepSAAS/server/src/shared/settings/carrierRequiredFields.js` | `storepepSAAS/server/src/shared/storepepHelperFunctions/printSettingsHelperFunctions.js` |
| 12 | `storepepSAAS/server/src/shared/listeners/index.js` | `storepepSAAS/server/src/shared/uploadDocumentsForOrders.js` |
| 12 | `storepepSAAS/server/src/shared/batchProcessHelper.js` | `storepepSAAS/server/src/shared/storePepBatch.js` |

_...and 638 more. Run `query` for the full list._

### Routes (38 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 9 | `storepepSAAS/server/src/routes/products.js` | `storepepSAAS/server/src/routes/webhooks.js` |
| 7 | `storepepSAAS/server/src/routes/internalOrderWebhook.js` | `storepepSAAS/server/src/routes/orders.js` |
| 7 | `storepepSAAS/server/src/routes/internal/index.js` | `storepepSAAS/server/src/routes/internal/shipmentBatches.js` |
| 7 | `storepepSAAS/server/src/routes/batchProcess.js` | `storepepSAAS/server/src/routes/internal/shipmentBatches.js` |
| 7 | `storepepSAAS/server/src/routes/batchProcess.js` | `storepepSAAS/server/src/routes/internal/index.js` |
| 6 | `storepepSAAS/server/src/routes/batchProcess.js` | `storepepSAAS/server/src/routes/orders.js` |
| 6 | `storepepSAAS/server/src/routes/batchProcess.js` | `storepepSAAS/server/src/routes/internalOrderWebhook.js` |
| 4 | `storepepSAAS/server/src/routes/multiCarrierConnector.js` | `storepepSAAS/server/src/routes/storepepConnector.js` |
| 4 | `storepepSAAS/server/src/routes/magentoStorepepConnector.js` | `storepepSAAS/server/src/routes/storepepConnector.js` |
| 4 | `storepepSAAS/server/src/routes/internal/carrier.js` | `storepepSAAS/server/src/routes/internal/carrierService.js` |
| 4 | `storepepSAAS/server/src/routes/internal/batch.js` | `storepepSAAS/server/src/routes/internal/carrierService.js` |
| 4 | `storepepSAAS/server/src/routes/internal/batch.js` | `storepepSAAS/server/src/routes/internal/carrier.js` |
| 3 | `storepepSAAS/server/src/routes/magentoStorepepConnector.js` | `storepepSAAS/server/src/routes/multiCarrierConnector.js` |
| 3 | `storepepSAAS/server/src/routes/internal/index.js` | `storepepSAAS/server/src/routes/storepepConnector.js` |
| 3 | `storepepSAAS/server/src/routes/internal/index.js` | `storepepSAAS/server/src/routes/multiCarrierConnector.js` |
| 3 | `storepepSAAS/server/src/routes/internal/index.js` | `storepepSAAS/server/src/routes/magentoStorepepConnector.js` |
| 3 | `storepepSAAS/server/src/routes/internal/document.js` | `storepepSAAS/server/src/routes/pickList.js` |
| 3 | `storepepSAAS/server/src/routes/internal/document.js` | `storepepSAAS/server/src/routes/manifest.js` |
| 3 | `storepepSAAS/server/src/routes/internal/carrierService.js` | `storepepSAAS/server/src/routes/internal/index.js` |
| 3 | `storepepSAAS/server/src/routes/internal/carrier.js` | `storepepSAAS/server/src/routes/internal/index.js` |

_...and 18 more. Run `query` for the full list._

### Models (6 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 24 | `storepepSAAS/server/src/models/orders.js` | `storepepSAAS/server/src/models/ordersMaster.js` |
| 9 | `storepepSAAS/server/src/models/productHSCodes.js` | `storepepSAAS/server/src/models/products.js` |
| 7 | `storepepSAAS/server/src/models/orders.js` | `storepepSAAS/server/src/models/shipmentBatches.js` |
| 7 | `storepepSAAS/server/src/models/carriers.js` | `storepepSAAS/server/src/models/upsSettings.js` |
| 3 | `storepepSAAS/server/src/models/products.js` | `storepepSAAS/server/src/models/stores.js` |
| 3 | `storepepSAAS/server/src/models/productHSCodes.js` | `storepepSAAS/server/src/models/stores.js` |

### Redux-Actions (47 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 9 | `storepepSAAS/client/src/actions/orders/ordersActions.js` | `storepepSAAS/client/src/actions/productsActions.js` |
| 8 | `storepepSAAS/client/src/actions/common.js` | `storepepSAAS/client/src/actions/types.js` |
| 5 | `storepepSAAS/client/src/actions/touchless-print/index.js` | `storepepSAAS/client/src/actions/touchless-print/types.js` |
| 5 | `storepepSAAS/client/src/actions/touchless-print/actions.js` | `storepepSAAS/client/src/actions/touchless-print/types.js` |
| 5 | `storepepSAAS/client/src/actions/touchless-print/actions.js` | `storepepSAAS/client/src/actions/touchless-print/index.js` |
| 3 | `storepepSAAS/client/src/actions/product-custom-values/index.js` | `storepepSAAS/client/src/actions/product-custom-values/type.js` |
| 3 | `storepepSAAS/client/src/actions/product-custom-values/api.js` | `storepepSAAS/client/src/actions/product-custom-values/type.js` |
| 3 | `storepepSAAS/client/src/actions/product-custom-values/api.js` | `storepepSAAS/client/src/actions/product-custom-values/index.js` |
| 3 | `storepepSAAS/client/src/actions/product-custom-values/actions.js` | `storepepSAAS/client/src/actions/product-custom-values/type.js` |
| 3 | `storepepSAAS/client/src/actions/product-custom-values/actions.js` | `storepepSAAS/client/src/actions/product-custom-values/index.js` |
| 3 | `storepepSAAS/client/src/actions/product-custom-values/actions.js` | `storepepSAAS/client/src/actions/product-custom-values/api.js` |
| 3 | `storepepSAAS/client/src/actions/print/index.js` | `storepepSAAS/client/src/actions/print/types.js` |
| 3 | `storepepSAAS/client/src/actions/print/actions.js` | `storepepSAAS/client/src/actions/print/types.js` |
| 3 | `storepepSAAS/client/src/actions/print/actions.js` | `storepepSAAS/client/src/actions/print/index.js` |
| 3 | `storepepSAAS/client/src/actions/order/types.js` | `storepepSAAS/client/src/actions/print/types.js` |
| 3 | `storepepSAAS/client/src/actions/order/types.js` | `storepepSAAS/client/src/actions/print/index.js` |
| 3 | `storepepSAAS/client/src/actions/order/types.js` | `storepepSAAS/client/src/actions/print/actions.js` |
| 3 | `storepepSAAS/client/src/actions/manifest/types.js` | `storepepSAAS/client/src/actions/print/types.js` |
| 3 | `storepepSAAS/client/src/actions/manifest/types.js` | `storepepSAAS/client/src/actions/print/index.js` |
| 3 | `storepepSAAS/client/src/actions/manifest/types.js` | `storepepSAAS/client/src/actions/print/actions.js` |

_...and 27 more. Run `query` for the full list._

### Redux-Reducers (4 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 6 | `storepepSAAS/client/src/reducers/common.js` | `storepepSAAS/client/src/reducers/rootReducers.js` |
| 5 | `storepepSAAS/client/src/reducers/rootReducers.js` | `storepepSAAS/client/src/reducers/touchlessPrint.js` |
| 5 | `storepepSAAS/client/src/reducers/common.js` | `storepepSAAS/client/src/reducers/touchlessPrint.js` |
| 3 | `storepepSAAS/client/src/reducers/productCustomsPrices.js` | `storepepSAAS/client/src/reducers/rootReducers.js` |

### Ui-Components (209 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 28 | `storepepSAAS/client/src/components/form/views/common/batchProcess.js` | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` |
| 27 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/client/src/components/form/views/common/moreFilters/filterMenu.js` |
| 23 | `storepepSAAS/client/src/components/form/views/common/batchProcessTable.js` | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` |
| 22 | `storepepSAAS/client/src/components/form/views/common/batchProcess.js` | `storepepSAAS/client/src/components/form/views/common/batchProcessTable.js` |
| 19 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/client/src/components/form/views/common/ordersTable.js` |
| 18 | `storepepSAAS/client/src/components/form/views/common/orderUpdateDetails.js` | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` |
| 14 | `storepepSAAS/client/src/components/form/views/bulkActions/bulkActionConditions.js` | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` |
| 14 | `storepepSAAS/client/src/components/form/views/bulkActions/bulkActionConditions.js` | `storepepSAAS/client/src/components/form/views/common/batchProcess.js` |
| 13 | `storepepSAAS/client/src/components/form/views/common/ordersTable.js` | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` |
| 13 | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` | `storepepSAAS/client/src/components/form/views/common/ordersTable.js` |
| 11 | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderUpdateIcon.js` |
| 11 | `storepepSAAS/client/src/components/form/views/common/orderUpdateDetails.js` | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderUpdateIcon.js` |
| 10 | `storepepSAAS/client/src/components/form/views/summary/order-summary/OrderSummaryContainerNew.js` | `storepepSAAS/client/src/components/form/views/summary/orderSummaryContainer.js` |
| 10 | `storepepSAAS/client/src/components/form/views/common/ordersTable.js` | `storepepSAAS/client/src/components/form/views/summary/orderSummaryContainer.js` |
| 10 | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` | `storepepSAAS/client/src/components/pages/header/searchBar.js` |
| 10 | `storepepSAAS/client/src/components/form/views/common/batchProcessTable.js` | `storepepSAAS/client/src/components/pages/header/searchBar.js` |
| 10 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/client/src/components/form/views/common/orders/quickActions.js` |
| 9 | `storepepSAAS/client/src/components/form/views/common/batchProcessTable.js` | `storepepSAAS/client/src/components/form/views/common/ordersTable.js` |
| 9 | `storepepSAAS/client/src/components/form/views/allorders.js` | `storepepSAAS/client/src/components/form/views/common/batchProcessTable.js` |
| 9 | `storepepSAAS/client/src/components/form/settings/carriers/australiaPost.js` | `storepepSAAS/client/src/components/form/settings/carriers/getDefaultValues.js` |

_...and 189 more. Run `query` for the full list._

### Client (21 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 5 | `storepepSAAS/client/src/componentWrapper.js` | `storepepSAAS/client/src/storepepUsersRoutes.js` |
| 4 | `storepepSAAS/client/src/utils/sentry/index.js` | `storepepSAAS/client/src/utils/sentry/tracker.js` |
| 4 | `storepepSAAS/client/src/storepepUsersRoutes.js` | `storepepSAAS/client/src/utils/constants.js` |
| 4 | `storepepSAAS/client/src/reduxStore.js` | `storepepSAAS/client/src/utils/sentry/tracker.js` |
| 4 | `storepepSAAS/client/src/reduxStore.js` | `storepepSAAS/client/src/utils/sentry/index.js` |
| 4 | `storepepSAAS/client/src/integratedStoresAndCarriers.js` | `storepepSAAS/client/src/utils/constants.js` |
| 4 | `storepepSAAS/client/src/integratedStoresAndCarriers.js` | `storepepSAAS/client/src/storepepUsersRoutes.js` |
| 4 | `storepepSAAS/client/src/index.js` | `storepepSAAS/client/src/utils/sentry/tracker.js` |
| 4 | `storepepSAAS/client/src/index.js` | `storepepSAAS/client/src/utils/sentry/index.js` |
| 4 | `storepepSAAS/client/src/index.js` | `storepepSAAS/client/src/reduxStore.js` |
| 4 | `storepepSAAS/client/src/componentWrapper.js` | `storepepSAAS/client/src/utils/constants.js` |
| 4 | `storepepSAAS/client/src/componentWrapper.js` | `storepepSAAS/client/src/integratedStoresAndCarriers.js` |
| 3 | `storepepSAAS/client/src/utils/sentry/vitals.js` | `storepepSAAS/client/src/utils/utilFunctions.js` |
| 3 | `storepepSAAS/client/src/utils/sentry/tracker.js` | `storepepSAAS/client/src/utils/utilFunctions.js` |
| 3 | `storepepSAAS/client/src/utils/sentry/tracker.js` | `storepepSAAS/client/src/utils/sentry/vitals.js` |
| 3 | `storepepSAAS/client/src/utils/sentry/index.js` | `storepepSAAS/client/src/utils/utilFunctions.js` |
| 3 | `storepepSAAS/client/src/utils/sentry/index.js` | `storepepSAAS/client/src/utils/sentry/vitals.js` |
| 3 | `storepepSAAS/client/src/reduxStore.js` | `storepepSAAS/client/src/utils/utilFunctions.js` |
| 3 | `storepepSAAS/client/src/reduxStore.js` | `storepepSAAS/client/src/utils/sentry/vitals.js` |
| 3 | `storepepSAAS/client/src/index.js` | `storepepSAAS/client/src/utils/utilFunctions.js` |

_...and 1 more. Run `query` for the full list._

### Server (381 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 105 | `storepepSAAS/server/config.json` | `storepepSAAS/server/featureToggles.json` |
| 68 | `storepepSAAS/server/featureToggles.json` | `storepepSAAS/server/src/storePepConstants.js` |
| 35 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/storePepConstants.js` |
| 12 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/modules/carrierRegistration/services/carrierRegistrationService.js` |
| 10 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/modules/order-presets/domain/OrderPresets.js` |
| 10 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/modules/common/s3/helper.js` |
| 10 | `storepepSAAS/server/config.json` | `storepepSAAS/server/src/middlewares/authenticateInternalApi.js` |
| 9 | `storepepSAAS/server/src/storePepConstants.js` | `storepepSAAS/server/src/supportScripts/subscribeToShopifyInventoryWebhooks.js` |
| 9 | `storepepSAAS/server/src/modules/package/service/PackageService.js` | `storepepSAAS/server/src/modules/package/service/index.js` |
| 9 | `storepepSAAS/server/src/modules/package/service/DocumentViewService.js` | `storepepSAAS/server/src/modules/package/service/index.js` |
| 9 | `storepepSAAS/server/src/modules/package/service/DocumentViewService.js` | `storepepSAAS/server/src/modules/package/service/PackageService.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/index.js` | `storepepSAAS/server/src/modules/package/service/index.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/index.js` | `storepepSAAS/server/src/modules/package/service/PackageService.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/index.js` | `storepepSAAS/server/src/modules/package/service/DocumentViewService.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/PackagesViewRepository.js` | `storepepSAAS/server/src/modules/package/service/index.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/PackagesViewRepository.js` | `storepepSAAS/server/src/modules/package/service/PackageService.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/PackagesViewRepository.js` | `storepepSAAS/server/src/modules/package/service/DocumentViewService.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/PackagesViewRepository.js` | `storepepSAAS/server/src/modules/package/projection/index.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/OrderDocumentsViewRepository.js` | `storepepSAAS/server/src/modules/package/service/index.js` |
| 9 | `storepepSAAS/server/src/modules/package/projection/OrderDocumentsViewRepository.js` | `storepepSAAS/server/src/modules/package/service/PackageService.js` |

_...and 361 more. Run `query` for the full list._

### Other (1 pairs)

| Co-changes | File A | File B |
|------------|--------|--------|
| 3 | `storepepSAAS/client/npm-shrinkwrap.json` | `storepepSAAS/client/package.json` |

---

## Noise Filter

| Excluded | Reason |
|----------|--------|
| `package-lock.json`, `yarn.lock` | Changed in nearly every dependency update |
| `migrations/` | One-off batch additions — not structural coupling |
| `*.test.js`, `*.spec.ts` | Mirror their source file |
| `/dist/`, `/build/` | Generated files |
| `*.md`, `CHANGELOG` | Changed opportunistically in PRs |
| Commits touching >30 files | Mass reformats / lint sweeps |

---

## Related

- [Features & Test Coverage](../features.md)
- [Architecture Overview](overview.md)
- [Backend Architecture](backend-architecture.md)
