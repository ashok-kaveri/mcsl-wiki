---
title: Carrier Configuration
category: module
domain: shipping
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Carrier Configuration

## Overview

Carrier configuration defines how merchants connect their shipping carrier accounts to StorePep. Each carrier requires specific credentials, preferences, and settings stored in a carrier document. The carrier model supports 43 different carriers with carrier-specific fields totaling 487 lines of schema definition.

**Location**: `server/src/models/carriers.js:7-487`

**Purpose**: Store carrier credentials, account preferences, and operational settings per account.

## Carrier Model Schema

### Common Fields (All Carriers)

**Identity & Status** (`carriers.js:9-20`):
```javascript
{
  carrierID: String,        // UUID, unique identifier
  carrierName: String,      // Display name ("FedEx Ground Account")
  carrierType: String,      // Carrier code (C2, C3, etc.)
  accountUUID: String,      // StorePep account owner
  vendorUUID: String,       // Multi-vendor support
  isActive: Boolean,        // Enabled for use
  status: String,           // IN_USE | ARCHIVED
  createdBy: String,        // User who created
  updatedBy: String,        // Last user to modify
  bufferDaysToTransitTime: Number,  // Add days to carrier's estimate
  bufferTime: Number        // Processing time buffer
}
```

**Authentication** (`carriers.js:24-34`):
```javascript
{
  productionKey: Boolean,   // true = production, false = test/sandbox
  accountNumber: String,    // Carrier account number
  password: String,         // API password
  apiKey: String,           // API key/token
  apiSecret: String,        // API secret
  // Carrier-specific auth fields follow
}
```

**Label & Invoice Preferences** (`carriers.js:29-44`):
```javascript
{
  labelPrintSize: String,         // "4x6" (thermal) or "8.5x11" (letter)
  invoiceType: String,            // Commercial invoice template
  invoiceLanguage: String,        // Invoice language code
  useDimensions: Boolean,         // Use package dimensions for rates
  printInstructionsOnLabel: Boolean,
  instructionType: String,
  customInstruction: String
}
```

**Operational Settings** (`carriers.js:27-44`):
```javascript
{
  companyCloseTime: String,       // "17:00" - when warehouse closes
  pickupStartTime: String,        // "09:00" - earliest pickup time
  pickupSpecialServices: Array,   // Special services for pickup
  packingType: String,            // How to pack items
  reasonForExport: String,        // Default export reason
  countryOfOrigin: String,        // Default country of manufacture
  gstIdentificationNumber: String,
  importExportNumber: String
}
```

## Carrier-Specific Fields

### FedEx (50+ fields)

**Authentication** (`carriers.js:82-86`):
```javascript
{
  webServiceKey: String,          // FedEx API key
  webServicePassword: String,     // FedEx API password
  meterNumber: String,            // FedEx meter number
  accountNumber: String           // FedEx account number
}
```

**Label & Printing** (`carriers.js:86-92`):
```javascript
{
  labelStockType: String,         // PAPER_4X6, PAPER_LETTER, STOCK_4X6.75
  paymentType: String,            // SENDER, RECIPIENT, THIRD_PARTY
  pickupService: String,          // Pickup service type
  rateRequestType: String,        // 'LIST' | 'ACCOUNT' (default: LIST)
  codCollectionType: String       // COD collection method
}
```

**Freight & Special Services** (`carriers.js:91-108`):
```javascript
{
  freightAccountNumber: String,
  freightBillingAddressUUID: String,
  freightShipFromAddressUUID: String,
  freightPackageDimensionsInInches: {
    defaultLength: Number,
    defaultWidth: Number,
    defaultHeight: Number
  },
  customsDutiesPayor: String,     // SENDER | RECIPIENT | THIRD_PARTY
  dropOffType: String,            // REGULAR_PICKUP | DROP_BOX | etc.
  termsOfSale: String,            // FOB, CIF, etc.
  defaultAddressClassificationForRates: String,  // RESIDENTIAL | COMMERCIAL
  isAddressValidationEnabled: Boolean,
  includeShippingInCI: Boolean,   // Include shipping in commercial invoice
  displayInsuranceOnCI: Boolean,
  isEtdEnabled: Boolean,          // Electronic Trade Documents
  enablePostUpload: Boolean,
  isLocalPickupLocationEnabled: Boolean
}
```

**Signatures & Branding** (`carriers.js:109-123`):
```javascript
{
  customerSignature: {
    fileName: String,
    fileSize: Number,
    fileType: String,
    image: String               // Base64 encoded
  },
  letterHead: {
    fileName: String,
    fileSize: Number,
    fileType: String,
    image: String
  },
  useSignature: Boolean,
  useLetterHead: Boolean
}
```

**SmartPost & Advanced** (`carriers.js:124-173`):
```javascript
{
  maxDryIceWeightPerPackageInKgs: Number,
  isSmartPostEnabled: Boolean,
  indicia: String,                // SmartPost indicia
  hubId: String,                  // SmartPost hub ID
  ancillaryEndorsement: String,
  tinType: String,                // Tax ID type
  csbType: String,                // CSB5 | CSB4 (Canada specific)
  eCommerceShipments: String,
  meisShipments: String,
  shipmentUnderBOND: String,
  lutNumber: String,              // LUT number (India)
  bondNumber: String,
  gstEnabled: Boolean,
  IECNumber: String,              // Import/Export Code
  isFreightDirectEnabled: Boolean,
  freightDeliveryInstructions: String,
  freightSpecialServiceType: Array,
  thirdPartyAccountNumber: String,
  isFedexOneRateEnabled: Boolean,
  isFedexSaturdayServiceEnabled: Boolean,
  isFedexHomeDeliveryServiceEnabled: Boolean,
  fedexHomeDeliveryServiceType: String,
  fedexRegion: String,
  // ... event notification settings
  addEventNotification: Boolean,
  recipientRole: Array,
  recipientEvent: Array,
  notificationEmailAddress: String,
  languageCode: String,
  formatSpecificationType: String
}
```

**Importer of Record** (`carriers.js:164-176`):
```javascript
{
  isImporterOfRecordEnabled: Boolean,
  autoUploadDocuments: Boolean,
  enableThirdPartyConsignee: Boolean,
  importerAccountNumber: String,
  importerTinType: String,
  importerTinNumber: String,
  importerAddressUUID: String,
  shipmentPayerAddressUUID: String,
  physicalPackagingType: String,
  labelMaskableDataType: Array,
  hazardousTypeOfPackaging: String,
  hazardousPackagingMaterial: String,
  isProformaNeeded: Boolean
}
```

### UPS (40+ fields)

**Authentication** (`carriers.js:178-180`):
```javascript
{
  userId: String,               // UPS user ID
  accessKey: String,            // UPS access key
  password: String,             // UPS password
  accountNumber: String         // UPS account number
}
```

**Rates & Services** (`carriers.js:180-206`):
```javascript
{
  negotiatedRates: Boolean,     // Use negotiated rates if available
  pickupType: String,           // DAILY_PICKUP | ONE_TIME_PICKUP | etc.
  customerClassification: String,
  pickupServiceCode: String,
  conditionallyRemovePhoneNumber: Boolean,
  isSurePostEnabled: Boolean,   // UPS SurePost (USPS last mile)
  isFreightEnable: Boolean,
  enableAutomaticAdditionalHandling: Boolean,
  freightClass: String,
  handlingUnit: String,
  isRateWithTax: Boolean,
  connectionMode: String,
  declarationStatement: String,
  additionalComments: String,
  upsRegularPackingType: String,
  dutiesAndTaxesPayer: String,
  dutiesAndTaxesPayerAccountNumber: String,
  enableLabelReferences: Boolean,
  upsOrderReference1: String,
  upsSurePostEndorsement: String,
  emergencyContactNumber: String,
  emergencyContactName: String,
  thirdPartyAddressUUID: String,
  showApplyPromoButton: Boolean,
  accountType: String,
  isPromoCodeApplied: Boolean,
  shipperRelease: Boolean
}
```

### DHL (30+ fields)

**Authentication & Basic** (`carriers.js:46-66`):
```javascript
{
  siteId: String,               // DHL site ID
  password: String,
  accountNumber: String,
  dutyPaymentType: String,
  imageType: String,            // Label format
  airWaybill: Boolean,
  numberOfAirBills: Number,
  activateTrackingCustomMessage: Boolean,
  pltEnabled: Boolean,          // Paperless Trade
  trackingCustomMessage: String,
  enableReturnLabel: Boolean,
  returnAccountNumber: String
}
```

**Branding & Invoice** (`carriers.js:57-73`):
```javascript
{
  companyLogo: {
    fileName: String,
    fileSize: Number,
    fileType: String,
    image: String
  },
  accountRates: Boolean,        // Use account-specific rates
  associationType: String,      // B2B | B2C
  bankADCode: String,
  useDHLInvoice: String,
  includeTaxInInvoice: Boolean,
  enableNfei: Boolean,          // New Foreign Exchange Interface
  bankAccountNumber: String,
  bondNumberforDHL: String,
  traderType: String,
  placeOfIncoterm: String
}
```

### USPS (Multiple Variants)

**Stamps.com** (`carriers.js:237-243`):
```javascript
{
  apiKey: String,
  apiSecret: String,
  paperSize: String,            // Label size
  hiddenPostage: Boolean,       // Hide postage amount on label
  isSampleLabel: Boolean,       // Test mode
  commercialPlusRates: Boolean, // Commercial Plus pricing
  packageLocation: String,
  pickupSpecialInstructions: String
}
```

### Canada Post (`carriers.js:246-261`):
```javascript
{
  customerNumber: String,       // Canada Post customer number
  contractNumber: String,       // Contract number
  billThirdParty: Boolean,
  useGroupId: Boolean,
  groupId: String,
  contractId: String,
  platformId: String,
  optionQualifierOne: Boolean,
  displayOrderNoteForCanadaPost: Boolean,
  shipmentPayerAccountNumber: String,
  serviceType: String,          // CONTRACT | NON_CONTRACT
  quoteType: String,            // COMMERCIAL | COUNTER
  rateCost: String,             // BASE | DUE | BASE_SURCHARGE | BASE_WITHOUT_TAXES
  paymentMethod: String,        // Account | CreditCard
  labelSize: String,            // 8.5x11 | 4x6
  notification: Array,
  isPlatFormIdRequired: Boolean,
  pickupInstructions: String,
  zonosKey: String              // Zonos integration (landed cost)
}
```

### Australia Post (`carriers.js:270-289`):
```javascript
{
  accountNumber: String,
  apiKey: String,
  accountSource: String,
  apiPassword: String,
  excludeGstInRates: Boolean,
  allowPartialDelivery: Boolean,
  labelLayouts: {
    parcelPost: String,
    expressPost: String,
    starTrack: String,
    starTrackCourier: String,
    starTrackOnDemand: String,
    international: String       // Default: A4-1pp
  },
  reasonForExportDescription: String,
  displayOrderNoteForAuPost: Boolean,
  authorityToLeave: Boolean,
  showTaxAmountOnCheckout: Boolean,
  chargeAccounts: Array,
  selectedChargeAccount: String
}
```

### Regional Carriers (Examples)

**Delhivery** (India) (`carriers.js:263-269`):
```javascript
{
  clientName: String,
  apiKey: String,
  userName: String,
  ratesType: String,
  defaultDelhiveryWarehouse: String,
  includePhoneNumber: Boolean
}
```

**Blue Dart** (India) (`carriers.js:290-300`):
```javascript
{
  apiKey: String,
  shippingApiKey: String,
  trackingApiKey: String,
  originServiceAreaCode: String,
  originServiceCenterCode: String,
  autoPickup: Boolean,
  includeOrderDisplayId: Boolean,
  specialInstructions: String,
  displayOrderNoteForBluedart: Boolean,
  allowSplitShipmentsForNonMpsCarriers: Boolean
}
```

**PostNord** (Nordic) (`carriers.js:355-370`):
```javascript
{
  apiKey: String,
  partyIdType: String,
  partyId: String,
  swiftCode: String,
  bankName: String,
  packageTypeCode: String,
  itemIdType: String,
  enableaccountCodDetails: Boolean,
  EORIorPersonalIdNumber: String,
  categoryOfItemOptions: Array,
  postnordLabelType: String,
  postnordReturnLabelType: String,
  enableEmail: Boolean,
  displayOrderNoteForPostnord: Boolean,
  imageType: String             // PDF | ZPL
}
```

## Multi-Account Support

### Account Association

Each carrier configuration belongs to an account:
```javascript
{
  accountUUID: String,          // Owner account
  vendorUUID: String            // For multi-vendor scenarios
}
```

**Use cases**:
- Merchant has multiple carrier accounts (different billing)
- Multi-warehouse: Different FedEx accounts per location
- Multi-vendor: Different UPS accounts per vendor

### Active/Inactive Status

```javascript
{
  isActive: Boolean,            // Enabled for rate shopping & label generation
  status: String                // IN_USE | ARCHIVED
}
```

**Workflow**:
1. **Active** (`isActive: true, status: IN_USE`): Carrier appears in rate shopping
2. **Inactive** (`isActive: false`): Carrier hidden from rate shopping but not deleted
3. **Archived** (`status: ARCHIVED`): Carrier no longer in use, kept for historical records

## Configuration Workflow

### 1. Add New Carrier

**Frontend**: User navigates to Settings → Carriers → Add Carrier

**Backend Flow**:
1. User selects carrier type (FedEx, UPS, etc.)
2. Form loads with carrier-specific fields
3. User enters credentials (account number, API key, etc.)
4. **Credential Validation** (`validateCarrierCredentials()`):
   - Test API call to carrier
   - Verify authentication success
   - Detect production vs test mode
5. Save carrier configuration to DB
6. Set `isActive: true` to enable

### 2. Edit Carrier

**API**: `PUT /api/carriers/:carrierId`

**Editable Fields**:
- Credentials (if changed)
- Preferences (label size, invoice type)
- Operational settings (pickup time, buffer days)

**Non-editable**:
- `carrierType` (can't change FedEx to UPS)
- `carrierID` (immutable UUID)

### 3. Test Carrier Connection

**Method**: `POST /api/carriers/:carrierId/test`

**Purpose**: Verify credentials still valid

**Implementation**:
```javascript
const helper = getCarrierAdaptor(carrier.carrierType);
const testResult = await helper.validateCarrierCredentials(testData, carrier);

if (testResult.success) {
  return { message: 'Connection successful', productionKey: testResult.productionKey };
} else {
  return { error: testResult.message };
}
```

### 4. Deactivate Carrier

**API**: `PUT /api/carriers/:carrierId`

**Body**: `{ isActive: false }`

**Effect**: Carrier no longer shown in rate shopping, existing labels unaffected

### 5. Archive Carrier

**API**: `PUT /api/carriers/:carrierId`

**Body**: `{ status: 'ARCHIVED' }`

**Effect**: Carrier hidden from UI, historical data preserved

## Carrier Defaults

### Ship-From Address

Many carriers require a default ship-from address:
```javascript
{
  freightShipFromAddressUUID: String    // FedEx
  // Address referenced by UUID, not embedded
}
```

**Usage**: Auto-populate ship-from on orders if not specified

### Service Preferences

Carriers can have default service preferences:
```javascript
{
  defaultAddressClassificationForRates: 'COMMERCIAL',  // FedEx
  serviceType: 'CONTRACT',                             // Canada Post
  rateRequestType: 'LIST'                              // FedEx
}
```

## Production vs Test Mode

### Mode Detection

**Field**: `carrier.productionKey`

**Values**:
- `true` = Production mode (real charges, real labels)
- `false` = Test/sandbox mode (test labels, no charges)

**Auto-detection**: During credential validation, most carriers indicate mode in API response

### Switching Modes

To switch modes, merchant must:
1. Obtain production credentials from carrier
2. Update carrier configuration with production keys
3. Re-validate credentials
4. System auto-detects `productionKey: true`

## Buffer Time Configuration

### Transit Time Buffers

**Field**: `carrier.bufferDaysToTransitTime`

**Purpose**: Add extra days to carrier's transit time estimate

**Example**:
- Carrier says: "Delivery in 3 days"
- Buffer: 2 days
- Display to customer: "Delivery in 5 days"

**Use case**: Account for processing time, carrier delays, holidays

### Processing Time Buffer

**Field**: `carrier.bufferTime`

**Purpose**: Warehouse processing time before shipment

**Example**: Orders placed after 2pm ship next business day

## Label Customization

### Label Size

**Field**: `carrier.labelPrintSize`

**Values**:
- `"4x6"` - Thermal printer label (most common)
- `"8.5x11"` - Letter size (desktop printer)
- `"4x6.75"` - Alternative thermal size

**Carrier-specific** variations (e.g., FedEx `labelStockType`)

### Label Branding

**Custom Logos**:
```javascript
{
  companyLogo: {
    fileName: "logo.png",
    fileSize: 15000,
    fileType: "image/png",
    image: "base64encodeddata..."
  }
}
```

**Used by**: DHL, some regional carriers

**Custom Letterhead** (for invoices):
```javascript
{
  letterHead: {
    fileName: "letterhead.pdf",
    // ... similar structure
  },
  useLetterHead: true
}
```

## API Endpoints

**Location**: `server/src/routes/carriers.js` (not yet explored)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/carriers` | List all carriers for account |
| POST | `/api/carriers` | Add new carrier |
| GET | `/api/carriers/:id` | Get carrier details |
| PUT | `/api/carriers/:id` | Update carrier |
| DELETE | `/api/carriers/:id` | Delete carrier |
| POST | `/api/carriers/:id/test` | Test carrier connection |
| POST | `/api/carriers/:id/validate` | Validate credentials |

## Dependencies

- [Carrier System Overview](./carrier-system-overview.md) - Adaptor pattern
- [Rate Shopping](./rate-shopping.md) - How carriers are selected for rates
- [Label Generation](./label-generation.md) - Carrier credentials used for labels
- [Order Lifecycle](../orders/order-lifecycle.md) - Carrier selection in processing

## Referenced By

- Rate shopping queries carriers by `accountUUID` and `isActive: true`
- Label generation fetches carrier by `carrierID`
- Order model stores `carrierIdSelected` referencing carrier

## Configuration

**Account Settings**:
- Default carrier (if multiple of same type)
- Carrier priority order for rate display
- Auto-select cheapest carrier

**Feature Toggles**:
- Enable/disable specific carriers per account
- Rollout new carrier integrations gradually

## Common Patterns

### Query Active Carriers for Account

```javascript
const carriers = await Carriers.find({
  accountUUID: accountUUID,
  isActive: true,
  status: constants.IN_USE
});
```

### Get Carrier for Order

```javascript
const carrier = await Carriers.findOne({
  carrierID: order.carrierIdSelected
});
```

### Validate Credentials on Save

```javascript
// When creating/updating carrier
const helper = getCarrierAdaptor(carrier.carrierType);
const validation = await helper.validateCarrierCredentials(testData, carrier);

if (!validation.success) {
  throw new Error(`Invalid credentials: ${validation.message}`);
}

carrier.productionKey = validation.productionKey;
await carrier.save();
```

## Test Coverage

**Automated E2E Tests**: 3 Playwright tests covering UPS carrier configuration

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| UPS Label Image Type | `carrierOtherDetails/UPS/imageType.spec.ts` | ✅ Passing |
| UPS Pickup Service | `carrierOtherDetails/UPS/pickupService.spec.ts` | ✅ Passing |
| Reason for Export | `carrierOtherDetails/UPS/reasonForExport.spec.ts` | ✅ Passing |

**Test Coverage**: 3/45+ carrier configurations tested (UPS only)

**Tested Carriers**: UPS (C3, C38)

**Untested Carriers**: FedEx, DHL, USPS, Canada Post, and 40+ other carriers

**Test Suite Location**: `mcsl-test-automation/tests/carrierOtherDetails/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Known Issues / Tech Debt

1. **Schema bloat**: 487 lines with carrier-specific fields mixed together - consider carrier-type-specific sub-schemas
2. **No field validation**: Many fields have no enum validation or format checking
3. **Password storage**: Some passwords stored in plain text - should use encryption
4. **Deprecated fields**: Comments indicate fields to remove ("need to remove this in next release")
5. **Inconsistent naming**: Some fields use camelCase, others snake_case
6. **No versioning**: Schema changes could break existing carrier configs

## Related Pages

- [Carrier System Overview](./carrier-system-overview.md)
- [Carrier Integration](./carrier-integration.md)
- [Rate Shopping](./rate-shopping.md)
- [Label Generation](./label-generation.md)
- [Carrier Integrations](./carrier-integrations.md)
