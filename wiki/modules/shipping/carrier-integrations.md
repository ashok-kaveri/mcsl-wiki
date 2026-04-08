---
title: Carrier Integrations
category: module
domain: shipping
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Carrier Integrations

## Overview

StorePep integrates with **46 carrier configurations** covering **43 unique carriers** across major markets including North America, Europe, Asia Pacific, and South America. This document provides a comprehensive reference of all supported carriers, their carrier codes, regions, API types, and special features.

**Total Carriers**: 43 unique carriers
**Total Configurations**: 46 (includes multiple API versions for major carriers)
**Geographic Coverage**: Global (50+ countries)

## Carrier List

### North America

#### United States

**FedEx (C2)** - FedEx Legacy SOAP API
- **Code**: `C2` (`FEDEX_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: API Key, Password, Account Number, Meter Number
- **Features**:
  - Ground, Express, Freight services
  - SmartPost (now Ground Economy)
  - Hold at Location
  - Saturday Delivery
  - Signature options (Indirect, Direct, Adult)
  - Dry Ice shipments
  - One Rate packaging
- **Label Formats**: PDF, ZPL (ZPLII)
- **International**: Yes, with commercial invoice generation
- **Location**: `server/src/shared/API/carriers/fedex/`

**FedEx REST (C39)** - FedEx Modern REST API
- **Code**: `C39` (`FEDEX_REST_CARRIER_CODE`)
- **API**: REST/JSON with OAuth 2.0
- **Authentication**: Client ID, Client Secret
- **Features**: Same as C2 but modern API
- **Label Formats**: PDF, ZPL
- **Migration Status**: Active, replacing C2
- **Location**: `server/src/shared/API/carriers/fedExRest/`

**FedEx Same Day City (C37)**
- **Code**: `C37` (`FEDEX_SAME_DAY_CITY_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: Same-day delivery within select cities
- **Special**: Time-definite delivery windows
- **Location**: `server/src/shared/API/carriers/fedexSameDayCity/`

**UPS (C3)** - UPS Legacy XML API
- **Code**: `C3` (`UPS_CARRIER_CODE`)
- **API**: XML over HTTP
- **Authentication**: Username, Password, Access License Key
- **Features**:
  - Ground, Next Day Air, 2nd Day Air
  - SurePost (last-mile USPS)
  - Negotiated rates support
  - Carbon neutral shipping
  - Quantum View notifications
- **Label Formats**: PDF, ZPL
- **International**: Yes, with customs forms
- **Location**: `server/src/shared/API/carriers/ups/`

**UPS OAuth (C38)** - UPS Modern REST API
- **Code**: `C38` (`UPS_OAUTH_CARRIER_CODE`)
- **API**: REST/JSON with OAuth 2.0
- **Authentication**: Client ID, Client Secret
- **Features**: Same as C3 but modern OAuth authentication
- **Migration Status**: Active, replacing C3
- **Location**: `server/src/shared/API/carriers/upsRestApi/`

**USPS via Stamps.com (C4)**
- **Code**: `C4` (`STAMPS_USPS_CARRIER_CODE`)
- **API**: Stamps.com SOAP API
- **Authentication**: Integration ID, Username, Password
- **Features**:
  - First-Class, Priority, Priority Express
  - Media Mail, Library Mail
  - Commercial pricing
  - Commercial Plus pricing
  - Sample labels (test mode)
  - Certified Mail, Registered Mail
- **Label Formats**: PDF, PNG
- **International**: Yes (Priority Mail International, Express Mail International)
- **Location**: `server/src/shared/API/carriers/stamps.com(usps)/`

**USPS Direct (C5)**
- **Code**: `C5` (`USPS_CARRIER_CODE`)
- **API**: USPS Direct XML API
- **Authentication**: User ID
- **Features**: Basic USPS services
- **Location**: `server/src/shared/API/carriers/usps/`

**USPS REST (C45)**
- **Code**: `C45` (`USPS_REST_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key
- **Features**: Modern REST interface for USPS
- **Migration Status**: Active
- **Location**: `server/src/shared/API/carriers/uspsRest/`

**USPS REST v2 (C46)**
- **Code**: `C46` (`USPS_REST_V2_CARRIER_CODE`)
- **API**: REST/JSON v2
- **Status**: Next-generation USPS API

**USPS OAuth (C48)**
- **Code**: `C48` (`USPS_OAUTH_CARRIER_CODE`)
- **API**: REST/JSON with OAuth 2.0
- **Status**: Newest USPS authentication method

**Amazon Shipping (C43)**
- **Code**: `C43` (`AMAZON_SHIPPING_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: Access Key ID, Secret Access Key, Region
- **Features**:
  - Amazon-specific shipping rates
  - Prime delivery integration
  - Amazon Logistics network
- **Availability**: Requires Amazon seller account
- **Location**: `server/src/shared/API/carriers/amazonShipping/`

**XPO Logistics (C35)**
- **Code**: `C35` (`XPO_LOGISTICS_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: LTL and full truckload freight
- **Specialization**: B2B freight shipping
- **Location**: `server/src/shared/API/carriers/xpoLogistics/`

#### Canada

**Canada Post (C6)**
- **Code**: `C6` (`CANADA_POST_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: API Key, Username, Password
- **Features**:
  - Expedited Parcel, Xpresspost, Priority
  - Contract vs counter rates
  - Service points (FlexDelivery)
  - Proof of Age requirement
  - Card for pickup
- **Label Formats**: PDF, ZPL
- **International**: Yes
- **Special**: Bilingual labels (English/French)
- **Location**: `server/src/shared/API/carriers/canadaPost/`

**Purolator (C16)**
- **Code**: `C16` (`PUROLATOR_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: API Key, Username, Password
- **Features**:
  - Express, Ground services
  - Dangerous goods support
  - Chain of Signature
- **Coverage**: Canada-wide, US cross-border
- **Location**: `server/src/shared/API/carriers/purolator/`

**Canpar (C36)**
- **Code**: `C36` (`CANPAR_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: Express and ground delivery across Canada
- **Coverage**: Canada
- **Location**: `server/src/shared/API/carriers/canpar/`

#### Latin America

**Chil Express (C18)**
- **Code**: `C18` (`CHIL_EXPRESS_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: Chile
- **Features**: Domestic Chilean shipping
- **Location**: `server/src/shared/API/carriers/chilExpress/`

### Europe

**DHL Express (C1)**
- **Code**: `C1` (`DHL_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: Site ID, Password, Account Number
- **Features**:
  - Worldwide Express, 9:00, 12:00 delivery
  - Duty/Tax payment options (DDU, DDP)
  - Paperless trade
  - Archive retrieval
- **Label Formats**: PDF, ZPL2
- **International**: Yes, global network
- **Special Services**: Medical express, dangerous goods
- **Location**: `server/src/shared/API/carriers/dhlExpress/`

**DHL Packet (C10)**
- **Code**: `C10` (`DHL_PACKET_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: Lightweight packet service (< 2kg)
- **Coverage**: International mail
- **Location**: `server/src/shared/API/carriers/dhlPacket/`

**DHL Sweden (C17)**
- **Code**: `C17` (`DHL_SWEDEN_CARRIER_CODE`)
- **API**: SOAP/XML
- **Coverage**: Sweden domestic and international
- **Location**: `server/src/shared/API/carriers/dhlSweden/`

**Royal Mail (C29)**
- **Code**: `C29` (`ROYAL_MAIL_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: Application ID, Username, Password
- **Features**:
  - 1st Class, 2nd Class
  - Signed For, Special Delivery
  - International Standard, Tracked
- **Coverage**: UK domestic and international
- **Label Formats**: PDF
- **Location**: `server/src/shared/API/carriers/royalMail/`

**Royal Mail Rates (C44)**
- **Code**: `C44` (`ROYAL_MAIL_RATES_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: Rate calculation only
- **Location**: `server/src/shared/API/carriers/royalMailRates/`

**Parcel Force (C12)**
- **Code**: `C12` (`PARCEL_FORCE_CARRIER_CODE`)
- **API**: SOAP/XML
- **Features**: Express services (Royal Mail subsidiary)
- **Coverage**: UK and international
- **Special**: Large parcel and pallets
- **Location**: `server/src/shared/API/carriers/parcelForce/`

**PostNord (C21)**
- **Code**: `C21` (`POST_NORD_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key, Customer ID
- **Features**:
  - Service points
  - Home delivery
  - Business distribution
- **Coverage**: Sweden, Denmark, Norway, Finland
- **Location**: `server/src/shared/API/carriers/postNord/`

**PostNL (C31)**
- **Code**: `C31` (`POST_NL_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key, Customer Number
- **Features**:
  - Parcel service
  - Mailbox parcel
  - Same-day delivery
- **Coverage**: Netherlands, Belgium
- **Location**: `server/src/shared/API/carriers/postNL/`

**TNT (C13)**
- **Code**: `C13` (`TNT_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: Username, Password, Account Number
- **Features**:
  - Express services (now part of FedEx)
  - Economy Express
  - Dangerous goods
- **Coverage**: Europe, international
- **Location**: `server/src/shared/API/carriers/tnt/`

**Geodis MyParcel (C23)**
- **Code**: `C23` (`GEODIS_MYPARCEL_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: Europe
- **Features**: Parcel and freight services
- **Location**: `server/src/shared/API/carriers/geodisMyParcel/`

### Asia Pacific

**Australia Post (C8)**
- **Code**: `C8` (`AUSTRALIA_POST_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key, Account Number, Password
- **Features**:
  - Express Post, Parcel Post
  - International Economy, Standard
  - MyPost Business integration
  - Safe Drop, Authority to Leave
- **Coverage**: Australia domestic and international
- **Label Formats**: PDF
- **Location**: `server/src/shared/API/carriers/australiaPost/`

**Australia Post MyPost Business (C33)**
- **Code**: `C33` (`AUPOST_MYPOST_BUSINESS_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: Business account integration
- **Coverage**: Australia
- **Location**: `server/src/shared/API/carriers/auPostMyPostBusiness/`

**Australia Post MyPost Business OAuth (C49)**
- **Code**: `C49` (`AUPOST_MYPOST_BUSINESS_OAUTH_CARRIER_CODE`)
- **API**: REST/JSON with OAuth 2.0
- **Features**: Modern OAuth authentication for MyPost Business
- **Location**: `server/src/shared/API/carriers/auPostMyPostBusinessOauth/`

**TNT Australia (C20)**
- **Code**: `C20` (`TNT_AUSTRALIA_CARRIER_CODE`)
- **API**: SOAP/XML
- **Coverage**: Australia domestic
- **Features**: Express delivery
- **Location**: `server/src/shared/API/carriers/tntAustralia/`

**Couriers Please (C25)**
- **Code**: `C25` (`COURIERS_PLEASE_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: Australia
- **Features**: Domestic parcel delivery
- **Location**: `server/src/shared/API/carriers/courierPlease/`

**Sendle (C24)**
- **Code**: `C24` (`SENDLE_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key, Sendle ID
- **Features**:
  - Carbon-neutral shipping
  - Door-to-door pickup
  - Easy Send (drop-off)
- **Coverage**: Australia, US
- **Special**: 100% carbon-neutral
- **Location**: `server/src/shared/API/carriers/sendle/`

**MyFastway (C34)**
- **Code**: `C34` (`MY_FASTWAY_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: Australia, New Zealand, Ireland
- **Features**: Parcel delivery
- **Location**: `server/src/shared/API/carriers/myfastway/`

**New Zealand Post (C30)**
- **Code**: `C30` (`NEW_ZEALAND_POST_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: New Zealand domestic and international
- **Features**: CourierPost, ParcelPost
- **Location**: `server/src/shared/API/carriers/nzpost/`

#### India

**Delhivery (C7)**
- **Code**: `C7` (`DELHIVERY_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key, Client ID
- **Features**:
  - Surface, Express delivery
  - Cash on Delivery (COD)
  - Reverse pickup
- **Coverage**: India domestic
- **Special**: COD remittance support
- **Location**: `server/src/shared/API/carriers/delhivery/`

**Blue Dart (C9)**
- **Code**: `C9` (`BLUE_DART_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key, License Key
- **Features**:
  - Domestic Express, Surface
  - International
  - COD
- **Coverage**: India domestic and international
- **Special**: DHL partnership for international
- **Location**: `server/src/shared/API/carriers/blueDart/`

**Xpressbees (C26)**
- **Code**: `C26` (`XPRESS_BEES_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: India
- **Features**:
  - COD support
  - Prepaid and COD
  - Surface and air
- **Location**: `server/src/shared/API/carriers/xpressbees/`

**Daakit (C50)**
- **Code**: `C50` (`DAAKIT_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: India
- **Features**: Domestic Indian logistics
- **Location**: `server/src/shared/API/carriers/daakit/`

#### Other Asia

**Hong Kong Post (C19)**
- **Code**: `C19` (`HONGKONG_POST_CARRIER_CODE`)
- **API**: SOAP/XML
- **Coverage**: Hong Kong domestic and international
- **Features**:
  - SpeedPost (Express)
  - Air mail, Surface mail
  - e-Cert (electronic customs)
- **Location**: `server/src/shared/API/carriers/hongkongPost/`

### Middle East

**Aramex (C11)**
- **Code**: `C11` (`ARAMEX_CARRIER_CODE`)
- **API**: SOAP/XML
- **Authentication**: Username, Password, Account Number
- **Features**:
  - Express, Economy services
  - COD support
  - Shop & Ship
- **Coverage**: Middle East, North Africa, global
- **Label Formats**: PDF
- **Location**: `server/src/shared/API/carriers/aramex/`

### Multi-Carrier Aggregators

**EasyPost (C22)**
- **Code**: `C22` (`EASYPOST_CARRIER_CODE`)
- **API**: REST/JSON
- **Authentication**: API Key
- **Features**:
  - Access to 100+ carriers through single API
  - Address validation
  - Insurance
  - Tracking
  - Rate shopping across carriers
- **Supported Carriers**: USPS, FedEx, UPS, DHL, regional carriers
- **Use Case**: Quick onboarding, carriers not directly integrated
- **Label Formats**: PDF, PNG, ZPL (carrier-dependent)
- **Location**: `server/src/shared/API/carriers/easyPost/`

**Eshipz (C47)**
- **Code**: `C47` (`ESHIPZ_CARRIER_CODE`)
- **API**: REST/JSON
- **Features**: Multi-carrier aggregator for India
- **Coverage**: India (aggregates Indian carriers)
- **Location**: `server/src/shared/API/carriers/eshipz/`

### Other

**Landmark Global (C28)**
- **Code**: `C28` (`LANDMARK_GLOBAL_CARRIER_CODE`)
- **API**: REST/JSON
- **Coverage**: International cross-border e-commerce
- **Features**: Customs clearance, last-mile delivery
- **Location**: `server/src/shared/API/carriers/landMarkGlobal/`

**APC Postal Logistics (C40)**
- **Code**: `C40` (`APC_POSTAL_LOGISTICS_CODE`)
- **API**: REST/JSON
- **Coverage**: Europe, US cross-border
- **Features**: International lightweight packets
- **Location**: `server/src/shared/API/carriers/apcPostalLogistics/`

## Carrier Code Reference

Quick lookup table of all carrier codes:

| Code | Carrier | Region |
|------|---------|--------|
| C1 | DHL Express | Global |
| C2 | FedEx (SOAP) | Global |
| C3 | UPS (XML) | Global |
| C4 | USPS via Stamps.com | US |
| C5 | USPS Direct | US |
| C6 | Canada Post | Canada |
| C7 | Delhivery | India |
| C8 | Australia Post | Australia |
| C9 | Blue Dart | India |
| C10 | DHL Packet | Europe/International |
| C11 | Aramex | Middle East/Global |
| C12 | Parcel Force | UK |
| C13 | TNT | Europe |
| C15 | FedEx (New) | Global |
| C16 | Purolator | Canada |
| C17 | DHL Sweden | Sweden |
| C18 | Chil Express | Chile |
| C19 | Hong Kong Post | Hong Kong |
| C20 | TNT Australia | Australia |
| C21 | PostNord | Scandinavia |
| C22 | EasyPost | Multi-carrier aggregator |
| C23 | Geodis MyParcel | Europe |
| C24 | Sendle | Australia/US |
| C25 | Couriers Please | Australia |
| C26 | Xpressbees | India |
| C28 | Landmark Global | International |
| C29 | Royal Mail | UK |
| C30 | New Zealand Post | New Zealand |
| C31 | PostNL | Netherlands/Belgium |
| C33 | Australia Post MyPost Business | Australia |
| C34 | MyFastway | Australia/NZ |
| C35 | XPO Logistics | US |
| C36 | Canpar | Canada |
| C37 | FedEx Same Day City | US |
| C38 | UPS OAuth | Global |
| C39 | FedEx REST | Global |
| C40 | APC Postal Logistics | Europe/US |
| C43 | Amazon Shipping | US |
| C44 | Royal Mail Rates | UK |
| C45 | USPS REST | US |
| C46 | USPS REST v2 | US |
| C47 | Eshipz | India |
| C48 | USPS OAuth | US |
| C49 | Australia Post MyPost Business OAuth | Australia |
| C50 | Daakit | India |

## API Protocol Breakdown

### SOAP/XML APIs (Legacy)
- DHL Express (C1)
- FedEx SOAP (C2)
- Canada Post (C6)
- Purolator (C16)
- TNT (C13)
- Parcel Force (C12)
- Aramex (C11)
- Royal Mail (C29)
- Hong Kong Post (C19)

### REST/JSON APIs (Modern)
- FedEx REST (C39)
- UPS OAuth (C38)
- USPS REST (C45, C46, C48)
- Amazon Shipping (C43)
- Australia Post (C8, C33, C49)
- Delhivery (C7)
- Blue Dart (C9)
- EasyPost (C22)
- PostNord (C21)
- PostNL (C31)
- Sendle (C24)
- Xpressbees (C26)
- All other modern integrations

### XML over HTTP (Legacy)
- UPS XML (C3)
- USPS Direct (C5)

### OAuth 2.0 Authentication
- FedEx REST (C39)
- UPS OAuth (C38)
- USPS OAuth (C48)
- Australia Post MyPost Business OAuth (C49)

## Special Features by Carrier

### COD (Cash on Delivery)
- Delhivery (C7)
- Blue Dart (C9)
- Xpressbees (C26)
- Aramex (C11)
- Eshipz (C47)

### Hold at Location / Service Points
- FedEx (C2, C39) - Hold at FedEx Location
- UPS (C3, C38) - UPS Access Point
- Canada Post (C6) - FlexDelivery
- PostNord (C21) - Service points
- PostNL (C31) - PostNL points

### Saturday/Sunday Delivery
- FedEx (C2, C39)
- UPS (C3, C38)
- USPS (C4)

### Same-Day Delivery
- FedEx Same Day City (C37)
- PostNL (C31)

### Dangerous Goods Support
- FedEx (C2, C39) - Dry Ice, Hazmat
- DHL Express (C1) - Medical, Hazmat
- Purolator (C16)
- TNT (C13)

### Carbon Neutral / Sustainability
- UPS (C3, C38) - Carbon Neutral option
- Sendle (C24) - 100% carbon neutral
- FedEx (C2, C39) - Carbon offset program

### Freight Services
- FedEx Freight (via C2, C39)
- UPS Freight (via C3, C38)
- XPO Logistics (C35) - LTL/FTL specialist
- Purolator (C16)

## Feature Support Matrix

| Feature | Carriers Supporting |
|---------|---------------------|
| **Rate Shopping** | All carriers |
| **Label Generation** | All except C44 (Royal Mail Rates) |
| **Tracking** | All carriers with label generation |
| **Address Validation** | FedEx, UPS, USPS, EasyPost, Canada Post |
| **Pickup Scheduling** | FedEx, UPS, DHL, Canada Post, Australia Post |
| **Manifest / End of Day** | FedEx, UPS, USPS, Canada Post, Australia Post |
| **Return Labels** | FedEx, UPS, USPS, Canada Post, DHL, EasyPost |
| **International Shipping** | FedEx, UPS, DHL, USPS, Canada Post, Aramex, most others |
| **Commercial Invoice** | FedEx, UPS, DHL, USPS (international services) |
| **Insurance** | FedEx, UPS, USPS, EasyPost, most carriers |
| **Signature Required** | FedEx, UPS, USPS, DHL, Canada Post, most carriers |

## Migration Paths

### Legacy to Modern API

**FedEx Migration**: C2 (SOAP) → C39 (REST)
- Both APIs currently supported
- REST API recommended for new integrations
- SOAP API maintenance mode

**UPS Migration**: C3 (XML) → C38 (OAuth REST)
- Both APIs currently supported
- OAuth required for new accounts (as of 2024)
- XML API deprecation planned

**USPS Evolution**: C4 (Stamps) → C5 (Direct) → C45 (REST) → C46 (REST v2) → C48 (OAuth)
- Multiple generations due to USPS API changes
- C4 (Stamps.com) still most feature-complete
- C48 (OAuth) newest, future-proof

**Australia Post Migration**: C8 → C33 → C49 (OAuth)
- C49 with OAuth most secure
- C8 still widely used

## Geographic Coverage Summary

### North America
- **US**: 11 carrier configurations (FedEx, UPS, USPS, Amazon, XPO, Sendle)
- **Canada**: 3 carriers (Canada Post, Purolator, Canpar)
- **Mexico**: Via FedEx, UPS, DHL international

### Europe
- **UK**: Royal Mail, Parcel Force
- **Netherlands/Belgium**: PostNL
- **Scandinavia**: PostNord, DHL Sweden
- **Pan-Europe**: DHL Express, TNT, Geodis MyParcel

### Asia Pacific
- **Australia**: 5 carriers (Australia Post variants, TNT, Couriers Please, Sendle, MyFastway)
- **New Zealand**: NZ Post, MyFastway
- **India**: 4 carriers (Delhivery, Blue Dart, Xpressbees, Daakit, Eshipz)
- **Hong Kong**: Hong Kong Post
- **China**: Via DHL, FedEx, UPS international

### Middle East
- **UAE, Saudi Arabia, others**: Aramex

### Latin America
- **Chile**: Chil Express
- **Others**: Via DHL, FedEx, UPS international

### Africa
- Via DHL, FedEx, UPS, Aramex international services

## Integration Complexity

### Simple (REST API, straightforward)
- EasyPost (C22) - aggregator simplifies multi-carrier
- Sendle (C24)
- Delhivery (C7)
- PostNL (C31)

### Moderate (REST/SOAP, some special features)
- FedEx REST (C39)
- UPS OAuth (C38)
- Australia Post (C8)
- Canada Post (C6)
- Royal Mail (C29)

### Complex (SOAP, many special services, customs)
- FedEx SOAP (C2) - 50+ carrier-specific fields
- UPS XML (C3) - 40+ carrier-specific fields
- DHL Express (C1) - complex customs, duty options
- Purolator (C16) - dangerous goods, chain of signature

### Very Complex (Multi-carrier aggregation)
- EasyPost (C22) - abstracts 100+ carriers
- Eshipz (C47) - Indian carrier aggregation

## Dependencies

- [Carrier System Overview](./carrier-system-overview.md) - Architecture and adaptor pattern
- [Carrier Configuration](./carrier-configuration.md) - Configuration for each carrier
- [Rate Shopping](./rate-shopping.md) - Rate fetching across carriers
- [Label Generation](./label-generation.md) - Label creation per carrier

## Referenced By

- Carrier adaptor uses these integrations
- Rate shopping calls all active carriers
- Label generation routes to specific carrier

## Configuration

**Adding a New Carrier**:
1. Create new directory in `server/src/shared/API/carriers/[carrierName]/`
2. Add carrier code constant to `storePepConstants.js`
3. Implement `ShipmentHelper` class with required methods
4. Add case to `ShipmentAdaptor.getShipmentCreatorBasedOnCarrier()`
5. Add service code mappings to `serviceCodes.js`
6. Create carrier model schema fields in `carriers.js`

**Environment Variables**:
- Carrier API URLs (sandbox vs production)
- API timeouts per carrier
- Rate limits per carrier

## Common Patterns

### Check Carrier Support for Feature

```javascript
const carriersSupportingHoldAtLocation = [
  constants.FEDEX_CARRIER_CODE,
  constants.FEDEX_REST_CARRIER_CODE,
  constants.UPS_CARRIER_CODE,
  constants.UPS_OAUTH_CARRIER_CODE,
  constants.CANADA_POST_CARRIER_CODE,
];

const supportsHoldAtLocation = carriersSupportingHoldAtLocation.includes(carrier.carrierType);
```

### Get Carrier Display Name

```javascript
const carrierNames = {
  [constants.FEDEX_CARRIER_CODE]: 'FedEx',
  [constants.UPS_CARRIER_CODE]: 'UPS',
  [constants.DHL_CARRIER_CODE]: 'DHL Express',
  // ... etc
};

const displayName = carrierNames[carrier.carrierType] || 'Unknown Carrier';
```

## Known Issues / Tech Debt

1. **Inconsistent API versions**: Some carriers have 3-4 API versions causing confusion
2. **Service code mapping complexity**: 1500+ service codes across all carriers
3. **Feature detection**: No centralized feature matrix, scattered across carrier implementations
4. **OAuth token management**: Manual refresh for OAuth carriers
5. **Carrier sunset dates**: No tracking of deprecated carrier APIs
6. **Regional availability**: No validation that carrier supports destination country

## Related Pages

- [Carrier System Overview](./carrier-system-overview.md)
- [Carrier Configuration](./carrier-configuration.md)
- [Rate Shopping](./rate-shopping.md)
- [Label Generation](./label-generation.md)
- [Order Lifecycle](../orders/order-lifecycle.md)
