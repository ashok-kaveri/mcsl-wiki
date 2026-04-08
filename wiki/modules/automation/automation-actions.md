---
title: Automation Actions
category: module
domain: automation
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Automation Actions

## Overview

Automation actions are **operations applied to orders** when automation rule conditions match. Actions configure carrier selection, package dimensions, addresses, special services, and delivery options without manual intervention. Every matched automation rule executes its associated actions sequentially to prepare orders for label generation.

**Location**: `server/src/shared/storepepAutomation/AutomationActionsManager.js`

**Core Class**: `AutomationActionsManager` (lines 98-632)

## Architecture

### Action Application Flow

**Entry Point**: `applyActionsToOrderAndReturnOrder(order, packages, actions)`

**Location**: `AutomationActionsManager.js:617-629`

```javascript
async applyActionsToOrderAndReturnOrder(order, packagesToProcess, actionsFromDb) {
  let orderToApplyAction = Object.assign({}, order);
  let packagesToApplyAction = packagesToProcess;
  let orderUpdateFields = {};

  // Apply each action sequentially
  for (let index = 0; index < actionsFromDb.length; index++) {
    const action = actionsFromDb[index];
    const actionAppliedOrder = await this.applyAutomationActionBasedOnActionType[action.actionType](
      orderToApplyAction, packagesToApplyAction, action, orderUpdateFields
    );
    orderUpdateFields = actionAppliedOrder.orderUpdatedFields;
    orderToApplyAction = actionAppliedOrder.order;
    packagesToApplyAction = actionAppliedOrder.actionAppliedPackage;
  }

  return { order: orderToApplyAction, orderUpdatedFields: orderUpdateFields, packages: packagesToApplyAction };
}
```

**Behavior**:
- Actions execute **sequentially** in database order
- Each action receives the output of the previous action
- Later actions can overwrite earlier actions' changes
- All actions apply to the same order/package objects

### Action Dispatcher

**Constructor Mapping**: `AutomationActionsManager.js:582-615`

```javascript
constructor() {
  this.applyAutomationActionBasedOnActionType = {
    [actionsMapper.SET_CARRIER_SERVICE]: this.setCarrierService,
    [actionsMapper.SET_PACKAGE_DIMENSION]: this.setPackageDimension,
    [actionsMapper.SET_PACKAGE_WEIGHT]: this.setPackageWeight,
    [actionsMapper.ADJUST_PACKAGE_WEIGHT]: this.adjustPackageWeight,
    [actionsMapper.SET_SHIPPING_FROM_ADDRESS]: this.setShipFromAddress,
    [actionsMapper.SET_FROM_ADDRESS_TO_DISPLAY_ON_LABEL]: this.setDisplayFromAddress,
    [actionsMapper.SET_SOLD_TO_ADDRESS]: this.setSoldToAddress,
    [actionsMapper.MAP_ORDER_META_FIELDS_TO_SHIPPING_ADDRESS]: this.mapMetaFieldsToShippingAddress,
    [actionsMapper.SET_THIRD_PARTY_AS_SHIPMENT_CHARGES_PAYER]: this.setShipmentPayer,
    [actionsMapper.SET_DUTIES_AND_TAXES_PAYER]: this.setDutiesPayer,
    [actionsMapper.ADD_INSURANCE_REQUIRED]: this.addInsurance,
    [actionsMapper.ADD_CARRIER_SERVICE]: this.addCarrierService,
    [actionsMapper.ADD_DHL_SPECIAL_SERVICES]: this.addDhlSpecialServices,
    [actionsMapper.ADD_DHL_SWEDEN_SPECIAL_SERVICES]: this.addDhlSwedenSpecialServices,
    [actionsMapper.ADD_MY_FASTWAY_SPECIAL_SERVICES]: this.addMyFastwaySpecialServices,
    [actionsMapper.ADD_ARAMEX_SPECIAL_SERVICES]: this.addAramexSpecialServices,
    [actionsMapper.ADD_CANADA_POST_SPECIAL_SERVICES]: this.addCanadaPostSpecialServices,
    [actionsMapper.ADD_CANPAR_SPECIAL_SERVICES]: this.addCanparSpecialServices,
    [actionsMapper.ADD_NEW_ZEALAND_POST_SPECIAL_SERVICES]: this.addNewZealandPostSpecialServices,
    [actionsMapper.ADD_DELIVERY_CONFIRMATION]: this.addDeliveryConfirmation,
    [actionsMapper.ENABLE_AUTO_GENERATE_LABEL]: this.enableAutoGenerateLabel,
    [actionsMapper.ENABLE_SATURDAY_DELIVERY]: this.enableSaturdayDelivery,
    [actionsMapper.ENABLE_AUTO_ADDRESS_CORRECTION]: this.enableAutoAddressCorrection,
    [actionsMapper.MARK_AS_NOT_TO_SHIP]: this.markAsNotToShip,
    [actionsMapper.ADD_XPO_LOGISTICS_SPECIAL_SERVICES]: this.addXpoLogisticsSpecialServices,
    [actionsMapper.MAP_ADDRESS_FIELDS_TO_ORDER_META]: this.mapAddressToOrderMeta,
    [actionsMapper.SET_DEFAULT_SERVICE_POINTS_FOR_POSTNORD]: this.setDefaultServicePointForPostNord,
    [actionsMapper.ADD_POSTNORD_SPECIAL_SERVICES]: this.addPostNordSpecialServices,
    [actionsMapper.SET_PREFERRED_CARRIER_SERVICE]: this.setPreferredCarrierService,
    [actionsMapper.SET_DEFAULT_SERVICE_POINTS_FOR_DHL_SWEDEN]: this.setDefaultServicePointForDhlSweden,
  };
}
```

## Action Types

### 1. Set Carrier Service

**Action Type**: `SET_CARRIER_SERVICE`

**Purpose**: Sets the primary carrier and service(s) for this order

**Function**: `setCarrierService(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:99-141`

**Action Fields**:
```javascript
{
  actionType: 'SET_CARRIER_SERVICE',
  carrierName: 'FedEx',
  carrierType: 'C1',
  preferredCarrier: 'fedex-carrier-id',
  preferredService: ['FEDEX_GROUND', 'FEDEX_2_DAY'],  // Array of service codes
  easypostCarrier: 'FedEx',  // For EasyPost integration
  easypostCarrierType: 'FedEx'
}
```

**Order Updates**:
```javascript
order.availableCarrierAndService = [{
  carrierName: 'FedEx',
  carrierId: 'fedex-carrier-id',
  carrierType: 'C1',
  source: constants.AUTOMATION,
  sourceType: constants.AUTOMATION,
  services: [
    { serviceType: 'FEDEX_GROUND', serviceName: 'FedEx Ground', rate: 0, selected: false },
    { serviceType: 'FEDEX_2_DAY', serviceName: 'FedEx 2Day', rate: 0, selected: false }
  ]
}]
```

**Behavior**:
- **Replaces** entire `availableCarrierAndService` array (sets to single carrier)
- Multiple services allowed per carrier
- Rate shopping will populate rates later
- Service selection happens after rate fetching

### 2. Set Preferred Carrier Service (with Fallback)

**Action Type**: `SET_PREFERRED_CARRIER_SERVICE`

**Purpose**: Sets preferred carrier with automatic fallback carrier

**Function**: `setPreferredCarrierService(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:520-555`

**Action Fields**:
```javascript
{
  actionType: 'SET_PREFERRED_CARRIER_SERVICE',
  // Preferred carrier
  preferredCarrier: 'ups-carrier-id',
  preferredService: ['03'],  // UPS Ground
  carrierType: 'C3',
  easypostCarrier: 'UPS',
  easypostCarrierType: 'UPS',
  // Fallback carrier
  fallbackCarrier: 'fedex-carrier-id',
  fallbackService: ['FEDEX_GROUND'],
  fallbackEasypostCarrier: 'FedEx',
  fallbackEasypostCarrierType: 'FedEx'
}
```

**Order Updates**:
```javascript
order.availableCarrierAndService = [
  {
    carrierId: 'ups-carrier-id',
    services: [{ serviceType: '03', serviceName: 'UPS Ground' }],
    isPreferred: true,
    isFallback: false
  },
  {
    carrierId: 'fedex-carrier-id',
    services: [{ serviceType: 'FEDEX_GROUND', serviceName: 'FedEx Ground' }],
    isPreferred: false,
    isFallback: true
  }
]
```

**Behavior**:
- **Adds** both carriers to `availableCarrierAndService` array
- If preferred carrier fails rate fetch, system uses fallback
- Both carriers go through rate shopping
- Preferred carrier selected if available

### 3. Add Carrier Service

**Action Type**: `ADD_CARRIER_SERVICE`

**Purpose**: Adds additional carrier/service without replacing existing ones

**Function**: `addCarrierService(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:274-305`

**Behavior**:
- **Appends** to `availableCarrierAndService` array
- Does NOT replace existing carriers
- Useful for multi-carrier rate shopping
- Multiple automation actions can add different carriers

### 4. Set Package Dimensions

**Action Type**: `SET_PACKAGE_DIMENSION`

**Purpose**: Sets length, width, height for all packages

**Function**: `setPackageDimension(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:143-153`

**Action Fields**:
```javascript
{
  actionType: 'SET_PACKAGE_DIMENSION',
  length: 12,
  width: 10,
  height: 8
}
```

**Package Updates**:
```javascript
packagesToProcess.forEach((pack) => {
  pack.dimensions = {
    length: 12,
    width: 10,
    height: 8
  };
});
```

**Behavior**:
- Applies to **all packages** in the order
- Unit determined by store's dimension unit setting
- Overwrites any existing dimensions from product data

### 5. Set Package Weight

**Action Type**: `SET_PACKAGE_WEIGHT`

**Purpose**: Sets absolute weight for all packages

**Function**: `setPackageWeight(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:155-165`

**Action Fields**:
```javascript
{
  actionType: 'SET_PACKAGE_WEIGHT',
  packageWeight: 5.5  // in store's weight unit
}
```

**Order/Package Updates**:
```javascript
packagesToProcess.forEach((pack) => {
  pack.totalWeight = 5.5;
});
order.totalWeight = 5.5 * packagesToProcess.length;
```

**Behavior**:
- Sets **exact weight** (not adjustment)
- Applies to all packages equally
- Order total weight = package weight × number of packages
- Weight unit from store configuration

### 6. Adjust Package Weight

**Action Type**: `ADJUST_PACKAGE_WEIGHT`

**Purpose**: Increases/decreases product weights by percentage

**Function**: `adjustPackageWeight(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:167-190`

**Action Fields**:
```javascript
{
  actionType: 'ADJUST_PACKAGE_WEIGHT',
  adjustWeight: 10,  // Percentage
  condition: '+' | '-'  // Add or subtract
}
```

**Logic**:
```javascript
packageToProcess.products = packageToProcess.products.map((product) => {
  const weightToAdjust = parseFloat(product.weight) * (parseFloat(action.adjustWeight) / 100);
  let adjustedWeight = 1;

  if (parseFloat(weightToAdjust) < parseFloat(product.weight)) {
    adjustedWeight = calculateBasedOnCondition[action.condition](
      parseFloat(product.weight),
      weightToAdjust
    );
  }

  product.weight = getFixedWeightDecimalValues(adjustedWeight);
  return product;
});
```

**Use Case**: Add packing materials weight (e.g., +10% for boxes/padding)

### 7. Set Ship-From Address

**Action Type**: `SET_SHIPPING_FROM_ADDRESS`

**Purpose**: Sets origin address for label generation

**Function**: `setShipFromAddress(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:192-207`

**Action Fields**:
```javascript
{
  actionType: 'SET_SHIPPING_FROM_ADDRESS',
  addressUUID: 'warehouse-address-uuid'
}
```

**Order Updates**:
```javascript
order.shipFromAddress = {
  addressUUID: 'warehouse-address-uuid',
  name: 'Main Warehouse',
  streetLines: ['123 Warehouse Blvd'],
  city: 'New York',
  stateOrProvinceCode: 'NY',
  postalCode: '10001',
  countryCode: 'US',
  // ... full address object
}
```

**WMS Integration**:
```javascript
if (await wmsEnabledFor(order.accountUUID)) {
  const selectedWarehouse = await selectWarehouseForOrder(order);
  if (selectedWarehouse) {
    order.shipFromAddress = await getShipFromAddress({
      addressUUID: selectedWarehouse.addressUUID
    });
  }
}
```

**Behavior**:
- **WMS warehouse selection overrides automation address**
- If WMS enabled, geo-based/address-based warehouse selection takes priority
- See [Warehouse Selection](../warehouses/warehouse-selection.md)

### 8. Set Display From Address

**Action Type**: `SET_FROM_ADDRESS_TO_DISPLAY_ON_LABEL`

**Purpose**: Sets return address printed on label (different from ship-from)

**Function**: `setDisplayFromAddress(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:209-217`

**Action Fields**:
```javascript
{
  actionType: 'SET_FROM_ADDRESS_TO_DISPLAY_ON_LABEL',
  displayAddressUUID: 'corporate-office-uuid'
}
```

**Use Case**: Ship from warehouse but display corporate office as return address

### 9. Set Sold-To Address

**Action Type**: `SET_SOLD_TO_ADDRESS`

**Purpose**: Sets sold-to party for accounting/customs (B2B transactions)

**Function**: `setSoldToAddress(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:219-227`

**Action Fields**:
```javascript
{
  actionType: 'SET_SOLD_TO_ADDRESS',
  soldToAddressUUID: 'sold-to-party-uuid'
}
```

**Use Case**: International shipments where sold-to differs from ship-to

### 10. Map Order Meta to Shipping Address

**Action Type**: `MAP_ORDER_META_FIELDS_TO_SHIPPING_ADDRESS`

**Purpose**: Copies order metadata field to shipping address field

**Function**: `mapMetaFieldsToShippingAddress(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:229-242`

**Action Fields**:
```javascript
{
  actionType: 'MAP_ORDER_META_FIELDS_TO_SHIPPING_ADDRESS',
  orderMetaKey: '_custom_delivery_instructions',  // WooCommerce meta field
  shippingAddressKey: 'address2',  // Target shipping address field
  prefix: 'Instructions: '  // Optional prefix
}
```

**Logic**:
```javascript
if (order.meta_data) {
  const metaField = order.meta_data.find(e => e.key === action.orderMetaKey);
  if (metaField && metaField.value && action.shippingAddressKey) {
    if (order.shipping[action.shippingAddressKey]) {
      order.shipping[action.shippingAddressKey] += `${action.prefix}${metaField.value},`;
    } else {
      order.shipping[action.shippingAddressKey] = `${action.prefix}${metaField.value}`;
    }
  }
}
```

**Use Case**: Map custom checkout fields to address lines (e.g., apartment number, delivery notes)

### 11. Set Third-Party Billing

**Action Type**: `SET_THIRD_PARTY_AS_SHIPMENT_CHARGES_PAYER`

**Purpose**: Bill shipping charges to third-party account

**Function**: `setShipmentPayer(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:244-253`

**Action Fields**:
```javascript
{
  actionType: 'SET_THIRD_PARTY_AS_SHIPMENT_CHARGES_PAYER',
  shipmentChargePayerAccountNumber: '123456789',  // Carrier account number
  shipmentChargePayerAddressUUID: 'third-party-address-uuid'
}
```

**Order Updates**:
```javascript
order.shipmentChargePayerAccountNumber = '123456789';
order.shipmentChargePayerAddress = { /* full address */ };
```

**Use Case**: Customer pays shipping via their FedEx/UPS account

### 12. Set Duties Payer

**Action Type**: `SET_DUTIES_AND_TAXES_PAYER`

**Purpose**: Sets who pays customs duties/taxes (international shipments)

**Function**: `setDutiesPayer(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:255-265`

**Action Fields**:
```javascript
{
  actionType: 'SET_DUTIES_AND_TAXES_PAYER',
  dutiesAndTaxesPayer: 'SENDER' | 'RECIPIENT' | 'THIRD_PARTY',
  dutiesAndTaxesPayerAccountNumber: '123456789',  // If THIRD_PARTY
  dutiesAndTaxesPayerAddressUUID: 'payer-address-uuid'
}
```

**Use Case**: DDP (Delivered Duty Paid) vs DDU (Delivered Duty Unpaid) shipments

### 13. Add Insurance

**Action Type**: `ADD_INSURANCE_REQUIRED`

**Purpose**: Enables carrier insurance for this shipment

**Function**: `addInsurance(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:267-272`

**Action Fields**:
```javascript
{
  actionType: 'ADD_INSURANCE_REQUIRED',
  isInsuranceRequired: true
}
```

**Order Updates**:
```javascript
order.isInsuranceRequired = true;
```

**Behavior**:
- Insurance amount calculated from order total during label generation
- Carrier-specific insurance implementation varies

### 14. Add Delivery Confirmation

**Action Type**: `ADD_DELIVERY_CONFIRMATION`

**Purpose**: Requires signature on delivery

**Function**: `addDeliveryConfirmation(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:386-405`

**Action Fields**:
```javascript
{
  actionType: 'ADD_DELIVERY_CONFIRMATION',
  deliveryConfirmationType: constants.UPS_OPTIONS.SIGNATURE_CONFIRMATION |
                            constants.UPS_OPTIONS.ADULT_SIGNATURE_CONFIRMATION
}
```

**Order Updates**:
```javascript
// For SIGNATURE_CONFIRMATION
order.signatureConfirmation = { isRequired: true };
order.adultSignatureConfirmation = { isRequired: false };

// For ADULT_SIGNATURE_CONFIRMATION
order.adultSignatureConfirmation = { isRequired: true };
order.signatureConfirmation = { isRequired: false };
```

**Use Case**: High-value items, age-restricted products (alcohol, tobacco)

### 15. Add Carrier-Specific Special Services

#### DHL Special Services

**Action Type**: `ADD_DHL_SPECIAL_SERVICES`

**Function**: `addDhlSpecialServices(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:307-319`

**Action Fields**:
```javascript
{
  actionType: 'ADD_DHL_SPECIAL_SERVICES',
  dhlSpecialServices: ['SATURDAY_DELIVERY', 'DANGEROUS_GOODS', 'NON_STACKABLE']
}
```

#### DHL Sweden Special Services

**Action Type**: `ADD_DHL_SWEDEN_SPECIAL_SERVICES`

**Location**: `AutomationActionsManager.js:321-327`

#### Aramex Special Services

**Action Type**: `ADD_ARAMEX_SPECIAL_SERVICES`

**Function**: `addAramexSpecialServices(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:341-346`

**Behavior**:
```javascript
order.aramexSpecialServices.push(...action.aramexSpecialServices);
order.aramexSpecialServices = removeDuplicatesFromArray(order.aramexSpecialServices);
```

**Pattern**: Appends to existing services, removes duplicates

#### Canada Post Special Services

**Action Type**: `ADD_CANADA_POST_SPECIAL_SERVICES`

**Function**: `addCanadaPostSpecialServices(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:362-368`

**Behavior**:
```javascript
order.canadaPostSpecialServices = [];
order.canadaPostSpecialServices.push(action.canadaPostSpecialServices);
```

**Pattern**: **Replaces** existing services (clears array first)

#### PostNord Special Services

**Action Type**: `ADD_POSTNORD_SPECIAL_SERVICES`

**Location**: `AutomationActionsManager.js:506-518`

#### New Zealand Post Special Services

**Action Type**: `ADD_NEW_ZEALAND_POST_SPECIAL_SERVICES`

**Location**: `AutomationActionsManager.js:348-353`

#### Canpar Special Services

**Action Type**: `ADD_CANPAR_SPECIAL_SERVICES`

**Location**: `AutomationActionsManager.js:335-339`

#### MyFastway Special Services

**Action Type**: `ADD_MY_FASTWAY_SPECIAL_SERVICES`

**Location**: `AutomationActionsManager.js:329-333`

#### XPO Logistics Special Services

**Action Type**: `ADD_XPO_LOGISTICS_SPECIAL_SERVICES`

**Location**: `AutomationActionsManager.js:355-360`

### 16. Enable Saturday Delivery

**Action Type**: `ENABLE_SATURDAY_DELIVERY`

**Function**: `enableSaturdayDelivery(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:412-416`

**Order Updates**:
```javascript
order.isSaturdayDeliveryEnabled = true;
```

**Carriers**: FedEx, UPS (additional fee applies)

### 17. Enable Auto Label Generation

**Action Type**: `ENABLE_AUTO_GENERATE_LABEL`

**Function**: `enableAutoGenerateLabel(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:407-411`

**Order Updates**:
```javascript
order.isAutoGenerateLabelEnable = true;
```

**Behavior**: Label automatically generated after automation + rate shopping completes

### 18. Enable Auto Address Correction

**Action Type**: `ENABLE_AUTO_ADDRESS_CORRECTION`

**Function**: `enableAutoAddressCorrection(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:418-422`

**Order Updates**:
```javascript
order.isAutoAddressCorrectionEnable = true;
```

**Behavior**: Uses carrier address validation API before label generation

### 19. Mark as Not To Ship

**Action Type**: `MARK_AS_NOT_TO_SHIP`

**Purpose**: Prevents order from being shipped (fulfillment hold)

**Function**: `markAsNotToShip(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:424-463`

**Order Updates**:
```javascript
order.storePepStatus = constants.NOT_TO_SHIP;
order.batchStatus = constants.FREE;
order.isAutomationFailed = true;
order.updatedBy = constants.AUTOMATION;

// Clear shipping-related fields
order.shipmentWeight = '';
order.masterTrackingId = '';
order.carrierTypeSelected = '';
order.carrierIdSelected = '';
order.totalPackage = '';
order.shipmentPackage = '';
order.carrier = '';

// Clear timestamp fields
order.processedAt = undefined;
order.shippedAt = undefined;
order.labelCreatedAt = undefined;
order.shipFromAddress = undefined;

// Preserve customer-selected carriers but reset rates
order.availableCarrierAndService = order.availableCarrierAndService.reduce((acc, cs) => {
  if (cs.source === constants.CUSTOMER_SELECTED) {
    cs.selected = false;
    cs.services = cs.services.map((s) => {
      s.rate = 0;
      s.selected = false;
      s.status = undefined;
      return s;
    });
    acc.push(cs);
  }
  return acc;
}, []);

// Clear carrier-specific services
order.dhlSpecialServices = [];
order.aramexSpecialServices = [];
```

**Use Case**: Fraud detection, inventory hold, payment verification required

### 20. Set Default Service Point for PostNord

**Action Type**: `SET_DEFAULT_SERVICE_POINTS_FOR_POSTNORD`

**Purpose**: Automatically selects nearest PostNord pickup location

**Function**: `setDefaultServicePointForPostNord(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:465-504`

**Logic**:
```javascript
const shipmentAdaptor = await new ShipmentAdaptor()
  .getShipmentCreatorBasedOnCarrier(constants.POST_NORD_CARRIER_CODE);

const servicePointsResponse = await shipmentAdaptor.getHoldAtLocations(order, preferedCarrier);

if (servicePointsResponse.servicePoints && servicePointsResponse.servicePoints.length > 0) {
  const { servicePoints } = servicePointsResponse;

  // Find nearest by distance
  const nearestServicePoints = servicePoints.reduce(
    (prev, curr) => prev.routeDistance < curr.routeDistance ? prev : curr,
    {}
  );

  order.localPickupLocation.pickupLocationName = nearestServicePoints.name;
  order.localPickupLocation.pickupLocationId = nearestServicePoints.servicePointId;
  order.localPickupLocation.locationType = nearestServicePoints.type?.typeName;
  order.localPickupLocation.pickupLocationAddress = {
    address: {
      residential: false,
      streetLines: nearestServicePoints.deliveryAddress.streetName,
      city: nearestServicePoints.deliveryAddress.city,
      postalCode: nearestServicePoints.deliveryAddress.postalCode,
      countryCode: nearestServicePoints.deliveryAddress.countryCode,
      phoneNumber: nearestServicePoints.phoneNoToCashRegister,
      streetNumber: nearestServicePoints.deliveryAddress.streetNumber
    }
  };
}
```

**Use Case**: Nordic countries (Sweden, Norway, Denmark, Finland) pickup locations

### 21. Set Default Service Point for DHL Sweden

**Action Type**: `SET_DEFAULT_SERVICE_POINTS_FOR_DHL_SWEDEN`

**Purpose**: Automatically selects nearest DHL Sweden service point

**Function**: `setDefaultServicePointForDhlSweden(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:557-579`

**Logic**:
```javascript
const preferredCarrier = await findOneCarrierWithLean({
  accountUUID: order.accountUUID,
  carrierType: constants.DHL_SWEDEN_CARRIER_CODE,
  isActive: true
});

const shipmentAdaptor = await new ShipmentAdaptor()
  .getShipmentCreatorBasedOnCarrier(constants.DHL_SWEDEN_CARRIER_CODE);

const servicePointsResponse = await shipmentAdaptor.getServicePoints(order, preferredCarrier);

if (servicePointsResponse.status) {
  const { data } = servicePointsResponse;
  const nearestServicePoint = data.reduce(
    (prev, curr) => (prev.routeDistance < curr.routeDistance ? prev : curr),
    {}
  );

  const updatedOrder = updateOrderWithServicePoint(order, nearestServicePoint);
}
```

### 22. Map Address to Order Meta

**Action Type**: `MAP_ADDRESS_FIELDS_TO_ORDER_META`

**Purpose**: Extracts address field value to order metadata

**Function**: `mapAddressToOrderMeta(order, packages, action, orderUpdatedFields)`

**Location**: `AutomationActionsManager.js:370-384`

**Action Fields**:
```javascript
{
  actionType: 'MAP_ADDRESS_FIELDS_TO_ORDER_META',
  metaField: 'postcode',  // Source address field
  metaName: 'delivery_zone',  // Target meta field name
  metaPosition: 'FIRST_4' | 'LAST_4' | 'ALL'  // What part to extract
}
```

**Logic**:
```javascript
const metaPositonMapper = {
  FIRST_4: (value) => value.slice(0, 4),
  LAST_4: (value) => value.slice(-4),
  ALL: (value) => value,
};

if (order.shipping[metaField]) {
  const metaFieldValue = order.shipping[metaField];
  const metaActualValue = metaPositonMapper[metaPosition](metaFieldValue);

  if (metaActualValue) {
    if (!order.mapped_meta) {
      order.mapped_meta = {};
    }
    order.mapped_meta[metaName] = metaActualValue;
  }
}
```

**Use Case**: Extract postal code prefix for zone-based routing/reporting

## Action Data Model

**Model**: `AutomationActions`

**Location**: `server/src/models/automationActions.js`

**Schema** (partial):
```javascript
{
  automationId: String,  // Links to AutomationSetting
  accountUUID: String,
  actionType: String,  // One of actionsMapper values

  // Carrier/Service fields
  carrierName: String,
  carrierType: String,
  preferredCarrier: String,
  preferredService: [String],
  fallbackCarrier: String,
  fallbackService: [String],

  // Package fields
  length: Number,
  width: Number,
  height: Number,
  packageWeight: Number,
  adjustWeight: Number,
  condition: String,

  // Address fields
  addressUUID: String,
  displayAddressUUID: String,
  soldToAddressUUID: String,
  shipmentChargePayerAddressUUID: String,
  dutiesAndTaxesPayerAddressUUID: String,

  // Billing fields
  shipmentChargePayerAccountNumber: String,
  dutiesAndTaxesPayer: String,
  dutiesAndTaxesPayerAccountNumber: String,

  // Special services
  dhlSpecialServices: [String],
  aramexSpecialServices: [String],
  canadaPostSpecialServices: [String],
  postNordSpecialServices: [String],

  // Mapping fields
  orderMetaKey: String,
  shippingAddressKey: String,
  prefix: String,
  metaField: String,
  metaName: String,
  metaPosition: String,

  // Flags
  isInsuranceRequired: Boolean,
  deliveryConfirmationType: String,

  createdBy: String,
  updatedBy: String
}
```

## Common Patterns

### Create Automation Action

```javascript
const automationAction = new AutomationActions({
  automationId: 'automation-rule-id',
  accountUUID: 'account-uuid',
  actionType: 'SET_CARRIER_SERVICE',
  carrierName: 'FedEx',
  carrierType: 'C1',
  preferredCarrier: 'fedex-carrier-id',
  preferredService: ['FEDEX_GROUND'],
  createdBy: 'user-uuid'
});

await automationAction.save();
```

### Multi-Action Rule

**Example**: Set carrier + dimensions + insurance

```javascript
// Action 1: Set carrier
const action1 = new AutomationActions({
  automationId: 'rule-id',
  actionType: 'SET_CARRIER_SERVICE',
  preferredCarrier: 'ups-carrier-id',
  preferredService: ['03']
});

// Action 2: Set dimensions
const action2 = new AutomationActions({
  automationId: 'rule-id',
  actionType: 'SET_PACKAGE_DIMENSION',
  length: 12,
  width: 10,
  height: 8
});

// Action 3: Add insurance
const action3 = new AutomationActions({
  automationId: 'rule-id',
  actionType: 'ADD_INSURANCE_REQUIRED',
  isInsuranceRequired: true
});

await Promise.all([action1.save(), action2.save(), action3.save()]);
```

**Result**: When rule matches, all three actions apply sequentially

## Integration Points

### Rate Shopping

**After automation actions apply**, rate shopping fetches rates for carriers in `availableCarrierAndService`:

```javascript
// Automation sets carriers
order.availableCarrierAndService = [
  { carrierId: 'fedex-id', services: [{ serviceType: 'FEDEX_GROUND', rate: 0 }] }
];

// Rate shopping populates rates
await addRateInfoToOrder(order, ...);

// Result
order.availableCarrierAndService = [
  { carrierId: 'fedex-id', services: [{ serviceType: 'FEDEX_GROUND', rate: 12.50 }] }
];
```

See [Rate Shopping](../shipping/rate-shopping.md)

### Label Generation

**Label generation** reads automation-configured settings:

```javascript
const label = await createLabel({
  order,
  shipFromAddress: order.shipFromAddress,  // From automation
  carrierType: selectedCarrier.carrierType,  // From automation
  serviceType: selectedService.serviceType,  // From automation
  isInsuranceRequired: order.isInsuranceRequired,  // From automation
  signatureConfirmation: order.signatureConfirmation,  // From automation
  dhlSpecialServices: order.dhlSpecialServices  // From automation
});
```

See [Label Generation](../shipping/label-generation.md)

### Warehouse Management

**WMS warehouse selection** can override ship-from address:

```javascript
// Automation sets initial address
order.shipFromAddress = automationAddress;

// WMS overrides based on inventory/geography
if (wmsEnabled) {
  const warehouse = await selectWarehouseForOrder(order);
  order.shipFromAddress = warehouse.address;  // Overrides automation
}
```

See [Warehouse Selection](../warehouses/warehouse-selection.md)

## Test Coverage

**Automated E2E Tests**: 11 Playwright tests covering automation rules and actions

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| **Automation Criteria** | | |
| Quantity Between Threshold | `automationRules/automationCriteria/quantityBetween.spec.ts` | ✅ Passing |
| Product Price Conditions | `automationRules/automationCriteria/price.spec.ts` | ✅ Passing |
| Product Shipping Class | `automationRules/automationCriteria/productShippingClass.spec.ts` | ✅ Passing |
| Total Price Range | `automationRules/automationCriteria/totalPriceRange.spec.ts` | ✅ Passing |
| Total Weight Range | `automationRules/automationCriteria/totalWeightRange.spec.ts` | ✅ Passing |
| Total Weight Rule | `automationRules/automationCriteria/totalWeightRule.spec.ts` | ✅ Passing |
| Shipping Zone | `automationRules/automationCriteria/zone.spec.ts` | ✅ Passing |
| **Automation Actions** | | |
| Set Carrier & Service | `automationRules/actionDetails/setCarrierService.spec.ts` | ✅ Passing |
| Auto Label Generation | `automationRules/labelAutomation.spec.ts` | ✅ Passing |
| Auto Rate Shopping | `automationRules/rateAutomation.spec.ts` | ✅ Passing |
| General Automation Rules | `automationRules/automationRules.spec.ts` | ✅ Passing |

**Test Coverage**: 11/24 automation actions tested (46% coverage)

**Tested Actions**:
- ✅ SET_CARRIER_SERVICE (Action #1)
- ✅ Automation criteria (7 types tested)
- ✅ Label automation workflow
- ✅ Rate automation workflow

**Untested Actions** (13 remaining):
- SET_DEFAULT_PACKAGE_DIMENSIONS (#2)
- ADJUST_PACKAGE_DIMENSIONS (#3)
- SET_DEFAULT_PACKAGE_WEIGHT (#4)
- ADJUST_PACKAGE_WEIGHT (#5)
- SET_DEFAULT_SHIP_FROM_ADDRESS (#6)
- SET_DEFAULT_DISPLAY_FROM_ADDRESS (#7)
- SET_DEFAULT_SOLD_TO_ADDRESS (#8)
- MAP_ORDER_META_DATA_TO_ADDRESS (#9)
- ENABLE_THIRD_PARTY_BILLING (#10)
- SET_DUTIES_AND_TAXES_PAYER (#11)
- ADD_INSURANCE (#12)
- ADD_DELIVERY_CONFIRMATION (#13)
- Multiple carrier-specific services (#14-24)

**Test Suite Location**: `mcsl-test-automation/tests/automationRules/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Known Issues / Tech Debt

1. **No action priority**: Actions execute in database order, not explicit sequence
2. **No rollback**: If action fails mid-way, partial changes persist
3. **Action overwriting**: Later actions overwrite earlier ones (e.g., SET_CARRIER_SERVICE replaces entire carrier array)
4. **No conditional actions**: Can't say "if X then action A else action B" within single rule
5. **Limited validation**: Invalid addressUUID causes action to fail silently
6. **Carrier-specific coupling**: Many actions tightly coupled to specific carriers (DHL, Aramex, etc.)
7. **No action composition**: Can't reuse common action groups across rules

## Related Pages

- [Automation Overview](./automation-overview.md) - Rule engine architecture
- [Automation Conditions](./automation-conditions.md) - Condition matching logic
- [Rate Shopping](../shipping/rate-shopping.md) - Post-automation rate fetching
- [Label Generation](../shipping/label-generation.md) - Uses automation-configured settings
- [Warehouse Selection](../warehouses/warehouse-selection.md) - Overrides automation addresses
