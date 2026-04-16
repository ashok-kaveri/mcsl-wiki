---
title: Carrier System Overview
category: module
domain: shipping
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Carrier System Overview

## Overview

The carrier system is the foundation of StorePep's multi-carrier shipping capability. It provides a unified abstraction layer over 43 different shipping carriers, enabling merchants to fetch rates, generate labels, track shipments, and schedule pickups through a single consistent interface regardless of the underlying carrier API.

**Core Value**: Merchants configure carriers once, then StorePep handles all the complexity of different API protocols, authentication methods, request formats, and response parsing.

## Architecture

### Adaptor Pattern

**Location**: `server/src/shared/storepepAdaptors/shipmentAdaptor.js:1-180`

The Shipment Adaptor implements the **Factory Pattern** to provide carrier-specific implementations through a unified interface:

```javascript
class ShipmentAdaptor {
  getShipmentCreatorBasedOnCarrier(carrierType) {
    switch (carrierType) {
      case constants.FEDEX_CARRIER_CODE:       // 'C2'
        return new FedexShipmentHelper();
      case constants.UPS_CARRIER_CODE:         // 'C3'
        return new UpsShipmentHelper();
      case constants.DHL_CARRIER_CODE:         // 'C1'
        return new DHLShipmentCreator();
      case constants.EASYPOST_CARRIER_CODE:    // 'C22'
        return new EasyPostShipmentHelper();
      // ... 40+ more carriers
    }
  }
}
```

**Usage**:
```javascript
const adaptor = new ShipmentAdaptor();
const carrierHelper = adaptor.getShipmentCreatorBasedOnCarrier(carrierType);

// All carriers implement same interface:
const rates = await carrierHelper.getRates(order, packages, carrier);
const label = await carrierHelper.createShipment(order, packages, carrier);
const tracking = await carrierHelper.getTracking(trackingNumber, carrier);
```

### Unified Carrier Interface

Every carrier implementation provides these methods:

| Method | Purpose | Returns |
|--------|---------|---------|
| `getRates(order, packages, carrier)` | Fetch shipping rates for all available services | Rate object with service→price mapping |
| `createShipment(order, packages, carrier)` | Generate shipping label | Label URL, tracking number, documents |
| `cancelShipment(shipmentId, carrier)` | Void label, refund postage | Success/failure status |
| `getTracking(trackingNumber, carrier)` | Get current tracking status | Tracking events, delivery status |
| `createPickup(orders, carrier)` | Schedule carrier pickup | Pickup confirmation number |
| `createManifest(orders, carrier)` | Generate end-of-day manifest | Manifest document URL |
| `validateAddress(address, carrier)` | Validate/correct shipping address | Validated address, suggestions |

**Not all carriers support all methods** (e.g., some don't support manifest, some don't offer address validation).

## Carrier Categories

### 1. Direct Integrations (Custom API Clients)

Carriers with custom-built API integrations:

**Major Carriers** (high volume, complex APIs):
- **FedEx**: SOAP API, REST API (dual implementation)
- **UPS**: XML API, REST OAuth API (dual implementation)
- **DHL Express**: SOAP API
- **USPS**: Multiple variants (Stamps.com, direct USPS, USPS REST)
- **Canada Post**: SOAP API

**Regional/Specialized**:
- **Australia**: Australia Post, TNT Australia, Couriers Please, Sendle
- **UK/Europe**: Royal Mail, Parcel Force, PostNord, PostNL, TNT
- **Asia**: Aramex, Hong Kong Post, Delhivery, Blue Dart, Xpressbees, Daakit
- **Other**: Purolator, Canpar, XPO Logistics, MyFastway, New Zealand Post

**Total**: 38 direct integrations with custom API clients

### 2. EasyPost Aggregation

**EasyPost** (code: `C22`) provides multi-carrier access through a single API:

**Location**: `server/src/shared/API/carriers/easyPost/easyPostShipmentHelper.js` (27KB)

**Advantages**:
- Unified API for 100+ carriers (USPS, FedEx, UPS, DHL, regional carriers)
- Faster onboarding for new carriers
- Standardized error handling
- Address validation included
- Rate normalization

**When Used**:
- Merchants want carriers not directly integrated
- Merchants prioritize setup speed over cost
- Testing new carriers before direct integration

**EasyPost Carrier Mapping**:
- StorePep carrier configuration can map to EasyPost carrier names
- Field: `order.easypostCarrier`, `order.easypostCarrierType`

### 3. Dual API Implementations

Some carriers have **two separate integrations** (legacy + modern):

**FedEx**:
- `FEDEX_CARRIER_CODE` ('C2') - SOAP/XML API (legacy)
- `FEDEX_REST_CARRIER_CODE` ('C39') - REST API (modern, OAuth)

**UPS**:
- `UPS_CARRIER_CODE` ('C3') - XML API (legacy)
- `UPS_OAUTH_CARRIER_CODE` ('C38') - REST OAuth API (modern)

**USPS**:
- `STAMPS_USPS_CARRIER_CODE` ('C4') - Stamps.com integration
- `USPS_CARRIER_CODE` ('C5') - Direct USPS API
- `USPS_REST_CARRIER_CODE` ('C45') - USPS REST API
- `USPS_REST_V2_CARRIER_CODE` ('C46') - USPS REST v2
- `USPS_OAUTH_CARRIER_CODE` ('C48') - USPS OAuth

**Why Dual**:
- Migration period (phasing out legacy, adopting modern)
- Different feature sets (old API has features new one lacks)
- Merchant preference (some prefer Stamps.com account integration)

## Data Flow

### Rate Shopping Flow

```
1. Order transitions to PROCESSING
   ↓
2. addRateInfoToOrder() called
   ↓
3. Fetch enabled carriers from DB (accountUUID)
   ↓
4. For each carrier:
   - Get adaptor: new ShipmentAdaptor().getShipmentCreatorBasedOnCarrier()
   - Call getRates()
   - Carrier helper builds API request
   - Calls carrier API (SOAP/REST/XML)
   - Parses response
   - Normalizes rate structure
   ↓
5. Promise.all() waits for all carriers
   ↓
6. Process results:
   - Map service codes to friendly names
   - Calculate transit times
   - Apply currency conversion if needed
   - Filter unavailable services
   ↓
7. Store in order.availableCarrierAndService[]
   ↓
8. Apply service selection (cheapest, fastest)
   ↓
9. Socket notification to frontend with rates
```

**Parallel Execution**: All carrier API calls run concurrently via `Promise.all()` for performance.

### Label Generation Flow

```
1. User clicks "Generate Label" or auto-gen enabled
   ↓
2. labelAndFullfillOrder() called
   ↓
3. Validate order ready (carrier selected, address valid, packages configured)
   ↓
4. Get carrier helper via adaptor
   ↓
5. Build shipment request:
   - Order data enhancer adds required fields
   - Package data with dimensions/weight
   - Ship-from/ship-to addresses
   - Special services (signature, insurance, etc.)
   - Customs data (international)
   ↓
6. Call carrierHelper.createShipment()
   ↓
7. Carrier-specific API call:
   - FedEx: SOAP ProcessShipment request
   - UPS: XML ShipmentRequest
   - DHL: REST createShipment call
   - EasyPost: POST /shipments with buy
   ↓
8. Process response:
   - Extract label URL (PDF/PNG/ZPL)
   - Extract tracking number
   - Extract commercial invoice URL (international)
   - Parse any warnings/errors
   ↓
9. Store results:
   - order.trackingId = tracking number
   - order.currentLabelSummaryUUID = reference to label doc
   - order.storePepStatus = LABEL_CREATED
   ↓
10. Generate additional documents:
    - Packing slip (Puppeteer PDF)
    - Commercial invoice (if international)
    - Return label (if requested)
    ↓
11. Sync to store (optional):
    - Update order status on e-commerce platform
    - Add tracking number to order
    ↓
12. Socket notification with label URL
```

## API Protocol Support

StorePep integrates with carriers using multiple API protocols:

| Protocol | Carriers Using | Example |
|----------|----------------|---------|
| **SOAP/XML** | FedEx (legacy), DHL, Canada Post, Purolator | Complex enterprise APIs |
| **REST/JSON** | FedEx (modern), UPS OAuth, Amazon Shipping, many regional | Modern cloud-native APIs |
| **XML over HTTP** | UPS (legacy), USPS | Legacy HTTP POST with XML body |
| **Third-party Gateway** | EasyPost, Eshipz | Aggregator APIs |

**Authentication Methods**:
- **API Key/Secret**: Most modern REST APIs
- **Username/Password + Account Number**: Legacy SOAP APIs (FedEx, UPS)
- **OAuth 2.0**: UPS REST, FedEx REST, USPS REST
- **Developer Key + Production Key**: EasyPost, Stamps.com

## Wrapper Functions

**Location**: `server/src/shared/storepepWrapperFunctions.js:1-80`

### getCarrierAdaptor

```javascript
const getCarrierAdaptor = (carrierType) =>
  new ShipmentAdapter().getShipmentCreatorBasedOnCarrier(carrierType);
```

**Purpose**: Convenience function to get carrier helper

**Usage**:
```javascript
const fedexHelper = getCarrierAdaptor(constants.FEDEX_CARRIER_CODE);
const rates = await fedexHelper.getRates(order, packages, carrier);
```

### getRatesBasedOnCarrierType

**Location**: Referenced in `addRateInfoToOrder.js:32`

**Purpose**: Route to appropriate carrier's `getRates()` method

**Flow**:
1. Determine carrier type from `carrierTypeSelected`
2. Get adaptor for that carrier
3. Call `getRates()` with order, packages, carrier config
4. Return normalized rate structure

## Service Code Mapping

**Location**: `server/src/shared/serviceCodes.js` (1500+ lines)

Maps carrier-specific service codes to human-readable names:

**DHL Service Codes**:
```javascript
{
  'D': 'DHL EXPRESS WORLDWIDE',
  'E': 'DHL EXPRESS 9:00',
  'N': 'DHL DOMESTIC EXPRESS',
  'P': 'DHL EXPRESS WORLDWIDE',
  // ... 30+ DHL codes
}
```

**FedEx Service Codes**:
```javascript
{
  'PRIORITY_OVERNIGHT': 'Fedex Priority Overnight',
  'FEDEX_2_DAY': 'Fedex 2 Day',
  'FEDEX_GROUND': 'Fedex Ground',
  'INTERNATIONAL_PRIORITY': 'FedEx International Priority®',
  'SMART_POST': 'Fedex Ground® Economy',
  // ... 50+ FedEx services
}
```

**UPS Service Codes**:
```javascript
{
  '01': 'UPS Next Day Air',
  '02': 'UPS Second Day Air',
  '03': 'UPS Ground',
  '07': 'UPS Worldwide Express',
  '11': 'UPS Standard',
  // ... 30+ UPS codes
}
```

**Purpose**:
- Display friendly names to users
- Consistent naming across carriers
- Localization support (future)

## Carrier Constants

**Location**: `server/src/storePepConstants.js:39-89`

All carrier type codes:

```javascript
const constants = {
  DHL_CARRIER_CODE: 'C1',
  FEDEX_CARRIER_CODE: 'C2',
  UPS_CARRIER_CODE: 'C3',
  STAMPS_USPS_CARRIER_CODE: 'C4',
  USPS_CARRIER_CODE: 'C5',
  CANADA_POST_CARRIER_CODE: 'C6',
  // ... 43 total carrier codes
  EASYPOST_CARRIER_CODE: 'C22',
  UPS_OAUTH_CARRIER_CODE: 'C38',
  FEDEX_REST_CARRIER_CODE: 'C39',
  // ...
};
```

**Naming Convention**: `C{number}` (C1-C50)

**Special Codes**:
- `MULTI_CARRIER_ISSUER`: For multi-carrier scenarios
- `UPS_DAP_CARRIER_CODE_FOR_ANALYTICS`: Analytics-specific variant
- `CANADA_POST_CARRIER_MANUAL_CONFIG_CODE`: Manual configuration variant

## Error Handling

### Unified Error Response Format

All carrier helpers return standardized error structure:

```javascript
{
  status: constants.FAILURE,
  error: {
    carrierErrorMessage: "Readable error message",
    carrierErrorCode: "CARRIER_SPECIFIC_CODE",
    field: "fieldName", // Which field caused error
    requestObject: {},  // What was sent to carrier
    apiResponse: {}     // Raw carrier response
  }
}
```

### Common Error Categories

1. **Authentication Errors**: Invalid credentials, expired API key
2. **Address Errors**: Undeliverable address, invalid ZIP code
3. **Package Errors**: Weight exceeds limits, invalid dimensions
4. **Service Errors**: Service not available for origin/destination
5. **Account Errors**: Carrier account not configured, insufficient funds
6. **Rate Errors**: No rates available for this shipment

### Error Event Publishing

**Events**:
- `RateFetchUnsuccessfulForCarrier` - Rate fetch failed
- `LabelGenerationFailed` - Label creation failed
- `CarrierAPITimeout` - Carrier API didn't respond

**Location**: `server/src/shared/ratesApi/events.js`

## Performance Optimizations

### 1. Parallel Rate Fetching

```javascript
const promises = carriers.map(carrier =>
  getRates(order, packages, carrier)
);
const results = await Promise.all(promises);
```

**Benefit**: Fetch from 5 carriers in ~2 seconds instead of ~10 seconds sequentially

### 2. Rate Caching

Rates cached for 15 minutes to avoid redundant API calls:
- Key: Hash of (origin, destination, weight, dimensions, services)
- TTL: 15 minutes
- Storage: Redis

### 3. Request Throttling

Carrier API rate limits respected:
- FedEx: 1000 requests/hour per account
- UPS: 250 requests/hour (developer key)
- USPS: 5000 requests/hour

**Implementation**: Token bucket algorithm per carrier

## Testing & Validation

### Carrier Credential Validation

**Method**: `validateCarrierCredentails(data, carrier)`

**Location**: Each carrier helper implements this

**Purpose**: Test credentials without generating a label

**Flow**:
1. Call lightweight carrier API endpoint (e.g., address validation)
2. Parse response for authentication success/failure
3. Determine if using production or test credentials
4. Return: `{ success: boolean, productionKey: boolean, message: string }`

**Usage**:
- When merchant adds carrier configuration
- Periodic health checks on carrier accounts

### Sample Label Generation

**Field**: `carrier.isSampleLabel`

**Purpose**: Generate test labels without actual postage charge

**Carriers supporting**: USPS (Stamps.com), some via EasyPost test mode

## Dependencies

- [Carrier Configuration](./carrier-configuration.md) - Carrier model and account setup
- [Carrier Integration](./carrier-integration.md) - Engineering reference: file conventions, HTTP retry, error dicts, checklist for adding a carrier
- [Rate Shopping](./rate-shopping.md) - Rate fetching and selection logic
- [Label Generation](./label-generation.md) - Detailed label creation flow
- [Carrier Integrations](./carrier-integrations.md) - List of all 43 carriers
- [Order Lifecycle](../orders/order-lifecycle.md) - Order processing flow
- [Backend Architecture](../../architecture/backend-architecture.md) - Service layer pattern

## Referenced By

- Rate shopping uses adaptor to fetch rates from all carriers
- Label generation uses adaptor to create shipments
- Order processing depends on carrier availability
- Manifest generation uses adaptor per carrier

## Configuration

**Environment Variables**:
- Carrier API URLs (test vs production)
- API timeout settings
- Retry policies

**Account Settings**:
- Enabled carriers per account
- Carrier priority/preference
- Default carrier for automation

**Feature Toggles**:
- New carrier rollout (enable for specific accounts first)
- Legacy vs modern API selection
- EasyPost fallback

## Common Patterns

### Get Rates from All Enabled Carriers

```javascript
const carriers = await findCarriersWithLean({
  accountUUID,
  isActive: true
});

const ratesPromises = carriers.map(carrier => {
  const helper = getCarrierAdaptor(carrier.carrierType);
  return helper.getRates(order, packages, carrier);
});

const ratesResults = await Promise.all(ratesPromises);
```

### Generate Label for Selected Carrier

```javascript
const carrierHelper = getCarrierAdaptor(order.carrierTypeSelected);

const shipmentData = {
  orderDataForTheOrderToShip: order,
  storedPackageDetailsForTheOrderToShip: packages,
  preferredCarrier: carrier
};

const result = await carrierHelper.createShipment(shipmentData);

if (result.status === constants.SUCCESS) {
  order.trackingId = result.trackingNumber;
  order.labelUrl = result.labelUrl;
}
```

## Known Issues / Tech Debt

1. **Inconsistent error structures**: Some carrier helpers return different error formats
2. **Missing cancellation support**: Not all carriers implement `cancelShipment()`
3. **No retry mechanism**: Failed API calls don't auto-retry with exponential backoff
4. **Hardcoded timeouts**: API timeouts not configurable per carrier
5. **Limited tracking**: Some carriers don't implement `getTracking()`
6. **OAuth token refresh**: Manual process for carriers using OAuth

## Related Pages

- [Carrier Configuration](./carrier-configuration.md)
- [Rate Shopping](./rate-shopping.md)
- [Label Generation](./label-generation.md)
- [Carrier Integrations](./carrier-integrations.md)
- [Order Bulk Actions](../orders/order-bulk-actions.md)
