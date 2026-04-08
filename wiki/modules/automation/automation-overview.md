---
title: Automation Overview
category: module
domain: automation
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Automation Overview

## Overview

Automation is the **core business logic engine** of StorePep that processes every incoming order through a rule-based system. Automation rules define conditions (e.g., "if order total > $100") and actions (e.g., "use FedEx Ground") to automatically configure carrier selection, package dimensions, addresses, and special services without manual intervention.

**Core Value**: Automation eliminates repetitive manual configuration for high-volume shipping operations by applying business rules consistently to all orders.

**Every order flows through automation** during the order processing lifecycle.

## Architecture

### Rule Engine Components

**Location**: `server/src/shared/storepepAutomation/`

**Core Classes**:
1. **StorepepAutomationManager** (`StorepepAutomationManager.js:15-67`) - Orchestrates automation execution
2. **StorePepAutomationDataEngine** (`storePepAutomationDataEngine.js:16-113`) - Matches rules to orders
3. **AutomationConditionsManager** (`AutomationConditionsManager.js:55-...`) - Evaluates conditions
4. **AutomationActionsManager** (`AutomationActionsManager.js:98-...`) - Applies actions

### Data Models

**AutomationSetting** (`models/automationSettings.js:5-20`):
```javascript
{
  automationId: String,         // Unique rule ID
  accountUUID: String,          // Account owning this rule
  vendorUUID: String,           // Vendor scope (for multi-vendor)
  active: Boolean,              // Rule enabled/disabled
  ruleName: String,             // Human-readable rule name
  automationConditionUUID: String, // Link to conditions
  sequenceNumber: Number,       // Execution priority (lower = first)
  groupNumber: Number,          // Rule grouping
  ruleInfo: String,             // Human-readable summary of rule
  createdBy: String,
  updatedBy: String
}
```

**AutomationConditions** (`models/automationConditions.js:5-57`) - See [Automation Conditions](./automation-conditions.md)

**AutomationActions** (`models/automationActions.js:5-99`) - See [Automation Actions](./automation-actions.md)

## Execution Flow

### 1. Trigger Points

Automation executes when:
- **Order imported** from e-commerce platform
- **Order status changes** to `PROCESSING`
- **Manual re-run** via "Re-run Automation" button
- **Bulk action** applies automation to multiple orders

### 2. Entry Point

**Function**: `packageAutomation(orders, currentUser, accountUUID, vendorUUID, newSocketEvent, context)`

**Location**: `StorepepAutomationManager.js:16-44`

**Flow**:
```javascript
async packageAutomation(orders, currentUser, accountUUID, vendorUUID, newSocketEvent, context) {
  // 1. Fetch all active automation rules for this account
  const automationRulesForThisAccount = await findAutomationSettingWithSort({
    accountUUID,
    vendorUUID,
    active: true,
  }, {
    sequenceNumber: 1,  // Sort by priority
  });

  // 2. Process each order through all rules
  for (let i = 0; i < orders.length; i += 1) {
    const order = orders[i];
    const automationHelperDataObject = {
      storeUUID: order.storeUUID,
      vendorUUID,
      accountUUID,
      currentUser
    };

    // 3. Apply automation to this order
    await new StorePepAutomationDataEngine()
      .getAutomationSettingsDataForOrder(
        order,
        automationRulesForThisAccount,
        automationHelperDataObject,
        context
      );
  }

  // 4. Emit completion event for real-time updates
  if (newSocketEvent) {
    const subOrderUUIDs = orders.map(({ subOrderUUID }) => subOrderUUID);
    EventPublisher.emit(new OrderPackageAutomationFlowCompleted({ accountUUID, subOrderUUIDs }));
  }
}
```

### 3. Rule Matching Loop

**Function**: `getAutomationSettingsDataForOrder(order, automationRules, automationHelperDataObject, context)`

**Location**: `storePepAutomationDataEngine.js:55-111`

**Flow**:
```javascript
async getAutomationSettingsDataForOrder(order, automationRules, automationHelperDataObject, context) {
  let totalMatchedRules = 0;

  // Process rules in priority order (sequenceNumber)
  for (let index = 0; index < automationRules.length; index += 1) {
    const automationRule = automationRules[index];

    // 1. Fetch fresh order data
    const orderToProcess = await findOneOrderWithLean({
      subOrderUUID: order.subOrderUUID,
      storeUUID: order.storeUUID,
      accountUUID: automationHelperDataObject.accountUUID
    });

    // 2. Fetch packages for this order
    const packagesToProcess = await findPackagesWithLean({
      subOrderUUID: order.subOrderUUID,
      storeUUID: order.storeUUID,
      accountUUID: automationHelperDataObject.accountUUID,
      packageType: constants.PACKAGE_TYPE_STORED_PACKAGE
    });

    // 3. Fetch conditions for this rule
    const automationConditionsFromDb = await findAutomationConditions({
      accountUUID: automationRule.accountUUID,
      automationId: automationRule.automationId,
      automationConditionUUID: automationRule.automationConditionUUID
    });

    if (!automationConditionsFromDb.length) {
      continue; // No conditions = skip rule
    }

    // 4. Check if ALL conditions match this order
    const matchedCondition = await new AutomationConditionsManager()
      .getMatchedAutomationConditions(
        orderToProcess,
        automationConditionsFromDb,
        automationHelperDataObject
      );

    if (!matchedCondition) {
      continue; // Conditions didn't match, try next rule
    }

    // 5. Conditions matched! Fetch actions
    const actionsFromDb = await findAutomationActions({
      accountUUID: automationRule.accountUUID,
      automationId: automationRule.automationId
    });

    if (!actionsFromDb.length) {
      continue; // No actions defined
    }

    // 6. Apply all actions to the order
    const { order, orderUpdatedFields, packages } = await new AutomationActionsManager()
      .applyActionsToOrderAndReturnOrder(
        orderToProcess,
        packagesToProcess,
        actionsFromDb
      );

    // 7. Save changes to database
    await this.updateActionAppliedOrder(
      order,
      orderUpdatedFields,
      packages,
      automationHelperDataObject
    );

    totalMatchedRules += 1;
  }

  // 8. If NO rules matched, add error to order
  if (!totalMatchedRules) {
    const updateObject = {
      processErrors: {
        hasError: true,
        message: 'There is no matching Automation rules. Please make sure you have a Matching Automation rule by Adding or Editing your rules @ Automation settings.',
        level: constants.ERROR_LEVELS.LEVEL_1,
      },
    };
    await findOneOrderAndUpdate({ subOrderUUID: order.subOrderUUID }, updateObject);
  }
}
```

### 4. Condition Evaluation

**All conditions must match** for the rule to apply (AND logic).

**Function**: `getMatchedAutomationConditions(order, conditions, automationHelperDataObject)`

**Location**: `AutomationConditionsManager.js`

**Condition Types Checked**:
1. Zone (shipping destination)
2. Store (which e-commerce platform)
3. Vendor (multi-vendor marketplace)
4. Quantity (item count range)
5. Weight (total weight range)
6. Price (order total range)
7. Time (time-based scheduling)
8. Shipping Method (customer-selected method)

See [Automation Conditions](./automation-conditions.md) for detailed condition logic.

### 5. Action Application

**Once conditions match**, all actions execute sequentially.

**Function**: `applyActionsToOrderAndReturnOrder(order, packages, actions)`

**Location**: `AutomationActionsManager.js`

**Action Types Applied**:
1. Set carrier/service (with fallback)
2. Set package dimensions
3. Set package weight
4. Adjust package weight (+/- percentage)
5. Set ship-from address
6. Set sold-to address
7. Map order meta to shipping address
8. Set third-party billing
9. Set duties/taxes payer
10. Add insurance
11. Add delivery confirmation (signature)
12. Add carrier-specific special services
13. Add Saturday delivery
14. Map address fields to order meta

See [Automation Actions](./automation-actions.md) for detailed action logic.

### 6. Database Updates

**Updated after actions apply**:

**Order Fields**:
```javascript
{
  availableCarrierAndService: [],  // Carrier/service options from automation
  shipFromAddress: {},             // Origin address
  displayFromAddress: {},          // Display address (if different)
  soldToAddress: {},               // Sold-to address (accounting)
  totalWeight: Number,             // Adjusted weight
  isInsuranceRequired: Boolean,
  signatureConfirmation: { isRequired: Boolean },
  adultSignatureConfirmation: { isRequired: Boolean },
  shipmentChargePayerAccountNumber: String,
  shipmentChargePayerAddress: {},
  dutiesAndTaxesPayer: String,
  dutiesAndTaxesPayerAccountNumber: String,
  dutiesPayerAddress: {},
  dhlSpecialServices: { specialServices: [] },
  canadaPostSpecialServices: [],
  // ... more carrier-specific fields
  updatedBy: String
}
```

**Package Fields**:
```javascript
{
  carrierTypeSelected: String,
  carrierIdSelected: String,
  serviceTypeSelected: String,
  dimensions: { length: Number, width: Number, height: Number },
  totalWeight: Number,
  products: [],  // Product weights may be adjusted
  isCarrierSet: Boolean,
  updatedBy: String
}
```

## Rule Priority and Sequencing

### Sequence Number

**Field**: `automationSetting.sequenceNumber`

**Purpose**: Determines execution order of rules

**Behavior**:
- Rules sorted by `sequenceNumber: 1` (ascending)
- Lower number = higher priority (executes first)
- Rule #1 (sequenceNumber=1) runs before Rule #2 (sequenceNumber=2)

**Example**:
```
Rule 1: sequenceNumber=1, "Domestic orders use UPS"
Rule 2: sequenceNumber=2, "Heavy orders use FedEx Freight"
Rule 3: sequenceNumber=3, "International orders use DHL"
```

An order matching **both Rule 1 and Rule 2** will:
1. Execute Rule 1 first → Sets UPS
2. Execute Rule 2 next → Overwrites with FedEx Freight
3. **Final result**: FedEx Freight

### First Match Wins vs All Rules Apply

**Current Behavior**: **All matching rules execute** in sequence order.

**Implication**: Later rules can overwrite earlier rules' settings.

**Best Practice**: Order rules from most specific to least specific, with higher-priority rules having lower sequence numbers.

**Alternative Pattern** (not currently implemented): "First match wins" would stop after the first matching rule.

## Group Numbers

**Field**: `automationSetting.groupNumber`

**Purpose**: Logical grouping of related rules (UI organization)

**Note**: Currently used for display purposes only, does not affect execution logic.

## Rule Info String

**Field**: `automationSetting.ruleInfo`

**Purpose**: Human-readable summary of the rule's conditions and actions

**Example**:
```
"If order total > $100 and destination = US, then use FedEx Ground with insurance"
```

**Generation**: Typically generated by frontend when rule is created/updated

**Usage**: Displayed in automation rule list for quick scanning

## Error Handling

### No Matching Rules

**Scenario**: Order doesn't match ANY automation rules

**Behavior**:
```javascript
if (!totalMatchedRules) {
  const updateObject = {
    processErrors: {
      hasError: true,
      message: 'There is no matching Automation rules. Please make sure you have a Matching Automation rule by Adding or Editing your rules @ Automation settings.',
      level: constants.ERROR_LEVELS.LEVEL_1,
    },
  };
  await findOneOrderAndUpdate({ subOrderUUID: order.subOrderUUID }, updateObject);
}
```

**Result**: Order blocked from label generation with error displayed

**Resolution**: Merchant must add/edit automation rules to cover this order scenario

### Action Failures

**Scenario**: Action throws error (e.g., invalid address UUID)

**Behavior**: Error caught and logged, automation continues with next rule

**Location**: `storePepAutomationDataEngine.js:26-37` (try-catch wrapper)

## Integration with Order Lifecycle

### When Automation Runs

**Order Import Flow**:
```
1. Order imported from store (Shopify, WooCommerce, etc.)
2. Order status = INITIAL
3. Order transitions to PROCESSING
4. → Automation runs ← (packageAutomation called)
5. Actions applied (carrier set, dimensions set, etc.)
6. Rate shopping triggered (if carrier not set yet)
7. Service selection (cheapest, fastest, or preferred)
8. Order ready for label generation
```

**Manual Re-run**:
- User clicks "Re-run Automation" button
- Clears existing automation-applied settings
- Re-runs all rules from scratch

**Bulk Actions**:
- "Apply Automation" bulk action
- Runs automation on selected orders
- Useful after adding/editing automation rules

## Warehouse Integration

**WMS (Warehouse Management System)** integration can override automation-set addresses:

**Function**: `setShipFromAddress()`

**Location**: `AutomationActionsManager.js:192-207`

```javascript
async setShipFromAddress(order, packagesToProcess, action, orderUpdatedFields) {
  // 1. Set address from automation action
  order.shipFromAddress = await getShipFromAddress({
    addressUUID: action.addressUUID,
    isActive: true,
    status: constants.IN_USE
  });

  // 2. If WMS enabled, warehouse selection overrides automation address
  if (await wmsEnabledFor(order.accountUUID)) {
    const selectedWarehouse = await selectWarehouseForOrder(order);
    if (selectedWarehouse) {
      order.shipFromAddress = await getShipFromAddress({
        addressUUID: selectedWarehouse.addressUUID
      });
    }
  }

  orderUpdatedFields = Object.assign(orderUpdatedFields, { shipFromAddress: '' });
  return { order, actionAppliedPackage: packagesToProcess, orderUpdatedFields };
}
```

**Behavior**: WMS warehouse selection (geo-based, address-based) takes precedence over automation rules.

## Event Sourcing

### Event Published

**Event**: `OrderPackageAutomationFlowCompleted`

**Location**: `orders/events/index.js`

**Payload**:
```javascript
{
  accountUUID: String,
  subOrderUUIDs: [String]  // Array of order UUIDs that completed automation
}
```

**Purpose**:
- Real-time UI updates via Socket.io
- Downstream processing triggers (rate shopping, label generation)
- Audit trail of automation execution

## API Endpoints

**Location**: `server/src/routes/automation.js`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/add` | POST | Create new automation rule |
| `/update` | POST | Update existing rule |
| `/getautomationsettings` | POST | List all rules for account |
| `/getautomationsettingsforthisid` | POST | Get single rule details |
| `/removethisautomationsettings` | POST | Delete rule |
| `/saveautomationpriority` | POST | Reorder rule priority (sequenceNumber) |
| `/rerunautomation` | POST | Re-run automation on failed orders |

## Dependencies

- [Automation Conditions](./automation-conditions.md) - Condition types and matching logic
- [Automation Actions](./automation-actions.md) - Action types and application logic
- [Order Lifecycle](../orders/order-lifecycle.md) - Integration with order processing
- [Carrier System](../shipping/carrier-system-overview.md) - Carrier/service selection
- [Warehouses/WMS](../warehouses/warehouse-selection.md) - Warehouse selection overrides

## Referenced By

- Order processing triggers automation for every order
- Bulk actions can re-run automation
- Rate shopping uses carrier/service from automation
- Label generation depends on automation-configured settings

## Configuration

**Account Settings**:
- Automation enabled/disabled globally
- Preferred carrier selection feature toggle

**Rule Settings**:
- Per-rule active/inactive toggle
- Sequence number for priority
- Group number for organization

## Common Patterns

### Create Basic Automation Rule

```javascript
// 1. Create automation setting
const automationSetting = new AutomationSetting({
  automationId: generateUUID(),
  accountUUID: "account-uuid",
  vendorUUID: "vendor-uuid",
  active: true,
  ruleName: "Domestic orders use UPS Ground",
  automationConditionUUID: generateUUID(),
  sequenceNumber: 1,
  ruleInfo: "If destination = US, then use UPS Ground"
});
await automationSetting.save();

// 2. Create condition (destination = US)
const automationCondition = new AutomationConditions({
  automationId: automationSetting.automationId,
  automationConditionUUID: automationSetting.automationConditionUUID,
  accountUUID: "account-uuid",
  conditionType: "zone",
  condition: "==",
  zone: "US"
});
await automationCondition.save();

// 3. Create action (set UPS Ground)
const automationAction = new AutomationActions({
  automationId: automationSetting.automationId,
  accountUUID: "account-uuid",
  actionType: "setCarrierService",
  preferredCarrier: "ups-carrier-id",
  carrierType: "C3",
  preferredService: ["03"], // UPS Ground service code
  carrierName: "UPS"
});
await automationAction.save();
```

### Re-run Automation for Order

```javascript
const order = await findOneOrderWithLean({ subOrderUUID: "order-uuid" });

// Clear existing automation settings
order.availableCarrierAndService = [];
order.shipFromAddress = null;
// ... clear other automation-set fields

await order.save();

// Re-run automation
await new StorepepAutomationManager().packageAutomation(
  [order],
  currentUser,
  accountUUID,
  vendorUUID,
  true,  // emit socket event
  context
);
```

## Known Issues / Tech Debt

1. **All rules execute**: No "first match wins" option causes later rules to overwrite earlier ones
2. **No OR logic**: All conditions must match (AND only), no way to say "condition A OR condition B"
3. **No condition negation within rule**: Can't say "NOT zone US" (must create separate rule)
4. **Action ordering**: Actions execute in database order, not explicit sequence
5. **No rollback**: If action fails mid-way, partial changes persist
6. **No dry-run mode**: Can't preview what automation would do without applying it
7. **Limited audit trail**: No detailed log of which rule matched and why

## Related Pages

- [Automation Conditions](./automation-conditions.md)
- [Automation Actions](./automation-actions.md)
- [Order Lifecycle](../orders/order-lifecycle.md)
- [Carrier System Overview](../shipping/carrier-system-overview.md)
- [Warehouse Selection](../warehouses/warehouse-selection.md)
