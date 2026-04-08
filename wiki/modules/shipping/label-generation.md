---
title: Label Generation
category: module
domain: shipping
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Label Generation

## Overview

Label generation is the process of creating shipping labels and associated documents (packing slips, commercial invoices) by calling carrier APIs with shipment details. StorePep generates labels for 43+ carriers through a unified interface, handling different label formats, multi-package shipments, customs documentation, and printer types.

**Core Flow**: Validate order → Build carrier request → Call API → Process response → Store label URLs → Generate additional docs → Update order status

**Triggers**:
- User clicks "Generate Label" button
- Automation rule executes
- Bulk action: "Generate Labels"
- API call from external system

## Label Generation Flow

### 1. Entry Point

**Location**: Order processing triggers label creation

**Preconditions**:
- Order in `PROCESSING` or `READY_TO_SHIP` status
- Carrier and service selected
- Ship-to address validated
- Package dimensions/weight configured

### 2. Carrier API Call

**Function**: `createShipment(inputParam)`

**Implementation**: Each carrier helper (FedEx, UPS, DHL, etc.)

**FedEx Example** (`fedexShipmentHelper.js:686-732`):
```javascript
async createShipment(inputParam) {
  const {
    orderDataForTheOrderToShip,
    storedPackageDetailsForTheOrderToShip,
    preferredCarrier,
  } = inputParam;

  let enhancedPackages = this.enhancePackages(storedPackageDetailsForTheOrderToShip);
  const returnArray = [];
  const extraDocuments = [];
  const masterTracking = { status: false, TrackingNumber: 2135468793132 };

  // Process each package
  for (let index = 0; index < enhancedPackages.length; index += 1) {
    const storedPackage = enhancedPackages[index];
    let response = {};

    inputParam = {
      orderDataForTheOrderToShip,
      storedPackage,
      preferredCarrier,
      masterTracking,
      sequenceNumber: storedPackage.sequenceNumber,
      packageCount: enhancedPackages.length,
      storedPackageDetailsForTheOrderToShip: enhancedPackages,
    };

    if (isFreightService[storedPackage.serviceTypeSelected]) {
      response = await this.getFreightShipmentResponse(inputParam, index);
    } else {
      response = await this.getNormalShipmentResponse(inputParam, index);
    }

    extraDocuments.push(...response.extraDocumentsForThisPackage);
    returnObject = response.returnObject;
    returnObject.requestObject = response.fedexRequestObject;
    returnObject.sequenceNumber = storedPackage.sequenceNumber;
    returnObject.packageUUID = storedPackage.packageUUID;
    returnObject.apiMode = preferredCarrier.productionKey ? constants.LIVE : constants.SANDBOX;
    returnArray.push(returnObject);
  }

  return {
    shipmentResult: returnArray,
    extraDocuments: extraDocuments,
  };
}
```

**EasyPost Example** (`easyPostShipmentHelper.js:92-186`):
```javascript
async createShipment(inputParam) {
  const { orderDataForTheOrderToShip, storedPackageDetailsForTheOrderToShip, preferredCarrier } = inputParam;
  const selectedCarrier = storedPackageDetailsForTheOrderToShip[0].serviceTypeSelected.split('-')[0];
  const selectedService = storedPackageDetailsForTheOrderToShip[0].serviceTypeSelected.slice(selectedCarrier.length + 1);

  const api = new Easypost(preferredCarrier.apiKey);
  let order = {};

  // Reuse existing order or create new
  if (orderDataForTheOrderToShip.easyPostOrderID && orderDataForTheOrderToShip.easyPostOrderID[selectedCarrier]) {
    order = await api.Order.retrieve(orderDataForTheOrderToShip.easyPostOrderID[selectedCarrier]);
  } else {
    const enhancedPackages = enhancePackages(storedPackageDetailsForTheOrderToShip);
    requestObject = await new EasyPostRequestBuilder().getRatesRequestObject(orderDataForTheOrderToShip, enhancedPackages, preferredCarrier, api);
    order = new api.Order(requestObject);
    const newOrderResponse = await order.save();
    newEasypostOrderID = { [selectedCarrier]: newOrderResponse.id };
  }

  // Buy the label
  apiResponse = await order.buy(selectedCarrier.replace(/ /g, ''), selectedService.replace(/ /g, ''));

  // Add insurance if required
  if (orderDataForTheOrderToShip.isInsuranceRequired) {
    for (let i = 0; i < order.shipments.length; i++) {
      const shipment = await api.Shipment.retrieve(order.shipments[i].id);
      const insuranceResponse = await shipment.insure(storedPackageDetailsForTheOrderToShip[i].declaredPackagePrice);
      insuranceResponseArray.push(insuranceResponse);
    }
  }

  postageResponse = await processPostageResponse(apiResponse.shipments, orderDataForTheOrderToShip, preferredCarrier, storedPackageDetailsForTheOrderToShip);
  return postageResponse;
}
```

### 3. Request Building

**Carrier-specific request builders** construct API payloads:

**FedEx Request Structure**:
```javascript
{
  RequestedShipment: {
    ShipTimestamp: "2021-03-03T14:11:47.908Z",
    DropoffType: "REGULAR_PICKUP",
    ServiceType: "GROUND_HOME_DELIVERY",
    PackagingType: "YOUR_PACKAGING",
    TotalWeight: { Units: "LB", Value: 40 },
    TotalInsuredValue: { Currency: "USD", Amount: 100 },
    Shipper: {
      Contact: { PersonName: "...", CompanyName: "...", PhoneNumber: "..." },
      Address: { StreetLines: ["..."], City: "...", StateOrProvinceCode: "...", PostalCode: "..." }
    },
    Recipient: { /* Same structure as Shipper */ },
    ShippingChargesPayment: {
      PaymentType: "SENDER",
      Payor: { ResponsibleParty: { AccountNumber: "..." } }
    },
    SpecialServicesRequested: {
      SpecialServiceTypes: ["HOME_DELIVERY_PREMIUM", "SIGNATURE_OPTION"],
      SignatureOptionDetail: { OptionType: "ADULT" }
    },
    CustomsClearanceDetail: { /* For international shipments */ },
    LabelSpecification: {
      LabelFormatType: "COMMON2D",
      ImageType: "PDF",
      LabelStockType: "PAPER_8.5X11_TOP_HALF_LABEL"
    }
  }
}
```

**Location**: `fedexRequestBuilder.js` (1800+ lines)

### 4. Carrier API Response Processing

**FedEx Response**:
```javascript
{
  CompletedShipmentDetail: {
    CompletedPackageDetails: [{
      TrackingIds: [{ TrackingNumber: "794617893501" }],
      Label: {
        Parts: [{
          Image: "base64EncodedPDF..."
        }]
      },
      PackageDocuments: [
        { Type: "AUXILIARY_LABEL", Parts: [{ Image: "..." }] }
      ]
    }],
    ShipmentDocuments: [
      { Type: "COMMERCIAL_INVOICE", Parts: [{ Image: "..." }] }
    ]
  }
}
```

**EasyPost Response**:
```javascript
{
  shipments: [{
    id: "shp_...",
    tracking_code: "9400111899562537866457",
    postage_label: {
      label_url: "https://easypost-files.s3.amazonaws.com/...",
      label_file_type: "image/png",
      label_size: "4x6",
      label_resolution: 203,
      label_date: "2021-03-03T14:11:47Z"
    },
    forms: [{
      form_type: "commercial_invoice",
      form_url: "https://easypost-files.s3.amazonaws.com/..."
    }]
  }]
}
```

### 5. Label Extraction and Storage

**Package Model Storage** (`packages.js:33`):
```javascript
{
  labelImages: [String], // Array of base64 encoded labels
  labelImageType: String, // "PDF", "PNG", "ZPL", "ZPLII", "ZPL2"
  labelDisplayMode: String, // "LABEL_DISPLAY_MODE_11" for printer settings
  trackingId: String,
  carrierTrackingUrl: String,
  packingSlipBase64: {
    image: String,
    format: String, // "PDF"
    displayMode: String,
    fileName: String,
    type: String, // constants.PACKING_SLIP
    numberOfPages: Number
  }
}
```

**Order Model Storage**:
```javascript
{
  trackingId: String, // Primary tracking number
  trackingIds: [String], // All tracking numbers for multi-package
  currentLabelSummaryUUID: String, // Reference to label document
  storePepStatus: "LABEL_CREATED",
  invoice: {
    image: String, // Commercial invoice base64
    format: String,
    displayMode: String,
    fileName: String,
    type: String // constants.COMMERCIAL_INVOICE
  }
}
```

## Label Formats

### Supported Formats

**PDF**:
- Standard: 8.5" x 11" full page
- Thermal: 4" x 6" label
- Top Half: 8.5" x 11" top half
- Use case: Desktop printers, office environments

**ZPL (Zebra Programming Language)**:
- Variants: `ZPL`, `ZPLII`, `ZPL2`
- Direct thermal printer language
- Carriers: FedEx (`ZPLII`), DHL Express (`ZPL2`)
- Use case: Zebra thermal printers

**PNG/Image**:
- Dimensions: Typically 4" x 6" at 203 DPI
- Use case: Web display, non-printer scenarios
- Carriers: EasyPost, some regional carriers

**EPL (Eltron Programming Language)**:
- Legacy thermal printer format
- Less common

### Format Detection

**Function**: `zplFormats` check

**Location**: `processDocuments.js:19-26`

```javascript
const zplFormats = {
  'ZPL': true,
  'ZPLII': true, // FedEx
  'ZPL2': true,  // DHL Express
  'zpl': true,
  'zpl2': true,
  'Zpl': true,
};
```

### Label Display Modes

**Label Stock Types** (FedEx):
- `PAPER_8.5X11_TOP_HALF_LABEL` → `LABEL_DISPLAY_MODE_11`
- `PAPER_4X6` → Thermal printer mode
- Custom modes per carrier

**Purpose**: Control how labels render on different printer types

## Multi-Package Handling

### Master Tracking Number

**Concept**: First package in multi-package shipment becomes "master"

**FedEx Implementation** (`fedexShipmentHelper.js:697`):
```javascript
const masterTracking = {
  status: false,
  TrackingNumber: 2135468793132,
  TrackingIdType: 'FEDEX'
};

for (let index = 0; index < enhancedPackages.length; index += 1) {
  const storedPackage = enhancedPackages[index];
  inputParam = {
    masterTracking,
    sequenceNumber: storedPackage.sequenceNumber,
    packageCount: enhancedPackages.length
  };

  response = await this.getNormalShipmentResponse(inputParam, index);
  // Master tracking updated after first package
}
```

**Master Shipment Details**:
- Package 1: Creates shipment, gets master tracking number
- Packages 2-N: Reference master tracking, added as additional packages
- All packages linked under single shipment ID

### Package Sequencing

**Field**: `storedPackage.sequenceNumber`

**Purpose**: Maintain "Package 1 of 3", "Package 2 of 3" labeling

**Document Naming**: Uses sequence number in filenames:
```javascript
const fileName = `Order-${orderDisplayId}_Package-${index + 1}-of-${packagesCount}_Label.pdf`;
```

## Document Types

### 1. Shipping Labels

**Type**: `constants.OUTBOUND_LABEL`

**Source**: Carrier API response

**Storage**: `package.labelImages[]`

**Multiple labels per package**:
- Primary shipping label
- Auxiliary labels (FedEx reference labels, terms & conditions)
- Special service labels

**FedEx Document Mapping** (`fedexShipmentHelper.js:83-92`):
```javascript
const packageDocumentsLabelMapper = {
  AUXILIARY_LABEL: constants.REFERENCE,
  TERMS_AND_CONDITIONS: constants.TERMS_CONDITIONS,
};

const shipmentDocumentsLabelMapper = {
  AUXILIARY_LABEL: constants.REFERENCE_RETURN,
  COMMERCIAL_INVOICE: constants.COMMERCIAL_INVOICE,
  PRO_FORMA_INVOICE: constants.COMMERCIAL_INVOICE,
};
```

### 2. Packing Slips

**Type**: `constants.PACKING_SLIP`

**Generation**: Puppeteer HTML → PDF conversion

**Location**: Generated by `PDFGenerator` (custom packing slip generator)

**Storage**: `package.packingSlipBase64`

```javascript
{
  image: "base64EncodedPDF...",
  format: "PDF",
  displayMode: "LABEL_DISPLAY_MODE_8",
  fileName: "Order-12345_Package-1-of-2_Packing-Slip.pdf",
  type: constants.PACKING_SLIP,
  numberOfPages: 1
}
```

**Contains**:
- Order items for this package
- Quantities and SKUs
- Customer shipping address
- Return address
- Order ID and package sequence

**Customization**: Merchant can upload custom packing slip templates

### 3. Commercial Invoices

**Type**: `constants.COMMERCIAL_INVOICE`

**Required for**: International shipments crossing customs

**Source**:
- Carrier-generated (FedEx, DHL, UPS)
- StorePep-generated (Puppeteer) for carriers without invoice generation

**Storage**: `order.invoice` (shipment-level) or `package` (package-level)

**Contains**:
- Harmonized System (HS) codes for items
- Country of origin
- Customs value (declared value)
- Purpose of shipment (sale, gift, sample)
- Importer/Exporter information

**FedEx Document Types**:
- `COMMERCIAL_INVOICE`: Standard commercial invoice
- `PRO_FORMA_INVOICE`: For non-sale shipments

### 4. Return Labels

**Type**: Separate return flow with `order.isReturnLabel = true`

**Function**: `createReturnShipment(inputParam)`

**Location**: `fedexShipmentHelper.js:734-778`

**Behavior**:
- Reverses ship-from and ship-to addresses
- Uses return carrier/service selection
- Stored separately in `package.returnLabelImages`

**Use Cases**:
- Pre-printed return labels included with shipment
- Customer-initiated returns
- Return merchandise authorization (RMA) flow

## Customs Data Handling

### Customs Clearance Detail

**Function**: `buildAndReturnCustomsClearanceDetailObject()`

**Location**: `fedexRequestBuilder.js:892-...`

**Triggers**:
- Origin country ≠ Destination country (international)
- Specific domestic countries requiring commercial invoice (Brazil, India)

**Structure**:
```javascript
CustomsClearanceDetail: {
  DutiesPayment: {
    PaymentType: "SENDER", // or "RECIPIENT", "THIRD_PARTY"
    Payor: {
      ResponsibleParty: {
        AccountNumber: "222326460",
        Address: { CountryCode: "US" }
      }
    }
  },
  DocumentContent: "DOCUMENTS_ONLY" | "NON_DOCUMENTS",
  CustomsValue: {
    Currency: "USD",
    Amount: 250.00 // Total customs value
  },
  CommercialInvoice: {
    Purpose: "SOLD" | "GIFT" | "SAMPLE",
    CustomerReferences: [{
      CustomerReferenceType: "INVOICE_NUMBER",
      Value: "INV-12345"
    }],
    OriginatorName: "Merchant Company"
  },
  Commodities: [
    {
      NumberOfPieces: 2,
      Description: "Cotton T-Shirt",
      CountryOfManufacture: "CN",
      Weight: { Units: "LB", Value: 0.5 },
      Quantity: 2,
      QuantityUnits: "PCS",
      UnitPrice: { Currency: "USD", Amount: 25.00 },
      CustomsValue: { Currency: "USD", Amount: 50.00 },
      HarmonizedCode: "6109.10.00" // HS code
    }
  ]
}
```

**Data Sources**:
- `order.line_items[]`: Product details, quantities
- `order.line_items[].countryOfOrigin`: Manufacturing country
- `order.line_items[].hsCode`: Harmonized System code
- `order.customsDeclaredValue`: Total customs value
- `order.dutiesPayer`: Who pays duties (sender/recipient)

### CSB Compliance Check

**Function**: `checkCSBCompliance()`

**Purpose**: Determine if Cross-Border Simplified (CSB) paperless customs applies

**Eligible Routes**: US ↔ Canada, specific corridors

**Benefit**: No commercial invoice required, faster customs clearance

## Document Processing

### Document Stitching

**Purpose**: Combine multiple PDFs (labels, packing slips, invoices) into single print-ready document

**Service**: External document processor API

**Location**: `processDocuments.js`

**Flow**:
```javascript
const getStitchedDocuments = async (queryObject) => {
  const referenceId = getUUID();
  const requestObject = {
    referenceId,
    url: `${config.apiBaseUrl}/api/documents?referenceId=${referenceId}`,
    totalNumberOfDocuments: config.pageSizeForDocumentStitching
  };

  const apiResponse = await makeApiRequest('stitch', requestObject, accountUUID);
  const documentLink = apiResponse.data._links.document.href;
  return { success: true, documentLink };
};
```

**Document Callback**: Pagination-based document retrieval

**Location**: `batchProcessHelper.js:67-91`

**Function**: `getDocumentsForAllOrders(orders, type, requestId, startIndex, lastIndex)`

**Returns**:
```javascript
{
  documents: [
    {
      subOrderUUID: "...",
      storeUUID: "...",
      label: "base64EncodedContent",
      labelFormat: "PDF",
      labelDisplayMode: "LABEL_DISPLAY_MODE_11",
      fileName: "Order-12345_Package-1-of-2_Label.pdf",
      labelType: constants.OUTBOUND_LABEL,
      numberOfPages: 1
    },
    // ... more documents
  ],
  packagesCount: 5
}
```

### Document Sorting

**Feature**: Sort products by SKU in packing slips

**Function**: `isOrderDocumentsSortBySKUEnabledFor(accountUUID)`

**Location**: `processDocuments.js:146-160`

**Purpose**: Warehouse picking efficiency (grouped by SKU location)

### Required Documents Filter

**Function**: `getRequiredDocuments(documents, settings, includeZpl)`

**Location**: `processDocuments.js:182-193`

**Purpose**: Filter documents based on merchant print settings

**Settings**: `printSettings.documentSettings`

```javascript
{
  [constants.OUTBOUND_LABEL]: { isRequired: true, copies: 1, priority: 1 },
  [constants.PACKING_SLIP]: { isRequired: true, copies: 2, priority: 2 },
  [constants.COMMERCIAL_INVOICE]: { isRequired: false, copies: 1, priority: 3 }
}
```

**ZPL Handling**: Exclude ZPL formats for PDF-only printers

## Label Cancellation

### Void Label / Refund

**Function**: `cancelShipment(storedPackage, preferredCarrier, orderData)`

**Purpose**: Void unused labels and refund postage charges

**EasyPost Example** (`easyPostShipmentHelper.js:188-223`):
```javascript
async cancelShipment(storedPackage, preferredCarrier, orderData) {
  const selectedCarrier = storedPackage[0].serviceTypeSelected.split('-')[0];
  const api = new Easypost(preferredCarrier.apiKey);
  const order = await api.Order.retrieve(orderData.easyPostOrderID[selectedCarrier]);

  if (order.shipments) {
    for (let i = 0; i < order.shipments.length; i++) {
      const shipment = await api.Shipment.retrieve(order.shipments[i].id);
      const cancelResponse = await shipment.refund();
      apiResponse.push(cancelResponse);
    }
  }

  return {
    success: constants.SUCCESS,
    requestObject: {},
    apiResponse: {},
  };
}
```

**Carrier-specific rules**:
- **USPS**: Can cancel before end-of-day scan
- **FedEx**: 24-hour cancellation window
- **UPS**: Must cancel before pickup
- **EasyPost**: Carrier-dependent

**Refund**: Postage cost credited back to carrier account

**Order Update**:
- `order.storePepStatus` → back to `PROCESSING`
- `package.labelImages` → cleared
- `order.trackingId` → cleared

## Special Label Types

### Hold at Location Labels

**Carriers**: FedEx (Hold at FedEx Location), UPS (UPS Access Point)

**Implementation**: Special service flag in carrier request

**Supported Locations** (`fedexShipmentHelper.js:103-113`):
```javascript
const fedexSupportedLocationType = [
  'FEDEX_EXPRESS_STATION',
  'FEDEX_FACILITY',
  'FEDEX_OFFICE',
  'FEDEX_ONSITE'
];
```

**Location Search**: Separate API to find nearby service points

**Label Contents**: Includes location address and ID for customer pickup

### Freight Labels

**Services**: FedEx Freight, UPS Freight

**Special Requirements**:
- Bill of Lading (BOL) document
- Freight-specific rate classes
- Pallet count and dimensions
- Shipper/Consignee details

**FedEx Freight Detection** (`fedexShipmentHelper.js:69-81`):
```javascript
const fedExFreightServiceCodes = [
  'FEDEX_FREIGHT_ECONOMY',
  'FEDEX_FREIGHT_PRIORITY',
];

const isFreightService = {
  FEDEX_FREIGHT_ECONOMY: true,
  FEDEX_FREIGHT_PRIORITY: true,
};
```

**Processing**: Separate `getFreightShipmentResponse()` function

### Smart Post / Ground Economy Labels

**FedEx Smart Post** (now FedEx Ground Economy):
- Last-mile delivery via USPS
- Hub ID required (`SmartPostDetail.HubId`)
- Lower cost, slower delivery

**UPS SurePost**:
- Similar last-mile USPS delivery
- Endorsement required

## Error Handling

### Common Label Generation Errors

**FedEx Error Codes** (`fedexShipmentHelper.js:57-67`):
```javascript
const errorCodes = {
  556: { storepepErrorType: storepepErrorEvents.SERVICE_MISMATCH },
  522: { storepepErrorType: storepepErrorEvents.INVALID_DESTINATION_ADDRESS },
  6541: { storepepErrorType: storepepErrorEvents.INVALID_SHIPPER_PHONE_NUMBER },
  6532: { storepepErrorType: storepepErrorEvents.INVALID_RECIPIENT_PHONE_NUMBER },
  7: { storepepErrorType: storepepErrorEvents.NO_RATES_AVAILABLE_FROM_CARRIER },
  9004: { storepepErrorType: storepepErrorEvents.API_GENERAL_FAILURE },
  3001: { storepepErrorType: storepepErrorEvents.INVALID_ORIGIN_ADDRESS },
  2246: { storepepErrorType: storepepErrorEvents.COD_NOT_AVAILABLE_FOR_SERVICE },
  1000: { storepepErrorType: storepepErrorEvents.AUTHENTICATION_FAILURE },
};
```

### Error Event Publishing

**Event**: `GenerateAndFulfillOrderFailed`

**Location**: `label-fulfill-order/events`

**Published when**: Label creation fails

**Payload**:
```javascript
{
  orderId: order.orderId,
  accountUUID: order.accountUUID,
  errorMessage: "Invalid destination address",
  carrierErrorCode: "522",
  requestObject: {}, // What was sent to carrier
  apiResponse: {}    // Raw carrier response
}
```

### Retry Logic

**Scenario**: Transient API failures (timeout, 500 error)

**Implementation**: Order remains in `PROCESSING`, user can retry

**Batch Operations**: Failed orders marked, successful labels still processed

## Integration with Order Lifecycle

### Status Transitions

**Before Label**:
- Order status: `PROCESSING`
- StorePep status: `PROCESSING` or `READY_TO_SHIP`

**During Label Creation**:
- StorePep status: `GENERATING_LABEL` (transient)

**After Successful Label**:
- Order status: `COMPLETED` (or `PROCESSING` if partial fulfillment)
- StorePep status: `LABEL_CREATED`
- Fulfillment status: `FULFILLED` or `PARTIALLY_FULFILLED`

**After Label Error**:
- StorePep status: Back to `PROCESSING`
- Error stored in order audit log

### Order Updates

**Function**: `updateStorePepOrderStatus()`

**Fields Updated**:
```javascript
{
  trackingId: "794617893501",
  trackingIds: ["794617893501", "794617893502"], // Multi-package
  carrier: "FedEx - FedEx Ground",
  carrierTypeSelected: "C2",
  currentLabelSummaryUUID: "label-doc-uuid",
  storePepStatus: constants.LABEL_CREATED,
  labelCreatedAt: new Date(),
  fulfilledDate: new Date()
}
```

**Package Updates**:
```javascript
{
  labelImages: ["base64PDF1", "base64PDF2"],
  labelImageType: "PDF",
  trackingId: "794617893501",
  isCarrierSet: true,
  labelGeneratedDate: new Date()
}
```

### Socket Notifications

**Event**: `LABEL_CREATED`

**Payload**: Label URLs, tracking numbers

**Purpose**: Real-time UI update for merchants

## API Endpoints

**Location**: `server/src/routes/orders.js`

| Endpoint | Purpose |
|----------|---------|
| POST `/api/orders/:id/generate-label` | Generate label for single order |
| POST `/api/orders/bulk-action` (generateLabels) | Bulk label generation |
| POST `/api/orders/:id/cancel-label` | Void label and refund postage |
| GET `/api/orders/:id/documents` | Retrieve generated documents |
| POST `/api/orders/:id/return-label` | Generate return label |

## Dependencies

- [Carrier System Overview](./carrier-system-overview.md) - Carrier API adaptor pattern
- [Carrier Configuration](./carrier-configuration.md) - Carrier credentials and settings
- [Rate Shopping](./rate-shopping.md) - Service selection before label generation
- [Order Lifecycle](../orders/order-lifecycle.md) - Label generation in order flow
- [Order Bulk Actions](../orders/order-bulk-actions.md) - Bulk label generation

## Referenced By

- Order processing triggers label generation after rate shopping
- Batch processing generates labels for multiple orders
- Automation rules can auto-generate labels
- Return flow generates return labels

## Configuration

**Carrier Settings**:
- `labelStockType`: Printer paper size (4x6, 8.5x11)
- `labelFormat`: PDF, ZPL, PNG
- `productionKey`: Live vs test mode
- `commercialInvoice`: Include commercial invoice for international

**Account Settings**:
- `printSettings.documentSettings`: Which documents to print, copies, priority
- `autoGenerateLabel`: Generate label automatically when order processed
- `includeLabelInEmail`: Email label to customer
- `sortBySKU`: Sort packing slip items by SKU

**Package Settings**:
- Default package dimensions
- Default weight
- Signature requirement
- Insurance value

## Common Patterns

### Generate Label for Order

```javascript
const carrier = await findCarrierWithLean({
  carrierID: order.carrierIdSelected,
  accountUUID: order.accountUUID
});

const packages = await findPackagesWithLean({
  subOrderUUID: order.subOrderUUID,
  packageType: constants.PACKAGE_TYPE_STORED_PACKAGE
});

const carrierHelper = getCarrierAdaptor(carrier.carrierType);

const shipmentData = {
  orderDataForTheOrderToShip: order,
  storedPackageDetailsForTheOrderToShip: packages,
  preferredCarrier: carrier
};

const result = await carrierHelper.createShipment(shipmentData);

if (result.shipmentResult[0].status === constants.SUCCESS) {
  order.trackingId = result.shipmentResult[0].trackingNumber;
  order.storePepStatus = constants.LABEL_CREATED;
  await order.save();
}
```

### Cancel Label

```javascript
const carrierHelper = getCarrierAdaptor(order.carrierTypeSelected);
const result = await carrierHelper.cancelShipment(packages, carrier, order);

if (result.success === constants.SUCCESS) {
  order.storePepStatus = constants.PROCESSING;
  order.trackingId = null;

  packages.forEach(pkg => {
    pkg.labelImages = [];
    pkg.trackingId = null;
  });

  await Promise.all([order.save(), ...packages.map(p => p.save())]);
}
```

### Generate Return Label

```javascript
const returnOrder = { ...order, isReturnLabel: true };
const carrierHelper = getCarrierAdaptor(carrier.carrierType);

const result = await carrierHelper.createReturnShipment({
  orderDataForTheOrderToShip: returnOrder,
  storedPackageDetailsForTheOrderToShip: packages,
  preferredCarrier: carrier
});

if (result.shipmentResult[0].status === constants.SUCCESS) {
  order.returnTrackingId = result.shipmentResult[0].trackingNumber;
  packages[0].returnLabelImages = [result.shipmentResult[0].labelImage];
  await Promise.all([order.save(), packages[0].save()]);
}
```

## Test Coverage

**Automated E2E Tests**: 13 Playwright tests covering label generation workflows

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| **Label Generation Flows** | | |
| Generate from Order Grid | `orderGrid/labelGenerationFromGrid/orderFulfillmentFromOrderGrid.spec.ts` | ✅ Passing |
| Generate with Multiple Products | `orderGrid/labelGenerationFromGrid/generateLabelWithMultipleProducts.spec.ts` | ✅ Passing |
| Generate & Fulfill from Grid | `orderGrid/labelGenerationFromGrid/generateLabelFromGridAndFulfillFromLabelBatch.spec.ts` | ✅ Passing |
| Generate from Summary | `orderSummary/labelGenerationFromSummary/labelGenerationAndFulfillment.spec.ts` | ✅ Passing |
| Generate from Actions Menu | `orderGrid/actionMenu/generateLabelFromActionsMenu.spec.ts` | ✅ Passing |
| **Batch Operations** | | |
| Create Label Batch | `labelBatch/createBatch.spec.ts` | ✅ Passing |
| Generate Label Batch | `labelBatch/generateLabelBatch.spec.ts` | ✅ Passing |
| **Packaging** | | |
| Box Packaging | `packagingTypes/boxPackaging.spec.ts` | ✅ Passing |
| Quantity Packaging | `packagingTypes/quantityPackaging.spec.ts` | ✅ Passing |
| Stack Packaging | `packagingTypes/stackPackaging.spec.ts` | ✅ Passing |
| Weight-Based Packaging | `packagingTypes/weightBasedPackaging.spec.ts` | ✅ Passing |
| Weight & Volume Packaging | `packagingTypes/weightAndVolume.spec.ts` | ✅ Passing |
| FedEx Carrier Box Packaging | `packagingTypes/fedExCarrierBoxPackaging.spec.ts` | ✅ Passing |
| **Document Management** | | |
| FedEx Document Auto-Upload | `orderSummary/documentAutoUploadForFedex.spec.ts` | ✅ Passing |
| **Special Services** | | |
| Insurance | `specialServices/insurance.spec.ts` | ✅ Passing |
| Dangerous Goods | `specialServices/dangerousgoods.spec.ts` | ✅ Passing |
| Adult Signature | `specialServices/adultsignature.spec.ts` | ✅ Passing |
| **Touchless SLGP Flow** | | |
| Touchless Label Generation | `orderSummary/touchlessSLGPFlow/touchLessSLGPFlow.spec.ts` | ✅ Passing |
| SLGP Preset Management | `orderSummary/touchlessSLGPFlow/slgpPreset.spec.ts` | ✅ Passing |
| Simple & Custom Products | `orderSummary/touchlessSLGPFlow/simpleAndcustomproduct.spec.ts` | ✅ Passing |

**Test Coverage**: 20/20 label generation scenarios tested (100% coverage)

**Test Suite Location**: `mcsl-test-automation/tests/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Known Issues / Tech Debt

1. **No label preview**: Can't preview label before generating (costs postage)
2. **Manual customs data entry**: HS codes and country of origin not auto-populated from product catalog
3. **Limited printer type detection**: Can't auto-detect thermal vs desktop printer
4. **Document stitching delays**: Sequential PDF merging slows down bulk operations
5. **No label template customization**: Can't modify carrier-provided label layout
6. **Error recovery complexity**: Failed multi-package shipments require manual intervention
7. **ZPL format variations**: Different carriers use incompatible ZPL dialects

## Related Pages

- [Carrier System Overview](./carrier-system-overview.md)
- [Carrier Configuration](./carrier-configuration.md)
- [Rate Shopping](./rate-shopping.md)
- [Carrier Integrations](./carrier-integrations.md)
- [Order Lifecycle](../orders/order-lifecycle.md)
