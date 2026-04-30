---
title: Frontend Architecture
category: architecture
status: complete
last_updated: 2026-04-30
git_reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020
---

# Frontend Architecture

## Overview

The StorePep frontend is a React-based single-page application (SPA) built with Redux for state management and Material-UI for component styling. It provides a comprehensive merchant dashboard for managing orders, shipping, products, and account settings.

**Location**: `client/src/`
**Entry Point**: `client/src/index.js:1-89`
**Build Output**: Webpack bundle served from S3/CDN

## Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 16.10.2 | UI framework |
| Redux | 4.0.1 | State management |
| Redux-Form | 7.4.2 | Form state management |
| Redux-Thunk | 2.3.0 | Async action middleware |
| React Router DOM | 4.3.1 | Client-side routing |
| Material-UI | 3.9.0 | Component library (v3) |
| material-ui (legacy) | 0.20.2 | Legacy components (v0) |
| Axios | 0.19.0 | HTTP client |
| Socket.io Client | 2.2.0 | Real-time updates |
| Webpack | 4.28.1 | Module bundler |
| Babel | 7.x | JavaScript transpilation |

## Directory Structure

```
client/src/
├── index.js                    # Application entry point, bootstrapping
├── reduxStore.js               # Redux store configuration
├── routes.js                   # Main routing configuration
├── storepepUsersRoutes.js      # Merchant user routes
├── storepepTeamRoutes.js       # Admin/team routes
├── muiTheme.js                 # Material-UI theme configuration
│
├── components/                 # React components
│   ├── pages/                  # Page-level components (27 pages)
│   │   ├── header/             # App header and navigation
│   │   ├── help/               # Help and documentation
│   │   ├── login/              # Authentication pages
│   │   ├── signup/             # Registration flow
│   │   ├── settings/           # Account settings
│   │   ├── products/           # Product management
│   │   ├── tracking/           # Shipment tracking
│   │   ├── storepepTeam/       # Admin pages
│   │   ├── subscriptionAndPayment/  # Billing pages
│   │   └── views/              # Various feature pages
│   ├── form/                   # Form-specific components
│   └── common/                 # Reusable UI components
│
├── actions/                    # Redux action creators (87 files)
│   ├── packaging/
│   ├── order/
│   ├── products/
│   ├── manifest/
│   ├── labels/
│   ├── workflows/
│   ├── jobs/
│   ├── authActions.js          # Authentication actions
│   ├── settingsActions.js      # Settings actions
│   └── ... (other domains)
│
├── reducers/                   # Redux reducers (26 files)
│   ├── orders.js
│   ├── products.js
│   ├── auth.js
│   ├── settings.js
│   └── ...
│
├── utils/                      # Utility modules (25+ files)
│   ├── setAuthorizationToken.js
│   ├── unauthorizedErrorHandler.js
│   ├── constants.js
│   ├── utilFunctions.js
│   ├── axiosFunctions.js
│   ├── tokenHelperFunctions.js
│   ├── sentry/                 # Error tracking setup
│   └── ...
│
├── customComponents/           # Custom reusable components
├── helperFunctions/            # Business logic helpers
├── ACL/                        # Access control components
├── socket/                     # Socket.io client setup
│   └── sockets.js
│
└── [other resources]
```

## Application Bootstrap

**File**: `client/src/index.js:1-89`

The application bootstraps in this sequence:

1. **Initialize Sentry** (`index.js:39`) - Error tracking for production
2. **Configure Axios** (`index.js:40`) - Set API base URL based on hostname
3. **Check for Auth Tokens** (`index.js:42-64`):
   - StorePep team token (admin access)
   - JWT token (merchant access)
   - Query param token (SSO/magic link)
4. **Dispatch Auth Actions** - Set current user in Redux store
5. **Configure Socket.io** (`index.js:69`) - Real-time connection setup
6. **Initialize Web Vitals** (`index.js:70`) - Performance monitoring
7. **Render React Tree** (`index.js:81-88`):
   ```javascript
   ReactDOM.render(
     <MuiThemeProvider theme={materialUiTheme}>
       <V0MuiThemeProvider muiTheme={getMuiTheme(muiTheme)}>
         <Provider store={store}>
           <Routes />
         </Provider>
       </V0MuiThemeProvider>
     </MuiThemeProvider>,
     document.getElementById('app')
   );
   ```

**Note**: Dual Material-UI providers support both v3 (modern) and v0 (legacy) components during migration.

## State Management (Redux)

### Store Structure

**File**: `client/src/reducers/rootReducers.js:55-115`

The Redux store combines 26+ reducers organized by domain:

```javascript
{
  // Authentication & User
  auth: {},                           // Merchant user auth (storepepUserReducer)
  storepepTeamAuth: {},               // Admin/team auth (storepepTeamReducer)
  displayLoginPopup: bool,            // Login modal state
  displaySessionExpiredPopup: bool,   // Session expiry modal
  accountSetupStatus: bool,           // Account setup completion

  // Orders
  orders: {},                         // Order page state
  totalorders: {},                    // Total order counts
  ordersLoader: bool,                 // Loading state
  ordersCount: {},                    // Count by status
  ordersFilters: {},                  // Filter state
  ordersTab: {},                      // Active tab state
  orderSearchRequest: {},             // Search query state

  // Products
  productsCount: {},                  // Product counts
  productsFilters: {},                // Product filter state
  productCustomValues: {},            // Custom product metadata

  // Shipping & Labels
  packaging: {},                      // Packaging settings
  storedPackages: {},                 // Saved package configurations
  returnPackages: {},                 // Return label packages
  label: {},                          // Label generation state
  addressDetails: {},                 // Origin address (originAddress)
  tracking: {},                       // Tracking state
  trackingOrdersCount: {},            // Tracking counts

  // Carriers
  carrierDetails: {},                 // Carrier info
  carrierServices: {},                // Carrier service options
  carrierHolidayServices: {},         // Holiday service availability
  carrierServiceNames: {},            // Display names
  carrierHalHelpConfig: {},           // HAL help config
  easypostSavedCarrierList: {},       // EasyPost carriers
  distinctCarrierTypes: {},           // Unique carrier types
  dhlExpress: {},                     // DHL Express settings

  // Stores & Platforms
  storeDetails: {},                   // Connected store info
  woocommerce: {},                    // WooCommerce settings

  // Automation & Workflows
  automationRule: {},                 // Automation rules state
  workflows: {},                      // Workflow definitions
  jobs: {},                           // Background jobs

  // UI & UX
  multiSelect: {},                    // Multi-select state
  batchKey: {},                       // Batch operation key
  toggleNavBarDrawer: bool,           // Drawer open/close
  subNavBarContext: {},               // Sub-navigation context
  notifications: [],                  // Notification queue
  notificationsCount: {},             // Unread counts
  clientToggles: {},                  // Feature toggles
  toggles: {},                        // Additional toggles

  // Templates
  packingSlipTemplate: {},            // Packing slip template
  taxInvoiceTemplate: {},             // Tax invoice template
  emailTemplate: {},                  // Email template
  pickListTemplate: {},               // Pick list template

  // Other
  generalSettings: {},                // App-wide settings
  licenseAgreements: {},              // Agreement acceptance state
  messagesStore: {},                  // Messaging system
  exportOrders: {},                   // Order export state
  touchlessPrint: {},                 // Touchless printing state
  vendorDetails: {},                  // Vendor information
  UTCTimeZoneOffset: {},              // Timezone offset
  dateFilterRange: {},                // Date range selection
  enabledFeatures: {},                // Feature entitlements
  subscriptionUpgrade: {},            // Subscription state

  // Redux-Form
  form: {}                            // Redux-Form state
}
```

**Reset Behavior** (`rootReducers.js:117-129`):
- `USER_LOGOUT` - Clears entire state
- `CLEAR_STOREPEP_USER` - Clears user state but retains admin auth and form state

### Action Pattern

All actions follow Redux conventions:

```javascript
// Action creator (actions/<domain>/actionName.js)
export const fetchOrders = (filters) => (dispatch) => {
  dispatch({ type: 'FETCH_ORDERS_REQUEST' });

  return axios.get('/api/orders', { params: filters })
    .then(response => {
      dispatch({
        type: 'FETCH_ORDERS_SUCCESS',
        payload: response.data
      });
    })
    .catch(error => {
      dispatch({
        type: 'FETCH_ORDERS_FAILURE',
        payload: error.message
      });
    });
};
```

**Location**: `client/src/actions/` (87 action files organized by domain)

### Reducer Pattern

Reducers handle state updates immutably:

```javascript
// reducers/orders.js
const initialState = {
  ordersList: [],
  loading: false,
  error: null
};

export default function(state = initialState, action) {
  switch (action.type) {
    case 'FETCH_ORDERS_REQUEST':
      return { ...state, loading: true };
    case 'FETCH_ORDERS_SUCCESS':
      return { ...state, loading: false, ordersList: action.payload };
    case 'FETCH_ORDERS_FAILURE':
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
}
```

**Location**: `client/src/reducers/` (26 reducer files)

### Middleware

- **Redux-Thunk**: Handles async actions (API calls)
- **Redux-Form**: Manages form state separately from domain state

## Routing

**Main Router**: `client/src/routes.js:1-109`

StorePep uses React Router v4 with a dual-tiered routing system supporting both merchant users and internal admin users.

### Root Routes (`routes.js`)

**Public Routes**:
- `/` - Redirect to login or dashboard based on auth state
- `/signUp` - User registration
- `/verify/:verificationtype/:verificationData` - Email verification
- `/forgotpassword` - Password reset
- `/accountsetup` - Account setup completion page

**Auth Detection** (`routes.js:56-92`):
- Checks `storepepteamToken` → redirect to `/storepepteam/home/accounts`
- Checks `jwtToken` → redirect to `/home/views/orders/status/allorders`
- No token → show login/signup

**Modals**:
- `LoginPopup` - Triggered by `displayLoginPopup` Redux state
- `SessionExpiredPopUp` - Triggered by `displaySessionExpiredPopup`
- `SubscriptionGracePeriodPopup` - Shown when subscription in grace period (non-payment routes only)

### 1. Merchant Routes (`storepepUsersRoutes.js`)

**File**: `client/src/storepepUsersRoutes.js:1-239` (239 lines, 100+ routes)

All merchant routes are wrapped with HOCs via `WrappedComponents` (`componentWrapper.js`) providing:
- Authentication check
- Account setup completion check
- Subscription tier validation

**Route Categories**:

**Profile & Billing**:
- `/home/myprofile/billingaddress`
- `/home/myprofile/payment` (Stripe/PayPal)
- `/home/myprofile/subscription`
- `/home/myprofile/subscription/change`
- `/home/myprofile/subscription/invoice`
- `/home/myprofile/changepassword`

**Orders & Views**:
- `/home/views/orders/status/:status` - Order grid by status
- `/home/views/orders/action/labelcreated/:batchId` - Batch results
- `/home/views/order/action/manifest/:identifier` - Manifest view
- `/home/views/order/action/pickup/:identifier` - Pickup view
- `/home/views/order/:orderId` - Order summary/details

**Settings**:
- `/home/settings/stores/:platform` - Store connections (Shopify, WooCommerce, Magento, etc.)
- `/home/settings/carriers/:carrier` - Carrier configuration (FedEx, UPS, USPS, DHL, etc.)
- `/home/settings/shipper/originaddress` - Shipper address
- `/home/settings/shipper/packaging` - Packaging settings
- `/home/settings/shipper/shippingzones` - Shipping zones
- `/home/settings/automation` - Automation rules
- `/home/settings/users` - User management

**Products & Tracking**:
- `/home/products` - Product catalog
- `/home/tracking` - Shipment tracking

**Advanced Features**:
- `/home/orderexport` - Order export
- `/home/jobs` - Background jobs
- `/home/widget` - Widget configuration
- `/home/settings/frontend-rates` - Frontend rates API (WooCommerce)

### 2. Admin Routes (`storepepTeamRoutes.js`)

Routes for StorePep internal team managing the platform:
- `/storepepteam/home/accounts` - Account management
- `/storepepteam/home/support` - Support tools
- `/storepepteam/home/analytics` - Platform analytics
- `/storepepteam/home/plans` - Plan management
- `/storepepteam/home/affiliates` - Affiliate program

**Route Protection**: All routes use HOC wrappers from `componentWrapper.js` checking:
- Authentication status
- Account setup completion
- Subscription tier (Lite, Advanced, Pro)
- Feature toggle flags

## Component Architecture

### Component Hierarchy

1. **Pages** (`components/pages/`): Top-level route components
   - Connect to Redux via `connect()`
   - Handle data fetching on mount
   - Compose smaller components

2. **Forms** (`components/form/`): Form components using Redux-Form
   - Declarative validation
   - Field-level and form-level validation
   - Submission handling with async actions

3. **Common** (`components/common/`): Reusable UI components
   - Presentational components (no Redux)
   - Props-driven behavior
   - Material-UI wrappers

4. **Custom Components** (`customComponents/`): Domain-specific reusable components
   - Tables, modals, dialogs
   - Domain logic embedded

### Component Pattern (Container/Presentational)

While not strictly enforced, many components follow this pattern:

```javascript
// Container component (connected to Redux)
class OrdersPageContainer extends Component {
  componentDidMount() {
    this.props.fetchOrders();
  }

  render() {
    return <OrdersPage {...this.props} />;
  }
}

const mapStateToProps = (state) => ({
  orders: state.orders.ordersList,
  loading: state.orders.loading
});

const mapDispatchToProps = { fetchOrders };

export default connect(mapStateToProps, mapDispatchToProps)(OrdersPageContainer);
```

## API Communication

### Axios Configuration

**File**: `client/src/utils/axiosFunctions.js`

Axios is configured with:
- Base URL based on environment (development vs production)
- Default headers (Content-Type, Authorization)
- Request interceptors (add auth tokens)
- Response interceptors (handle 401 unauthorized)

**Example**:
```javascript
axios.defaults.baseURL = getBaseURL(hostname);
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### Unauthorized Error Handling

**File**: `client/src/utils/unauthorizedErrorHandler.js`

When a 401 response is received:
1. Clear auth tokens from localStorage
2. Clear Redux auth state
3. Redirect to login page
4. Display error message to user

## Real-Time Updates (Socket.io)

**File**: `client/src/socket/sockets.js`

The client maintains a persistent WebSocket connection to receive real-time updates:

### Connection Setup
- Connects on app bootstrap
- Authenticates with JWT token
- Reconnects automatically on disconnect

### Event Handlers
- `order:updated` - Order status changes
- `tracking:updated` - Tracking information updates
- `label:generated` - Label generation completion
- `batch:completed` - Batch processing completion

### Redux Integration
Socket events dispatch Redux actions to update the store, triggering UI updates.

## UI Framework (Material-UI)

### Dual Version Setup

StorePep uses both Material-UI v3 and v0 (legacy) simultaneously:

**v3 (Modern)**:
- `@material-ui/core` 3.9.0
- Used for new components
- Modern theming via `createMuiTheme()`

**v0 (Legacy)**:
- `material-ui` 0.20.2
- Legacy components not yet migrated
- Older theming via `getMuiTheme()`

**Theme File**: `client/src/muiTheme.js`

### Common Components Used
- `TextField`, `Select`, `Checkbox`, `Radio`
- `Button`, `IconButton`, `Fab`
- `Table`, `TableRow`, `TableCell`
- `Dialog`, `Modal`, `Drawer`
- `AppBar`, `Toolbar`, `Menu`
- `Snackbar`, `CircularProgress`

### Additional UI Libraries
- **AG-Grid**: High-performance data tables (`ag-grid-react` 28.2.1)
- **React-Dates**: Date range pickers
- **React-DnD**: Drag-and-drop interactions
- **Draft-JS**: Rich text editor for email templates

## Build System (Webpack)

### Development
**Command**: `npm run dev`
- Webpack-dev-server on port 4000
- Hot module replacement
- Source maps for debugging

### Production
**Command**: `npm run build`
- Minification and optimization
- Code splitting for lazy loading
- Bundle uploaded to S3 via `webpack-s3-plugin`
- Asset hashing for cache busting

**Configuration**:
- Development: default webpack config
- Production: `webpack.prod-config.js`

### Babel Transpilation
Supports modern JavaScript (ES2015+) and JSX:
- `@babel/preset-env` - ES6+ features
- `@babel/preset-react` - JSX syntax
- Various plugins for async/await, class properties, object spread

## Access Control (ACL)

**Directory**: `client/src/ACL/`

The frontend implements role-based access control and feature gating through a set of configuration files and HOC wrappers.

### ACL Modules

| File | Purpose |
|------|---------|
| `config.js` | ACL configuration and role definitions |
| `userRoleBasedAccessMapper.js` | Maps user roles to allowed features/pages |
| `urlToPermissionMapper.js` | Maps routes to required permissions |
| `userBasedCarriers.js` | Restricts carrier access by account |
| `userBasedAutomationConditions.js` | Restricts automation rule types by subscription tier |
| `storepepProcessBasedPermissions.js` | Process-specific permissions (e.g., batch operations) |

### Permission Checks

Components are wrapped with HOCs that check:
- User authentication status (`isAuthenticated`)
- User subscription tier (Lite, Advanced, Pro)
- Feature toggle flags (`clientToggles`, `toggles` Redux state)
- Account-level permissions (multi-user accounts)
- URL-based permissions (route access)

**HOC Pattern**:
```javascript
// Component wrapper checking auth + subscription
export default withAuth(
  withSubscription('Pro')(
    withFeatureToggle('advanced_automation')(
      ComponentName
    )
  )
);
```

### Subscription Tiers

Access restrictions by tier:
- **Lite**: Basic label generation, limited carriers
- **Advanced**: Multi-user, automation rules, advanced features
- **Pro**: All features, API access, priority support

### Carrier Access Restrictions

Some carriers require specific subscription tiers or account approval:
- Amazon Shipping - Pro tier
- DHL eCommerce - Account approval
- Regional carriers - Geographic restrictions

## Form Management (Redux-Form)

Redux-Form integrates with Redux for:
- Centralized form state
- Field-level validation
- Async validation (e.g., checking if email exists)
- Submission handling
- Error display

**Example**:
```javascript
<Field
  name="email"
  component={renderTextField}
  label="Email Address"
  validate={[required, email]}
/>
```

## Direct Label Printing (QZ Tray)

**Package**: `qz-tray` 2.2.4

StorePep integrates with QZ Tray for direct thermal printer communication, enabling:
- Direct printing to label printers (Zebra, Dymo, Brother, etc.)
- Browser-to-printer communication without downloads
- Batch printing workflows
- Print queue management

**Use Cases**:
- Touchless label printing
- Bulk label generation → auto-print
- Packing slip and pick list printing

## Error Tracking (Sentry)

**Configuration**: `client/src/utils/sentry/`

- Initialized on app bootstrap
- Captures unhandled exceptions
- Captures Redux action errors
- Includes user context (user ID, account ID)
- Tracks performance (web vitals via `web-vitals` 3.4.0)

## Performance Optimization

1. **Code Splitting**: Webpack dynamic imports for lazy loading
2. **Memoization**: `recompose` library for pure component wrappers
3. **Virtualization**: AG-Grid for rendering large data tables efficiently
4. **Debouncing**: User input debounced for search and filters
5. **Caching**: Axios response caching for frequently accessed data

## Development Workflow

1. **Local Development**:
   ```bash
   cd client
   npm run dev  # Starts webpack-dev-server on localhost:4000
   ```

2. **Linting**:
   - ESLint with Airbnb config
   - Run on pre-commit hook (via Jenkins CI)

3. **Building**:
   ```bash
   npm run build  # Production build
   npm run build-dev  # Development build without upload
   ```

## Dependencies

- [Overview](./overview.md) - High-level system architecture
- [Technology Stack](./technology-stack.md) - Complete dependency listing
- [Data Flow](./data-flow.md) - How data moves through the frontend (to be created)
- [Authentication Flow](./authentication-flow.md) - JWT handling details (to be created)

## Referenced By

- All frontend module pages (orders, products, shipping, etc.)
- [Redux Patterns](../patterns/redux-patterns.md) (to be created)
- [API Conventions](../patterns/api-conventions.md) (to be created)

## Codebase Metrics

- **Total JavaScript Files**: 702 files in `client/src/`
- **Redux Action Types**: ~100 action types defined (`actions/types.js:1-100`)
- **Action Modules**: 30+ action modules organized by domain
- **Reducers**: 26+ reducers combined in root reducer
- **Routes**: 100+ routes across merchant and admin routing
- **LOC**: Routes file alone is 239 lines; codebase is extensive

## Known Issues / Tech Debt

1. **Material-UI Version Mixing**: Dual v0 and v3 providers add bundle size and complexity - migration in progress
2. **React Version**: React 16.10.2 is several major versions behind (v18+ available)
3. **Redux-Form**: Consider migrating to React Hook Form for better performance
4. **Axios Version**: 0.19.0 has known security vulnerabilities - needs update
5. **Class Components**: Most components are class-based - could benefit from hooks refactor
6. **Webpack 4**: Webpack 5+ offers better performance and tree-shaking
7. **Codebase Size**: 702 JS files suggest opportunity for modularization and code splitting optimization

## Related Pages

- [Backend Architecture](./backend-architecture.md)
- [Deployment Pipeline](./deployment-pipeline.md) (to be created)
- [Component Library](../patterns/component-patterns.md) (to be created)
