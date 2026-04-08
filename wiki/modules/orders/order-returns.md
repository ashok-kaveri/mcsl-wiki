---
title: Order Returns Management
category: module
domain: orders
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Order Returns Management

## Overview

StorePep supports full return label generation and tracking for customer returns. Merchants can generate return shipping labels that customers use to send products back, with separate tracking and batch management from outbound shipments.

**Key Concept**: Returns are tracked separately but linked to original orders. Each order can have its own return flow with distinct carrier selection, packaging, and tracking.

## Return vs. Outbound Shipment

| Aspect | Outbound Shipment | Return Shipment |
|--------|-------------------|-----------------|
| **Status Field** | `storePepStatus` | `returnBatchStatus` |
| **Carrier Fields** | `carrierIdSelected`, `serviceIdSelected` | `returnCarrierIdSelected`, `returnServiceIdSelected` |
| **Address** | `shipping` → `shipFromAddress` | `shipFromAddress` → `returnShipping` |
| **Packages** | Stored in `packages` collection | Return packages in Redux state |
| **Label Summary** | `currentLabelSummaryUUID` | `returnLabel[]` |
| **Tracking** | `trackingId`, `trackingNumbers[]` | `returnPackingSummary[]` |

## Data Model

**Location**: `server/src/models/orders.js:281-441`

### Return-Specific Fields

```javascript
{
  // Return carrier selection
  returnCarrierTypeSelected: String,
  returnCarrierIdSelected: String,
  returnServiceIdSelected: String,

  // Return shipping address (where return goes TO)
  returnShipping: {
    first_name, last_name, company,
    address_1, address_2, city, state, postcode,
    country, phone, email,
    isResidential: Boolean,
    signature: { fileName, fileSize, fileType, image },
    taxId, taxType
  },

  // Return ship-from address (customer's address)
  returnShipFromAddress: {
    addressName, addressUUID, personName, companyName,
    phoneNumber, addressLine1, addressLine2, addressLine3,
    city, stateCode, postalCode, email, country,
    regionCode, currency, isResidential
  },

  // Return batch tracking
  returnBatchStatus: String,  // FREE | BATCHED | PROCESSING | COMPLETED

  // Return summaries
  returnPackingSummary: Array,      // Package configurations
  returnAutomationSummary: Array,   // Automation applied to return
  returnLabel: Array,                // Return label documents

  // Return-specific documents
  returnLabelExtraDocuments: Array
}
```

## Return Lifecycle

### 1. Initiate Return

**Trigger**: User clicks "Create Return Label" for an order

**Prerequisites**:
- Original order exists (with or without outbound label)
- Return shipping address configured (usually merchant's warehouse)
- Return carrier selected or auto-selected

**API**: `POST /api/orders/:id/return/initiate`

### 2. Return Processing

**Frontend Flow** (`client/src/reducers/orders.js:28-93`):

**Redux Actions**:
1. `ADD_RETURN_PACKAGES` - Initialize return package state
2. `PROCESS_RETURN_LABEL` - Start return label generation
3. `UPDATE_RETURN_PACKAGES_GENERATED` - Packages calculated
4. `UPDATE_STORED_RETURN_PACKAGES_CREATE_SHIPMENT` - Label created
5. `DELETE_RETURNPACKAGE` - Cancel return

**Redux State Shape**:
```javascript
{
  returnPackages: [
    {
      id: orderId,                    // Order ID
      processShipment: Boolean,       // Return processing active
      shipmentId: String,             // Shipment ID from carrier
      returnPackagesGenerated: Boolean,
      returnPackages: [],             // Package details
      labelGenerated: Boolean,
      labelImagePdf: String,          // Label PDF URL
      productDetails: Object          // Items being returned
    }
  ]
}
```

### 3. Generate Return Label

**Backend Flow**:
1. **Select carrier** - Use `returnCarrierIdSelected` or auto-select
2. **Configure addresses**:
   - **From**: Customer address (`returnShipFromAddress`)
   - **To**: Merchant warehouse (`returnShipping`)
3. **Calculate packages** - Based on items being returned
4. **Call carrier API** - Generate return label
5. **Store label** - Add to `returnLabel[]` array
6. **Update status** - `returnBatchStatus` if batching enabled

### 4. Return Tracking

Once label generated:
- Tracking number added to `returnPackingSummary`
- Customer receives label (email or downloadable)
- Carrier tracking polled for return package status
- Merchant notified when return received

## Partial Returns

**Scenario**: Customer returns only some items from an order

**Implementation**:
1. User selects specific line items to return
2. System calculates return package weight/dimensions
3. Separate return label generated for returned items
4. Original order updated:
   - `line_items[].totalReturnedQuantity` incremented
   - `line_items[].currentReturnQuantity` set for this return
5. Refund/credit processing (if integrated with payment system)

**Line Item Return Tracking** (`models/orders.js:352-353`):
```javascript
line_items: [{
  totalReturnedQuantity: Number,   // Total returned across all returns
  currentReturnQuantity: Number    // Quantity in current return shipment
}]
```

## Return Address Configuration

### Default Return Address

**Typically**: Same as merchant's ship-from address (warehouse)

**Set via**:
- Account settings: Default return address for all orders
- Per-order override: Different return destination
- Store-specific: Multi-warehouse scenarios

### Return Ship-From Address

**Source**: Customer's original shipping address copied to `returnShipFromAddress`

**Can differ** if customer moved or prefers different pickup location

## Return Carriers

### Carrier Selection

**Options**:
1. **Same carrier as outbound** - Simplest for merchant
2. **Different carrier** - Cost optimization or carrier preference
3. **Prepaid return label** - Merchant pays upfront
4. **Collect return label** - Charged to customer

### Carrier-Specific Return Features

**FedEx**:
- FedEx Ground Return Service
- Electronic Return Label (email to customer)
- QR code returns (no printer needed)

**UPS**:
- UPS Return Service
- Print Return Label
- Electronic Return Label

**USPS**:
- USPS Returns (formerly Merchandise Return Service)
- Click-N-Ship returns

**Canada Post**:
- Return Service

## Return Batching

**Field**: `order.returnBatchStatus`

**Values**:
- `FREE` - Not in return batch
- `BATCHED` - Added to return batch
- `PROCESSING` - Return batch processing
- `COMPLETED` - Return batch complete

**Use case**: Process multiple returns together for pickup or dropoff

**Separate from outbound batches**: Returns batched independently

## Redux Return Package Management

**Location**: `client/src/reducers/orders.js:28-93`

### Return Package Reducer

Manages per-order return package state:

**ADD_RETURN_PACKAGES**:
```javascript
// Initialize return packages for all selected orders
dispatch({
  type: ADD_RETURN_PACKAGES,
  payload: returnPackages
});
```

**PROCESS_RETURN_LABEL**:
```javascript
// Mark order as processing return
dispatch({
  type: PROCESS_RETURN_LABEL,
  payload: {
    orderId: order._id,
    displayReturnshipment: true
  }
});
```

**UPDATE_RETURN_PACKAGES_GENERATED**:
```javascript
// Store generated packages
dispatch({
  type: UPDATE_RETURN_PACKAGES_GENERATED,
  payload: {
    orderId: order._id,
    packageGenerated: true,
    packages: calculatedPackages
  }
});
```

**UPDATE_STORED_RETURN_PACKAGES_CREATE_SHIPMENT**:
```javascript
// Label created successfully
dispatch({
  type: UPDATE_STORED_RETURN_PACKAGES_CREATE_SHIPMENT,
  payload: {
    orderId: order._id,
    shipmentId: shipment.id,
    labelGenerated: true,
    labelImagePdf: label.pdfUrl
  }
});
```

**DELETE_RETURNPACKAGE**:
```javascript
// Cancel return for order
dispatch({
  type: DELETE_RETURNPACKAGE,
  payload: { id: order._id }
});

// Implementation uses lodash.remove
state.returnPackages = remove(
  state.returnPackages,
  data => data.id !== action.payload.id
);
```

## Return Label Documents

### Label Types

1. **Return Shipping Label** - Primary label for package
2. **Return Packing Slip** - Items being returned
3. **Return Authorization** - RMA number, return instructions
4. **Commercial Invoice** - For international returns

**Storage**: `order.returnLabel[]`, `order.returnLabelExtraDocuments[]`

### Label Delivery

**Methods**:
- Download from StorePep UI
- Email to customer automatically
- Print by merchant (include with outbound shipment)
- QR code (customer scans at carrier location)

## Return Summaries

### Return Packing Summary

**Field**: `order.returnPackingSummary[]`

Tracks package details for return:
```javascript
{
  packageId: "uuid",
  weight: "2.5",
  dimensions: { length, width, height },
  trackingNumber: "1Z...",
  carrier: "UPS",
  service: "Ground"
}
```

### Return Automation Summary

**Field**: `order.returnAutomationSummary[]`

Automation rules applied to return processing (if any):
```javascript
{
  ruleId: "uuid",
  ruleName: "Auto-select UPS for returns",
  appliedAt: Date,
  actions: ["SELECT_CARRIER", "GENERATE_LABEL"]
}
```

## Integration with Order Status

### Order Status After Return

**Options**:
1. **No change** - Return tracked separately, order status unchanged
2. **Mark as returned** - Update `storePepStatus` to `RETURNED` (custom status)
3. **Sync to store** - Update e-commerce platform (WooCommerce "Refunded", Shopify "Returned")

**Common pattern**: Order remains `SHIPPED`, return tracked via `returnBatchStatus`

## API Endpoints

**Location**: `server/src/routes/orders.js`

### Return-Specific Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/orders/:id/return/initiate` | Start return process |
| POST | `/api/orders/:id/return/packages` | Calculate return packages |
| POST | `/api/orders/:id/return/label` | Generate return label |
| GET | `/api/orders/:id/return/status` | Get return tracking status |
| DELETE | `/api/orders/:id/return` | Cancel return |

## Frontend Components

**Location**: `client/src/components/pages/` (to be explored)

**Key Components**:
- Return label modal/dialog
- Return package configuration form
- Return tracking display
- Return batch management table

## Event Sourcing

**Events**:
- `ReturnLabelGenerated` - Return label created
- `ReturnPackageReceived` - Return arrived at warehouse
- `ReturnProcessed` - Return inspected and processed

**Location**: `server/src/shared/orders/events.js` (would need to add return events)

## Dependencies

- [Order Lifecycle](./order-lifecycle.md) - Original order management
- [Order Bulk Actions](./order-bulk-actions.md) - Bulk return processing
- [Carrier Integration](../shipping/carrier-integration.md) (to be created)
- [Order Address Management](./order-address-management.md) - Return address validation

## Referenced By

- Order detail page (return button)
- Return management dashboard
- Customer return portal (if implemented)

## Configuration

**Account Settings**:
- Default return address (warehouse)
- Default return carrier
- Return label auto-generation
- Return notification emails

**Feature Toggles**:
- Return label generation enabled
- Return batching enabled
- Return tracking enabled
- Return automation rules

## Common Patterns

### Generate Return Label for Single Order

```javascript
// Frontend
dispatch(processReturnLabel(orderId, returnShipmentData));

// Backend
1. Fetch order
2. Set returnShipping address (merchant warehouse)
3. Set returnShipFromAddress (customer address)
4. Select return carrier
5. Generate return label via carrier API
6. Store in returnLabel[]
7. Socket notification to frontend
```

### Bulk Return Label Generation

```javascript
// User selects multiple orders
const orderIds = selectedOrders.map(o => o._id);

// Dispatch bulk return action
dispatch(bulkReturnLabelGeneration(orderIds));

// Each order processed independently
// Socket updates per order completion
```

## Known Issues / Tech Debt

1. **Return state complexity**: Return state split between Redux (frontend) and database (backend)
2. **Partial return handling**: Limited support for multiple partial returns from same order
3. **Return reason tracking**: No structured return reason field (quality issue, wrong item, etc.)
4. **Return refund integration**: No automatic refund triggering on return receipt
5. **International returns**: Complex customs handling for cross-border returns not fully implemented

## Related Pages

- [Order Lifecycle](./order-lifecycle.md)
- [Order Bulk Actions](./order-bulk-actions.md)
- [Order Address Management](./order-address-management.md)
- [Batch Processing](../shipping/batch-processing.md) (to be created)
