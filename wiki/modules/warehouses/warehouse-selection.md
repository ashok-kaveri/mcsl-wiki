---
title: Warehouse Selection
category: module
domain: warehouses
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Warehouse Selection

## Overview

Warehouse selection is the **WMS (Warehouse Management System) module** that automatically selects the optimal warehouse to fulfill an order based on inventory availability, geographic proximity, and custom routing rules. The system uses a Strategy Pattern to support multiple selection algorithms and integrates with Odoo ERP for enterprise warehouse management.

**Core Value**: Automates multi-warehouse fulfillment by selecting the best warehouse for each order based on configurable business rules

**Location**: `server/src/modules/wms/`

**Key Features**:
- Strategy-based warehouse selection (geo-distance, address-based)
- Inventory-aware routing (only warehouses with stock)
- Overrides automation-configured ship-from address
- Odoo ERP integration for enterprise WMS

## Architecture

### WMS Module Structure

```
modules/wms/
├── index.js                          # Entry point
├── featureLoader.js                  # Feature flag loader
├── services/
│   ├── WarehouseSelectionContext.js  # Strategy context
│   └── OdooClientService.js          # Odoo integration
├── strategies/
│   ├── GeoDistanceStrategy.js        # Geo-based selection
│   └── AddressBasedStrategy.js       # Rule-based selection
├── interfaces/
│   └── WarehouseSelectionStrategy.js # Strategy interface
└── errors/
    ├── WarehouseNotFoundError.js
    └── WarehouseIdNotFoundError.js
```

### Strategy Pattern

**Interface**: `WarehouseSelectionStrategy`

**Location**: `server/src/modules/wms/interfaces/WarehouseSelectionStrategy.js`

```javascript
class WarehouseSelectionStrategy {
  async select(order, warehouseIds, rules) {
    throw new Error('Strategy must implement select method');
  }
}
```

**Strategies**:
1. **GeoDistanceStrategy**: Select nearest warehouse by distance
2. **AddressBasedStrategy**: Select based on address matching rules

### Warehouse Selection Context

**Location**: `server/src/modules/wms/services/WarehouseSelectionContext.js:58-95`

**Class**: `WarehouseSelectionContext`

```javascript
class WarehouseSelectionContext {
  constructor() {
    this.strategies = {
      GEOLOCATION: new GeoDistanceStrategy(),
      ADDRESS_BASED: new AddressBasedStrategy()
    };
  }

  async execute(order) {
    const {
      accountUUID,
      storeUUID,
      subOrderUUID,
      line_items: lineItems = []
    } = order;

    const context = `order [${subOrderUUID}] with account [${accountUUID}] and store [${storeUUID}]`;

    // 1. Fetch routing strategy and rules
    const { strategy, rules } = await findRoutingStrategyAndRulesUsing({
      accountUUID,
      storeUUID,
      context
    });

    // 2. Get strategy implementation
    const selectedStrategy = this.strategies[strategy];
    if (!selectedStrategy) {
      throw new Error(`Unknown Routing Strategy: ${strategy}`);
    }

    // 3. Find warehouses with sufficient stock
    const products = lineItems.map(({ product_id: productId, quantity }) => ({
      channelVariantId: productId.toString(),
      quantity
    }));

    const warehouseIds = await findWarehousesWithStock({
      accountUUID,
      storeUUID,
      products
    });

    // 4. Execute strategy to select warehouse
    const warehouse = await run(strategy, selectedStrategy, order, warehouseIds, rules, context);

    return warehouse;
  }
}
```

## Entry Point

**Function**: `selectWarehouseForOrder(order)`

**Location**: `server/src/modules/wms/index.js:7-16`

```javascript
async function selectWarehouseForOrder(order) {
  try {
    const context = new WarehouseSelectionContext();
    return await context.execute(order);
  } catch (error) {
    logger.error('Failed to select warehouse:', error);
    throw error;
  }
}

module.exports = {
  selectWarehouseForOrder
};
```

**Called From**: `AutomationActionsManager.js:192-207` (setShipFromAddress action)

```javascript
async setShipFromAddress(order, packagesToProcess, action, orderUpdatedFields) {
  // 1. Set address from automation
  order.shipFromAddress = await getShipFromAddress({
    addressUUID: action.addressUUID,
    isActive: true,
    status: constants.IN_USE
  });

  // 2. WMS warehouse selection OVERRIDES automation address
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

**Behavior**: WMS selection takes priority over automation rules

## Selection Strategies

### 1. Geo-Distance Strategy

**Strategy Name**: `GEOLOCATION`

**Location**: `server/src/modules/wms/strategies/GeoDistanceStrategy.js:11-44`

**Algorithm**: Select warehouse nearest to customer shipping address using geospatial query

```javascript
class GeoDistanceStrategy extends WarehouseSelectionStrategy {
  async select(order, warehouseIds) {
    const {
      accountUUID,
      storeUUID,
      shipping: { latitude, longitude } = {}
    } = order;

    // MongoDB geospatial query
    const warehouses = await warehouse.aggregate([
      {
        $geoNear: {
          near: { type: 'Point', coordinates: [longitude, latitude] },
          distanceField: 'distance',
          maxDistance: MAX_SEARCH_DISTANCE_METERS,  // 100 km
          spherical: true,
          key: 'location',
          query: {
            accountUUID,
            storeUUID,
            warehouseId: { $in: warehouseIds }  // Only warehouses with stock
          }
        }
      },
      {
        $limit: 10
      },
      {
        $project: {
          _id: 1,
          warehouseId: 1,
          name: 1,
          addressUUID: 1,
          location: 1,
          distance: 1
        }
      }
    ]).exec();

    if (!warehouses || !warehouses.length) {
      throw new WarehouseNotFoundError(
        `no warehouses found within ${MAX_SEARCH_DISTANCE_METERS} meters`
      );
    }

    // Return nearest warehouse
    return warehouses[0];
  }
}
```

**Requirements**:
- Customer shipping address must have latitude/longitude
- Warehouses must have geolocation data (GeoJSON Point)
- MongoDB geospatial index on `warehouse.location` field

**Warehouse Location Data**:
```javascript
{
  warehouseId: 'WH-001',
  name: 'Main Warehouse',
  addressUUID: 'address-uuid',
  location: {
    type: 'Point',
    coordinates: [-122.4194, 37.7749]  // [longitude, latitude]
  }
}
```

**Use Case**: Multi-warehouse retailers wanting to minimize shipping distance/cost

### 2. Address-Based Strategy

**Strategy Name**: `ADDRESS_BASED`

**Location**: `server/src/modules/wms/strategies/AddressBasedStrategy.js`

**Algorithm**: Select warehouse based on custom routing rules (e.g., state, zip code, country)

**Routing Rules Example**:
```javascript
{
  accountUUID: 'account-uuid',
  storeUUID: 'store-uuid',
  strategy: 'ADDRESS_BASED',
  rules: [
    {
      priority: 1,
      conditions: {
        country: 'US',
        state: 'CA'
      },
      warehouseId: 'WH-CA-001'  // West Coast warehouse
    },
    {
      priority: 2,
      conditions: {
        country: 'US',
        state: ['NY', 'NJ', 'CT']
      },
      warehouseId: 'WH-NY-001'  // East Coast warehouse
    },
    {
      priority: 3,
      conditions: {
        country: 'US'
      },
      warehouseId: 'WH-TX-001'  // Default US warehouse
    }
  ]
}
```

**Implementation**:
```javascript
class AddressBasedStrategy extends WarehouseSelectionStrategy {
  async select(order, warehouseIds, rules) {
    const { shipping } = order;

    // Sort rules by priority
    const sortedRules = rules.sort((a, b) => a.priority - b.priority);

    for (const rule of sortedRules) {
      const { conditions, warehouseId } = rule;

      // Check if warehouse has stock
      if (!warehouseIds.includes(warehouseId)) {
        continue;
      }

      // Match conditions
      let matches = true;

      if (conditions.country && shipping.countryCode !== conditions.country) {
        matches = false;
      }

      if (conditions.state) {
        const states = Array.isArray(conditions.state) ? conditions.state : [conditions.state];
        if (!states.includes(shipping.stateOrProvinceCode)) {
          matches = false;
        }
      }

      if (conditions.postalCodePrefix && !shipping.postalCode.startsWith(conditions.postalCodePrefix)) {
        matches = false;
      }

      if (matches) {
        // Found matching warehouse
        const warehouse = await Warehouse.findOne({ warehouseId });
        return warehouse;
      }
    }

    throw new WarehouseNotFoundError('No warehouse matches address rules');
  }
}
```

**Use Case**: Complex routing logic (regional warehouses, international splits)

## Inventory Filtering

**Before strategy execution**, filter warehouses with sufficient stock:

**Function**: `findWarehousesWithStock({ accountUUID, storeUUID, products })`

**Location**: `WarehouseSelectionContext.js:22-44`

```javascript
async function findWarehousesWithStock({ accountUUID, storeUUID, products }) {
  // 1. Query warehouse projections (inventory snapshots)
  const query = {
    accountUUID,
    storeUUID,
    channelVariantId: { $in: products.map(({ channelVariantId }) => channelVariantId) },
    quantity: { $gt: 0 }
  };

  const inventory = await WarehouseProjections.find(query, {
    channelVariantId: 1,
    quantity: 1,
    warehouseId: 1
  }).lean();

  if (!inventory || !inventory.length) {
    return [];
  }

  // 2. Group inventory by warehouse
  const warehouses = {};
  inventory.forEach(({ channelVariantId, quantity, warehouseId }) => {
    warehouses[warehouseId] = warehouses[warehouseId] || { warehouseId, products: {} };
    warehouses[warehouseId].products[channelVariantId] = (
      warehouses[warehouseId].products[channelVariantId] || 0
    ) + quantity;
  });

  // 3. Filter warehouses with SUFFICIENT stock for ALL products
  const sufficient = Object.values(warehouses).filter(({ products: warehouseProducts }) =>
    products.every(({ channelVariantId, quantity }) =>
      (warehouseProducts[channelVariantId] || 0) >= quantity
    )
  );

  return sufficient.map(({ warehouseId }) => warehouseId);
}
```

**Behavior**:
- Only warehouses with stock for **ALL line items** are considered
- Prevents split shipments (order fulfilled from single warehouse)
- If no warehouse has full stock, selection fails

## Routing Configuration

**Model**: `StoreOrderRoutingStrategy`

**Location**: `server/src/models/storeOrderRoutingStrategy.js`

**Schema**:
```javascript
{
  accountUUID: String,
  storeUUID: String,
  strategy: String,  // 'GEOLOCATION', 'ADDRESS_BASED'
  rules: [{
    priority: Number,
    conditions: {
      country: String,
      state: [String],
      postalCodePrefix: String
    },
    warehouseId: String
  }],
  isActive: Boolean
}
```

**Configuration Example**:
```javascript
const routingStrategy = new StoreOrderRoutingStrategy({
  accountUUID: 'account-uuid',
  storeUUID: 'store-uuid',
  strategy: 'GEOLOCATION',
  rules: [],  // No rules needed for geo-based
  isActive: true
});

await routingStrategy.save();
```

**Fetching Strategy**:

**Function**: `findRoutingStrategyAndRulesUsing({ accountUUID, storeUUID, context })`

**Location**: `WarehouseSelectionContext.js:10-20`

```javascript
async function findRoutingStrategyAndRulesUsing({ accountUUID, storeUUID, context }) {
  const { strategy = null, rules = [] } = await StoreOrderRoutingStrategy.findOne({
    accountUUID,
    storeUUID
  }).lean() || {};

  if (!strategy) {
    throw new Error(`No routing strategy configured for ${context}`);
  }

  logger.info(`Found routing strategy [${strategy}] with [${rules.length}] rules for ${context}`);
  return { strategy, rules };
}
```

## Warehouse Data Model

**Model**: `Warehouse`

**Location**: `server/src/models/warehouse.js`

**Schema**:
```javascript
{
  warehouseId: String,  // Unique warehouse ID
  accountUUID: String,
  storeUUID: String,
  name: String,
  addressUUID: String,  // Links to shipFromAddress

  // Geolocation
  location: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: [Number]  // [longitude, latitude]
  },

  // Status
  isActive: Boolean,
  isPrimary: Boolean,  // Default warehouse

  // Metadata
  createdBy: String,
  updatedBy: String
}
```

**Geospatial Index**:
```javascript
warehouseSchema.index({ location: '2dsphere' });  // Required for $geoNear
```

**Warehouse Projections** (Inventory):

**Model**: `WarehouseProjections`

**Schema**:
```javascript
{
  accountUUID: String,
  storeUUID: String,
  warehouseId: String,
  channelVariantId: String,  // Product variant ID
  quantity: Number,
  lastUpdated: Date
}
```

**Example**:
```javascript
{
  warehouseId: 'WH-001',
  storeUUID: 'store-uuid',
  channelVariantId: '123456',  // Product ID
  quantity: 50
}
```

## Odoo Integration

**Purpose**: Enterprise WMS integration with Odoo ERP

**Location**: `server/src/modules/wms/services/OdooClientService.js`

**Features**:
- Sync warehouses from Odoo to StorePep
- Sync inventory levels from Odoo
- Push order fulfillment status to Odoo

**Connection**:
```javascript
class OdooClientService {
  constructor(config) {
    this.odoo = new Odoo({
      url: config.odooUrl,
      port: config.odooPort,
      db: config.odooDatabase,
      username: config.odooUsername,
      password: config.odooPassword
    });
  }

  async syncWarehouses(accountUUID, storeUUID) {
    // Fetch warehouses from Odoo
    const odooWarehouses = await this.odoo.search_read('stock.warehouse', [
      ['active', '=', true]
    ], ['name', 'partner_id', 'code']);

    for (const odooWH of odooWarehouses) {
      // Map Odoo warehouse to StorePep
      const warehouse = new Warehouse({
        warehouseId: odooWH.code,
        accountUUID,
        storeUUID,
        name: odooWH.name,
        // ... map location from partner address
      });

      await warehouse.save();
    }
  }

  async syncInventory(warehouseId) {
    // Fetch stock levels from Odoo
    const stockQuants = await this.odoo.search_read('stock.quant', [
      ['location_id.warehouse_id.code', '=', warehouseId],
      ['quantity', '>', 0]
    ], ['product_id', 'quantity']);

    for (const quant of stockQuants) {
      await WarehouseProjections.updateOne(
        {
          warehouseId,
          channelVariantId: quant.product_id[0].toString()
        },
        {
          $set: { quantity: quant.quantity, lastUpdated: new Date() }
        },
        { upsert: true }
      );
    }
  }
}
```

## Feature Flags

**Function**: `wmsEnabledFor(accountUUID)`

**Location**: `server/src/modules/wms/featureLoader.js`

```javascript
async function wmsEnabledFor(accountUUID) {
  return await features.isEnabled('wms-warehouse-selection', accountUUID);
}

module.exports = {
  wmsEnabledFor
};
```

**Usage**:
```javascript
if (await wmsEnabledFor(order.accountUUID)) {
  const warehouse = await selectWarehouseForOrder(order);
  order.shipFromAddress = warehouse.address;
}
```

## Integration with Automation

**Automation Action**: `SET_SHIPPING_FROM_ADDRESS`

**Flow**:
```
1. Automation rule matches order
2. Action sets ship-from address (UUID from automation config)
   → order.shipFromAddress = automationAddress

3. WMS enabled check
   → if wmsEnabledFor(accountUUID) === true

4. Warehouse selection runs
   → warehouse = selectWarehouseForOrder(order)
   → Check inventory availability
   → Execute strategy (geo or address-based)
   → Return warehouse with addressUUID

5. WMS OVERRIDES automation address
   → order.shipFromAddress = warehouseAddress

6. Label generation uses WMS-selected address
```

**Code**:

**Location**: `AutomationActionsManager.js:192-207`

```javascript
async setShipFromAddress(order, packagesToProcess, action, orderUpdatedFields) {
  // Step 1: Set from automation
  order.shipFromAddress = await getShipFromAddress({
    addressUUID: action.addressUUID,
    isActive: true,
    status: constants.IN_USE
  });

  // Step 2: WMS override
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

## Common Patterns

### Configure Geo-Based Routing

```javascript
const routingStrategy = new StoreOrderRoutingStrategy({
  accountUUID: 'account-uuid',
  storeUUID: 'store-uuid',
  strategy: 'GEOLOCATION',
  rules: [],
  isActive: true
});

await routingStrategy.save();
```

### Configure Address-Based Routing

```javascript
const routingStrategy = new StoreOrderRoutingStrategy({
  accountUUID: 'account-uuid',
  storeUUID: 'store-uuid',
  strategy: 'ADDRESS_BASED',
  rules: [
    {
      priority: 1,
      conditions: { country: 'US', state: 'CA' },
      warehouseId: 'WH-CA-001'
    },
    {
      priority: 2,
      conditions: { country: 'CA' },
      warehouseId: 'WH-CANADA-001'
    },
    {
      priority: 3,
      conditions: { country: 'US' },
      warehouseId: 'WH-US-DEFAULT'
    }
  ],
  isActive: true
});

await routingStrategy.save();
```

### Add Warehouse

```javascript
const warehouse = new Warehouse({
  warehouseId: 'WH-001',
  accountUUID: 'account-uuid',
  storeUUID: 'store-uuid',
  name: 'Main Warehouse',
  addressUUID: 'address-uuid',
  location: {
    type: 'Point',
    coordinates: [-122.4194, 37.7749]  // San Francisco
  },
  isActive: true,
  isPrimary: true
});

await warehouse.save();
```

## Known Issues / Tech Debt

1. **No split shipment support**: If no warehouse has full stock, selection fails (should support multi-warehouse fulfillment)
2. **100km search radius hardcoded**: `MAX_SEARCH_DISTANCE_METERS` not configurable
3. **No fallback strategy**: If primary strategy fails, no secondary strategy attempted
4. **Address geocoding required**: Geo strategy needs lat/long (not always available from stores)
5. **No warehouse priority**: Cannot prefer specific warehouse over others
6. **Odoo integration incomplete**: Only basic sync implemented
7. **No inventory reservation**: Stock quantity not reserved during selection (race condition possible)

## Related Pages

- [Automation Actions](../automation/automation-actions.md) - WMS overrides automation address
- [Product Management](../products/product-management.md) - Inventory data source
- [Order Lifecycle](../orders/order-lifecycle.md) - Integration with order processing
