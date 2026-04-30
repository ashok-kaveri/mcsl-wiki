---
title: Shipping UI (Frontend)
category: module
domain: shipping
sources: [storepep-react]
status: complete
last_updated: 2026-04-30
git_reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020
---

# Shipping UI (Frontend)

## Overview

The shipping UI encompasses label generation, manifests, carrier configuration, rate shopping, and tracking interfaces. Built with React and Redux, it provides workflows for creating shipping labels, managing carrier accounts, generating manifests, and tracking shipments with real-time updates.

**Main Components**: Label generation, manifest management, tracking views, carrier configuration
**Redux State**: Multiple reducers for labels, tracking, manifests, carrier services, and package configuration

## Key Components

### Label Generation

**Components**:
- Order summary panel with rate selection (`client/src/components/form/views/summary/order-summary/`)
- Bulk label generation interface
- Package configuration modals
- Rate shopping comparison table
- Label preview and download

**User Flows**:

1. **Single Label Generation**:
   - User opens order summary
   - System fetches available rates from configured carriers
   - User selects carrier/service from rate table
   - User confirms package dimensions/weight
   - System generates label via API
   - Label preview displayed with download/print options

2. **Bulk Label Generation**:
   - User selects multiple orders from grid
   - User triggers bulk action "Generate Labels"
   - System processes orders in batch
   - Batch results view shows success/failure per order
   - Successful labels available for bulk download/print

3. **Rate Shopping**:
   - System queries all active carriers in parallel
   - Rates displayed in comparison table with:
     - Carrier name and service level
     - Delivery time estimate
     - Rate (with currency)
     - Special services available
   - User can sort by price, delivery time, or carrier
   - Selected rate highlighted

### Manifest & Pickup Management

**Components**: `client/src/components/form/views/common/manifest*.js`

**Files**:
- `manifest.js` - Main manifest interface
- `manifestOrderTable.js` - Orders in manifest view
- `manifestTable.js` - List of manifests
- `manifestLinkDialog.js` - Manifest download dialog

**Routes**:
- `/home/views/order/action/manifest/:identifier` - Single manifest view
- `/home/views/order/action/pickup/:identifier` - Pickup view

**Manifest Workflow**:
1. User generates labels for multiple orders
2. User navigates to manifest interface
3. System groups eligible orders by carrier
4. User creates manifest (end-of-day form)
5. System generates manifest document
6. Manifest available for download (PDF/CSV)
7. Optional: Schedule carrier pickup

**Supported Carriers**:
- USPS (SCAN form)
- FedEx (end-of-day close)
- UPS (end-of-day manifest)
- Canada Post
- DHL Express

### Tracking Interface

**Component**: `client/src/components/pages/tracking/tracking.js`
**Container**: `client/src/components/form/tracking/trackingContainer.js`

**Route**: `/home/tracking`

**Redux State**: `trackingOrdersCount` reducer

**Features**:
- Track multiple shipments simultaneously
- Real-time tracking updates via Socket.io
- Tracking history timeline
- Delivery status indicators
- Exception alerts (delayed, failed delivery)

**Tracking Statuses**:
- In Transit
- Out for Delivery
- Delivered
- Exception (requires attention)
- Return to Sender

**Data Flow**:
1. Orders with tracking numbers loaded from backend
2. System polls carriers for tracking updates (cron job)
3. Socket.io pushes real-time updates to connected clients
4. Redux state updated with new tracking events
5. UI reflects status changes without page refresh

### Carrier Configuration UI

**Main Component**: `client/src/components/form/settings/carriers/carriers.js:1-100`

**Route**: `/home/settings/carriers`

**Features**:
- Carrier selection and activation
- Credential management (API keys, account numbers)
- Test mode vs Production mode toggle
- Carrier-specific settings forms
- OAuth registration flows
- EasyPost integration management

**Carrier Categories** (displayed as collapsible sections):

1. **Featured Carriers**:
   - FedEx, UPS, USPS, DHL, Canada Post
   - Large carrier cards with quick activation

2. **Regional Carriers**:
   - Australia Post, Royal Mail, PostNord, etc.
   - Organized by geography

3. **Rates-Only Carriers**:
   - Carriers supporting rate fetching without label generation
   - Read-only integration

4. **EasyPost Carriers**:
   - Carriers available via EasyPost aggregator
   - Single EasyPost account unlocks multiple carriers

### Carrier-Specific Configuration Forms

**Location**: `client/src/components/form/settings/carriers/`

**70+ Carrier Forms** including:
- `fedEx.js` - FedEx SOAP configuration
- `fedexRest.js` - FedEx REST API configuration
- `ups.js` - UPS manual configuration
- `upsOauth.js` - UPS OAuth registration
- `usps.js` - USPS manual configuration
- `uspsOAuth.js` - USPS OAuth registration
- `stampsUsps.js` - Stamps.com USPS configuration
- `dhlexpress.js` - DHL Express configuration
- `canadaPost.js` - Canada Post configuration
- `australiaPost.js` - Australia Post configuration
- `royalMail.js` - Royal Mail configuration
- `easyPost.js` - EasyPost aggregator configuration
- ... 60+ more carrier configurations

**Common Form Fields**:
- Account number / API key
- Meter number (USPS, FedEx)
- Username / Password
- Test mode toggle
- Default service selection
- Special services enablement
- Packaging type preferences

**OAuth Carriers** (multi-step registration):
- UPS OAuth (`upsOauth.js`, `upsOauthRegistration.js`)
- USPS REST (`uspsOAuth.js`, `uspsRest.js`, `uspsRestV2.js`)
- Amazon Shipping (`amazonShipping.js`)
- Canada Post Connect (`canadaPostConnect.js`)
- FedEx REST (`fedexRest.js`, `fedexRestRegistration.js`, `fedexRestVerification.js`)

**OAuth Flow** (example: UPS):
1. User clicks "Connect UPS Account"
2. System generates OAuth state token
3. User redirected to UPS login
4. UPS redirects back with auth code
5. System exchanges code for access token
6. Token stored encrypted in database
7. Carrier marked as active

**FedEx REST Registration** (multi-step):
1. Address validation
2. Validation method selection (PIN/Invoice/Support)
3. PIN generation (SMS/Email) or invoice entry
4. Verification
5. Child credentials generated
6. Account active

### Rate Shopping UI

**Integration Points**:
- Order summary panel
- Bulk action modals
- Product-level shipping calculator

**Rate Display**:
```javascript
{
  carrierName: "FedEx",
  serviceName: "FedEx Ground",
  rate: 12.50,
  currency: "USD",
  deliveryDays: 3,
  deliveryDate: "2026-05-03",
  specialServices: ["Signature Required", "Insurance"],
  available: true,
  errorMessage: null
}
```

**Rate Comparison Table** (Material-UI Table):
- Sortable columns (rate, delivery time, carrier)
- Filter by carrier type
- Highlight cheapest / fastest options
- Show/hide special services
- Currency conversion (if multi-currency)

**Rate Caching**:
- Rates cached for 15 minutes (configurable)
- Cache invalidated on package dimension change
- Parallel rate fetching for performance

## Redux State Management

### Label State

**Reducer**: `label` (`client/src/reducers/settingsData.js:38-45`)

State shape:
```javascript
{
  label: {
    // Label generation settings
    defaultLabelFormat: "PDF",
    defaultLabelSize: "4x6",
    printAfterGeneration: false,
    autoSelectCheapest: false,
  }
}
```

### Tracking State

**Reducer**: `tracking` (`client/src/reducers/settingsData.js:78-85`)

State shape:
```javascript
{
  tracking: {
    // Tracking preferences
    enableEmailNotifications: true,
    enableSMSNotifications: false,
    trackingPageUrl: "https://example.com/track",
  }
}
```

**Tracking Counts Reducer**: `trackingOrdersCount` (`client/src/reducers/tracking.js`)

State shape:
```javascript
{
  inTransit: 42,
  delivered: 105,
  exception: 3,
  total: 150
}
```

### Carrier Services State

**Reducer**: `carrierServices` (`client/src/reducers/carrierServices.js`)

State shape:
```javascript
{
  services: [
    {
      carrierType: "fedex",
      carrierID: "abc123",
      services: [
        { code: "FEDEX_GROUND", name: "FedEx Ground", available: true },
        { code: "FEDEX_2_DAY", name: "FedEx 2Day", available: true },
        // ...
      ]
    },
    // ... other carriers
  ]
}
```

**Carrier Service Names Reducer**: `carrierServiceNames`

Maps carrier codes to display names for UI rendering.

### Package Configuration State

**Reducers**:
- `storedPackages` - Forward shipment packages
- `returnPackages` - Return label packages

State shape:
```javascript
{
  storedPackages: {
    [orderId]: [
      {
        packageId: "pkg1",
        length: 10,
        width: 8,
        height: 6,
        weight: 5,
        dimensionsUnit: "in",
        weightUnit: "lbs",
        generated: false,
        shipmentCreated: false,
      },
      // ... more packages
    ]
  }
}
```

**Package Lifecycle States**:
1. **Created** - Package configuration saved
2. **Generated** - Rates fetched, ready for label generation
3. **Shipment Created** - Label generated, tracking assigned
4. **Reset** - Package cleared (on cancel/edit)

## Redux Actions

### Settings Actions

**File**: `client/src/actions/settingsActions.js:1-433` (433 lines)

**Carrier Management**:
- `addCarrier(data)` - Add new carrier account
- `updateCarrierSettings(data)` - Update carrier configuration
- `archiveCarrierAction(carrierId)` - Remove carrier
- `fetchInfoFromCarrier(data)` - Fetch carrier account details
- `addFedexCarrier(data)` - FedEx-specific registration
- `getFedexEULA()` - Fetch FedEx EULA document
- `getCanadaPostAccountCreationToken(carrierId)` - Canada Post OAuth token

**EasyPost Integration**:
- When EasyPost carrier added/updated, automatically fetch available carriers
- Store EasyPost carrier list in Redux state
- Enable/disable EasyPost carriers based on production key

**Ship-From Address**:
- `shipFromAddressDetails(data)` - Update origin address

**Account Setup**:
- `accountSetupCompleted(data)` - Track account setup status

### Label Actions

**Directory**: `client/src/actions/labels/`

Label generation actions (exact actions not read, but inferred from usage):
- Generate single label
- Generate bulk labels
- Fetch rates for order
- Preview label
- Download label
- Print label via QZ Tray
- Void label (cancel shipment)

### Manifest Actions

**Directory**: `client/src/actions/manifest/`

Manifest management actions:
- Create manifest
- Fetch manifests
- Download manifest document
- Schedule pickup

### Package Actions

**File**: `client/src/actions/ordersActions.js:9-74`

- `storedPackagesStore(data)` - Add package configuration
- `returnPackagesStore(data)` - Add return package
- `updateStoredPackagesStore(data)` - Update package state
  - `generatePackage` → UPDATE_STORED_PACKAGES_GENERATED
  - `createShipment` → UPDATE_STORED_PACKAGES_CREATESHIPMENT
  - `resetShipment` → DELETE_STOREDPACKAGE
  - `processReturnLabel` → PROCESS_RETURN_LABEL
  - `returnPackageGenerated` → UPDATE_RETURN_PACKAGES_GENERATED

## UI Features

### Multi-Carrier Support

**70+ Carrier Configuration Forms**:

System supports configuration for 70+ carriers via dedicated forms:
- Each carrier has unique credential requirements
- Forms dynamically rendered based on carrier type
- Redux Form handles validation per carrier
- Conditional fields based on service type (express, ground, international)

**Carrier Categories UI**:
1. Featured carriers displayed prominently (large cards)
2. Other carriers in collapsible sections
3. Rates-only carriers in separate section
4. EasyPost carriers dynamically loaded

### Test Mode

**Toggle**: Production vs Test mode for development/testing

**Behavior**:
- Test mode uses sandbox credentials
- Test mode displays warning banner
- Test labels marked as "TEST" in UI
- No actual carrier charges in test mode

**Per-Carrier Test Toggle**:
- Each carrier can be individually toggled
- Mixed mode: Some carriers test, some production
- Useful for gradual rollout

### OAuth Registration Flows

**Supported OAuth Carriers**:
- UPS Ready OAuth
- UPS DAP OAuth
- USPS REST
- Amazon Shipping
- PostNord
- Canada Post Connect
- FedEx REST (proprietary OAuth-like flow)

**Registration UI Components**:
- `upsOauthRegistration.js` - UPS registration wizard
- `fedexRestRegistration.js` - FedEx registration wizard
- `fedexRestVerification.js` - FedEx verification step
- Multi-step wizards with progress indicators
- `waiting.js` - Polling state while awaiting OAuth callback

**OAuth State Management**:
- State token generated (CSRF protection)
- Polling loop checks registration status
- Success/failure feedback in UI
- Automatic redirect on completion

### Default Package Dimensions

**Component**: `client/src/components/form/settings/carriers/defaultPackageDimensions.js`

**Purpose**: Set carrier-specific default package dimensions to pre-fill label generation forms.

**Fields**:
- Default length, width, height
- Default weight
- Dimension/weight units
- Per-carrier defaults (FedEx may differ from UPS)

### Carrier Service Special Services

**UI**: Checkbox selections for add-on services

**Common Special Services**:
- Signature required (adult signature, indirect signature)
- Insurance (declared value)
- Saturday delivery
- Hold at location
- Dry ice
- Alcohol shipment
- Residential surcharge waiver
- COD (cash on delivery)

**Service Availability**:
- Special services filtered by carrier capability
- Some services only available for certain service levels
- Dynamic pricing displayed when service selected

### Shipping Zones

**Components**:
- `shippingZones.js` - Zone management interface
- `addOrEditShippingZone.js` - Zone editor
- `shippingZoneManager.js` - Zone business logic
- `shippingZoneValidator.js` - Zone validation rules

**Route**: `/home/settings/shipper/shippingzones`

**Purpose**: Define geographic zones for conditional carrier/service selection

**Features**:
- Zone by country, state/province, zip/postal code
- Zone-based carrier restrictions
- Zone-based service level defaults
- Zone-based rate markups

## Real-Time Updates

### Socket.io Events

**Label Generation**:
```javascript
socket.on('label:generated', ({ orderId, labelUrl, trackingNumber }) => {
  dispatch(updateOrderLabel(orderId, labelUrl, trackingNumber));
  dispatch(refreshOrderCounts());
});
```

**Tracking Updates**:
```javascript
socket.on('tracking:updated', ({ orderId, trackingEvent }) => {
  dispatch(addTrackingEvent(orderId, trackingEvent));
  // Show notification if status changed
  if (trackingEvent.status === 'delivered') {
    showNotification('Package delivered!');
  }
});
```

**Batch Processing**:
```javascript
socket.on('batch:completed', ({ batchId, results }) => {
  dispatch(updateBatchResults(batchId, results));
  // Navigate to batch results page
  history.push(`/home/views/orders/action/labelcreated/${batchId}`);
});
```

## Performance Optimizations

### Rate Fetching

**Parallel Requests**:
- All active carriers queried simultaneously
- Promise.all() for concurrent rate fetching
- Timeout per carrier (5 seconds)
- Failed carriers don't block others

**Caching**:
- Rate responses cached in Redux (15 min TTL)
- Cache key: order dimensions + weight + destination
- Cache invalidated on package change

### Carrier List Rendering

**Virtualization**:
- 70+ carrier forms not all rendered at once
- Lazy loading: Render only expanded sections
- Carrier card components use React.PureComponent

**Dynamic Imports**:
- Carrier-specific components code-split
- Loaded on-demand when user expands section
- Reduces initial bundle size

### Label Preview

**PDF Rendering**:
- Label PDFs rendered in iframe
- Download option avoids rendering overhead
- Print via QZ Tray bypasses browser print dialog

## Integration with Backend

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/settings/carrier/add` | POST | Add carrier account |
| `/api/settings/carrier/update` | POST | Update carrier settings |
| `/api/settings/carrier/fetch-info` | POST | Fetch carrier details |
| `/api/carriers/archive/:carrierId` | POST | Remove carrier |
| `/api/orders/:orderId/rates` | GET | Fetch shipping rates |
| `/api/orders/:orderId/label` | POST | Generate label |
| `/api/orders/bulk-label` | POST | Generate bulk labels |
| `/api/manifest/create` | POST | Create manifest |
| `/api/tracking/:trackingNumber` | GET | Fetch tracking details |

See [Label Generation](../shipping/label-generation.md) and [Carrier Configuration](../shipping/carrier-configuration.md) for backend implementation details.

## Dependencies

**Frontend**:
- [Frontend Architecture](../../architecture/frontend-architecture.md) - React, Redux setup
- [Redux Patterns](../../patterns/redux-patterns.md) - Action/reducer conventions
- [Orders UI](orders-ui.md) - Order selection for label generation

**Backend**:
- [Label Generation](../shipping/label-generation.md) - Backend label creation
- [Carrier Configuration](../shipping/carrier-configuration.md) - Backend carrier management
- [Shipment Tracking](../shipping/shipment-tracking.md) - Tracking system
- [Carrier OAuth Flow](../../patterns/carrier-oauth-flow.md) - OAuth registration pattern
- [FedEx REST Registration](../../patterns/carrier-fedex-rest-registration.md) - FedEx registration pattern

## Referenced By

- [Packaging UI](packaging-ui.md) - Package configuration for shipping
- [Settings UI](settings-ui.md) - Settings interface includes carrier configuration

## Known Issues / Tech Debt

1. **70+ Carrier Forms**: High maintenance burden, potential for form inconsistency
2. **Carrier-Specific Logic**: Scattered across components, could be centralized
3. **Rate Fetching Performance**: Sequential fallback on Promise.all failure can be slow
4. **OAuth Flow Complexity**: Multi-step wizards with polling can confuse users
5. **Test Mode Visibility**: Test mode banner could be more prominent
6. **EasyPost Dependency**: EasyPost carrier list not cached, fetched on every load
7. **Manifest UI**: Limited to certain carriers, not extensible
8. **Tracking Polling**: Inefficient for high-volume accounts, should use webhooks

## Test Coverage

See [Features](../../features.md) for test coverage of shipping workflows.

**Automated E2E Tests** (Playwright):
- Label generation (single and bulk)
- Rate shopping and carrier selection
- Manifest creation
- Tracking updates
- Carrier configuration (selected carriers)

**Coverage**: Medium (70-80%) - Core workflows tested, carrier-specific forms mostly manual verification.
