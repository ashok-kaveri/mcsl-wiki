---
title: Order Bulk Actions
category: module
domain: orders
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Order Bulk Actions

## Overview

Bulk actions allow users to perform operations on multiple orders simultaneously, improving efficiency for high-volume merchants. StorePep supports 40+ bulk action types covering status changes, carrier selection, packaging, special services, and more.

**Location**: `server/src/shared/orders/bulkactionHelper.js:1-2500+`

**Primary API**: `POST /api/orders/bulk-action`

## Architecture

### Bulk Action Flow

1. **User selects orders** in UI (checkboxes in order table)
2. **User selects action** from dropdown/menu
3. **Frontend dispatches** Redux action with order IDs and action type
4. **Backend processes** each order in the selection
5. **Socket.io pushes** real-time updates per order processed
6. **Frontend updates** order table incrementally

### Common Pattern

All bulk actions follow this signature:
```javascript
module.exports.actionName = async (
  orders,           // Array of order objects or IDs
  accountUUID,      // Account identifier
  currentUser,      // User performing action
  vendorUUID,       // Vendor identifier (multi-vendor scenarios)
  newSocketEvent,   // Socket.io emitter function
  ...additionalParams
) => {
  // Process each order
  // Update database
  // Emit socket events
  // Return success/error
};
```

## Status Management Actions

### Change Status to Initial

**Function**: `changeOrderStatusToInitialBulkAction`

**Purpose**: Reset orders to `INITIAL` state, clearing processing data

**When used**:
- Undo label generation
- Clear failed processing attempts
- Reset automation failures

**What gets reset**:
- `storePepStatus = INITIAL`
- Clear carrier selection
- Clear package configurations
- Clear label summaries
- Clear automation summaries
- Optional: preserve specific fields via `fieldsNotToReset` param

**Parameters**:
- `fieldsNotToReset` - Array of field names to preserve during reset
- `isBulkAction` - Boolean flag (default: true)
- `isWebhook` - Boolean, true if triggered by store webhook

### Change Status to Processing

**Function**: `changeOrderStatusToProcessingBulkAction`

**Purpose**: Move orders to `PROCESSING` state, triggering automation and rate fetching

**Flow**:
1. Validate order eligibility (must be in `INITIAL`, `PROCESSING`, or `LABEL_FAILURE`)
2. Set `storePepStatus = PROCESSING`
3. Add ship-from address (if not set)
4. Add product info to line items
5. Run automation rules
6. Fetch carrier rates
7. Select service based on `serviceSelectionMode`
8. Validate shipping address (if enabled)

**Dependencies**:
- `addShipFromAddressToOrders` - Apply default warehouse address
- `addProductsInfoToOrders` - Enrich line items with product data
- `StorepepAutomationManager` - Execute automation rules
- `addRateInfoToOrder` - Fetch carrier quotes
- `addServiceInfoToOrder` - Select best rate
- `addressCorrectionForOrders` - Validate addresses

### Mark as Not to Ship

**Function**: `markAsNotToShipBulkAction`

**Purpose**: Flag orders to skip shipping (hold, cancel, local pickup)

**Sets**:
- `storePepStatus = NOT_TO_SHIP`
- Removes from pending batches
- Optionally sync to store with custom status

### Reprocess Orders

**Function**: `reprocessOrders`

**Purpose**: Retry processing for failed orders (automation errors, rate fetch failures)

**When used**:
- After fixing carrier credentials
- After updating automation rules
- Manual retry for transient failures

**Eligibility**:
```javascript
const isOrderEligibleForReprocessing = {
  [constants.INITIAL]: true,
  [constants.PROCESSING]: true,
  [constants.LABEL_FAILURE]: true,
};
```

## Carrier & Service Selection

### Change Carrier

**Function**: `changeCarrierBulkAction`

**Purpose**: Switch carrier for selected orders

**Flow**:
1. Update `carrierIdSelected`, `carrierTypeSelected`
2. Re-fetch rates for new carrier
3. Auto-select cheapest service (or user-specified)
4. Update `availableCarrierAndService`

**Use cases**:
- Carrier outage/unavailable
- Better rates with alternative carrier
- Customer preference

### Select Carrier

**Function**: `selectCarrierBulkAction`

**Purpose**: Explicitly choose carrier and service for orders

**Parameters**:
- `carrierIdSelected` - Carrier UUID
- `carrierTypeSelected` - Carrier type (FedEx, UPS, etc.)
- `serviceIdSelected` - Service code

**Difference from Change Carrier**: This sets exact carrier/service without re-rating

### Refresh Shipping Rates

**Function**: `refreshShippingRatesBulkAction`

**Purpose**: Re-fetch rates from all configured carriers

**When used**:
- Rates stale (fetched more than X hours ago)
- Carrier pricing changed
- Package weight/dimensions updated

**Flow**:
1. For each order, call `addRateInfoToOrder()`
2. Update `availableCarrierAndService` array
3. Re-apply service selection mode (cheapest, etc.)
4. Socket notification with updated rates

## Packaging Actions

### Change Stored Package

**Function**: `changeStoredPackageBulkAction`

**Purpose**: Modify package configuration for orders (box size, weight, dimensions)

**Parameters**:
- Package template ID or custom dimensions
- Weight override
- Number of packages

**Updates**:
- `totalWeight`
- `totalPackage`
- Package collection entries

### Save Manual Packages

**Function**: `saveManualPackagesBulkAction`

**Purpose**: Override automatic packaging with manual package definitions

**Use case**: User wants specific box sizes/quantities instead of auto-calculated

**Triggers**: Rate refresh (package dimensions affect shipping cost)

### Add Stored Packages with Tracking Details

**Function**: `addStoredpackagesWithTrackingDetailsBulkAction`

**Purpose**: Manually add package details with pre-existing tracking numbers

**Use case**: Labels generated externally, importing tracking into StorePep

## Address Management

### Validate Shipping Addresses

**Function**: `validateShippingAddressesBulkAction`

**Purpose**: Validate and correct shipping addresses via carrier APIs

**Flow**:
1. Call `addressCorrectionForOrders(orders)`
2. Store corrected addresses in `correctedShippingAddresses[]`
3. Flag `isShippingAddressCorrectionRequired: true` if issues found
4. Socket update with validation results

**Integration**: Uses carrier address validation APIs (FedEx, UPS, USPS)

**See also**: [Order Address Management](./order-address-management.md)

### Set Ship-From Address

**Function**: `setShipFromAddressBulkAction`

**Purpose**: Assign warehouse/origin address to orders

**Parameters**:
- `addressUUID` - Saved address identifier
- Or full address object

**Updates**: `order.shipFromAddress`

**Triggers**: Rate refresh (origin affects shipping cost)

### Set Display From Address

**Function**: `setDisplayFromAddressBulkAction`

**Purpose**: Set return address shown on label (may differ from ship-from for branding)

**Updates**: `order.displayFromAddress`

## Special Services (Carrier-Specific)

### FedEx Special Services

**Function**: `addFedExSpecialServicesBulkAction`

**Services**:
- Saturday delivery
- Signature required
- Hold at FedEx location
- Dry ice shipment
- Alcohol shipment
- COD (cash on delivery)

**Storage**: `order.fedexSpecialServices[]`

### DHL Special Services

**Function**: `addDhlSpecialServicesBulkAction`

**Services**:
- Signature required
- Shipper's reference
- Paperless trade
- Duties paid by receiver
- Saturday delivery

**Storage**: `order.dhlSpecialServices.specialServices[]`

### DHL Sweden Special Services

**Function**: `addDhlSwedenSpecialServicesBulkAction`

**Regional variant** for DHL Sweden-specific services

### Canada Post Special Services

**Function**: `addCanadaPostSpecialServicesBulkAction`

**Services**:
- Signature required
- Card for pickup
- Do not safe drop
- Leave at door
- Deliver to post office

**Storage**: `order.canadaPostSpecialServices[]`

### PostNord Special Services

**Function**: `addPostNordSpecialServicesBulkAction`

**Services**:
- Service point delivery
- CN23 customs documents
- Quarantine certificate info
- Customs reference IDs

**Storage**: `order.postNordSpecialServices{}`

### Other Carrier Special Services

Similar functions for:
- **Aramex**: `addAramexSpecialServicesBulkAction`
- **Purolator**: `addPurolatorSpecialServicesBulkAction`
- **Canpar**: `addCanparSpecialServicesBulkAction`
- **XPO Logistics**: `addXpoLogisticsSpecialServicesBulkAction`
- **MyFastway**: `addMyFastwaySpecialServicesBulkAction`
- **New Zealand Post**: `addNewZealandPostSpecialServicesBulkAction`

## Service Point / Hold at Location

### Get FedEx Hold at Location Data

**Function**: `getFedexHoldAtLocationData`

**Purpose**: Search for FedEx locations near delivery address

**Returns**: List of FedEx Office, FedEx Ship Center, Walgreens locations

### Set Hold at Location

**Function**: `setHoldAtLocationBulkAction`

**Purpose**: Configure order for customer pickup at carrier location

**Parameters**:
- Location ID
- Location address
- Contact info

**Carriers supporting**: FedEx, UPS

### Remove Hold at Location

**Function**: `removeHoldAtLocationBulkAction`

**Purpose**: Revert to home delivery

### Get DHL Service Points

**Function**: `getDHLServicePoints`

**Purpose**: Find DHL Packstation or retail locations

### Set DHL Service Points

**Function**: `setDHLServicePoints`

**Purpose**: Set order for delivery to DHL service point

### Get PostNord Service Points

**Function**: `getPostNordServicePoints`

**Purpose**: Find PostNord pickup points

### Set PostNord Service Points

**Function**: `setPostNordServicePoints`

**Purpose**: Configure PostNord service point delivery

## Date & Scheduling Actions

### Change Shipping Date

**Function**: `changeOrderChangeShippingDateBulkAction`

**Purpose**: Set future shipping date for orders

**Parameters**:
- `dateToSet` - Target shipping date
- `UTCTimeZoneOffset` - Timezone adjustment

**Updates**: `order.storepepShippingDate`

**Use case**: Schedule orders for future batch processing

### Set Future Shipping Offset

**Function**: `setFutureShippingoffset`

**Purpose**: Set relative shipping date (e.g., "ship in 3 days")

**Parameters**:
- `offSetValue` - Number of days from today

**Updates**: `order.shippingDateoffSet`

### Set Home Delivery Date

**Function**: `setHomeDeliveryDateBulkAction`

**Purpose**: Request specific delivery date from carrier (if supported)

**Carriers supporting**: FedEx, UPS (premium services)

## International Shipping Actions

### Add Export Details

**Function**: `addExportDetailsBulkAction`

**Purpose**: Add customs/export documentation for international shipments

**Parameters**:
- Export reason (sale, gift, repair, return)
- HS codes
- Country of manufacture
- Customs value

### Add CSB Type

**Function**: `addCsbTypeBulkAction`

**Purpose**: Set Canada-specific shipment type (CSB = Canada Shipment Bureau)

### Add Express Freight Details

**Function**: `addExpressFreightDetailsBulkAction`

**Purpose**: Configure freight-specific options (pallets, LTL)

## Additional Service Options

### Enable Saturday Delivery

**Function**: `enableSaturdayDeliveryResponseBulkAction`

**Purpose**: Request Saturday delivery (carrier premium service)

**Updates**: `order.isSaturdayDeliveryEnabled = true`

### Send Documents Electronically

**Function**: `sendDocumentsElectronicallyBulkAction`

**Purpose**: Use electronic trade documents instead of paper (international)

**Reduces**: Customs clearance time

### Enable Automatic Additional Handling

**Function**: `enableAutomaticAdditionalHandlingBulkAction`

**Purpose**: Apply carrier surcharges for oversized/irregularly shaped packages

**Updates**: `order.isAutomaticAdditionalHandlingEnabled = true`

## Shipment Cancellation

### Cancel Shipment

**Function**: `cancelShipmentBulkAction`

**Purpose**: Void shipping labels and refund postage (if within carrier timeframe)

**Flow**:
1. Call carrier API to void label
2. Update `storePepStatus = LABEL_CANCELLED`
3. Clear tracking numbers
4. Optionally sync to store (mark unfulfilled)
5. Publish `OrderShipmentCancelled` event

**Helper**: `cancelShipmentForThisOrders` from `server/src/shared/cancelShipment.js`

**Time limits**:
- FedEx: Before end-of-day pickup
- UPS: Before pickup scan
- USPS: Before acceptance scan

### Archive Order Shipment

**Function**: `archiveOrderShipmentAction`

**Purpose**: Archive completed/cancelled orders (soft delete)

**Flow**:
1. Archive order: `orderUpdateCommandHandler(CreateArchiveOrderRequest)`
2. Archive packages: `packageUpdateCommandHandler(CreateArchivePackageRequest)`
3. Archive tracking: `trackingOrderUpdateCommandHandler(CreateArchiveTrackingOrderRequest)`
4. Archive fulfillment summaries

**Module-based**: Uses domain modules from `modules/order/`, `modules/package/`, etc.

## Order Update & Sync

### Apply Updates To (from Order Update Service)

**Function**: `applyUpdatesTo`

**Purpose**: Apply order changes from external Order Update Service

**Use case**: Centralized order management across multiple fulfillment centers

### Request Order Update

**Function**: `requestOrderUpdate`

**Purpose**: Trigger order refresh from e-commerce platform

**Flow**:
1. Generate import lock ID
2. Publish `OrderImportStarted` event
3. Call store adapter to fetch order by ID
4. Process via `processImportedOrders()`
5. Publish `OrderImportFinished` event

**Use case**: Customer changed address, need to re-import latest order data

## Frontend Integration

### Bulk Action Dispatcher

**Location**: `client/src/actions/ordersActions.js`

```javascript
export const applyBulkAction = (orderIds, actionType, payload) => dispatch => {
  dispatch({ type: BULK_ACTION_STARTED });

  return axios.post('/api/orders/bulk-action', {
    orderIds,
    actionType,
    ...payload
  })
  .then(response => {
    dispatch({ type: BULK_ACTION_SUCCESS, payload: response.data });
  })
  .catch(error => {
    dispatch({ type: BULK_ACTION_FAILURE, error: error.message });
  });
};
```

### Socket.io Updates

Real-time progress updates per order:
```javascript
socket.on('order:bulk-action-progress', ({ orderId, status, message }) => {
  // Update UI for this specific order
  dispatch(updateOrderInList(orderId, { status, message }));
});
```

## Event Sourcing

**Events Published**:
- `OrderBulkActionCompleted` - After bulk action finishes
- `OrderShipmentCancelled` - On label void
- `OrderImportStarted` / `OrderImportFinished` - On order refresh

**Location**: `server/src/shared/orders/events.js`

## Performance Considerations

### Batch Size Limits

Large bulk actions (100+ orders) are chunked:
```javascript
const CHUNK_SIZE = 50;
for (let i = 0; i < orders.length; i += CHUNK_SIZE) {
  const chunk = orders.slice(i, i + CHUNK_SIZE);
  await processBulkAction(chunk);
  // Socket update after each chunk
}
```

### Parallelization

Independent operations (rate fetching) run in parallel:
```javascript
await Promise.all(orders.map(order => fetchRates(order)));
```

Sequential operations (database updates) run serially to avoid conflicts.

## Error Handling

### Partial Success

If bulk action fails for some orders:
- Successful orders: Committed to DB
- Failed orders: Flagged with error message
- User notified: "Processed 45 of 50 orders, 5 errors"

### Cleanup on Failure

**Helper**: `cleanUpPartialSuccessOrder(order)`

Rolls back incomplete state if action fails mid-process.

## Dependencies

- [Order Lifecycle](./order-lifecycle.md) - Status transitions
- [Order Address Management](./order-address-management.md) - Address validation
- [Carrier Integration](../shipping/carrier-integration.md) (to be created)
- [Automation Rules](../workflows/automation-rules.md) (to be created)
- [Event Sourcing](../../patterns/event-sourcing.md) (to be created)

## Referenced By

- Order management UI components use these actions
- API routes delegate to these functions
- Automation workflows trigger bulk actions programmatically

## Configuration

**Feature Toggles**:
- Address validation on processing
- Auto-rate refresh frequency
- Bulk action size limits

**Account Settings**:
- Default ship-from address
- Service selection mode (cheapest, fastest)
- Carrier preferences

## Test Coverage

**Automated E2E Tests**: 12 Playwright tests covering bulk actions

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| Cancel Shipment | `orderGrid/actionMenu/cancelShipment.spec.ts` | ✅ Passing |
| Change Carrier & Service | `orderGrid/actionMenu/changeCarrierAndService.spec.ts` | ✅ Passing |
| Create Return Label | `orderGrid/actionMenu/createReturnLabel.spec.ts` | ✅ Passing |
| Generate Label from Actions | `orderGrid/actionMenu/generateLabelFromActionsMenu.spec.ts` | ✅ Passing |
| Initial & Reprocess Order | `orderGrid/actionMenu/initialAndReprocessOrder.spec.ts` | ✅ Passing |
| Manual Fulfillment | `orderGrid/actionMenu/manualFulfillment.spec.ts` | ✅ Passing |
| Mark as Not to Ship | `orderGrid/actionMenu/markAsNotToShip.spec.ts` | ✅ Passing |
| Prepare Shipment | `orderGrid/actionMenu/prepareShipment.spec.ts` | ✅ Passing |
| Quick Ship | `orderGrid/actionMenu/quickShip.spec.ts` | ✅ Passing |
| Set Ship From Address | `orderGrid/actionMenu/setShipFromAddress.spec.ts` | ✅ Passing |
| Edit Package from Action Menu | `orderGrid/newEditPackage/newEditPackageFromActionMenu.spec.ts` | ✅ Passing |
| Today's Label Button | `orderGrid/todaysLabelButton/fulfillTodaysOrders.spec.ts` | ✅ Passing |

**Test Coverage**: 12/40+ bulk actions tested (30% coverage)

**Test Suite Location**: `mcsl-test-automation/tests/orderGrid/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Known Issues / Tech Debt

1. **Large file size**: `bulkactionHelper.js` is 2500+ lines - should be split by action category
2. **Inconsistent error handling**: Some functions throw, others return error objects
3. **Mixed async patterns**: Some use async/await, some use callbacks
4. **Socket event naming**: Inconsistent event names across different actions
5. **Limited parallelization**: Many actions could benefit from concurrent processing

## Related Pages

- [Order Lifecycle](./order-lifecycle.md)
- [Order Returns](./order-returns.md)
- [Order Address Management](./order-address-management.md)
- [Batch Processing](../shipping/batch-processing.md) (to be created)
