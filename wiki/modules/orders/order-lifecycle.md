---
title: Order Lifecycle Management
category: module
domain: orders
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Order Lifecycle Management

## Overview

The order lifecycle is the core flow of StorePep - from importing orders from e-commerce platforms, through processing and carrier selection, to label generation and shipment. This document covers the primary order states and the transitions between them.

**Core Flow**: Import → Process → Label Generation → Ship → Track → Complete

## Order States

**Location**: `server/src/storePepConstants.js:278-345`

| State | Constant | Description |
|-------|----------|-------------|
| Initial | `INITIAL` | Order imported from store, not yet processed |
| Processing | `PROCESSING` | Order being prepared for shipping (carrier selection, packaging) |
| Reprocessing | `REPROCESSING` | Order failed automation/validation, being manually reviewed |
| Label Created | `LABEL_CREATED` | Shipping label successfully generated |
| Shipped | `SHIPPED` | Package handed to carrier, tracking active |
| Return Label Created | `RETURN_LABEL_CREATED` | Return label generated for customer return |

**State field**: `order.storePepStatus`

**Last store status**: `order.lastOrderStatus` - The original status from the e-commerce platform (e.g., "processing", "completed" in WooCommerce)

## Order Import

### Import Flow

1. **User initiates import** via UI or webhook from store
2. **API Endpoint**: `POST /api/orders/importorders`
   - **Location**: `server/src/routes/orders.js:471-486`
3. **Store adapter invoked**: Fetches orders from platform (Shopify, WooCommerce, etc.)
4. **Orders processed**: `processImportedOrders()` transforms platform-specific data to StorePep schema
5. **Event published**: `OrderImportStarted` / `OrderImportFinished` events emitted
6. **Socket notification**: Real-time update sent to connected clients

### Import Components

**Store Adapter**:
```javascript
// Location: server/src/shared/storepepAdaptors/StoreAdapter.js
const adaptor = new StoreAdapter();
const currentStoreAdapter = adaptor.getStoreAdapter(storeType);
await currentStoreAdapter.fetchOrders(currentUser, accountUUID, store, callback);
```

**Process Helper**:
- **Location**: `server/src/shared/orders/processOrderHelper.js`
- **Function**: `processImportedOrders(err, masterOrders, childOrders, type, context, importLockContext)`
- **Responsibilities**:
  - Validate order data
  - Transform to StorePep schema
  - Handle master/child order relationships (for split orders)
  - Set initial state (`INITIAL`)
  - Apply account-level defaults (ship-from address, packaging rules)

**Event Publishing**:
```javascript
// Location: server/src/shared/orders/events.js
await notifyOrderImportStatus(importLockId, store, OrderImportStarted);
// ... import processing ...
await notifyOrderImportStatus(importLockId, store, OrderImportFinished);
```

### Import Lock Mechanism

To prevent concurrent imports from the same store:
- **Import Lock ID**: UUID generated per import session
- **Purpose**: Prevents duplicate order creation during simultaneous webhook and manual imports
- **Tracked in**: Import context passed to processing functions

## Order Processing

### Transition: INITIAL → PROCESSING

**Trigger**: User manually clicks "Process" or automation rule executes

**API Endpoint**: `POST /api/orders/bulk-action` (with action type `CHANGE_STATUS_TO_PROCESSING`)

**What happens**:
1. Order status changed to `PROCESSING`
2. Automation rules evaluated (if configured)
3. Carrier and service selection logic runs:
   - Fetch available rates from configured carriers
   - Apply service selection mode (cheapest, fastest, etc.)
   - Store `availableCarrierAndService` array
4. Packaging calculation:
   - Calculate total weight from line items
   - Determine package configuration
   - Apply packing rules (single box, item-based, weight-based)
5. Address validation (if enabled):
   - Validate shipping address via carrier APIs
   - Flag if correction required

**Service Selection Modes** (`order.serviceSelectionMode`):
- `CHEAPEST_RATE` (default) - Select lowest cost carrier/service
- Future: `FASTEST_DELIVERY`, `PREFERRED_CARRIER`

**Location**: `server/src/routes/orders.js` bulk action handlers

### OrderProcessingService

**Location**: `server/src/shared/order/service/OrderProcessingService.js:1-150`

This service handles complex calculations when order quantities change (partial fulfillment scenarios):

**Key Methods**:

1. **`calculateTotals(lineItems, shippingLines, currency)`**
   - Aggregates line item prices
   - Sums discounts across items
   - Consolidates tax lines by title

2. **`recalculateDiscounts(item, originalQuantity)`**
   - Proportionally adjusts discount allocations when quantity changes
   - Updates both `amount` and `amount_set` (multi-currency)

3. **`recalculateTaxes(item, originalQuantity)`**
   - Proportionally adjusts tax amounts per item
   - Updates `price` and `price_set`

4. **`updateTaxLines(orderTaxLines)`**
   - Aggregates taxes from all items
   - Returns total tax amount

5. **`setOrderMoneyFields(order, totals)`**
   - Updates all monetary fields on order
   - Maintains `_set` fields for currency representation

**When used**:
- Partial fulfillment (only shipping some items from an order)
- Order splitting (creating multiple shipments from one order)
- Return processing (adjusting totals when items returned)

## Label Generation

### Transition: PROCESSING → LABEL_CREATED

**Trigger**: User clicks "Generate Label" or auto-generate is enabled

**API Endpoint**: `POST /api/orders/labels` (or similar label generation endpoint)

**Flow**:
1. **Validate order ready**:
   - Carrier and service selected
   - Ship-from address configured
   - Shipping address valid
   - Package details present

2. **Call carrier API**:
   - Location: `server/src/shared/API/carriers/<carrier-name>/`
   - Send shipment request with all details
   - Receive label URL and tracking number

3. **Store label details**:
   - `order.trackingId` - Primary tracking number
   - `order.currentLabelSummaryUUID` - Reference to label document
   - `order.storePepStatus = LABEL_CREATED`

4. **Generate documents**:
   - Shipping label PDF (thermal 4x6 or letter size)
   - Packing slip
   - Commercial invoice (for international)

5. **Sync back to store** (if configured):
   - Update order status on e-commerce platform
   - Add tracking number to order
   - Mark as fulfilled

**Label Summary**:
- Collection: `storepepOrderLabelSummary`
- Stores: Label URL, tracking numbers, carrier details, timestamp
- Referenced by: `order.currentLabelSummaryUUID`

**Helper Function**:
```javascript
// Location: server/src/shared/label-fulfill-order
await labelAndFullfillOrder(order, carrier, service, user);
```

### Auto-Generate Label

**Field**: `order.isAutoGenerateLabelEnable`

When `true`:
- Label automatically generated on transition to `PROCESSING`
- Skips manual "Generate Label" step
- Used for high-volume automated workflows

## Shipping & Tracking

### Transition: LABEL_CREATED → SHIPPED

**Trigger**:
- Manual mark as shipped
- Carrier pickup confirmation
- Tracking status update from carrier

**What happens**:
1. `order.storePepStatus = SHIPPED`
2. Tracking polling begins (via cron job)
3. Real-time tracking updates pushed via Socket.io
4. Store updated with shipped status

### Tracking Updates

**Cron Job**: Polls carrier APIs for tracking updates (every 30 minutes)

**Storage**:
- `order.trackingNumbers` - Array of tracking numbers (for multi-package shipments)
- Collection: `trackingOrder` - Detailed tracking events

**Real-time Push**:
```javascript
// Server pushes tracking updates to frontend
socket.emit('tracking:updated', { orderId, trackingInfo });
```

## Order Data Model

**Schema**: `server/src/models/orders.js:1-779`

### Core Fields

| Field Group | Key Fields | Purpose |
|-------------|------------|---------|
| **Identity** | `orderId`, `orderDisplayId`, `subOrderUUID` | Order identification |
| **Store Integration** | `storeId`, `storeType`, `storeName`, `storeUUID` | Link to e-commerce platform |
| **Status** | `storePepStatus`, `lastOrderStatus`, `status` | Lifecycle state tracking |
| **Carrier** | `carrier`, `carrierTypeSelected`, `carrierIdSelected`, `serviceIdSelected` | Shipping carrier selection |
| **Addresses** | `shipping`, `billing`, `shipFromAddress`, `soldToAddress` | Multi-address support |
| **Products** | `line_items[]` | Order items with quantities, prices, SKUs |
| **Pricing** | `total`, `subTotal`, `shipping_total`, `total_tax` | Order totals |
| **Tracking** | `trackingId`, `masterTrackingId`, `trackingNumbers[]` | Shipment tracking |
| **Automation** | `matchedAutomationRules`, `isAutomationFailed` | Automation execution |
| **Fulfillment** | `isFulfilled`, `currentFulfillmentSummaryUUID` | Fulfillment status |
| **Timestamps** | `date_created`, `date_modified`, `storepepShippingDate` | Temporal tracking |

### Calculated Fields

**Set on import/processing**:
- `totalWeight` - Sum of all line item weights
- `totalPackage` - Number of packages required
- `availableCarrierAndService` - Array of rate quotes from carriers

### Special Services

Carrier-specific service configurations stored per order:
- `aramexSpecialServices`
- `dhlSpecialServices`
- `canadaPostSpecialServices`
- `fedexSpecialServices`
- `postNordSpecialServices`
- `canparSpecialServices`
- `xpoLogisticsSpecialServices`
- `myFastwaySpecialServices`
- `newZealandPostSpecialServices`
- `dhlSwedenSpecialServices`

**Usage**: Enable carrier-specific options like:
- Saturday delivery
- Signature required
- Hold at location
- Delivery instructions

## Batch Processing

**Field**: `order.batchStatus`, `order.batchDetails`, `order.activeBatchId`

Orders can be grouped into batches for:
- Bulk label generation
- Manifest creation (end-of-day carrier pickup)
- Batch fulfillment to store

**Batch Status Values**:
- `FREE` - Not in any batch
- `BATCHED` - Added to a batch
- `PROCESSING` - Batch being processed
- `COMPLETED` - Batch processing complete

**Batch Details** (array):
```javascript
{
  batchId: "uuid",
  batchType: "LABEL_GENERATION" | "MANIFEST" | "FULFILLMENT",
  batchContext: "context-specific-data"
}
```

## Automation Integration

**Field**: `order.matchedAutomationRules` (array)

When an order transitions to `PROCESSING`, automation rules are evaluated:
1. Match order against configured rule conditions (SKU, value, destination, etc.)
2. Execute actions (select carrier, set packaging, apply special services)
3. Store matched rule IDs in `matchedAutomationRules`
4. Flag `isAutomationFailed: true` if automation encounters errors

**Automation Failure Handling**:
- Order moved to `REPROCESSING` state
- User notified via UI
- Manual intervention required

## Fulfillment Tracking

**Field**: `order.currentFulfillmentSummaryUUID`

**Collection**: `storepepOrderFulfillmentSummary`

Tracks fulfillment events:
- Partial vs. full fulfillment
- Items shipped per fulfillment
- Fulfillment date/time
- Sync status with store

**Partial Fulfillment**:
- `order.isFulfilled: false` until all items shipped
- Multiple fulfillment summaries per order
- Each fulfillment updates store separately

## Error Handling

**Cleanup Helper**:
- **Location**: `server/src/shared/orders/cleanupHelper.js`
- **Function**: `cleanUpPartialSuccessOrder(order)`
- **Purpose**: Rollback partially processed orders on failure

**Error Framework**:
- **Location**: `server/src/shared/orders/errors/app/OrdersErrorFrameWork.js`
- **Purpose**: Centralized error handling and user feedback

## API Endpoints

**Location**: `server/src/routes/orders.js` (2139 lines, 69 endpoints)

### Key Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/orders/importorders` | Import orders from store |
| GET | `/api/orders` | Fetch orders with filters/pagination |
| GET | `/api/orders/:id` | Get single order details |
| PUT | `/api/orders/:id` | Update order fields |
| POST | `/api/orders/bulk-action` | Execute bulk operations |
| POST | `/api/orders/labels` | Generate shipping labels |
| POST | `/api/orders/sync` | Sync status back to store |

## Frontend Integration

### Redux Actions

**Location**: `client/src/actions/ordersActions.js:1-191`

Key action creators:
- `fetchOrders(filters)` - Load orders from API
- `updateOrderStatus(orderId, status)` - Change order state
- `generateLabel(orderId)` - Trigger label creation
- `applyBulkAction(orderIds, action)` - Bulk operations

### Redux State

**Location**: `client/src/reducers/orders.js:1-100`

State shape:
```javascript
{
  orders: {
    id: number,  // Selected order ID
    totalorders: { id: number },  // Total order count
    ordersLoader: boolean,  // Loading state
    ordersCount: object  // Count by status
  }
}
```

### Socket.io Events

**Frontend Listener**: `client/src/socket/sockets.js`

Events received:
- `order:updated` - Order status changed
- `order:imported` - New orders imported
- `label:generated` - Label creation completed

## Dependencies

- [Backend Architecture](../../architecture/backend-architecture.md) - Service layer pattern
- [Order Bulk Actions](./order-bulk-actions.md) - Bulk operation details
- [Order Returns](./order-returns.md) - Return label flow
- [Order Address Management](./order-address-management.md) - Address validation
- [Shipping Carrier Integration](../shipping/carrier-integration.md) (to be created)
- [Store Integrations](../integrations/store-platforms.md) (to be created)
- [Automation Workflows](../workflows/automation-rules.md) (to be created)

## Referenced By

- Order bulk actions reference this lifecycle
- Shipping/label modules depend on order processing
- Fulfillment tracking extends this lifecycle

## Configuration

**Environment Variables**:
- Order import limits
- Default service selection mode
- Auto-label generation defaults

**Feature Toggles**:
- Auto-import on webhook
- Address validation
- Auto-label generation
- Store sync on status change

## Common Patterns

### Importing Orders
```javascript
// User clicks "Import Orders" button
dispatch(importOrders(storeId));

// Backend processes
const adapter = new StoreAdapter().getStoreAdapter(storeType);
await adapter.fetchOrders(user, accountUUID, store, callback);
await processImportedOrders(err, orders, type, context);
```

### Processing Order
```javascript
// User selects orders and clicks "Process"
dispatch(bulkAction(orderIds, 'CHANGE_STATUS_TO_PROCESSING'));

// Backend updates
order.storePepStatus = constants.PROCESSING;
// Run automation, fetch rates, validate address
```

### Generating Label
```javascript
// User clicks "Generate Label"
dispatch(generateLabel(orderId));

// Backend calls carrier API
const label = await carrierClient.createShipment(shipmentDetails);
order.trackingId = label.trackingNumber;
order.storePepStatus = constants.LABEL_CREATED;
```

## Known Issues / Tech Debt

1. **Large route file**: `orders.js` is 2139 lines - needs refactoring into smaller route modules
2. **Inconsistent error handling**: Some endpoints use try/catch, others use callback-style errors
3. **Mixed async patterns**: Some code uses async/await, older code uses callbacks
4. **OrderProcessingService scope**: Currently Shopify-specific, needs generalization
5. **State transition validation**: No formal state machine - transitions not strictly validated

## Related Pages

- [Order Bulk Actions](./order-bulk-actions.md)
- [Order Returns](./order-returns.md)
- [Order Address Management](./order-address-management.md)
- [Redux Patterns](../../patterns/redux-patterns.md) (to be created)
- [Event Sourcing](../../patterns/event-sourcing.md) (to be created)
