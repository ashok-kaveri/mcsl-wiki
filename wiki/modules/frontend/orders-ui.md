---
title: Orders UI (Frontend)
category: module
domain: orders
sources: [storepep-react]
status: complete
last_updated: 2026-04-30
git_reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020
---

# Orders UI (Frontend)

## Overview

The orders UI is the primary interface merchants use to view, filter, manage, and process orders. Built with React, Redux, and AG Grid, it provides a high-performance data table with real-time updates, bulk actions, and deep integration with the order processing pipeline.

**Main Component**: `client/src/components/form/views/allorders.js`
**Redux Actions**: `client/src/actions/ordersActions.js`, `client/src/actions/orders/`
**Redux State**: Multiple reducers managing orders, filters, tabs, and UI state

## Key Components

### AllOrders Grid Component

**File**: `client/src/components/form/views/allorders.js`

The primary order management interface providing:
- Paginated order listing with server-side filtering
- Multi-column sorting
- Status-based tabs (All, Initial, Processing, Label Created, Shipped)
- Bulk selection and actions
- Real-time order updates via Socket.io
- Quick filters (date range, search, carrier, store)

**Component Location**: Rendered at route `/home/views/orders/status/:status`

### Order Status Tabs

**Redux State**: `ordersTab` reducer (`client/src/reducers/allOrdersPageTabs.js`)

Status-based views:
- **All Orders** - Complete order list
- **Initial** - Newly imported, not yet processed
- **Processing** - In automation/rate shopping
- **Label Created** - Labels generated, ready to ship
- **Shipped** - Handed to carrier, tracking active
- **Reprocessing** - Failed automation, needs manual review

Tab state persisted in Redux to maintain user's active view across navigation.

### Order Filters

**Redux State**: `ordersFilters` reducer (`client/src/reducers/allOrdersPageFilters.js`)

Filter options:
- **Date Range**: Order date or created date (uses `react-dates` date range picker)
- **Store**: Filter by connected store (Shopify, WooCommerce, etc.)
- **Carrier**: Filter by selected carrier
- **Service**: Filter by shipping service level
- **Search**: Free-text search across order number, customer name, SKU, tracking
- **Status**: StorePep status or original store status
- **Tags**: Custom order tags

Filters applied as query params and sent to backend via `POST /api/orders` with filter object.

### Order Summary Panel

**Component**: `client/src/components/form/views/summary/order-summary/`

Detailed order view showing:
- Customer information (name, email, phone)
- Shipping and billing addresses
- Line items with product details
- Package configuration
- Selected carrier and service
- Rate comparison table
- Label preview and download
- Tracking information

**Route**: `/home/views/order/:orderId`

### Order Search

**Redux State**: `orderSearchRequest` reducer (`client/src/reducers/orderSearchRequest.js`)

Advanced search functionality supporting:
- Search by order number
- Search by tracking number
- Search by SKU
- Search by customer name/email
- Autocomplete suggestions

Search requests routed to order-search microservice for performance.

## Redux State Management

### Orders Reducer

**File**: `client/src/reducers/orders.js`

State shape:
```javascript
{
  ordersList: [],           // Current page of orders
  selectedOrder: {},        // Order in summary view
  loading: false,           // API request in progress
  error: null,              // Error message if request failed
}
```

### All Order Page Reducer

**File**: `client/src/reducers/allOrderPage.js`

State shape:
```javascript
{
  orders: [],               // Orders for current tab/filter
  totalCount: 0,            // Total matching orders (for pagination)
  currentPage: 1,
  pageSize: 50,
  sortBy: 'createdAt',
  sortDirection: 'desc',
}
```

### Orders Count Reducer

**File**: `client/src/reducers/orders.js` (ordersCount export)

Tracks order counts by status for tab badges:
```javascript
{
  initial: 42,
  processing: 18,
  labelCreated: 105,
  shipped: 523,
  total: 688,
}
```

Updated via Socket.io when orders change status.

### Stored Packages & Return Packages

**State**: `storedPackages`, `returnPackages` reducers

Manages package configurations for:
- Label generation (forward shipments)
- Return label generation
- Package dimension/weight overrides
- Multi-package shipments

**Actions** (`client/src/actions/ordersActions.js:9-74`):
- `storedPackagesStore(data)` - Add package configuration
- `updateStoredPackagesStore(data)` - Update package (generate, create shipment, reset)
- `returnPackagesStore(data)` - Add return package
- Package states: generate → create shipment → label created → reset

## Redux Actions

### Order Fetching

**File**: `client/src/actions/ordersActions.js:83-95`

```javascript
export const getOrders = (requestObject, url, isNewSortEnabled) => async (dispatch) => {
  await dispatch(newAction(OrderTypes.REQUESTED_ORDERS));

  const headers = {
    ...(isNewSortEnabled && {
      Accept: 'application/vnd.storepep.orders.service-v2+json'
    }),
  };

  const response = await axios.post(
    url || '/api/orders',
    requestObject,
    { headers }
  );

  await dispatch(newAction(OrderTypes.RECEIVED_ORDERS, {
    orders: response.data.orders,
  }));

  return response;
};
```

**Request Object Shape**:
```javascript
{
  page: 1,
  pageSize: 50,
  sortBy: 'createdAt',
  sortDirection: 'desc',
  filters: {
    status: 'initial',
    dateRange: { start: '2026-01-01', end: '2026-04-30' },
    storeId: 'abc123',
    // ...
  }
}
```

**Service Versioning**: `isNewSortEnabled` flag enables v2 orders API with improved sorting logic (header: `application/vnd.storepep.orders.service-v2+json`).

### Order Import

**File**: `client/src/actions/ordersActions.js:78-80`

```javascript
export function importOrders(request = {}) {
  return () => axios.post('/api/orders/importorders', request);
}
```

Triggers manual order import from connected store. Request includes:
- `storeId` - Which store to import from
- `dateRange` - Optional date filter for import
- `orderStatus` - Optional status filter

### Order Action Types

**File**: `client/src/actions/orders/ordersTypes.js`

Action type constants for Redux reducers:
- `REQUESTED_ORDERS` - Fetch started
- `RECEIVED_ORDERS` - Fetch completed
- `ORDER_SELECTED` - Order opened in summary view
- `ORDER_UPDATED` - Order changed (local or Socket.io)
- `ORDER_STATUS_CHANGED` - Status transition
- `ORDERS_COUNT_UPDATED` - Tab badge counts refreshed

### Order Actions Module

**Directory**: `client/src/actions/orders/` (index.js + sub-modules)

Additional order-specific actions:
- Bulk actions (process, generate labels, cancel)
- Status changes
- Address updates
- Package configuration
- Carrier service selection

## Real-Time Updates

### Socket.io Integration

**Event Handlers** (in order grid component):

```javascript
socket.on('order:updated', (orderData) => {
  dispatch(updateOrderInList(orderData));
});

socket.on('order:status:changed', ({ orderId, newStatus }) => {
  dispatch(updateOrderStatus(orderId, newStatus));
  dispatch(refreshOrderCounts()); // Update tab badges
});

socket.on('label:generated', ({ orderId, labelUrl }) => {
  dispatch(updateOrderLabel(orderId, labelUrl));
});
```

Updates trigger without manual refresh:
- Order status changes (automation completion, manual updates)
- Label generation completion (batch processing)
- Tracking updates (carrier status changes)
- Import completion (webhook or manual imports)

## UI Features

### Bulk Actions

**Location**: Action menu in order grid header

Actions available:
- Process orders (INITIAL → PROCESSING)
- Generate labels (PROCESSING → LABEL_CREATED)
- Mark as shipped (LABEL_CREATED → SHIPPED)
- Cancel shipments
- Change carrier/service
- Apply automation rules
- Export orders

Bulk action implementation routes to `POST /api/orders/bulk-action` with:
```javascript
{
  action: 'GENERATE_LABELS',
  orderIds: ['id1', 'id2', '...'],
  options: { /* action-specific options */ }
}
```

See [Order Bulk Actions](../orders/order-bulk-actions.md) for complete bulk action reference.

### Batch Processing View

**Route**: `/home/views/orders/action/labelcreated/:batchId`
**Component**: `client/src/components/form/views/common/batchProcessOrders.js`

After bulk label generation, shows:
- Batch summary (total orders, success count, failure count)
- Per-order results (label URL, tracking number, or error message)
- Bulk print button (prints all labels via QZ Tray)
- Download all labels (ZIP archive)
- Retry failed orders

### Order Grid Columns

Customizable columns via user settings:
- Order number (clickable to summary)
- Order date
- Customer name
- Destination (city, state, country)
- Line item count
- Total weight
- Selected carrier/service
- Rate
- StorePep status
- Store status
- Tracking number (clickable to tracking page)
- Actions (quick actions menu)

Column visibility, order, and width saved in user preferences.

### Performance Optimizations

**AG Grid Configuration**:
- Row virtualization - Only renders visible rows (handles 10,000+ orders)
- Server-side pagination - Fetches 50 orders at a time
- Lazy column rendering
- Cell caching for expensive calculations

**Debounced Search**:
- Search input debounced (500ms) to reduce API calls
- Autocomplete suggestions fetched from order-search service

**Memoization**:
- Expensive calculations (total weight, package count) memoized
- React.PureComponent used for row components to prevent unnecessary re-renders

## Data Flow

1. **User Action** (filter change, page navigation, bulk action)
2. **Redux Action Dispatched** (`getOrders`, `updateFilters`, etc.)
3. **API Request** (`POST /api/orders` with filter/pagination params)
4. **Backend Processing** (database query, apply filters, sort, paginate)
5. **Response Received** (orders array + total count)
6. **Redux State Updated** (`RECEIVED_ORDERS` action)
7. **Component Re-renders** (AG Grid updates with new data)
8. **Socket.io Updates** (real-time changes merged into grid)

## Related Backend Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/orders` | POST | Fetch orders with filters |
| `/api/orders/importorders` | POST | Import from store |
| `/api/orders/bulk-action` | POST | Execute bulk action |
| `/api/orders/:orderId` | GET | Fetch single order details |
| `/api/orders/:orderId/packages` | GET | Get package configurations |
| `/api/orders/:orderId/rates` | GET | Get available carrier rates |
| `/api/orders/export` | POST | Export orders to CSV |

See [Order Lifecycle](../orders/order-lifecycle.md) for backend implementation details.

## Dependencies

**Frontend**:
- [Frontend Architecture](../../architecture/frontend-architecture.md) - React, Redux setup
- [Redux Patterns](../../patterns/redux-patterns.md) - Action/reducer conventions

**Backend**:
- [Order Lifecycle](../orders/order-lifecycle.md) - Backend order processing
- [Order Bulk Actions](../orders/order-bulk-actions.md) - Bulk action implementations

**Integrations**:
- [Shipment Tracking](../shipping/shipment-tracking.md) - Tracking UI integration
- [Label Generation](../shipping/label-generation.md) - Label creation UI

## Referenced By

- [Order Bulk Actions](../orders/order-bulk-actions.md) - UI triggers for bulk actions
- [Order Returns](../orders/order-returns.md) - Return label UI
- [Batch Processing](../shipping/batch-processing.md) - Batch result views

## Known Issues / Tech Debt

1. **AG Grid v28**: Not on latest version (v31+), missing newer performance features
2. **Class-Based Components**: Most order components are class-based, could benefit from hooks
3. **Redux Boilerplate**: Verbose action/reducer pattern for simple state updates
4. **Filter State Complexity**: Filter state split across multiple reducers, could be consolidated
5. **Search Performance**: Full-text search on large datasets can be slow without proper indexing
6. **Real-time Scaling**: Socket.io updates for high-volume accounts can cause UI performance issues

## Test Coverage

See [Features](../../features.md) for test coverage of order management workflows.

**Automated E2E Tests** (Playwright):
- Order grid rendering and pagination
- Status tab switching
- Bulk action execution
- Order search functionality
- Real-time update handling

**Coverage**: Medium (70-80%) - Core workflows tested, edge cases manual verification.
