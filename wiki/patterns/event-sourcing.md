---
title: Event-Driven Architecture & Real-Time Updates
category: pattern
status: complete
last_updated: 2026-04-30
git_reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020
sources: [storepep-react]
---

# Event-Driven Architecture & Real-Time Updates

## Overview

StorePep implements an event-driven architecture using domain events and Socket.io for real-time client updates. This pattern decouples business logic from side effects, enables audit trails, and provides instant UI feedback without polling.

**Event Library**: `@phivejs/eventing` (custom event system)
**Real-Time**: Socket.io for bidirectional communication
**Pattern**: Domain events → Event listeners → Socket.io emit → Client Redux updates

## Architecture Components

### 1. Domain Events

**Base Class**: `DomainEvent` from `@phivejs/eventing`

**Location**: Event classes in `server/src/shared/*/events/` and `server/src/modules/*/domain/events.js`

**Event Structure**:
```javascript
class DomainEvent {
  constructor(name, payload) {
    this.name = name;
    this.payload = payload;
    this.timestamp = new Date();
  }
}
```

**Event Categories**:
- **Orders** - Order lifecycle events
- **App** - Application-level events (install, carrier config, analytics)
- **Shipping** - Label generation, tracking, manifests
- **Products** - Product import/sync
- **Subscription** - Payment and subscription events
- **Messages** - Internal messaging events

### 2. Event Listeners

**Pattern**: Observer pattern with `@phivejs/eventing`

**Registration**:
```javascript
const { addListenerTo } = require('@phivejs/eventing');

addListenerTo(
  { OrderCreated, OrderUpdated, OrderCancelled },
  listener(eventHandlers),
  'Order event listener'
);
```

**Listener Function**:
```javascript
const listener = (subscribers) => async (event) => {
  if (!event || !subscribers[event.name]) {
    return;
  }
  return subscribers[event.name](event);
};
```

### 3. Socket.io Publishing Listener

**File**: `server/src/shared/listeners/socketEventPublishingListener.js:1-268`

**Purpose**: Converts domain events to Socket.io messages for real-time client updates

**Event-to-Socket Mapping** (socketEventPublishingListener.js:25-148):
```javascript
const socketMessageFor = {
  [OrderImportCompleted.name]: payload => ({
    code: constants.SOCKET_ORDER_PROCESSING_CODE,
    payload,
  }),
  [LabelGenerated.name]: payload => ({
    code: payload.status === 'SUCCESS'
      ? 'SOCKET_LABEL_GENERATED_FULFILLMENT_PENDING_CODE'
      : 'SOCKET_LABEL_GENERATED_FAILED_FULFILLMENT_IGNORED_CODE',
    message: payload.status === 'SUCCESS'
      ? 'Label Generated, Fulfilling Order'
      : 'Label Generation Failed',
    payload,
  }),
  [OrderProcessingCompleted.name]: payload => ({
    code: payload.isProcessingContext
      ? constants.SOCKET_ORDER_PROCESSING_CODE
      : constants.SOCKET_ORDER_IMPORT_CODE,
    payload,
  }),
  // ... 30+ event mappings
};
```

**Process Flow** (socketEventPublishingListener.js:150-158):
```javascript
const processEvent = (event) => {
  try {
    const { accountUUID } = event.payload;
    emitNewSocketEvent({
      accountUUID,
      ...socketMessageFor[event.name](event.payload)
    });
  } catch (error) {
    logger.error(`Failed to process event`, error);
  }
};
```

### 4. Socket.io Server

**Emit Function**:
```javascript
const emitNewSocketEvent = ({ accountUUID, code, message, payload }) => {
  socket.to(accountUUID).emit('storepep', {
    accountUUID,
    code,
    message,
    payload,
    timestamp: new Date(),
  });
};
```

**Room-Based Targeting**:
- Clients join room based on `accountUUID`
- Events only sent to clients in same account
- Multi-tenant isolation

### 5. Socket.io Client

**File**: `client/src/socket/sockets.js:1-86`

**Connection Setup** (sockets.js:16-23):
```javascript
export const setSocketConfig = (host) => {
  const socketUrl = hostToUrl[host] || hostToUrl[constants.DEFAULT];
  const token = readToken('jwtToken') || readToken('storepepteamToken');
  const authHeaders = {
    query: {
      token,
      'storepep-service-id': constants.STOREPEP_SERVICE_ID
    }
  };
  socket = io(socketUrl, authHeaders);
  socket.on(constants.SOCKET_EMIT_EVENT_NAME_STOREPEP, handleInfoUpdates);
  socket.on(constants.SOCKET_EMIT_EVENT_NAME_ADMIN_DOWNLOAD, handleAdminDownloadUpdates);
}
```

**Event Channels**:
- `storepep` - Main event channel for order/shipping updates
- `storepep_info` - Info messages and alerts
- `storepep_admin_download` - Admin file downloads

**Listen Helper** (sockets.js:32-34):
```javascript
export const listenToSocket = (cb) => {
  socket.on(constants.SOCKET_EMIT_EVENT_NAME_STOREPEP, cb);
};
```

**Validation** (sockets.js:36-45):
```javascript
export const validateSocketResponse = (accountUUID, socketUpdates, componentSocketCode) => {
  // Check accountUUID matches (multi-tenant isolation)
  if (accountUUID === socketUpdates.accountUUID) {
    // Check if info message (shows alert)
    if (checkIfThisNewEventIsForThisComponent(socketUpdates, constants.SOCKET_INFO_CODE)) {
      alertInfo(socketUpdates.message, false, 4000, false);
      return false;
    }
    // Check if event matches component's expected code
    return checkIfThisNewEventIsForThisComponent(socketUpdates, componentSocketCode);
  }
  return false;
};
```

## Event Categories

### Order Events

**File**: `server/src/shared/orders/events/index.js`

**Event Classes**:

```javascript
// Import & Sync
class OrderImportStarted extends OrderEvent {}
class OrderImportProcessed extends OrderEvent {}
class OrderImportFinished extends OrderEvent {}
class OrderImportCompleted extends OrderEvent {}
class OrderSyncFailed extends OrderEvent {}
class OrderSyncIgnored extends OrderEvent {}

// Processing
class OrderProcessingCompleted extends OrderEvent {}
class OrderLabelAutomationFlowCompleted extends OrderEvent {}
class OrderPackageAutomationFlowCompleted extends OrderEvent {}

// Label Generation
class OrderLabelGenerationProcessCompleted extends OrderEvent {}
class OrderDocumentsGenerated extends OrderEvent {}
class PdfGenerationRequested extends OrderEvent {}

// Fulfillment
class OrderFulfillmentStatusUpdated extends OrderEvent {}
class OrderFulfillmentCancelled extends OrderEvent {}
class OrderMarkedAsExternallyFulfilled extends OrderEvent {}
class OrderShipmentCancelled extends OrderEvent {}

// Updates
class OrderShippingRatesUpdated extends OrderEvent {}
class OrderShippingServiceUpdated extends OrderEvent {}
class OrderShipFromAddressUpdated extends OrderEvent {}
class OrderShippingDateUpdated extends OrderEvent {}
class OrderUpdateInfoUpdated extends OrderEvent {}
class OrderManifestUpdated extends OrderEvent {}

// Bulk Operations
class OrderBulkActionCompleted extends OrderEvent {}

// Webhooks
class OrderCreatedWebhookReceived extends OrderEvent {}
class OrderUpdatedWebhookReceived extends OrderEvent {}
class OrderWebhookProcessed extends OrderEvent {}

// Other
class OrderRetryFulfillmentCompleted extends OrderEvent {}
class OrderCancelledProcessingCompleted extends OrderEvent {}
class OrderInvoiceRegenerated extends OrderEvent {}
class OrderPackingSlipsRegenerated extends OrderEvent {}
class OrderAutoUpdateRequestCompleted extends OrderEvent {}
class OrderMismatchIdentified extends OrderEvent {}
```

**Usage Example**:
```javascript
const { OrderProcessingCompleted } = require('./events');

// Emit event after order processing
await publish(new OrderProcessingCompleted({
  accountUUID: 'account-123',
  orderId: 'order-456',
  status: 'PROCESSING',
  isProcessingContext: true,
}));
```

### App Events

**File**: `server/src/shared/events/index.js:1-150`

**Analytics Events** (inherit from `AnalyticsEvent`, include user context):

```javascript
class AppInstalled extends AnalyticsEvent {}
class AppUnInstalled extends AnalyticsEvent {}
class ContactInfoUpdated extends AnalyticsEvent {}
class CarrierSaved extends AnalyticsEvent {}
class CarrierArchived extends BaseEvent {}
class CarrierMarkedInactive extends BaseEvent {}
class CheckOutRatesGenerated extends AnalyticsEvent {}
class LabelGenerated extends AnalyticsEvent {}
class StoreClosed extends AnalyticsEvent {}
class StoreReopened extends AnalyticsEvent {}
class StoreAdded extends DomainEvent {}
class VendorAdminAdded extends DomainEvent {}
class StorepepUserSignedUp extends DomainEvent {}
class SettingsInitializationFailed extends DomainEvent {}
```

**Analytics Event Structure**:
```javascript
class AnalyticsEvent extends DomainEvent {
  constructor(name, user, payload) {
    super(name, {
      ...payload,
      timestamp: new Date(),
      accountUUID: user.accountUUID,
      platform: user.platform,
      userRole: user.userRole,
      app: process.env.APP_NAME,
      category: 'app'
    });
  }
}
```

**Usage Example**:
```javascript
const { LabelGenerated } = require('./events');

// Emit analytics event
await publish(new LabelGenerated(user, {
  carrierType: 'fedex',
  status: 'SUCCESS',
  count: 1,
  carrierID: 'carrier-789',
}));
```

### Quick Ship Events

**File**: `server/src/shared/quick-ship/events/`

```javascript
class QuickShipCompleted extends DomainEvent {}
class QuickShipRequestFailed extends DomainEvent {}
```

### Message Events

**File**: `server/src/modules/messages/domain/events.js`

```javascript
class MessageAdded extends DomainEvent {}
class MessageArchived extends DomainEvent {}
```

### Label & Fulfillment Events

**File**: `server/src/shared/label-fulfill-order/events/`

```javascript
class GenerateAndFulfillOrderFailed extends DomainEvent {}
```

## Socket Event Codes

**File**: `client/src/utils/constants.js`

**Event Codes** (30+ codes):

```javascript
// Event Channels
SOCKET_EMIT_EVENT_NAME_STOREPEP: 'storepep',
SOCKET_EMIT_EVENT_NAME_STOREPEP_INFO: 'storepep_info',
SOCKET_EMIT_EVENT_NAME_ADMIN_DOWNLOAD: 'storepep_admin_download',

// Order Events
SOCKET_ORDER_IMPORT_CODE: 100,
SOCKET_ORDER_IMPORT_INFO_CODE: 101,
SOCKET_ORDER_PROCESSING_CODE: 200,
SOCKET_ORDER_REPROCESSING_CODE: 202,
SOCKET_ORDER_CANCELLATION_CODE: 600,
SOCKET_ORDER_UPDATED: 'SOCKET_ORDER_UPDATED',
SOCKET_ORDER_UPDATES_AVAILABLE: 'SOCKET_ORDER_UPDATES_AVAILABLE',

// Label & Manifest
SOCKET_LABEL_GENERATION_CODE: 300,
SOCKET_MANIFEST_CODE: 400,
SOCKET_MANIFEST_REFRESH_CODE: 'SMR001',

// General
SOCKET_INFO_CODE: 500,
SOCKET_ERROR_CODE: 501,
SOCKET_SUCCESS_CODE: 502,

// Feature-Specific
SOCKET_TRACKING_COMPLETED_CODE: 'T001',
SOCKET_PRODUCT_IMPORT_CODE: 'P001',
SOCKET_ORDER_SUMMARY_CODE: 'S100',
SOCKET_PRODUCT_SHIPPING_CLASS_IMPORT_CODE: 'PS100',
SOCKET_VENDORS_SYNC_CODE: 'V001',
SOCKET_PAYPAL_AGREEMENT_UPDATE_CODE: 'PP001',
SOCKET_PAYPAL_SUBSCRIPTION_UPDATE_CODE: 'PP002',
SOCKET_CANADA_POST_REGISTRATION_COMPLETE_CODE: 'SCPR001',
SOCKET_USER_SUBSCRIPTION_STOP_CODE: 'USS100',
SOCKET_RATES_REFRESHED_CODE: 'SOCKET_RATES_REFRESHED_CODE',
SOCKET_PACKAGE_UPDATE_CODE: 'SOCKET_PACKAGE_UPDATE_CODE',

// Admin
SOCKET_ADMIN_DOWNLOAD_CODE: 'A001',
```

## Client-Side Event Handling

### Component Integration Pattern

**Pattern 1: Component Lifecycle Hooks**

```javascript
class OrdersPage extends Component {
  componentDidMount() {
    this.socketCallback = this.handleSocketUpdate.bind(this);
    listenToSocket(this.socketCallback);
  }

  componentWillUnmount() {
    removeSocketEventListener(this.socketCallback);
  }

  handleSocketUpdate = (socketUpdates) => {
    const { accountUUID } = this.props.user;
    if (validateSocketResponse(accountUUID, socketUpdates, constants.SOCKET_ORDER_IMPORT_CODE)) {
      // Refresh orders list
      this.props.fetchOrders();
    }
  };
}
```

**Pattern 2: Redux Middleware Integration**

```javascript
// Socket middleware (conceptual - not in current codebase)
const socketMiddleware = (socket) => (store) => (next) => (action) => {
  if (action.type === 'SOCKET_EVENT_RECEIVED') {
    const { code, payload } = action.payload;

    switch (code) {
      case constants.SOCKET_ORDER_IMPORT_CODE:
        store.dispatch(refreshOrders(payload));
        break;
      case constants.SOCKET_LABEL_GENERATION_CODE:
        store.dispatch(updateOrderLabel(payload));
        break;
      // ... handle other codes
    }
  }

  return next(action);
};
```

### Info Message Handler

**File**: `client/src/socket/sockets.js:47-58`

```javascript
const handleInfoUpdates = (socketUpdates) => {
  const state = ReduxStore.getState('auth');
  let accountUUID = '';
  if (state && state.auth && state.auth.accountUUID) {
    ({ accountUUID } = state.auth);
  }
  if (validateSocketResponse(accountUUID, socketUpdates, constants.SOCKET_INFO_CODE)) {
    alertInfo(socketUpdates.message, false, 4000, false);
  }
};
```

**Purpose**: Display toast notifications for info events

### Admin Download Handler

**File**: `client/src/socket/sockets.js:60-81`

```javascript
const handleAdminDownloadUpdates = (socketUpdates) => {
  const state = ReduxStore.getState('storepepTeamAuth');
  let accountUUID = state.storepepTeamAuth?.user?.accountUUID;

  if (validateSocketResponse(accountUUID, socketUpdates, constants.SOCKET_ADMIN_DOWNLOAD_CODE)) {
    const uriInfo = getURIFileType(socketUpdates.downloadFormat);
    if (uriInfo) {
      let downloadData = socketUpdates.data;
      if (uriInfo.uriEncodeRequired) {
        downloadData = encodeURI(downloadData);
      }
      const element = document.createElement('a');
      element.setAttribute('href', uriInfo.uri + downloadData);
      element.setAttribute('download', `${socketUpdates.downloadName}.${uriInfo.fileType}`);
      element.click();
    }
  }
};
```

**Purpose**: Automatically download files when async export completes (CSV, PDF)

## Event Flow Diagrams

### Label Generation Flow

```
User clicks "Generate Label"
  ↓
Frontend dispatches action
  ↓
API: POST /api/orders/:orderId/label
  ↓
Backend: LabelService.generateLabel()
  ↓
Carrier API called
  ↓
Label generated successfully
  ↓
Event: publish(new LabelGenerated({ status: 'SUCCESS', ... }))
  ↓
Socket Listener: processLabelEventWithDocumentSettings()
  ↓
Socket emit: emitNewSocketEvent({ code: 'SOCKET_LABEL_GENERATED_FULFILLMENT_PENDING_CODE' })
  ↓
Frontend: socket.on('storepep', callback)
  ↓
Component receives event
  ↓
Redux action: updateOrderLabel(payload)
  ↓
UI re-renders with label URL
```

### Order Import Flow

```
Webhook received: POST /api/webhooks/shopify/orders/create
  ↓
Event: publish(new OrderCreatedWebhookReceived({ body, headers }))
  ↓
Order import service processes webhook
  ↓
Event: publish(new OrderImportStarted({ accountUUID, storeId }))
  ↓
Socket: emitNewSocketEvent({ code: constants.SOCKET_ORDER_PROCESSING_CODE })
  ↓
Frontend shows "Importing orders..." notification
  ↓
Orders imported and processed
  ↓
Event: publish(new OrderImportCompleted({ accountUUID, count }))
  ↓
Socket: emitNewSocketEvent({ code: constants.SOCKET_ORDER_PROCESSING_CODE })
  ↓
Frontend refreshes order list
  ↓
UI shows updated order count
```

### Bulk Action Flow

```
User selects 50 orders, clicks "Generate Labels"
  ↓
API: POST /api/orders/bulk-action
  ↓
Backend: BulkActionService.processBatch()
  ↓
Process orders in batches of 10
  ↓
For each batch:
  ↓
  Generate labels (parallel)
  ↓
  Event: publish(new LabelGenerated({ ... })) for each
  ↓
  Socket events emitted per order
  ↓
All batches complete
  ↓
Event: publish(new OrderBulkActionCompleted({ batchId, results }))
  ↓
Socket: emitNewSocketEvent({ code: constants.SOCKET_ORDER_IMPORT_CODE })
  ↓
Frontend navigates to batch results page
  ↓
UI shows success/failure per order
```

## Event Listener Registration

**File**: `server/src/shared/listeners/socketEventPublishingListener.js:233-265`

```javascript
const init = () => {
  addListenerTo({
    AppRegisteredForCarrierCalculatedRates,
    AppFailedToRegisterForCarrierCalculatedRates,
    OrderFulfillmentStatusUpdated,
    QuickShipCompleted,
    QuickShipRequestFailed,
    MessageAdded,
    MessageArchived,
    GenerateAndFulfillOrderFailed,
    LabelGenerated,
    OrderDocumentsGenerated,
    OrderLabelAutomationFlowCompleted,
    OrderProcessingCompleted,
    OrderBulkActionCompleted,
    OrderShippingRatesUpdated,
    OrderShippingServiceUpdated,
    OrderShipFromAddressUpdated,
    OrderShippingDateUpdated,
    OrderUpdateInfoUpdated,
    OrderFulfillmentCancelled,
    OrderMarkedAsExternallyFulfilled,
    OrderLabelGenerationProcessCompleted,
    OrderManifestUpdated,
    OrderRetryFulfillmentCompleted,
    OrderImportProcessingCompleted,
    OrderCancelledProcessingCompleted,
    OrderPackageAutomationFlowCompleted,
    OrderImportCompleted,
    OrderMismatchIdentified,
    OrderAutoUpdateRequestCompleted,
  }, listener(on), 'Socket event publishing listener');
};

module.exports = { init };
```

**Initialization**: Called on server startup to register all event → socket mappings

## Feature Toggles

**Socket Event Publishing Toggle**:

```javascript
if (features().isEnabled('socket.events.publish.disabled')) {
  logger.info(`Dropping ${event.name} since socket event publish is disabled`);
  return NO_RESULT;
}
```

**Purpose**: Disable Socket.io events without deploying (feature flag)

## Best Practices

### Event Naming

**Convention**: PastTense + Noun

✅ Good:
- `OrderCreated`
- `LabelGenerated`
- `ShipmentCancelled`

❌ Bad:
- `CreateOrder` (imperative, not past tense)
- `GeneratingLabel` (present continuous)
- `OrderCreate` (noun + verb)

### Event Payload

**Include Context**:
```javascript
new OrderProcessingCompleted({
  accountUUID: 'account-123',     // Required for routing
  orderId: 'order-456',           // Entity ID
  status: 'PROCESSING',           // New state
  previousStatus: 'INITIAL',      // Old state (for audit)
  isProcessingContext: true,      // Context flag
  userId: 'user-789',             // Who triggered
  timestamp: new Date(),          // When
});
```

**Don't include**:
- Large objects (send IDs, not full entities)
- Sensitive data (PII, credentials)
- Redundant data (frontend can fetch if needed)

### Event Listeners

**Do**:
- Keep listeners pure (no side effects beyond emitting)
- Use try/catch for resilience
- Log all events for debugging
- Validate event payloads

**Don't**:
- Make synchronous API calls in listeners
- Mutate event payload
- Throw errors (log and continue)
- Block event processing

### Socket.io Integration

**Do**:
- Validate `accountUUID` to prevent cross-account leakage
- Use event codes for client-side routing
- Include human-readable messages
- Disconnect cleanly on logout

**Don't**:
- Emit sensitive data (credentials, tokens)
- Emit to all clients (use rooms)
- Rely solely on Socket.io (have fallback polling)
- Send large payloads (send IDs, fetch details)

## Error Handling

### Event Publishing Errors

```javascript
try {
  await publish(new OrderCreated({ ... }));
} catch (error) {
  logger.error('Failed to publish event', error);
  // Don't fail the request
}
```

**Pattern**: Event publishing failures should not block business logic

### Socket Emission Errors

```javascript
const processEvent = (event) => {
  try {
    const { accountUUID } = event.payload;
    emitNewSocketEvent({ accountUUID, ...socketMessageFor[event.name](event.payload) });
    logger.info(`Processed event ${JSON.stringify(event)}`);
  } catch (error) {
    logger.error(`Failed to process event ${JSON.stringify(event)}`, error);
    // Continue processing other events
  }
};
```

**Pattern**: Socket emission failures logged but don't crash server

### Client-Side Errors

```javascript
try {
  if (validateSocketResponse(accountUUID, socketUpdates, expectedCode)) {
    this.props.fetchOrders();
  }
} catch (error) {
  console.error('Socket event handling failed', error);
  // UI continues to work, event ignored
}
```

**Pattern**: Client failures gracefully degrade (polling fallback)

## Performance Considerations

### Event Batching

**Problem**: 100 orders imported → 100 events → 100 socket emits

**Solution**: Batch events or use summary events

```javascript
// Instead of 100 OrderImportProcessed events
publish(new OrderImportProcessed({ orderId: 'order-1' }));
publish(new OrderImportProcessed({ orderId: 'order-2' }));
// ... x100

// Use single summary event
publish(new OrderImportCompleted({
  accountUUID,
  orderIds: ['order-1', 'order-2', ...],
  count: 100
}));
```

### Socket.io Scalability

**Challenge**: Socket.io connections don't share state across server instances

**Solution**: Use Redis adapter for multi-server Socket.io

```javascript
const redisAdapter = require('socket.io-redis');
io.adapter(redisAdapter({ host: 'redis-host', port: 6379 }));
```

**Benefit**: Events emitted on server-1 reach clients connected to server-2

### Client-Side Optimization

**Debounce Refresh**:
```javascript
handleSocketUpdate = debounce((socketUpdates) => {
  this.props.fetchOrders();
}, 500);
```

**Prevents**: Rapid-fire events causing excessive API calls

**Throttle Notifications**:
```javascript
// Max 1 notification per 2 seconds
handleSocketUpdate = throttle((socketUpdates) => {
  alertInfo(socketUpdates.message);
}, 2000);
```

## Audit Trail

**Event Persistence**: Events can be persisted to database for audit trail

```javascript
const { EventStore } = require('@phivejs/eventing');

// Store all events
EventStore.on('event', async (event) => {
  await db.events.create({
    name: event.name,
    payload: event.payload,
    timestamp: event.timestamp,
    accountUUID: event.payload.accountUUID,
  });
});
```

**Use Cases**:
- Compliance (SOC 2, HIPAA)
- Debugging (replay events)
- Analytics (event frequency, patterns)
- Event sourcing (rebuild state from events)

## Debugging

### Enable Event Logging

**Server-side**:
```javascript
logger.info(`Processing event ${event.name}`, event.payload);
```

**Client-side**:
```javascript
listenToSocket((socketUpdates) => {
  console.log('Socket event received:', socketUpdates);
  // ... handle event
});
```

### Socket.io DevTools

**Chrome Extension**: Socket.io DevTools

**Features**:
- View connected sockets
- Monitor events in real-time
- Inspect event payloads
- Test emit/receive

### Event Replay

**Debug Pattern**:
1. Capture event payload from logs
2. Replay event in dev environment
3. Observe behavior
4. Fix bug
5. Verify with replay

```javascript
// Manually trigger event for testing
const { OrderProcessingCompleted } = require('./events');
await publish(new OrderProcessingCompleted({
  accountUUID: 'test-account',
  orderId: 'test-order',
  status: 'PROCESSING',
  isProcessingContext: true,
}));
```

## Known Issues / Tech Debt

1. **No Event Versioning**: Event schema changes can break listeners
2. **No Dead Letter Queue**: Failed events not retried or stored
3. **No Event Ordering Guarantee**: Events may arrive out of order
4. **No Idempotency**: Same event processed twice causes duplicate actions
5. **Socket.io Single Point of Failure**: If Socket.io down, no real-time updates
6. **No Event Replay**: Can't rebuild state from event history
7. **Limited Event Filtering**: All events sent to all listeners (no selective subscription)
8. **No Rate Limiting**: High event volume can overwhelm clients

## Future Enhancements

**Suggested Improvements**:
1. **Event Versioning**: Version events (e.g., `OrderCreatedV2`) for schema evolution
2. **Event Store**: Persist all events for audit trail and replay
3. **Event Sourcing**: Rebuild state from event history
4. **Dead Letter Queue**: Retry failed events with exponential backoff
5. **Event Filtering**: Selective subscription to event types
6. **Event Deduplication**: Idempotency keys to prevent duplicate processing
7. **Event Ordering**: Sequence numbers to guarantee order
8. **Webhook Alternative**: Fallback to webhooks if Socket.io unavailable
9. **Event Analytics**: Dashboard showing event frequency, latency, failures
10. **Event Replay Tool**: Admin UI to replay events for debugging

## Related Pages

- [Backend Architecture](../architecture/backend-architecture.md) - Server-side architecture
- [Order Lifecycle](../modules/orders/order-lifecycle.md) - Order events in detail
- [Frontend Architecture](../architecture/frontend-architecture.md) - Socket.io client setup
- [Redux Patterns](redux-patterns.md) - Redux integration with Socket.io

## Dependencies

**Backend**:
- `@phivejs/eventing` - Event publishing and subscription
- `socket.io` - Real-time server
- Event classes in `server/src/shared/*/events/`

**Frontend**:
- `socket.io-client` - WebSocket client
- `client/src/socket/sockets.js` - Socket.io configuration
- Redux for state updates triggered by events

## Referenced By

- [Orders UI](../modules/frontend/orders-ui.md) - Real-time order updates
- [Shipping UI](../modules/frontend/shipping-ui.md) - Real-time label/tracking updates
- All real-time features rely on this event-driven pattern
