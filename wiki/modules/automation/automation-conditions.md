---
title: Automation Conditions
category: module
domain: automation
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Automation Conditions

## Overview

Automation conditions define **"IF"** criteria that must be met for a rule to execute. All conditions in a rule must match (AND logic) for actions to apply. StorePep supports 12 condition types covering shipping destinations, order attributes, timing, and addresses.

**Location**: `server/src/shared/storepepAutomation/AutomationConditionsManager.js:55-248`

**Evaluation**: Conditions evaluated sequentially; first non-match stops evaluation and rule doesn't apply.

## Condition Types

### 1. Zone (Shipping Destination)

**Field**: `conditionType: "zone"`

**Purpose**: Match orders based on shipping destination (country, state, postal code)

**Model Fields** (`automationConditions.js:17-19`):
```javascript
{
  zone: { type: [Array, String] },  // Zone UUID(s) or country code
  zoneNames: [String],              // Human-readable zone names
  condition: String                 // '==' or '!='
}
```

**Matching Logic** (`AutomationConditionsManager.js:83-103`):
```javascript
async checkIfZoneMatches(order, condition, automationHelperDataObject) {
  let success = false;
  const shippingAddress = order.shipping;

  if (Array.isArray(condition.zone)) {
    // Zone-based matching (complex)
    for (let index = 0; index < condition.zone.length; index += 1) {
      const zone = condition.zone[index];
      const zoneSettings = await findOneShippingZoneSettings({
        accountUUID: condition.accountUUID,
        shippingZoneUUID: zone
      });
      const conditions = await findShippingZoneConditions({
        accountUUID: condition.accountUUID,
        shippingZoneUUID: zone
      });

      success = this.processZoneMatch(conditions, shippingAddress, zoneSettings.matchAllConditions);
      success = (condition.condition === '==' && success) || (condition.condition === '!=' && !success);
      if (success) return success;
    }
  } else {
    // Simple country:state matching
    success = checkBasedOnConditionOperator[condition.condition](
      `${shippingAddress.country}${shippingAddress.state ? `:${shippingAddress.state}` : ''}`,
      condition.zone
    );
  }

  return success;
}
```

**Zone Matching Details** (`AutomationConditionsManager.js:30-44`):
```javascript
const matchZoneCondition = (zoneCondition, shippingAddress) => {
  let isFound = false;

  if (zoneCondition.conditionType === 'COUNTRY') {
    // Match by country code (e.g., "US", "CA", "UK")
    const foundIndex = zoneCondition.countryList.findIndex(
      cl => cl.toLowerCase() == shippingAddress.country.toLowerCase()
    );
    isFound = checkBasedOnCondition(zoneCondition.condition, foundIndex);

  } else if (zoneCondition.conditionType === 'COUNTRY_STATE') {
    // Match by country:state (e.g., "US:CA", "US:NY")
    const foundIndex = zoneCondition.countryStateList.findIndex(
      cl => cl.toLowerCase() == `${shippingAddress.country}${shippingAddress.state ? `:${shippingAddress.state}` : ''}`.toLowerCase()
    );
    isFound = checkBasedOnCondition(zoneCondition.condition, foundIndex);

  } else if (zoneCondition.conditionType === 'POSTAL_CODE') {
    // Match by postal code with wildcard support (e.g., "90*" matches 90001-90099)
    const foundIndex = zoneCondition.postalCodeList.findIndex(
      cl => cl.toString().toLowerCase() == shippingAddress.postcode.toString().toLowerCase() ||
           checkPostCodeWithRegex(cl.toString().toLowerCase(), shippingAddress.postcode.toString().toLowerCase())
    );
    isFound = checkBasedOnCondition(zoneCondition.condition, foundIndex);
  }

  return isFound;
};
```

**Wildcard Postal Codes** (`AutomationConditionsManager.js:21-28`):
```javascript
const checkPostCodeWithRegex = (rulePostCode, shippingPostCode) => {
  let result = false;
  if (rulePostCode.includes('*')) {
    const baseData = rulePostCode.substr(0, rulePostCode.indexOf('*'));
    result = shippingPostCode.startsWith(baseData, 0);
  }
  return result;
}
```

**Examples**:
- `zone: "US", condition: "=="` → Matches all US orders
- `zone: "US:CA", condition: "=="` → Matches California orders
- `zone: "90*", condition: "=="` → Matches postal codes starting with 90 (90001, 90210, etc.)
- `zone: ["CA", "MX"], condition: "!="` → Matches orders NOT going to Canada or Mexico

### 2. Store

**Field**: `conditionType: "store"`

**Purpose**: Match orders from specific e-commerce stores

**Model Fields**:
```javascript
{
  store: String,       // Store ID
  storeName: String,   // Human-readable store name
  storeType: String,   // Platform type (shopify, woocommerce, etc.)
  storeUUID: String,   // Store UUID
  condition: String    // '==' or '!='
}
```

**Matching Logic** (`AutomationConditionsManager.js:105-109`):
```javascript
checkIfStoreMatches(order, condition, automationHelperDataObject) {
  return checkBasedOnConditionOperator[condition.condition](
    condition.storeUUID,
    automationHelperDataObject.storeUUID
  );
}
```

**Examples**:
- Match orders from specific Shopify store
- Match orders from all WooCommerce stores (requires multiple conditions)
- Exclude orders from test store

### 3. Vendor

**Field**: `conditionType: "vendor"`

**Purpose**: Match orders assigned to specific vendors (multi-vendor marketplace)

**Model Fields**:
```javascript
{
  spVendorId: [String],  // Array of vendor IDs
  matchAll: Boolean,     // Match all vendors or any vendor
  condition: String      // '==' or '!='
}
```

**Matching Logic** (`AutomationConditionsManager.js:115-128`):
```javascript
checkIfVendorMatches(order, condition, automationHelperDataObject) {
  let success = condition.matchAll;

  if (condition.spVendorId.length > 1) {
    for (let index = 0; index < condition.spVendorId.length; index += 1) {
      success = checkBasedOnConditionOperator[condition.condition](
        condition.spVendorId[index],
        order.spVendorId
      );
      if (condition.matchAll ? !success : success) { // XOR operation
        return success;
      }
    }
  } else {
    return checkBasedOnConditionOperator[condition.condition](
      condition.spVendorId[0],
      order.spVendorId
    );
  }
  return success;
}
```

**Examples**:
- Match orders for Vendor A
- Match orders for Vendor A OR Vendor B
- Exclude orders from Vendor C

### 4. Quantity (Item Count)

**Field**: `conditionType: "quantity"`

**Purpose**: Match orders based on total item quantity

**Model Fields**:
```javascript
{
  minimumQuantity: Number,
  maximumQuantity: Number
}
```

**Matching Logic** (`AutomationConditionsManager.js:130-138`):
```javascript
checkIfQuantityMatches(order, condition, automationHelperDataObject) {
  let success = false;
  let totalQuantity = order.line_items.reduce((total, item) => total += item.quantity, 0);

  if ((totalQuantity >= condition.minimumQuantity) && (totalQuantity <= condition.maximumQuantity)) {
    success = true;
  }
  return success;
}
```

**Examples**:
- `min: 1, max: 5` → Matches orders with 1-5 items
- `min: 10, max: 999` → Matches bulk orders (10+ items)

### 5. Total Weight

**Field**: `conditionType: "totalWeight"`

**Purpose**: Match orders based on exact weight comparison

**Model Fields**:
```javascript
{
  totalWeight: Number,
  condition: String  // '==', '!=', '>', '<', '>=', '<='
}
```

**Matching Logic** (`AutomationConditionsManager.js:140-143`):
```javascript
checkIfTotalWeightMatches(order, condition, automationHelperDataObject) {
  const totalWeight = getTotalWeightFrom(order);
  return checkBasedOnConditionOperator[condition.condition](
    parseFloat(order.totalWeight || totalWeight),
    parseFloat(condition.totalWeight)
  );
}
```

**Weight Calculation** (`AutomationConditionsManager.js:46-53`):
```javascript
const getTotalWeightFrom = (order) => {
  const totalWeight = order.line_items.reduce(
    (acc, curr) => Number(acc) + Number(curr.quantity * curr.productInfo.weight),
    0
  );
  return order.totalWeight ? order.totalWeight : totalWeight;
};
```

**Examples**:
- `totalWeight: 10, condition: ">"` → Matches orders over 10 lbs/kg
- `totalWeight: 150, condition: "<="` → Matches orders 150 lbs or less

### 6. Total Weight Range

**Field**: `conditionType: "totalWeightRange"`

**Purpose**: Match orders within a weight range

**Model Fields**:
```javascript
{
  minimumTotalWeight: Number,
  maximumTotalWeight: Number
}
```

**Matching Logic** (`AutomationConditionsManager.js:169-176`):
```javascript
checkIfTotalWeightRangeMatches(order, condition, automationHelperDataObject) {
  const totalWeight = getTotalWeightFrom(order);
  let success = false;

  if ((totalWeight >= condition.minimumTotalWeight) && (totalWeight <= condition.maximumTotalWeight)) {
    success = true;
  }
  return success;
}
```

**Examples**:
- `min: 0, max: 10` → Small/light parcels
- `min: 10, max: 50` → Medium parcels
- `min: 50, max: 150` → Heavy parcels
- `min: 150, max: 999999` → Freight shipments

### 7. Price

**Field**: `conditionType: "price"`

**Purpose**: Match orders based on exact price comparison

**Model Fields**:
```javascript
{
  price: Number,
  condition: String  // '==', '!=', '>', '<', '>=', '<='
}
```

**Matching Logic** (`AutomationConditionsManager.js:144-146`):
```javascript
checkIfPriceMatches(order, condition, automationHelperDataObject) {
  return checkBasedOnConditionOperator[condition.condition](
    parseFloat(order.total),
    parseFloat(condition.price)
  );
}
```

**Examples**:
- `price: 100, condition: ">"` → Orders over $100
- `price: 500, condition: "<="` → Orders $500 or less

### 8. Total Price Range

**Field**: `conditionType: "totalPriceRange"`

**Purpose**: Match orders within a price range

**Model Fields**:
```javascript
{
  minimumTotalPrice: Number,
  maximumTotalPrice: Number
}
```

**Matching Logic** (`AutomationConditionsManager.js:178-185`):
```javascript
checkIfTotalPriceRangeMatches(order, condition, automationHelperDataObject) {
  let success = false;

  if ((order.total >= condition.minimumTotalPrice) && (order.total <= condition.maximumTotalPrice)) {
    success = true;
  }
  return success;
}
```

**Examples**:
- `min: 0, max: 50` → Low-value orders
- `min: 50, max: 200` → Medium-value orders
- `min: 200, max: 999999` → High-value orders (may require insurance)

### 9. Time

**Field**: `conditionType: "time"`

**Purpose**: Match orders created before/after a specific time of day

**Model Fields**:
```javascript
{
  hour: String,      // Hour (0-23)
  minute: String,    // Minute (0-59)
  timeZone: String,  // IANA timezone (e.g., "America/New_York")
  condition: String  // '<' (before) or '>' (after)
}
```

**Matching Logic** (`AutomationConditionsManager.js:148-154`):
```javascript
checkIfTimeMatches(order, condition, automationHelperDataObject) {
  const orderCreatedDate = momentTz(order.date_created);
  const orderCreatedTime = momentTz(moment(), condition.timeZone).set({
    hour: orderCreatedDate.hours(),
    minute: orderCreatedDate.minutes(),
    second: orderCreatedDate.seconds()
  });
  const cutOffTime = momentTz().tz(condition.timeZone).set({
    hour: condition.hour,
    minute: condition.minute
  });

  return checkBasedOnConditionOperatorForTime[condition.condition](orderCreatedTime, cutOffTime);
}
```

**Examples**:
- `hour: 14, minute: 0, condition: "<"` → Orders created before 2:00 PM (same-day shipping cutoff)
- `hour: 9, minute: 30, condition: ">"` → Orders created after 9:30 AM

**Use Case**: Same-day shipping cutoff times (orders before 2 PM ship today, orders after ship tomorrow)

### 10. Shipping Method

**Field**: `conditionType: "shippingMethod"`

**Purpose**: Match orders based on customer-selected shipping method

**Model Fields**:
```javascript
{
  shippingMethod: String,  // Method code or title
  condition: String        // '==' or '!='
}
```

**Matching Logic** (`AutomationConditionsManager.js:201-206`):
```javascript
checkIfShippingMethodMatches(order, condition, automationHelperDataObject) {
  let success = false;
  success = checkBasedOnConditionOperator[condition.condition](order.shippingMethodCode, condition.shippingMethod) ||
            checkBasedOnConditionOperator[condition.condition](order.shippingMethodTitle, condition.shippingMethod);
  return success;
}
```

**Examples**:
- Match "Expedited Shipping" method
- Match "Free Shipping" method
- Exclude "Standard Shipping" method

**Use Case**: Customer selects "Next Day Shipping" → automation sets FedEx Priority Overnight

### 11. PO Box Address

**Field**: `conditionType: "poBoxAddress"`

**Purpose**: Detect if shipping address is a PO Box

**Matching Logic** (`AutomationConditionsManager.js:187-199`):
```javascript
checkIfAddressIsPOBox(order, condition, automationHelperDataObject) {
  let address = '';
  const poBoxPatterns = config.automation.address.poBoxPatterns;

  if (order && order.shipping && order.shipping.address_1) {
    address = order.shipping.address_1;
  }

  return poBoxPatterns.some((pattern) => {
    const regex = new RegExp(pattern, 'i');
    return regex.test(address);
  });
}
```

**PO Box Patterns** (from config):
```javascript
[
  'P\\.?\\s*O\\.?\\s*Box',  // P.O. Box, PO Box, P O Box
  'Post\\s*Office\\s*Box',  // Post Office Box
  'PMB',                     // Private Mail Box
  'HC\\s*\\d+\\s*Box',       // Rural route box
  // ... more patterns
]
```

**Examples**:
- Detect "P.O. Box 123" → route to USPS (FedEx/UPS don't deliver to PO Boxes)
- Detect "PMB 456" → route to appropriate carrier

### 12. Any (Always True)

**Field**: `conditionType: "any"`

**Purpose**: Always matches (used as fallback/default rule)

**Matching Logic** (`AutomationConditionsManager.js:156-162`):
```javascript
checkIfAnyMatches(order, condition, automationHelperDataObject) {
  let success = true;
  if (order.storePepStatus == constants.NOT_TO_SHIP) {
    success = false;
  }
  return success;
}
```

**Examples**:
- Catchall rule: "If no other rules match, use default carrier"

## Condition Operators

**Supported Operators**:
- `==` - Equals
- `!=` - Not equals
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal

**Implementation** (`shared/storepepHelperFunctions/conditionCheckHelper.js`):
```javascript
const checkBasedOnConditionOperator = {
  '==': (actualValue, ruleValue) => actualValue == ruleValue,
  '!=': (actualValue, ruleValue) => actualValue != ruleValue,
  '>': (actualValue, ruleValue) => actualValue > ruleValue,
  '<': (actualValue, ruleValue) => actualValue < ruleValue,
  '>=': (actualValue, ruleValue) => actualValue >= ruleValue,
  '<=': (actualValue, ruleValue) => actualValue <= ruleValue,
};
```

## Condition Evaluation Flow

**Function**: `getMatchedAutomationConditions(order, conditions, automationHelperDataObject)`

**Location**: `AutomationConditionsManager.js:227-248`

**Algorithm**: All conditions must match (AND logic)

```javascript
async getMatchedAutomationConditions(order, conditions, automationHelperDataObject) {
  let success = true;

  for (let index = 0; index < conditions.length; index++) {
    const condition = conditions[index];

    // Dispatch to condition-specific matcher
    let result = await this.checkForAutomationConditionMatchesBasedOnConditionType[condition.conditionType](
      order,
      condition,
      automationHelperDataObject
    );

    // If ANY condition fails, rule doesn't match
    if (!result) {
      success = false;
      break;  // Short-circuit: stop evaluating remaining conditions
    }
  }

  return success;
}
```

**Condition Type Dispatcher** (`AutomationConditionsManager.js:209-224`):
```javascript
this.checkForAutomationConditionMatchesBasedOnConditionType = {
  zone: this.checkIfZoneMatches.bind(this),
  store: this.checkIfStoreMatches,
  vendor: this.checkIfVendorMatches,
  quantity: this.checkIfQuantityMatches,
  totalWeight: this.checkIfTotalWeightMatches,
  price: this.checkIfPriceMatches,
  time: this.checkIfTimeMatches,
  totalWeightRange: this.checkIfTotalWeightRangeMatches,
  any: this.checkIfAnyMatches,
  totalPriceRange: this.checkIfTotalPriceRangeMatches,
  shippingMethod: this.checkIfShippingMethodMatches,
  poBoxAddress: this.checkIfAddressIsPOBox,
};
```

## Multi-Condition Examples

### Example 1: Domestic Heavy Orders
```javascript
// Rule: "Domestic orders over 50 lbs use FedEx Freight"
Conditions:
1. Zone = "US" (AND)
2. Total Weight Range: min 50, max 999999 (AND)

Result: Matches US orders weighing 50+ lbs
```

### Example 2: High-Value International
```javascript
// Rule: "International orders over $500 require insurance"
Conditions:
1. Zone != "US" (AND)
2. Total Price Range: min 500, max 999999 (AND)

Result: Matches non-US orders over $500
```

### Example 3: Same-Day Shipping Cutoff
```javascript
// Rule: "Orders before 2 PM use same-day pickup"
Conditions:
1. Time < 14:00 (AND)
2. Zone = "US" (AND)
3. Shipping Method == "Expedited" (AND)

Result: Matches expedited US orders created before 2 PM
```

## Limitations

1. **AND Logic Only**: All conditions must match; no OR logic available
2. **No Negation**: Can't negate within a condition (must create separate rule)
3. **No Nested Conditions**: Can't group conditions like "(A AND B) OR (C AND D)"
4. **No Custom Functions**: Can't define custom condition logic
5. **Fixed Condition Types**: Limited to 12 predefined types

**Workarounds**:
- OR logic: Create multiple rules with same actions
- Negation: Use `!=` operator or create inverse rule
- Complex logic: Break into multiple sequential rules

## Dependencies

- [Automation Overview](./automation-overview.md) - Rule engine and execution flow
- [Automation Actions](./automation-actions.md) - Actions applied when conditions match
- [Shipping Zones](#) - Zone definition for geographic conditions
- [Order Lifecycle](../orders/order-lifecycle.md) - Order data structure

## Referenced By

- Automation engine evaluates conditions for every order
- Rule creation UI presents condition types
- Debugging tools show which conditions matched/failed

## Configuration

**Condition Mapper** (`automationConditionsAndActionsMapper.js`):
```javascript
const conditionsMapper = {
  ZONE: 'zone',
  STORE: 'store',
  VENDOR: 'vendor',
  QUANTITY: 'quantity',
  TOTAL_WEIGHT: 'totalWeight',
  PRICE: 'price',
  TIME: 'time',
  TOTAL_WEIGHT_RANGE: 'totalWeightRange',
  ANY: 'any',
  TOTAL_PRICE_RANGE: 'totalPriceRange',
  SHIPPING_METHOD: 'shippingMethod',
  PO_BOX_ADDRESS: 'poBoxAddress',
};
```

## Related Pages

- [Automation Overview](./automation-overview.md)
- [Automation Actions](./automation-actions.md)
- [Order Lifecycle](../orders/order-lifecycle.md)
