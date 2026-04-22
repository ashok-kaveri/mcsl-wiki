---
title: Carriers and Adapters
category: architecture
sources: [storepep-react]
status: complete
last_updated: 2026-04-23
git_reference: e5bf9867ce1e02cdbf9b2da90f081f15fa0be345
---

# Carriers and Adapters

## Overview

StorePep integrates with **45+ shipping carriers** through a unified adapter pattern. Each carrier integration consists of:

- **Carrier Code**: Unique constant (C1-C54) defined in `storePepConstants.js:41-90`
- **Carrier Name**: Human-readable identifier used throughout the system
- **Adapter Class**: ShipmentHelper implementation in `server/src/shared/API/carriers/<carrier>/`
- **API Protocol**: SOAP/XML, REST/JSON, or custom XML format
- **API Endpoints**: Sandbox and production URLs for carrier APIs

The **ShipmentAdaptor factory** (`server/src/shared/storepepAdaptors/shipmentAdaptor.js:1-191`) routes shipment requests to the appropriate carrier-specific adapter based on the carrier code.

**Total Carriers**: 45+ integrations (C1-C54 range, some codes reserved for variants)

---

## Complete Carrier Catalog

### Major US & International Carriers

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C1 | DHL_EXPRESS | DHL Express | DHLShipmentCreator | SOAP/XML | API via config | API via config |
| C2 | FEDEX | FedEx (SOAP) | FedexShipmentHelper | SOAP | https://wsbeta.fedex.com | https://ws.fedex.com |
| C39 | FEDEX_REST | FedEx (REST) | FedExRestShipmentHelper | REST/JSON | API via config | API via config |
| C37 | FEDEX_SAME_DAY_CITY | FedEx Same Day City | SameDayCityShipmentHelper | REST/JSON | API via config | API via config |
| C3 | UPS | UPS (SOAP) | UpsShipmentHelper | SOAP | https://wwwcie.ups.com | https://onlinetools.ups.com |
| C38 | UPS_OAUTH | UPS (OAuth/REST) | UpsRestApiShipmentHelper | REST/OAuth | API via config | API via config |
| C4 | STAMPS_USPS | USPS (Stamps.com) | StampsUspsShipmentHelper | SOAP | API via config | API via config |
| C5 | USPS | USPS (Legacy) | USPSShipmentHelper | XML | API via config | API via config |
| C45 | USPS_REST | USPS (REST) | USPSRestShipmentHelper | REST/JSON | API via config | API via config |
| C46 | USPS_REST_V2 | USPS REST V2 | (Via C45) | REST/JSON | API via config | API via config |
| C48 | USPS_OAUTH | USPS (OAuth) | (Via C45) | REST/OAuth | API via config | API via config |

### Australia & New Zealand

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C8 | AUSTRALIA_POST | eParcel (Australia Post) | AustraliaPostShipmentHelper | REST/JSON | API via config | API via config |
| C33 | AUPOST_MYPOST_BUSINESS | MyPost Business | AuPostMyPostBusinessShipmentHelper | REST/JSON | API via config | API via config |
| C49 | AUPOST_MYPOST_BUSINESS_OAUTH | MyPost Business (OAuth) | AuPostMPBOAuthShipmentHelper | REST/OAuth | API via config | API via config |
| C32 | APC_POSTAL_LOGISTICS | APC Postal Logistics | ApcShipmentHelper | REST/JSON | API via config | API via config |
| C25 | COURIERS_PLEASE | Couriers Please | CouriersPleaseShipmentHelper | REST/JSON | API via config | API via config |
| C34 | MY_FASTWAY | My Fastway | MyFastwayShipmentHelper | REST/JSON | API via config | API via config |
| C30 | NEW_ZEALAND_POST | New Zealand Post | NzPostShipmentHelper | REST/JSON | API via config | API via config |
| C24 | SENDLE | Sendle | SendleShipmentHelper | REST/JSON | API via config | API via config |
| C20 | TNT_AUSTRALIA | TNT Australia | TntAustraliaShipmentHelper | SOAP/XML | API via config | API via config |

### Canada

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C6 | CANADA_POST | Canada Post | CanadaPostShipmentHelper | SOAP/XML | API via config | API via config |
| C27 | CANADA_POST_CARRIER_MANUAL_CONFIG | Canada Post (Manual) | CanadaPostShipmentHelper | SOAP/XML | API via config | API via config |
| C36 | CANPAR | Canpar | CanparShipmentHelper | REST/JSON | API via config | API via config |
| C16 | PUROLATOR | Purolator | PurolatorShipmentHelper | SOAP/XML | API via config | API via config |
| C35 | XPO_LOGISTICS | XPO Logistics | XPOShipmentHelper | REST/JSON | API via config | API via config |

### India

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C9 | BLUE_DART | Blue Dart | BlueDartShipmentHelper | XML | API via config | API via config |
| C7 | DELHIVERY | Delhivery | DelhiveryShipmentHelper | REST/JSON | API via config | API via config |
| C54 | DELHIVERY_PROXY | Delhivery (Proxy) | DelhiveryProxyShipmentHelper | REST/JSON | API via config | API via config |
| C50 | DAAKIT | Daakit | DaakitShipmentHelper | REST/JSON | API via config | API via config |
| C26 | XPRESS_BEES | XpressBees | XpressBeesShipmentHelper | REST/JSON | API via config | API via config |
| C47 | ESHIPZ | eShipz | EshipzShipmentHelper | REST/JSON | API via config | API via config |

### Europe

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C10 | DHL_PACKET | DHL Packet | DHLPacketShipmentHelper | REST/JSON | API via config | API via config |
| C17 | DHL_SWEDEN | DHL Sweden | DHLSwedenShipmentHelper | REST/JSON | API via config | API via config |
| C23 | GEODIS_MYPARCEL | Geodis MyParcel | GeodisMyParcelShipmentHelper | REST/JSON | API via config | API via config |
| C12 | PARCEL_FORCE | ParcelForce | ParcelForceShipmentHelper | REST/JSON | API via config | API via config |
| C21 | POST_NORD | PostNord | PostNordShipmentHelper | REST/JSON | API via config | API via config |
| C31 | POST_NL | PostNL | PostNlShipmentHelper | REST/JSON | API via config | API via config |
| C29 | ROYAL_MAIL | Royal Mail | RoyalMailShipmentHelper | REST/JSON | API via config | API via config |
| C44 | ROYAL_MAIL_RATES | Royal Mail (Rates Only) | RoyalMailRatesHelper | REST/JSON | API via config | API via config |
| C13 | TNT | TNT | TntShipmentHelper | SOAP/XML | API via config | API via config |

### Middle East & Asia

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C11 | ARAMEX | Aramex | AramexShipmentHelper | SOAP/XML | API via config | API via config |
| C19 | HONGKONG_POST | Hong Kong Post | HKShipmentHelper | REST/JSON | API via config | API via config |

### Latin America

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C18 | CHIL_EXPRESS | Chil Express (Chile) | ChilieXpressShipmentHelper | REST/JSON | API via config | API via config |

### Multi-Carrier Aggregators

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C22 | EASYPOST | EasyPost | EasyPostShipmentHelper | REST/JSON | API via config | API via config |
| C28 | LANDMARK_GLOBAL | Landmark Global | LandmarkGlobalShipmentHelper | REST/JSON | API via config | API via config |

### Special Integrations

| Code | Carrier Name | Descriptive Name | Adapter Class | Protocol | Sandbox URL | Production URL |
|------|--------------|------------------|---------------|----------|-------------|----------------|
| C43 | AMAZON_SHIPPING | Amazon Shipping | AmazonShipmentHelper | REST/JSON | API via config | API via config |

### Reserved / Deprecated Codes

| Code | Carrier Name | Descriptive Name | Notes |
|------|--------------|------------------|-------|
| C14 | UPS_API_INTEGRATION_CODE | UPS API Integration | Legacy integration mode |
| C15 | FEDEX_CARRIER_CODE_NEW | FedEx (New) | Alias for C2 in some contexts |

---

## API Protocol Types

### SOAP/XML Carriers

**Authentication**: WSDL-based, uses SOAP envelopes with credentials
**Carriers**: FedEx (C2), UPS (C3), Canada Post (C6), Purolator (C16), DHL Express (C1), TNT (C13), TNT Australia (C20), Aramex (C11)

**Characteristics**:
- Legacy integrations (pre-2018)
- WSDL definitions for service contracts
- XML request/response payloads
- Typically slower response times
- More complex error handling

**Example Endpoints**:
- FedEx SOAP: `wsbeta.fedex.com` (sandbox), `ws.fedex.com` (production)
- UPS SOAP: `wwwcie.ups.com` (sandbox), `onlinetools.ups.com` (production)

### REST/JSON Carriers

**Authentication**: OAuth 2.0, API keys, or bearer tokens
**Carriers**: FedEx REST (C39), UPS OAuth (C38), Australia Post (C8), DHL Packet (C10), Sendle (C24), EasyPost (C22), and most modern integrations

**Characteristics**:
- Modern APIs (2018+)
- JSON payloads
- Faster response times
- Better error messages
- Standardized HTTP status codes

### Custom XML Carriers

**Authentication**: API keys with custom XML format
**Carriers**: Blue Dart (C9), USPS Legacy (C5)

**Characteristics**:
- Proprietary XML schemas
- Non-SOAP XML over HTTP POST
- Carrier-specific authentication patterns

---

## Legacy → Modern API Migration

Several carriers maintain both legacy and modern API integrations during transition periods:

| Carrier | Legacy (SOAP) | Modern (REST) | Sandbox URL | Production URL | Status |
|---------|---------------|---------------|-------------|----------------|--------|
| FedEx | C2 | C39 | wsbeta.fedex.com | ws.fedex.com | Both active; C2 being phased out |
| UPS | C3 | C38 | wwwcie.ups.com | onlinetools.ups.com | Both active; C38 preferred |
| USPS | C5 | C45 | API via config | API via config | Both active; C45 preferred |
| Australia Post | C8 | C49 (OAuth) | API via config | API via config | C8 stable; C49 for OAuth flows |

**Migration Strategy**:
- Both versions remain active during transition
- Environment variable controls which API is used: `FEDEX_API_INTEGRATION_MODE`, `UPS_API_INTEGRATION_MODE`
- New accounts default to REST/OAuth variants
- Legacy accounts can migrate at their own pace

---

## Special Carrier Configurations

### FedEx Regional Credentials

FedEx requires different credentials per region (`storepepConfig.js`):

- **US (FDXU)**: FedEx US accounts
- **APAC**: Asia-Pacific region
- **LAC**: Latin America & Caribbean
- **MEISA**: Middle East, Indian Subcontinent, Africa
- **CA**: Canada
- **AMEA**: Africa, Middle East, Asia (alternate grouping)

Each region has its own:
- Meter number
- Account number
- API key/password
- Production vs sandbox credentials

### UPS Integration Modes

Controlled by `UPS_API_INTEGRATION_MODE` environment variable:

- **`production`**: Uses live UPS credentials and endpoints
- **`sandbox`**: Uses test credentials and `wwwcie.ups.com` endpoint

Additionally, `UPS_DAP_INTEGRATION_MODE` controls DAP (Delivered At Place) functionality.

### EasyPost Aggregator Accounts

EasyPost (C22) acts as a multi-carrier aggregator with 100+ carrier account types mapped in `storePepConstants.js:92-158`:

**Example Account Types**:
- `AmazonMwsAccount` - Amazon MWS integration
- `CanadaPostAccount` - Canada Post via EasyPost
- `FedexAccount` - FedEx via EasyPost
- `UpsAccount` - UPS via EasyPost
- `UspsAccount` - USPS via EasyPost
- `DhlExpressAccount` - DHL Express via EasyPost

**Why EasyPost?**:
- Single API for multiple carriers
- No need to maintain individual carrier integrations
- Simplified credential management
- Unified rate shopping across carriers

### Australia Post eParcel Variants

Australia Post has 3 distinct integrations:

1. **C8 (AUSTRALIA_POST)**: eParcel API - legacy REST integration
2. **C33 (AUPOST_MYPOST_BUSINESS)**: MyPost Business API - newer REST integration
3. **C49 (AUPOST_MYPOST_BUSINESS_OAUTH)**: MyPost Business with OAuth 2.0 authentication

**Key Differences**:
- C8 uses API key authentication
- C33 uses API key with different endpoint structure
- C49 uses OAuth 2.0 token-based authentication
- Different service code mappings per variant

### USPS API Evolution

USPS has 4 integration codes representing API evolution:

1. **C5 (USPS)**: Legacy USPS XML API
2. **C4 (STAMPS_USPS)**: Stamps.com USPS integration (SOAP)
3. **C45 (USPS_REST)**: USPS REST API
4. **C48 (USPS_OAUTH)**: USPS OAuth variant (uses C45 adapter)

---

## Configuration Reference

### Carrier Code Constants

**Location**: `storepepSAAS/server/src/storePepConstants.js:41-90`

Defines all carrier codes (C1-C54) as named constants:
```javascript
DHL_CARRIER_CODE: 'C1',
FEDEX_CARRIER_CODE: 'C2',
UPS_CARRIER_CODE: 'C3',
// ... etc.
```

### Carrier Name Mappings

**Location**: `storepepSAAS/server/src/storePepConstants.js:159-203`

Maps carrier codes to human-readable names:
```javascript
DHL_EXPRESS: 'DHL_EXPRESS',
FEDEX: 'FEDEX',
UPS: 'UPS',
// ... etc.
```

### API Configuration

**Location**: `storepepSAAS/server/src/storepepConfig.js`

Contains:
- API base URLs (sandbox and production)
- Carrier-specific credentials (account numbers, API keys, meter numbers)
- Regional credential mappings (FedEx regions, etc.)
- Environment-dependent settings

### Adapter Factory

**Location**: `storepepSAAS/server/src/shared/storepepAdaptors/shipmentAdaptor.js:1-191`

The `ShipmentAdaptor` class routes requests to carrier-specific adapters via `getShipmentCreatorBasedOnCarrier(carrierType)` switch statement.

**Example**:
```javascript
case constants.FEDEX_CARRIER_CODE:
  shipmentHelper = new FedexShipmentHelper();
  break;
case constants.FEDEX_REST_CARRIER_CODE:
  shipmentHelper = new FedExRestShipmentHelper();
  break;
```

### Carrier-Specific Adapters

**Location**: `storepepSAAS/server/src/shared/API/carriers/<carrier>/`

Each carrier has its own directory containing:
- `<carrier>ShipmentHelper.js` - Main adapter class
- `<carrier>RequestBuilder.js` - API request construction
- `<carrier>Tracker.js` - Tracking functionality (if applicable)
- Helper utilities specific to that carrier

---

## Environment Variables

Key environment variables for carrier configuration:

| Variable | Purpose | Values |
|----------|---------|--------|
| `UPS_API_INTEGRATION_MODE` | UPS API mode | `production`, `sandbox` |
| `UPS_DAP_INTEGRATION_MODE` | UPS DAP functionality | `production`, `sandbox` |
| `FEDEX_API_INTEGRATION_MODE` | FedEx API mode | `production`, `sandbox` |
| `NODE_ENV` | Application environment | `production`, `development`, `staging` |

These variables control which endpoints and credentials are used at runtime.

---

## Adding a New Carrier

To integrate a new carrier:

1. **Assign Carrier Code**: Add to `storePepConstants.js`:
   ```javascript
   NEW_CARRIER_CODE: 'C<next_available>',
   NEW_CARRIER: 'NEW_CARRIER',
   ```

2. **Create Adapter**: Create `server/src/shared/API/carriers/newCarrier/`:
   - `newCarrierShipmentHelper.js` - Implement ShipmentHelper interface
   - `newCarrierRequestBuilder.js` - API request construction
   - Supporting utilities as needed

3. **Register in Factory**: Add case to `shipmentAdaptor.js`:
   ```javascript
   case constants.NEW_CARRIER_CODE:
     shipmentHelper = new NewCarrierShipmentHelper();
     break;
   ```

4. **Add Configuration**: Add credentials/endpoints to `storepepConfig.js`

5. **Map Services**: Add service code mappings in adapter

6. **Implement Required Methods**:
   - `createShipment()` - Label generation
   - `createReturnShipment()` - Return labels
   - `getRates()` - Rate shopping
   - `trackShipment()` - Tracking
   - `requestPickup()` - Pickup scheduling (if supported)
   - `voidShipment()` - Shipment cancellation

---

## Known Issues / Tech Debt

### API Deprecations

- **FedEx SOAP (C2) deprecation**: FedEx announced end-of-life for SOAP APIs (target: 2025-2026). Migrate to C39 (FedEx REST).
- **UPS XML/SOAP sunset**: UPS is phasing out SOAP in favor of OAuth/REST (C38). Timeline: ongoing through 2026.
- **USPS XML API (C5) retirement**: USPS is deprecating legacy XML API. Migrate to C45 (USPS REST).

### Rate Limiting Differences

- **UPS OAuth (C38)**: Stricter rate limits than legacy SOAP (C3) - 1000 requests/hour vs 5000/hour
- **FedEx REST (C39)**: Different throttling rules per endpoint type (rates vs labels vs tracking)

### Regional Endpoint Complexity

- **FedEx Regional Routing**: Different API endpoints per region (US vs APAC vs EMEA) complicates configuration
- **Australia Post eParcel Delays**: Polling-based status updates can cause delays (see ZI-058)

### Authentication Token Management

- **OAuth Token Refresh**: UPS OAuth (C38) and USPS OAuth (C48) require token refresh logic - current implementation caches tokens but needs retry handling
- **Session Timeouts**: Some carriers (Blue Dart C9) have short-lived sessions requiring frequent re-authentication

### Carrier-Specific Data Validation

- **Address Validation**: Different carriers have different address requirements (e.g., Australia Post requires suburb, UPS requires state codes)
- **Weight/Dimension Limits**: Each carrier has different limits - need centralized validation before adapter call
- **Service Code Variability**: Same service (e.g., "Ground") has different codes across carriers - mapping complexity

---

## Related Pages

- [Label Generation](../modules/shipping/label-generation.md) - How carriers are used for label creation
- [Rate Shopping](../modules/shipping/rate-shopping.md) - Multi-carrier rate comparison
- [Shipment Tracking](../modules/shipping/shipment-tracking.md) - Carrier tracking integration
- [Platform Connectors](../modules/stores/platform-connectors.md) - Store integrations that feed carrier selection
- [Backend Architecture](backend-architecture.md) - Overall system architecture
