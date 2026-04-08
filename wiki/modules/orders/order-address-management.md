---
title: Order Address Management
category: module
domain: orders
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Order Address Management

## Overview

Address management in StorePep handles validation, correction, and storage of multiple address types per order. Addresses are critical for shipping - incorrect addresses lead to failed deliveries, return-to-sender, and additional carrier fees. StorePep validates addresses via carrier APIs and stores correction suggestions for user review.

**Key Features**:
- Multiple address types per order (shipping, billing, ship-from, return, etc.)
- Address validation via carrier APIs (FedEx, UPS, USPS)
- Correction suggestions with source tracking
- Auto-correction with user confirmation
- Residential vs. commercial classification
- Geocoding (latitude/longitude) support

## Address Types

### 1. Shipping Address

**Field**: `order.shipping`

**Purpose**: Customer delivery address (where package goes TO)

**Structure** (`models/orders.js:86-107`):
```javascript
{
  first_name: String,
  last_name: String,
  company: String,
  address_1: String,      // Primary address line
  address_2: String,      // Apartment, suite, etc.
  address_3: String,      // Additional line (rare)
  city: String,
  suburb: String,         // Used in some countries
  state: String,          // State/province code
  postcode: String,
  postcodeExtra: String,  // ZIP+4 extension (US)
  email: String,
  country: String,        // ISO country code
  phone: String,
  isResidential: Boolean, // true = home, false = business
  correctionType: String, // "VALIDATED" | "CORRECTED" | "FAILED"
  correctionSource: String, // "FEDEX" | "UPS" | "USPS" | "MANUAL"
  taxId: String,          // Tax ID for international
  latitude: Number,       // Geocode (if available)
  longitude: Number       // Geocode (if available)
}
```

### 2. Corrected Shipping Addresses

**Fields**:
- `order.correctedShipping` (deprecated, to be removed)
- `order.correctedShippingAddresses[]` (current, supports multiple suggestions)

**Purpose**: Store address validation results from carrier APIs

**Why Array**: Some carriers return multiple valid suggestions (e.g., "123 Main St" vs. "123 Main Street")

### 3. Billing Address

**Field**: `order.billing`

**Purpose**: Customer billing address (often same as shipping)

**Structure**: Same as shipping address

**Usage**:
- Payment processing
- Fraud prevention
- Tax calculation (billing state determines tax in some jurisdictions)

### 4. Ship-From Address

**Field**: `order.shipFromAddress`

**Purpose**: Warehouse/origin address (where package ships FROM)

**Structure** (`models/orders.js:149-180`):
```javascript
{
  addressName: String,     // "Main Warehouse", "LA Fulfillment Center"
  addressUUID: String,     // Reference to saved address
  personName: String,
  companyName: String,
  phoneNumber: String,
  addressLine1: String,
  addressLine2: String,
  addressLine3: String,
  city: String,
  suburb: String,
  stateCode: String,
  postalCode: String,
  email: String,
  country: String,
  regionCode: String,
  currency: String,
  isResidential: Boolean,
  signature: {             // Digital signature for customs
    fileName, fileSize, fileType, image
  },
  taxId: String,
  delhiveryLocationName: String,  // India-specific
  postingLocation: String,         // India Post
  siteCode: String,                // Carrier-specific
  taxIdType: String
}
```

### 5. Display From Address

**Field**: `order.displayFromAddress`

**Purpose**: Return address shown on label (may differ from ship-from for branding)

**Example**: Ship from warehouse A, but show corporate HQ as return address

### 6. International Shipping Addresses

For cross-border shipments:

**Sold-To Address** (`order.soldToAddress`):
- **Purpose**: Buyer's address for customs (may differ from shipping for gifts)

**Shipment Charge Payer Address** (`order.shipmentChargePayerAddress`):
- **Purpose**: Address of party paying shipping costs (if third-party)

**Duties Payer Address** (`order.dutiesPayerAddress`):
- **Purpose**: Address of party paying import duties/taxes

### 7. Return Shipping Addresses

**Fields**:
- `order.returnShipping` - Where returns go TO (merchant warehouse)
- `order.returnShipFromAddress` - Where returns ship FROM (customer)

**See**: [Order Returns](./order-returns.md) for details

## Address Validation System

### Validation Flow

1. **Trigger**: Order transitions to `PROCESSING` or user clicks "Validate Address"
2. **Adapter Selection**: Choose carrier validation API (FedEx, UPS, USPS)
3. **API Call**: Send shipping address to carrier
4. **Response Processing**:
   - **Valid**: Address confirmed, mark as validated
   - **Corrected**: Carrier suggests changes, store in `correctedShippingAddresses[]`
   - **Invalid**: Address undeliverable, flag for manual review
5. **User Review**: If corrections suggested, show to user for approval
6. **Apply Changes**: User selects corrected address or manually edits

### Address Correction Engine

**Location**: `server/src/shared/storepepAddressCorrector/addressCorrectionEngine.js`

**Function**: `addressCorrectionForOrders(orders, options)`

**Process**:
```javascript
for (const order of orders) {
  if (!order.shipping) continue;

  // Call carrier validation API
  const validationResult = await carrierAdapter.validateAddress(order.shipping);

  if (validationResult.corrected) {
    // Store corrected addresses
    order.correctedShippingAddresses.push({
      ...validationResult.correctedAddress,
      correctionType: 'CORRECTED',
      correctionSource: validationResult.carrier  // 'FEDEX', 'UPS', etc.
    });

    // Flag for user review
    order.isShippingAddressCorrectionRequired = true;
  } else if (validationResult.valid) {
    // Mark as validated
    order.shipping.correctionType = 'VALIDATED';
    order.shipping.correctionSource = validationResult.carrier;
  } else {
    // Failed validation
    order.shipping.correctionType = 'FAILED';
    order.isShippingAddressCorrectionRequired = true;
  }

  await order.save();
}
```

### Address Validation Adaptor

**Location**: `server/src/shared/addressValidationAdapter.js`

**Purpose**: Abstract carrier-specific validation APIs

**Supported Carriers**:
- FedEx Address Validation
- UPS Address Validation
- USPS Address Verification

**Adaptor Pattern**:
```javascript
class AddressValidationAdapter {
  async validateAddress(address, carrier = 'FEDEX') {
    const adaptor = this.getAdaptor(carrier);
    return await adaptor.validate(address);
  }

  getAdaptor(carrier) {
    switch (carrier) {
      case 'FEDEX': return new FedexAddressValidator();
      case 'UPS': return new UpsAddressValidator();
      case 'USPS': return new UspsAddressValidator();
      default: throw new Error(`Unsupported carrier: ${carrier}`);
    }
  }
}
```

### Address Correction Adaptor

**Location**: `server/src/shared/storepepAdaptors/addressCorrectionAdaptor.js`

**Purpose**: Wrapper for address correction engine with account-level settings

**Features**:
- Account-specific carrier preferences for validation
- Auto-correction rules (e.g., always accept first suggestion)
- Validation caching (avoid re-validating same address)

## Address Helper Functions

**Location**: `server/src/shared/storepepHelperFunctions/addressHelperFuctions.js`

### updateOrderAddress

**Function**: `updateOrderAddress(order, addressType, newAddress)`

**Purpose**: Update address on order with validation

**Parameters**:
- `order` - Order document
- `addressType` - 'shipping' | 'billing' | 'shipFromAddress' | etc.
- `newAddress` - New address object

**Flow**:
1. Validate address format
2. Call address validation API (optional)
3. Update order field
4. Clear `correctedShippingAddresses` if shipping address changed
5. Reset `isShippingAddressCorrectionRequired` flag

### confirmAddressChanges

**Function**: `confirmAddressChanges(order, selectedCorrectionIndex)`

**Purpose**: Apply user-selected corrected address

**Flow**:
1. Retrieve selected suggestion from `correctedShippingAddresses[index]`
2. Copy to `order.shipping`
3. Clear `correctedShippingAddresses` array
4. Set `isShippingAddressCorrectionRequired = false`
5. Mark `correctionType = 'CORRECTED'`

## Bulk Address Validation

**Function**: `validateShippingAddressesBulkAction`

**Location**: `server/src/shared/orders/bulkactionHelper.js`

**Purpose**: Validate multiple orders' addresses at once

**Flow**:
```javascript
await validateShippingAddressesBulkAction(orders, currentUser, accountUUID, newSocketEvent);

// For each order:
// 1. Validate via addressCorrectionForOrders()
// 2. Store results in correctedShippingAddresses[]
// 3. Socket emit with validation status per order
// 4. Return summary (X validated, Y corrected, Z failed)
```

**See**: [Order Bulk Actions](./order-bulk-actions.md) for details

## Residential vs. Commercial Detection

**Field**: `order.shipping.isResidential`

**Importance**: Carriers charge different rates for residential vs. commercial delivery

**Detection Methods**:
1. **User input**: Checkbox on order form
2. **Address validation API**: FedEx/UPS return residential indicator
3. **Heuristics**: Presence of company name suggests commercial
4. **Manual override**: User can change after validation

**Impact on Rates**:
- Residential surcharge ($3-5 per package)
- Different service availability (Saturday delivery, etc.)

## Address Classification

**Field**: `order.addressClassification`

**Values**:
- `UNKNOWN` (default)
- `RESIDENTIAL`
- `COMMERCIAL`
- `PO_BOX`
- `MILITARY`

**Uses**:
- Carrier restriction enforcement (some services don't deliver to PO boxes)
- Rate calculation
- Service selection

## Geocoding

**Fields**: `order.shipping.latitude`, `order.shipping.longitude`

**Source**:
- Carrier address validation APIs may return geocodes
- Google Maps API integration (if configured)
- Manual entry

**Uses**:
- Delivery route optimization
- Service area validation
- Pickup location search (hold at location)

## Auto-Correction Settings

**Account-Level Configuration**:

**Enable Auto-Correction**:
- **Field**: `order.isAutoAddressCorrectionEnable`
- **Behavior**: Automatically apply first correction suggestion without user review

**Validation Trigger**:
- On order import
- On status change to PROCESSING
- Manual bulk validation

**Carrier Preference**:
- Primary: FedEx (most comprehensive in US)
- Fallback: UPS
- US-specific: USPS (most accurate for US domestic)

## Correction Type Tracking

**Field**: `order.shipping.correctionType`

**Values**:
- `undefined` - Not yet validated
- `VALIDATED` - Confirmed as-is by carrier
- `CORRECTED` - User selected carrier suggestion
- `FAILED` - Invalid address, undeliverable
- `MANUAL` - User manually edited after validation

**Purpose**: Audit trail for address changes

## Correction Source Tracking

**Field**: `order.shipping.correctionSource`

**Values**:
- `FEDEX` - Validated via FedEx API
- `UPS` - Validated via UPS API
- `USPS` - Validated via USPS API
- `MANUAL` - User manually edited
- `STORE` - Original address from e-commerce platform

**Purpose**: Know which carrier validated the address

## Frontend Address Management

### Address Display

**Components**: (to be explored)
- Address card component (read-only display)
- Address editor (form with fields)
- Address validation modal (show corrections)

### Address Validation Modal

**Flow**:
1. User clicks "Validate Address" or automatic on processing
2. Backend validates, returns suggestions
3. Modal shows:
   - Original address
   - Suggested corrections (multiple if available)
   - "Use This" button per suggestion
   - "Edit Manually" option
4. User selects or edits
5. Address updated, modal closes

### Address Correction Badge

**UI Indicator**: Orders with `isShippingAddressCorrectionRequired: true` show warning badge

**Action**: Click badge to open validation modal

## API Endpoints

**Location**: `server/src/routes/orders.js`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/orders/:id/address/validate` | Validate single order address |
| POST | `/api/orders/bulk-action` (validate) | Validate multiple orders |
| PUT | `/api/orders/:id/address/shipping` | Update shipping address |
| PUT | `/api/orders/:id/address/confirm-correction` | Apply selected correction |
| GET | `/api/orders/:id/address/suggestions` | Get correction suggestions |

## Address Validation Errors

### Common Issues

1. **Invalid ZIP Code**: Incorrect or non-existent postal code
2. **Ambiguous Address**: Multiple valid interpretations
3. **PO Box Restriction**: Carrier doesn't deliver to PO boxes
4. **Incomplete Address**: Missing required fields (city, state)
5. **Unrecognized Street**: Street name not in carrier database

### Error Handling

```javascript
if (validationResult.error) {
  switch (validationResult.errorCode) {
    case 'INVALID_ZIP':
      // Suggest nearby ZIP codes
      break;
    case 'PO_BOX_RESTRICTED':
      // Notify user, suggest alternative carrier
      break;
    case 'INCOMPLETE':
      // Highlight missing fields
      break;
    default:
      // Manual review required
  }
}
```

## Dependencies

- [Order Lifecycle](./order-lifecycle.md) - Address validation during processing
- [Order Bulk Actions](./order-bulk-actions.md) - Bulk address validation
- [Carrier Integration](../shipping/carrier-integration.md) (to be created)
- [Order Returns](./order-returns.md) - Return address handling

## Referenced By

- Order processing flow validates addresses
- Label generation requires valid addresses
- Rate shopping uses address for calculation

## Configuration

**Account Settings**:
- Primary validation carrier (FedEx, UPS, USPS)
- Auto-correction enabled/disabled
- Validation triggers (on import, on processing, manual)
- Residential detection method

**Feature Toggles**:
- Address validation enabled
- Geocoding enabled
- Multi-suggestion support

## Common Patterns

### Validate Address on Processing

```javascript
// User clicks "Process Orders"
dispatch(changeOrderStatusToProcessingBulkAction(orderIds));

// Backend flow
for (const order of orders) {
  // ... other processing steps ...

  // Validate address
  if (accountSettings.addressValidationEnabled) {
    await addressCorrectionForOrders([order]);

    if (order.isShippingAddressCorrectionRequired) {
      // Socket notification: address needs review
      socket.emit('address:validation-required', {
        orderId: order._id,
        suggestions: order.correctedShippingAddresses
      });
    }
  }
}
```

### Apply Corrected Address

```javascript
// Frontend: User selects suggestion in modal
dispatch(confirmAddressCorrection(orderId, suggestionIndex));

// Backend
const order = await Order.findById(orderId);
const selectedAddress = order.correctedShippingAddresses[suggestionIndex];

await confirmAddressChanges(order, suggestionIndex);

// order.shipping now = selected suggestion
// order.isShippingAddressCorrectionRequired = false
```

## Known Issues / Tech Debt

1. **Deprecated field**: `correctedShipping` marked for removal, migration to `correctedShippingAddresses[]` incomplete
2. **Geocoding integration**: Latitude/longitude fields exist but not consistently populated
3. **Address caching**: No caching layer for validation results - same address validated multiple times
4. **Multi-language addresses**: Limited support for non-Latin character addresses
5. **Address classification**: `addressClassification` field underutilized
6. **PO Box detection**: Relies on carrier API, could benefit from client-side regex check

## Related Pages

- [Order Lifecycle](./order-lifecycle.md)
- [Order Bulk Actions](./order-bulk-actions.md)
- [Order Returns](./order-returns.md)
- [Carrier Integration](../shipping/carrier-integration.md) (to be created)
- [API Conventions](../../patterns/api-conventions.md) (to be created)
