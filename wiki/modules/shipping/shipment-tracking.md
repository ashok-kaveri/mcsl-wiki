---
title: Shipment Tracking
category: module
domain: shipping
status: complete
last_updated: 2026-04-08
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Shipment Tracking

## Overview

Shipment tracking monitors the location and delivery status of packages after label generation by polling carrier APIs for tracking updates. StorePep supports tracking for 45+ carriers with automatic updates every 6 hours, real-time Socket.io notifications, and customer email alerts on key delivery events.

**Core Value**: Merchants and customers gain visibility into shipment progress without manually checking carrier websites. Exceptions and delays are automatically detected and flagged for attention.

**Update Frequency**: Every 6 hours via scheduled cron job (00:00, 06:00, 12:00, 18:00 UTC)

## Architecture

### Three-Layer Data Model

**1. TrackingOrders** - Parent-level tracking
- One record per order
- Aggregated status across all packages
- Links to original order via `orderId` and `subOrderUUID`

**2. TrackingPackages** - Individual package tracking
- One record per package
- Stores carrier-specific tracking numbers
- Current status and estimated delivery date

**3. TrackingHistory** - Event timeline
- Multiple records per package (one per checkpoint)
- Chronological tracking events from carrier
- Location, status, timestamp for each scan

### Database Schemas

**TrackingOrders Model** (`server/src/models/trackingOrders.js:1-88`):
```javascript
{
  orderId: String,                    // Original order ID from store
  subOrderUUID: String,               // StorePep internal order UUID
  accountUUID: String,                // Merchant account
  storeUUID: String,                  // E-commerce store
  vendorUUID: String,                 // Multi-vendor support

  // Carrier & Service
  carrier: String,                    // "FedEx - FedEx Ground"
  carrierType: String,                // "C2" (carrier code)
  carrierServiceType: String,         // Service level

  // Status
  status: String,                     // INITIAL, IN_TRANSIT, DELIVERED, etc.
  lastTrackingStatus: String,         // Human-readable last status
  estimatedDeliveryDate: Date,        // ETA from carrier
  lastTrackedTime: Date,              // Last time tracking was updated

  // Addresses
  shipping: {                         // Delivery address
    firstName, lastName, address1, city, state, zip, country, phone
  },
  shipFrom: {                         // Origin address
    name, address1, city, state, zip, country
  },

  // Tracking Numbers
  trackingNumbers: [String],          // All tracking numbers for this order

  // Return Flow
  isReturned: Boolean,                // True for return shipments

  // Timestamps
  createdAt: Date,
  updatedAt: Date
}
```

**TrackingPackages Model** (`server/src/models/trackingPackages.js:1-97`):
```javascript
{
  storepepTrackingNumber: String,     // StorePep internal tracking ID (unique)
  carrierTrackingId: String,          // Carrier's tracking number
  subOrderUUID: String,               // Links to order
  packageUUID: String,                // Links to package
  accountUUID: String,
  storeUUID: String,

  // Status
  status: String,                     // INITIAL, IN_TRANSIT, DELIVERED_UC, etc.
  lastTrackingStatus: String,         // Text description
  estimatedDeliveryDate: Date,
  carrierDeliveredTime: Date,         // Actual delivery timestamp
  attentionType: String,              // Exception classification (1-6)

  // Carrier-Specific IDs
  canadaPostShipmentId: String,
  australiaPostShipmentId: String,
  easypostTrackingUrl: String,
  tntMarketType: String,

  // Timestamps
  createdAt: Date,
  updatedAt: Date,
  lastTrackedTime: Date
}
```

**TrackingHistory Model** (`server/src/models/trackingHistory.js:1-51`):
```javascript
{
  dateAndTime: Date,                  // Checkpoint timestamp
  status: String,                     // Status at this checkpoint
  location: String,                   // City, State or facility name
  summary: String,                    // Human-readable event description

  // Tracking Numbers
  trackingNumber: String,             // Carrier tracking number
  storepepTrackingNumber: String,     // StorePep tracking ID
  carrierTrackingCode: String,        // Carrier-specific status code

  // Context
  subOrderUUID: String,
  accountUUID: String,
  storeUUID: String,

  // Direction
  direction: String,                  // "FORWARD" (outbound) or "RETURN"

  // Timestamps
  createdAt: Date,
  updatedAt: Date
}
```

## Tracking Status Values

**Status Constants** (`server/src/storePepConstants.js:278-345`):

| Status | Constant | Meaning |
|--------|----------|---------|
| Initial | `INITIAL` | Tracking record created, no carrier scans yet |
| In Transit | `IN_TRANSIT` | Package in carrier's network, moving to destination |
| Out for Delivery | `OUT_FOR_DELIVERY` | Package on delivery vehicle, arriving today |
| Delivered | `DELIVERED_UC` | Successfully delivered to recipient |
| Exception 1 | `EXCEPTION_1` | Critical exception (lost, damaged, refused) |
| Exception 2 | `EXCEPTION_2` | Moderate exception (delayed, held at customs) |
| Exception 3 | `EXCEPTION_3` | Minor exception (delivery attempted, rescheduled) |

### Status Progression

```
INITIAL
  ↓
IN_TRANSIT
  ↓
OUT_FOR_DELIVERY
  ↓
DELIVERED_UC

OR diverge to:
  ↓
EXCEPTION_1/2/3
```

## Tracking Update Flow

### 1. Scheduled Updates (Automatic)

**Cron Job Configuration** (`server/src/shared/cronJob/cronJobContainer.js:175-180`):
```javascript
const trackingJob = new CronJob(
  everySixHours,          // "0 */6 * * *" (every 6 hours at minute 0)
  runDailyTrackingTask,
  null,
  true,
  'Africa/Casablanca'     // Timezone
);
```

**Schedule**: 00:00, 06:00, 12:00, 18:00 UTC daily

### 2. Daily Tracking Task

**Function**: `runDailyTrackingTask()`

**Location**: `server/src/shared/storepepTracking/storepepTrackingEngine.js:195-216`

**Flow**:
```javascript
async runDailyTrackingTask() {
  // 1. Get all accounts in system
  const accounts = await Account.find({ isActive: true });

  for (const account of accounts) {
    // 2. Find non-delivered tracking orders for this account
    const trackingOrders = await TrackingOrder.find({
      accountUUID: account.accountUUID,
      status: { $nin: [constants.DELIVERED, constants.CANCELLED] }
    });

    if (trackingOrders.length > 0) {
      // 3. Re-run tracking for all orders
      await reRunTracking(
        trackingOrders,
        { accountUUID: account.accountUUID },
        applicationConfig
      );
    }

    // 4. Update last tracked timestamp
    await updateLastTrackedTime(account.accountUUID);
  }
}
```

### 3. Re-Running Tracking

**Function**: `reRunTracking(orders, currentUser, applicationConfig)`

**Location**: `server/src/shared/storepepTracking/storepepTrackingEngine.js:218-241`

**Flow**:
```javascript
async reRunTracking(orders, currentUser, applicationConfig) {
  for (const order of orders) {
    // 1. Get all tracking packages for this order
    const trackingPackages = await TrackingPackages.find({
      subOrderUUID: order.subOrderUUID
    });

    // 2. Track each package and get updated status
    const updatedStatus = await trackAndUpdateTrackingDetails(
      trackingPackages,
      order,
      currentUser,
      applicationConfig
    );

    // 3. Update TrackingOrder with aggregated status
    order.status = updatedStatus;
    order.lastTrackedTime = new Date();
    await order.save();

    // 4. Emit Socket.io event for real-time UI update
    await emitNewSocketEvent({
      eventCode: constants.SOCKET_TRACKING_COMPLETED_CODE,
      accountUUID: order.accountUUID,
      data: { orderId: order.orderId, status: updatedStatus }
    });

    // 5. Trigger email notification if warranted
    await triggerTrackingEmailIfNeeded(order, trackingPackages);
  }
}
```

### 4. Tracking Detail Update

**Function**: `trackAndUpdateTrackingDetails(trackingPackages, order, currentUser, applicationConfig)`

**Location**: `server/src/shared/storepepTracking/storepepTrackingEngine.js:244-278`

**Flow**:
```javascript
async trackAndUpdateTrackingDetails(trackingPackages, order, currentUser, applicationConfig) {
  const statusResults = [];

  for (const trackingPackage of trackingPackages) {
    // 1. Get carrier configuration
    const carrier = await Carrier.findOne({
      carrierID: order.carrierIdSelected,
      accountUUID: order.accountUUID
    });

    // 2. Get carrier adaptor
    const shipmentAdaptor = new ShipmentAdaptor();
    const carrierHelper = shipmentAdaptor.getShipmentCreatorBasedOnCarrier(
      order.carrierType
    );

    // 3. Call carrier tracking API
    const trackingHistory = await carrierHelper.makeTrackingRequest(
      trackingPackage.carrierTrackingId,
      carrier
    );

    // 4. Process tracking history array
    for (const event of trackingHistory) {
      // Check if this checkpoint already exists
      const existingEvent = await TrackingHistory.findOne({
        storepepTrackingNumber: trackingPackage.storepepTrackingNumber,
        dateAndTime: event.dateAndTime,
        location: event.location,
        status: event.status
      });

      // Only insert new checkpoints
      if (!existingEvent) {
        await TrackingHistory.create({
          ...event,
          storepepTrackingNumber: trackingPackage.storepepTrackingNumber,
          trackingNumber: trackingPackage.carrierTrackingId,
          subOrderUUID: order.subOrderUUID,
          accountUUID: order.accountUUID,
          direction: order.isReturned ? 'RETURN' : 'FORWARD'
        });
      }
    }

    // 5. Extract latest status and delivery info
    const latestEvent = trackingHistory[trackingHistory.length - 1];
    trackingPackage.status = latestEvent.status;
    trackingPackage.lastTrackingStatus = latestEvent.summary;
    trackingPackage.lastTrackedTime = new Date();

    if (latestEvent.status === constants.DELIVERED_UC) {
      trackingPackage.carrierDeliveredTime = latestEvent.dateAndTime;
    }

    await trackingPackage.save();
    statusResults.push(latestEvent.status);
  }

  // 6. Aggregate status across all packages
  return aggregatePackageStatuses(statusResults);
}
```

### 5. Status Aggregation Logic

**Function**: `aggregatePackageStatuses(statusResults)`

**Rules**:
```javascript
function aggregatePackageStatuses(statuses) {
  // If ANY package has exception, order is exception
  if (statuses.some(s => s.includes('EXCEPTION'))) {
    return statuses.find(s => s.includes('EXCEPTION'));
  }

  // If ALL packages delivered, order is delivered
  if (statuses.every(s => s === constants.DELIVERED_UC)) {
    return constants.DELIVERED_UC;
  }

  // If ANY package out for delivery, order is out for delivery
  if (statuses.some(s => s === constants.OUT_FOR_DELIVERY)) {
    return constants.OUT_FOR_DELIVERY;
  }

  // Otherwise, most common status
  return statuses[0] || constants.IN_TRANSIT;
}
```

## Carrier Tracking Implementations

**Adaptor Pattern** (`server/src/shared/storepepAdaptors/shipmentAdaptor.js:1-180`):

All carriers implement `makeTrackingRequest(trackingNumber, carrier)` method that returns:
```javascript
[
  {
    dateAndTime: Date,              // Checkpoint timestamp
    status: String,                 // StorePep status (IN_TRANSIT, etc.)
    location: String,               // "Memphis, TN" or facility name
    summary: String,                // Human-readable event description
    carrierTrackingCode: String     // Carrier-specific status code
  },
  // ... more checkpoints in chronological order
]
```

### Supported Carriers (45+)

**North America**:
- FedEx (SOAP: C2, REST: C39, Same Day: C37)
- UPS (XML: C3, OAuth REST: C38)
- USPS (Stamps.com: C4, Direct: C5, REST: C45, REST v2: C46, OAuth: C48)
- Canada Post (C6), Purolator (C16), Canpar (C36)
- Amazon Shipping (C43), XPO Logistics (C35)

**Europe**:
- DHL (Express: C1, Packet: C10, Sweden: C17)
- TNT (Global: C13, Australia: C20)
- Royal Mail (C29, Rates: C44), Parcel Force (C12)
- PostNord (C21), PostNL (C31)
- Geodis MyParcel (C23)

**Asia-Pacific**:
- Australia Post (C8, MyPost: C33, MyPost OAuth: C49)
- New Zealand Post (C30)
- Hong Kong Post (C19)
- Delhivery (C7), Blue Dart (C9), Xpressbees (C26), Daakit (C50)
- Couriers Please (C25), Sendle (C24), MyFastway (C34)

**Middle East**:
- Aramex (C11)

**Latin America**:
- Chil Express (C18)

**Multi-Carrier Aggregators**:
- EasyPost (C22) - 100+ carriers through single API
- Eshipz (C47) - Indian carrier aggregator

**Other**:
- Landmark Global (C28), APC Postal Logistics (C40)

### Carrier-Specific Tracking Examples

See [Carrier Tracking Implementations](#carrier-tracking-implementations-detailed) section below for FedEx, UPS, EasyPost examples.

## Status Mapping

**Helper**: `storepepMappedTrackingStatus(carrierStatus, carrierType)`

**Location**: `server/src/shared/storepepTracking/trackingStatusHelper.js:1-200`

**Purpose**: Maps carrier-specific status codes to StorePep unified statuses

**Example Mappings**:

**FedEx**:
```javascript
{
  'IT': constants.IN_TRANSIT,           // In Transit
  'OD': constants.OUT_FOR_DELIVERY,     // Out for Delivery
  'DL': constants.DELIVERED_UC,         // Delivered
  'DE': constants.EXCEPTION_1,          // Delivery Exception
  'AR': constants.IN_TRANSIT,           // Arrived at FedEx location
  'DP': constants.IN_TRANSIT,           // Departed FedEx location
  'PU': constants.IN_TRANSIT            // Picked up
}
```

**UPS**:
```javascript
{
  'I': constants.IN_TRANSIT,
  'X': constants.EXCEPTION_2,
  'D': constants.DELIVERED_UC,
  'M': constants.OUT_FOR_DELIVERY,
  'P': constants.IN_TRANSIT             // Pickup
}
```

**USPS**:
```javascript
{
  'Accepted': constants.IN_TRANSIT,
  'In Transit': constants.IN_TRANSIT,
  'Out for Delivery': constants.OUT_FOR_DELIVERY,
  'Delivered': constants.DELIVERED_UC,
  'Alert': constants.EXCEPTION_2,
  'Pre-Shipment': constants.INITIAL
}
```

**Fallback**: If no mapping found, defaults to `IN_TRANSIT`

### Attention Types

**Field**: `trackingPackage.attentionType`

**Values**: `"1"` (highest priority) through `"6"` (lowest priority)

**Purpose**: Classify exceptions by severity for merchant prioritization

**Examples**:
- **1**: Lost, damaged, refused by recipient
- **2**: Held at customs, clearance delay
- **3**: Weather delay, delivery attempted but failed
- **4**: Address correction required
- **5**: Held at carrier facility per customer request
- **6**: General delay, no specific issue

## Real-Time Updates via Socket.io

### Socket Event Flow

**1. Tracking Update Completed**:
```javascript
// server/src/shared/storepepTracking/storepepTrackingEngine.js
await emitNewSocketEvent({
  eventCode: constants.SOCKET_TRACKING_COMPLETED_CODE,
  accountUUID: order.accountUUID,
  data: {
    orderId: order.orderId,
    status: updatedStatus,
    trackingHistory: latestCheckpoints
  }
});
```

**2. Socket Connector** (`server/src/shared/storepepSocket.js:1-150`):
```javascript
async emitNewSocketEvent(newEmitEventObject) {
  const { eventCode, accountUUID, data } = newEmitEventObject;

  // 1. Generate JWT token
  const token = jwt.sign(
    { accountUUID, eventCode },
    config.apiKey + config.apiSecret,
    { expiresIn: '5m' }
  );

  // 2. Map event code to channel
  const channel = eventBasedChannels[eventCode] || SOCKET_EVENT_NAME;

  // 3. POST to WebSocket server
  await axios.post(`${STOREPEP_WEBSOCKET_SERVER_URL}/api/update`, {
    channel,
    data
  }, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'storepep-service-id': config.serviceId
    }
  });
}
```

**3. Event Channel Mapping**:
```javascript
const eventBasedChannels = {
  [constants.SOCKET_TRACKING_COMPLETED_CODE]: 'SOCKET_TRACKING_EVENT',
  [constants.SOCKET_INFO_CODE]: 'SOCKET_INFO_EVENT_NAME',
  [constants.SOCKET_ADMIN_DOWNLOAD_CODE]: 'SOCKET_ADMIN_DOWNLOAD_EVENT',
  // default: 'SOCKET_EVENT_NAME'
};
```

**4. Frontend Listener** (`client/src/components/form/tracking/trackingContainer.js:180-210`):
```javascript
listenToSocket() {
  const socket = io(WEBSOCKET_SERVER_URL, {
    auth: { token: this.props.authToken }
  });

  socket.on('SOCKET_TRACKING_EVENT', (data) => {
    const { orderId, status, trackingHistory } = data;

    // Update Redux store
    this.props.updateTrackingOrder(orderId, {
      status,
      trackingHistory
    });

    // Optionally show toast notification
    if (status === constants.DELIVERED_UC) {
      showNotification(`Order ${orderId} delivered!`);
    } else if (status.includes('EXCEPTION')) {
      showNotification(`Order ${orderId} has exception!`, 'error');
    }
  });
}
```

## Email Notifications

### Email Trigger Logic

**Function**: `triggerATrackingNotificationMailToCustomer(trackingPackage, order, latestEvent)`

**Location**: `server/src/shared/storepepTracking/trackingEventsEmailHelper.js:1-150`

**Decision Flow**:
```javascript
async function shouldSendEmail(trackingPackage, latestEvent) {
  // 1. Check if account has email notifications enabled
  const settings = await GeneralSettings.findOne({
    accountUUID: trackingPackage.accountUUID
  });

  if (!settings.trackingSettings.isRealTimeTrackingMailsRequired) {
    return false;
  }

  // 2. Get previous tracking event
  const previousEvent = await TrackingHistory.findOne({
    storepepTrackingNumber: trackingPackage.storepepTrackingNumber,
    dateAndTime: { $lt: latestEvent.dateAndTime }
  }).sort({ dateAndTime: -1 });

  if (!previousEvent) {
    return true; // First event, send email
  }

  // 3. Check if this event is meaningful
  const locationChanged = previousEvent.location !== latestEvent.location;
  const statusChanged = previousEvent.status !== latestEvent.status;
  const attentionTypeChanged = previousEvent.attentionType !== latestEvent.attentionType;

  // 4. Prevent duplicate emails for same location/status/time
  if (!locationChanged && !statusChanged && !attentionTypeChanged) {
    return false;
  }

  // 5. Key events always trigger email
  const keyStatuses = [
    constants.OUT_FOR_DELIVERY,
    constants.DELIVERED_UC,
    constants.EXCEPTION_1,
    constants.EXCEPTION_2
  ];

  if (keyStatuses.includes(latestEvent.status)) {
    return true;
  }

  return locationChanged || statusChanged;
}
```

### Email Template Generation

**Function**: `generateTrackingEmailTemplate(trackingPackage, order, trackingHistory)`

**Location**: `server/src/shared/storepepTracking/trackingEmailTemplateGenerator.js:1-250`

**Template Variables**:
```javascript
{
  customerName: order.shipping.firstName + ' ' + order.shipping.lastName,
  orderNumber: order.orderDisplayId,
  trackingNumber: trackingPackage.carrierTrackingId,
  carrierName: order.carrier,
  currentStatus: trackingPackage.lastTrackingStatus,
  estimatedDeliveryDate: trackingPackage.estimatedDeliveryDate,
  trackingUrl: getCarrierTrackingUrl(trackingPackage.carrierTrackingId, order.carrierType),
  checkpoints: trackingHistory.map(event => ({
    date: event.dateAndTime,
    location: event.location,
    status: event.summary
  }))
}
```

**Email Types**:
1. **Out for Delivery** - "Your package is out for delivery today"
2. **Delivered** - "Your package has been delivered"
3. **Exception** - "There's an issue with your delivery"
4. **Location Update** - "Your package is moving" (optional, can be disabled)

## API Endpoints

**Location**: `server/src/routes/tracking.js:1-350`

### Endpoint Reference

| Method | Path | Purpose | Request | Response |
|--------|------|---------|---------|----------|
| POST | `/api/tracking/` | Get tracking orders with filters | `{ accountUUID, filters, pagination }` | `{ orders: [], count: N }` |
| GET | `/api/tracking/package/:subOrderUUID/:storeUUID` | Get tracking packages for order | Path params | `{ packages: [] }` |
| POST | `/api/tracking/count` | Get counts by status | `{ accountUUID, dateRange }` | `{ initial: N, inTransit: N, delivered: N, exceptions: N, returns: N }` |
| POST | `/api/tracking/retrackall` | Manual re-track all orders | `{ accountUUID }` | `{ success: true, ordersTracked: N }` |
| POST | `/api/tracking/onetrackingdetails` | Get detailed history for shipment | `{ storepepTrackingNumber }` | `{ history: [], package: {}, order: {} }` |
| POST | `/api/tracking/generateTrackingEmailTemplate` | Generate email template | `{ storepepTrackingNumber }` | `{ html: "...", subject: "..." }` |
| GET | `/api/tracking/default` | Get default email template | None | `{ template: "..." }` |

### Example API Calls

**Get Tracking Orders**:
```javascript
POST /api/tracking/
{
  "accountUUID": "acc-123",
  "filters": {
    "status": "IN_TRANSIT",
    "dateFrom": "2024-01-01",
    "dateTo": "2024-01-31"
  },
  "pagination": {
    "page": 1,
    "limit": 50
  }
}
```

**Manual Re-track All**:
```javascript
POST /api/tracking/retrackall
{
  "accountUUID": "acc-123"
}

// Response
{
  "success": true,
  "ordersTracked": 127,
  "message": "Tracking update initiated for 127 orders"
}
```

## Frontend Components

### Component Hierarchy

```
TrackingContainer (Redux-connected)
  ├── TrackingFilters (date range, status tabs, search)
  ├── TrackingOrdersTable
  │     └── TrackingOrderRow (one per order)
  │           ├── Order details
  │           ├── Status badge with color
  │           ├── Tracking number
  │           ├── Last update time
  │           └── Click → Opens modal
  └── TrackingDetailsModal
        ├── TrackingHistory (timeline of checkpoints)
        ├── TrackingMap (optional, carrier-dependent)
        └── TrackingActions (re-track, email customer)
```

### TrackingContainer

**Location**: `client/src/components/form/tracking/trackingContainer.js:1-350`

**Redux State**:
```javascript
const mapStateToProps = (state) => ({
  trackingOrders: state.tracking.orders,
  trackingCounts: state.tracking.counts,
  isLoading: state.tracking.isLoading,
  authToken: state.auth.token
});

const mapDispatchToProps = {
  getTrackingOrdersAction,
  getTrackingOrdersCountAction,
  getOneTrackingDetailsAction,
  retrackAllOrdersAction
};
```

**Component Lifecycle**:
```javascript
componentDidMount() {
  // 1. Load tracking orders
  this.fetchTrackingOrders();

  // 2. Load status counts
  this.fetchTrackingCounts();

  // 3. Setup Socket.io listener
  this.listenToSocket();

  // 4. Setup auto-refresh (optional)
  this.refreshInterval = setInterval(() => {
    this.fetchTrackingOrders();
  }, 5 * 60 * 1000); // Every 5 minutes
}

componentWillUnmount() {
  // Cleanup
  clearInterval(this.refreshInterval);
  socket.off('SOCKET_TRACKING_EVENT');
}
```

### TrackingOrders Row

**Location**: `client/src/components/form/tracking/trackingOrders.js:1-200`

**Status Color Logic**:
```javascript
getStatusColor(order) {
  const { status, estimatedDeliveryDate } = order;

  if (status === constants.DELIVERED_UC) {
    return 'green'; // Delivered
  }

  if (status.includes('EXCEPTION')) {
    return 'red'; // Exception
  }

  if (status === constants.OUT_FOR_DELIVERY) {
    return 'blue'; // Out for delivery
  }

  // Check if delayed
  const now = new Date();
  const eta = new Date(estimatedDeliveryDate);
  const daysDiff = (now - eta) / (1000 * 60 * 60 * 24);

  if (daysDiff > 3) {
    return 'red'; // Severely delayed
  } else if (daysDiff > 1) {
    return 'orange'; // At risk
  }

  return 'gray'; // Normal in transit
}
```

### TrackingHistory Display

**Location**: `client/src/components/form/tracking/trackingHistory.js:1-150`

**Timeline Rendering**:
```javascript
render() {
  const { trackingHistory } = this.props;

  return (
    <div className="tracking-timeline">
      {trackingHistory.map((event, index) => (
        <div key={index} className="checkpoint">
          <div className="checkpoint-dot" />
          <div className="checkpoint-line" />
          <div className="checkpoint-content">
            <div className="checkpoint-date">
              {formatDate(event.dateAndTime)}
            </div>
            <div className="checkpoint-location">
              {event.location}
            </div>
            <div className="checkpoint-status">
              {event.summary}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Redux Actions

**Location**: `client/src/actions/trackingActions.js:1-150`

**Action Creators**:
```javascript
export const getTrackingOrdersAction = (filters) => async (dispatch) => {
  dispatch({ type: TRACKING_ORDERS_REQUEST });

  try {
    const response = await axios.post('/api/tracking/', {
      accountUUID: filters.accountUUID,
      filters,
      pagination: filters.pagination
    });

    dispatch({
      type: TRACKING_ORDERS_SUCCESS,
      payload: response.data.orders
    });
  } catch (error) {
    dispatch({
      type: TRACKING_ORDERS_FAILURE,
      error: error.message
    });
  }
};

export const retrackAllOrdersAction = (accountUUID) => async (dispatch) => {
  dispatch({ type: RETRACK_ALL_REQUEST });

  try {
    const response = await axios.post('/api/tracking/retrackall', {
      accountUUID
    });

    dispatch({
      type: RETRACK_ALL_SUCCESS,
      payload: response.data
    });

    // Show success toast
    showNotification(`Tracking update initiated for ${response.data.ordersTracked} orders`);
  } catch (error) {
    dispatch({
      type: RETRACK_ALL_FAILURE,
      error: error.message
    });
  }
};
```

## Carrier Tracking Implementations (Detailed)

### FedEx REST API Tracking

**Location**: `server/src/shared/API/carriers/fedExRest/fedExShipmentTracker.js:1-200`

**Implementation**:
```javascript
async makeTrackingRequest(trackingNumber, carrier) {
  // 1. Get OAuth token
  const token = await this.getOAuthToken(carrier);

  // 2. Build tracking request
  const requestBody = {
    trackingInfo: [{
      trackingNumberInfo: {
        trackingNumber: trackingNumber
      }
    }],
    includeDetailedScans: true
  };

  // 3. Call FedEx Track API
  const response = await axios.post(
    `${carrier.apiUrl}/track/v1/trackingnumbers`,
    requestBody,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-locale': 'en_US'
      }
    }
  );

  // 4. Parse response
  const scanEvents = response.data.output.completeTrackResults[0]
    .trackResults[0].scanEvents || [];

  // 5. Transform to StorePep format
  const trackingHistory = scanEvents.map(event => ({
    dateAndTime: new Date(event.date),
    status: this.mapFedExStatus(event.eventType),
    location: `${event.scanLocation.city}, ${event.scanLocation.stateOrProvinceCode}`,
    summary: event.eventDescription,
    carrierTrackingCode: event.eventType
  }));

  return trackingHistory.reverse(); // Chronological order
}

mapFedExStatus(fedexEventType) {
  const statusMap = {
    'PU': constants.IN_TRANSIT,        // Picked up
    'AR': constants.IN_TRANSIT,        // Arrived at FedEx location
    'DP': constants.IN_TRANSIT,        // Departed FedEx location
    'IT': constants.IN_TRANSIT,        // In transit
    'OD': constants.OUT_FOR_DELIVERY,  // Out for delivery
    'DL': constants.DELIVERED_UC,      // Delivered
    'DE': constants.EXCEPTION_1,       // Delivery exception
    'CA': constants.EXCEPTION_2        // Customer not available
  };

  return statusMap[fedexEventType] || constants.IN_TRANSIT;
}
```

### UPS OAuth API Tracking

**Location**: `server/src/shared/API/carriers/upsRestApi/upsShipmentTracker.js:1-180`

**Implementation**:
```javascript
async makeTrackingRequest(trackingNumber, carrier) {
  // 1. Get OAuth token
  const token = await this.getOAuthToken(carrier);

  // 2. Call UPS Track API
  const response = await axios.get(
    `${carrier.apiUrl}/api/track/v1/details/${trackingNumber}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'transId': uuid(),
        'transactionSrc': 'StorePep'
      },
      params: {
        locale: 'en_US',
        returnSignature: 'false'
      }
    }
  );

  // 3. Parse response
  const packageData = response.data.trackResponse.shipment[0].package[0];
  const activities = packageData.activity || [];

  // 4. Transform to StorePep format
  const trackingHistory = activities.map(activity => ({
    dateAndTime: new Date(`${activity.date} ${activity.time}`),
    status: this.mapUPSStatus(activity.status.type),
    location: `${activity.location.address.city}, ${activity.location.address.stateProvinceCode}`,
    summary: activity.status.description,
    carrierTrackingCode: activity.status.code
  }));

  return trackingHistory.reverse(); // Chronological order
}

mapUPSStatus(upsStatusType) {
  const statusMap = {
    'I': constants.IN_TRANSIT,         // In Transit
    'X': constants.EXCEPTION_2,        // Exception
    'D': constants.DELIVERED_UC,       // Delivered
    'M': constants.OUT_FOR_DELIVERY,   // Out for Delivery
    'P': constants.IN_TRANSIT,         // Pickup
    'MV': constants.IN_TRANSIT         // Manifest Pickup
  };

  return statusMap[upsStatusType] || constants.IN_TRANSIT;
}
```

### EasyPost Tracking

**Location**: `server/src/shared/API/carriers/easyPost/easyPostShipmentTracker.js:1-120`

**Implementation**:
```javascript
async makeTrackingRequest(trackingNumber, carrier) {
  const Easypost = require('@easypost/api');
  const api = new Easypost(carrier.apiKey);

  // 1. Retrieve tracker from EasyPost
  const tracker = await api.Tracker.retrieve(trackingNumber);

  // 2. Get tracking details
  const trackingDetails = tracker.tracking_details || [];

  // 3. Transform to StorePep format
  const trackingHistory = trackingDetails.map(detail => ({
    dateAndTime: new Date(detail.datetime),
    status: this.mapEasyPostStatus(detail.status),
    location: `${detail.tracking_location.city}, ${detail.tracking_location.state}`,
    summary: detail.message,
    carrierTrackingCode: detail.status
  }));

  // 4. Add estimated delivery date if available
  if (tracker.est_delivery_date) {
    trackingHistory.estimatedDeliveryDate = new Date(tracker.est_delivery_date);
  }

  return trackingHistory;
}

mapEasyPostStatus(easypostStatus) {
  const statusMap = {
    'pre_transit': constants.INITIAL,
    'in_transit': constants.IN_TRANSIT,
    'out_for_delivery': constants.OUT_FOR_DELIVERY,
    'delivered': constants.DELIVERED_UC,
    'available_for_pickup': constants.OUT_FOR_DELIVERY,
    'return_to_sender': constants.EXCEPTION_2,
    'failure': constants.EXCEPTION_1,
    'cancelled': constants.EXCEPTION_1,
    'error': constants.EXCEPTION_1
  };

  return statusMap[easypostStatus] || constants.IN_TRANSIT;
}
```

## Return Shipment Tracking

**Field**: `trackingOrder.isReturned = true`

**Flow**:
```
1. Customer initiates return
   ↓
2. Return label generated (see Order Returns module)
   ↓
3. TrackingOrder created with isReturned: true
   ↓
4. TrackingPackages created with return tracking numbers
   ↓
5. TrackingHistory records marked with direction: "RETURN"
   ↓
6. Tracking updates follow same cron schedule
   ↓
7. Status progresses: INITIAL → IN_TRANSIT → DELIVERED
   ↓
8. Return delivered notification sent to merchant
```

**Differentiation**:
- Return orders shown in separate tab/filter in UI
- Email notifications go to merchant, not customer
- Status colors may differ (returns prioritized differently)

## Performance Optimizations

### 1. Batch Tracking Updates

Instead of sequential API calls:
```javascript
// Instead of this (slow):
for (const pkg of packages) {
  await trackPackage(pkg);
}

// Do this (parallel):
await Promise.all(packages.map(pkg => trackPackage(pkg)));
```

### 2. Carrier Rate Limiting

**Implementation**: Token bucket algorithm per carrier

```javascript
const rateLimiter = new RateLimiter({
  [constants.FEDEX_CARRIER_CODE]: { tokensPerHour: 1000, maxBurst: 10 },
  [constants.UPS_CARRIER_CODE]: { tokensPerHour: 250, maxBurst: 5 },
  [constants.DHL_CARRIER_CODE]: { tokensPerHour: 500, maxBurst: 10 }
});

await rateLimiter.acquire(carrierType);
await carrierHelper.makeTrackingRequest(trackingNumber);
```

### 3. Caching Tracking Results

**TTL**: 1 hour (tracking doesn't change rapidly)

```javascript
const cacheKey = `tracking:${trackingNumber}:${carrierType}`;
const cachedResult = await redis.get(cacheKey);

if (cachedResult) {
  return JSON.parse(cachedResult);
}

const result = await carrierHelper.makeTrackingRequest(trackingNumber);
await redis.setex(cacheKey, 3600, JSON.stringify(result)); // 1 hour TTL
return result;
```

### 4. Selective Tracking Updates

Only track orders that are likely to have updates:
```javascript
const shouldTrack = (trackingPackage) => {
  const hoursSinceLastTrack = (Date.now() - trackingPackage.lastTrackedTime) / (1000 * 60 * 60);

  // Don't track if updated in last 2 hours
  if (hoursSinceLastTrack < 2) return false;

  // Always track if out for delivery
  if (trackingPackage.status === constants.OUT_FOR_DELIVERY) return true;

  // Track in-transit packages every 6 hours
  if (trackingPackage.status === constants.IN_TRANSIT && hoursSinceLastTrack >= 6) return true;

  return false;
};
```

## Error Handling

### Tracking API Failures

**Common Errors**:
1. **Invalid Tracking Number**: Carrier returns 404 or "not found"
2. **Authentication Failure**: Expired OAuth token, invalid credentials
3. **Rate Limit Exceeded**: Carrier throttling
4. **Network Timeout**: Carrier API slow/unavailable

**Handling**:
```javascript
async function safeTrackingRequest(trackingNumber, carrier) {
  try {
    return await carrierHelper.makeTrackingRequest(trackingNumber, carrier);
  } catch (error) {
    if (error.response?.status === 404) {
      // Tracking number not found - likely too recent
      logger.warn(`Tracking not available yet: ${trackingNumber}`);
      return null; // Will retry on next cron cycle
    }

    if (error.response?.status === 401) {
      // Auth failure - refresh token and retry
      await refreshCarrierToken(carrier);
      return await carrierHelper.makeTrackingRequest(trackingNumber, carrier);
    }

    if (error.response?.status === 429) {
      // Rate limited - exponential backoff
      await sleep(Math.pow(2, retryCount) * 1000);
      return await carrierHelper.makeTrackingRequest(trackingNumber, carrier);
    }

    // Other errors - log and continue
    logger.error(`Tracking failed for ${trackingNumber}:`, error);
    return null;
  }
}
```

## Dependencies

- [Carrier System Overview](./carrier-system-overview.md) - Adaptor pattern for carrier APIs
- [Carrier Integrations](./carrier-integrations.md) - List of 45+ supported carriers
- [Label Generation](./label-generation.md) - Labels created before tracking begins
- [Order Lifecycle](../orders/order-lifecycle.md) - Tracking fits into order flow
- [Order Returns](../orders/order-returns.md) - Return shipment tracking

## Referenced By

- Order detail pages display tracking status
- Customer-facing tracking pages use these APIs
- Email notifications triggered by tracking updates
- Dashboard analytics aggregate tracking data

## Configuration

**Environment Variables**:
- `TRACKING_CRON_SCHEDULE`: Cron expression for tracking updates (default: `0 */6 * * *`)
- `TRACKING_BATCH_SIZE`: Number of orders to track per batch (default: 50)
- `CARRIER_API_TIMEOUT`: Timeout for carrier tracking API calls (default: 30000ms)

**Account Settings**:
- `trackingSettings.isRealTimeTrackingMailsRequired`: Enable/disable email notifications
- `trackingSettings.emailOnOutForDelivery`: Email when out for delivery
- `trackingSettings.emailOnDelivered`: Email when delivered
- `trackingSettings.emailOnException`: Email on exceptions/delays

**Feature Toggles**:
- `enableTrackingCron`: Enable/disable automatic tracking updates
- `enableTrackingEmailNotifications`: Master switch for all tracking emails
- `enableSocketTrackingEvents`: Enable/disable real-time Socket.io updates

## Common Patterns

### Fetch Tracking for Order

```javascript
// Get tracking packages for an order
const trackingPackages = await TrackingPackages.find({
  subOrderUUID: order.subOrderUUID
});

// Get tracking history for each package
const trackingHistory = await Promise.all(
  trackingPackages.map(pkg =>
    TrackingHistory.find({
      storepepTrackingNumber: pkg.storepepTrackingNumber
    }).sort({ dateAndTime: 1 })
  )
);
```

### Manual Re-track Single Order

```javascript
const order = await TrackingOrder.findOne({ orderId });
const packages = await TrackingPackages.find({ subOrderUUID: order.subOrderUUID });

await trackAndUpdateTrackingDetails(packages, order, currentUser, applicationConfig);

// Emit socket event
await emitNewSocketEvent({
  eventCode: constants.SOCKET_TRACKING_COMPLETED_CODE,
  accountUUID: order.accountUUID,
  data: { orderId: order.orderId, status: order.status }
});
```

### Display Tracking Timeline

```javascript
// Component code
const TrackingTimeline = ({ storepepTrackingNumber }) => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchTrackingHistory(storepepTrackingNumber).then(setHistory);
  }, [storepepTrackingNumber]);

  return (
    <div className="timeline">
      {history.map((event, i) => (
        <div key={i} className="checkpoint">
          <div className="date">{formatDate(event.dateAndTime)}</div>
          <div className="location">{event.location}</div>
          <div className="status">{event.summary}</div>
        </div>
      ))}
    </div>
  );
};
```

## Test Coverage

**Automated E2E Tests**: 1 Playwright test covering tracking functionality

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| Track Order from Order Grid | `orderGrid/trackingFromGrid/trackOrderFromOrderGrid.spec.ts` | ✅ Passing |

**Test Coverage**: 1/15+ tracking features tested (7% coverage)

**Tested Scenarios**:
- ✅ Access tracking from order grid
- ✅ View tracking history timeline

**Untested Scenarios**:
- ❌ Automatic tracking updates (cron job)
- ❌ Carrier API integration testing
- ❌ Status mapping verification
- ❌ Email notification triggers
- ❌ Socket.io real-time updates
- ❌ Multi-package tracking aggregation
- ❌ Return shipment tracking
- ❌ Manual re-track functionality
- ❌ Tracking for 45+ different carriers
- ❌ Error handling for invalid tracking numbers
- ❌ Rate limiting behavior
- ❌ Tracking cache functionality

**Test Suite Location**: `mcsl-test-automation/tests/orderGrid/trackingFromGrid/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Known Issues / Tech Debt

1. **No webhook support**: Relies on polling instead of carrier push notifications
2. **Rate limit handling**: Basic implementation, could be more sophisticated
3. **Duplicate checkpoint detection**: Simple equality check may miss near-duplicates
4. **No retry queue**: Failed tracking requests not queued for retry
5. **Inconsistent carrier response parsing**: Each carrier has custom parser, no standardization
6. **No tracking analytics**: Missing aggregated metrics (avg delivery time, exception rates)
7. **Email template customization limited**: Merchants can't fully customize tracking emails
8. **No SMS notifications**: Only email supported for customer notifications

## Related Pages

- [Carrier System Overview](./carrier-system-overview.md)
- [Carrier Integrations](./carrier-integrations.md)
- [Label Generation](./label-generation.md)
- [Order Lifecycle](../orders/order-lifecycle.md)
- [Order Returns](../orders/order-returns.md)
