---
title: Product Management
category: module
domain: products
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Product Management

## Overview

Product management handles **product catalog data** imported from e-commerce stores, including product variants, SKUs, inventory levels, dimensions/weight, and carrier-specific metadata (dangerous goods, harmonization codes, delivery signatures). Products serve as the master data source for order line items during order processing and label generation.

**Purpose**: Centralized product catalog with shipping-related attributes
- **Physical attributes**: Weight, dimensions for rate calculation
- **Customs data**: HS codes, country of origin for international shipping
- **Carrier requirements**: Dangerous goods, alcohol, dry ice declarations
- **Inventory**: Stock levels for warehouse selection

**Location**: `server/src/models/products.js`, `server/src/shared/products/`

## Architecture

### Product Data Model

**Model**: `ProductsNew`

**Location**: `server/src/models/products.js:6-191`

**Schema** (191 lines):
```javascript
{
  // Core identification
  productUUID: String,  // Internal UUID
  productId: Number,  // Store product ID
  storeProductId: String,  // Store's string ID (some platforms use strings)
  inventoryItemId: Number,  // Shopify inventory item ID
  sku: String,  // Stock Keeping Unit

  // Store linkage
  storeUUID: String,
  storeType: String,  // SHOPIFY, WOOCOMMERCE, etc.
  storeName: String,
  accountUUID: String,
  vendorUUID: String,  // For multi-vendor marketplaces

  // Product hierarchy
  productType: String,  // SIMPLE, GROUPED, VARIABLE, VARIANT, SUBSCRIPTION
  parentId: Number,  // For variants: parent product ID
  masterProductId: Number,  // Top-level product ID
  storeMasterProductId: String,
  childIds: [Number],  // For grouped/variable products

  // Basic info
  name: String,
  shortDescription: String,
  description: String,
  total: Number,  // Price
  currency: String,

  // Physical attributes
  weight: Number,
  length: Number,
  width: Number,
  height: Number,
  weightUnit: String,  // kg, lb, oz, g
  dimensionsUnit: String,  // cm, in

  // Shipping settings
  isShippingRequired: Boolean,  // Digital products = false
  excludeFromShipping: Boolean,  // Exclude from shipping calculations

  // Images
  productImage: {
    id: String,
    src: String  // URL
  },
  productImagesList: [{
    id: String,
    src: String
  }],

  // Inventory
  stock: {
    quantity: Number
  },

  // Categorization
  categories: [{
    id: String,
    name: String
  }],
  tags: [String],
  shippingClass: String,  // WooCommerce shipping class
  shippingClassId: String,

  // Customs/International
  harmonizationCode: String,  // HS code for customs
  importCommodityCode: String,
  countryOfManufacture: String,
  stateOfManufacture: String,
  districtOfManufacture: String,
  isTaxable: Boolean,

  // Vendor (multi-vendor)
  vendorName: String,

  // Carrier-specific: Delivery Signature
  isDeliverySignatureRequired: Boolean,
  deliverySignature: {
    [constants.FEDEX_CARRIER_CODE]: {
      optionType: String  // 'DIRECT', 'INDIRECT', 'ADULT', 'NO_SIGNATURE_REQUIRED'
    },
    [constants.UPS_CARRIER_CODE]: {
      dCISType: String  // '1' = Signature Required, '2' = Adult Signature
    },
    [constants.USPS_CARRIER_CODE]: {
      signatureType: String
    },
    [constants.PUROLATOR_CARRIER_CODE]: {
      optionType: String
    },
    [constants.EASYPOST_CARRIER_CODE]: {
      optionType: String
    }
  },

  // Carrier-specific: Dry Ice
  isDryIcePresent: Boolean,
  dryIce: {
    common: {
      weight: String,
      weightUnit: String  // kg, lb
    },
    [constants.UPS_CARRIER_CODE]: {
      regulationSet: String  // 'CFR', 'IATA'
    }
  },

  // Carrier-specific: Dangerous Goods
  isDangerousGoodsPresent: Boolean,
  dangerousGoods: {
    common: {
      uNCode: String,  // UN1234
      technicalName: String,
      classDivision: String,  // '3', '4.1', '8', etc.
      packagingGroup: String  // 'I', 'II', 'III'
    },
    [constants.DHL_CARRIER_CODE]: {
      contentId: String,
      labelDesc: String
    },
    [constants.FEDEX_CARRIER_CODE]: {
      regulation: String,  // 'IATA', 'DOT', 'CFR'
      accessibility: String,  // 'ACCESSIBLE', 'INACCESSIBLE'
      batteryMaterialType: String,
      batteryPackingType: String,
      batteryRegulatorySubType: String,
      isCargoAircraftOnly: Boolean,
      isOtherDangerousGoods: Boolean,
      isBattery: Boolean,
      options: String
    },
    [constants.UPS_CARRIER_CODE]: {
      chemicalRecordIdentifier: String,
      properShippingName: String,
      commodityRegulatedLevelCode: String,  // 'LQ' = Limited Quantity, 'FR' = Fully Regulated
      packagingType: String,
      packagingGroupType: String,
      transportationMode: String,  // 'GROUND', 'AIR'
      regulationSet: String  // 'CFR', 'IATA'
    },
    [constants.AUSTRALIA_POST_CARRIER_CODE]: {
      transportableByAir: Boolean,
      dgDeclaration: String
    },
    [constants.AMAZON_SHIPPING_CARRIER_CODE]: {
      dgPackingInstructions: String,
      liquidVolume: Number,
      liquidVolumeUnit: String
    }
  },

  // Carrier-specific: Alcohol
  isAlcoholPresent: Boolean,
  alcohol: {
    [constants.FEDEX_CARRIER_CODE]: {
      recipientType: String  // 'LICENSEE', 'CONSUMER'
    }
  },

  // Carrier-specific: Restricted Articles (UPS)
  enableRestrictedArticle: Boolean,
  restrictedArticle: {
    [constants.UPS_CARRIER_CODE]: {
      DiagnosticSpecimensIndicator: Boolean,
      AlcoholicBeveragesIndicator: Boolean,
      PerishablesIndicator: Boolean,
      PlantsIndicator: Boolean,
      SeedsIndicator: Boolean,
      SpecialExceptionsIndicator: Boolean,
      TobaccoIndicator: Boolean,
      ECigarettesIndicator: Boolean,
      HempCBDIndicator: Boolean
    }
  },

  // Pre-packed products
  isPrePacked: Boolean,  // Product already packaged (no additional packaging needed)

  // Insurance/Value
  declaredValue: Number,  // Declared value for customs
  customInsuredValue: Number,  // Custom insurance amount

  // Freight
  freightClass: String,  // NMFC freight class (50, 55, 60, ..., 500)

  // Document shipments
  isDocument: Boolean,  // Document-only shipment (no physical goods)

  // Unique identifier
  productIdentifier: String,  // Custom identifier

  // Metadata
  fullResponse: Object,  // Store's full product response
  isActive: Boolean,
  date_created: Date,
  date_modified: Date,
  createdBy: String,
  updatedBy: String
}
```

### Product Types

**Product Type Enum**:
```javascript
productType: {
  enum: [
    constants.PRODUCT_TYPE_SIMPLE,              // 'SIMPLE'
    constants.PRODUCT_TYPE_GROUPED,             // 'GROUPED'
    constants.PRODUCT_TYPE_VARIABLE,            // 'VARIABLE'
    constants.PRODUCT_TYPE_VARIANT,             // 'VARIANT'
    constants.PRODUCT_TYPE_SUBSCRIPTION,        // 'SUBSCRIPTION'
    constants.PRODUCT_TYPE_VARIABLE_SUBSCRIPTION // 'VARIABLE_SUBSCRIPTION'
  ]
}
```

**Type Definitions**:

1. **SIMPLE**: Single product with no variations
   ```javascript
   {
     productType: 'SIMPLE',
     productId: 123,
     name: 'Blue T-Shirt',
     sku: 'TSHIRT-BLUE',
     weight: 0.5,
     total: 19.99
   }
   ```

2. **VARIABLE**: Parent product with variants
   ```javascript
   {
     productType: 'VARIABLE',
     productId: 456,
     name: 'T-Shirt',  // Parent name
     childIds: [789, 790, 791],  // Variant IDs
     // No SKU/weight/price at parent level
   }
   ```

3. **VARIANT**: Child of variable product
   ```javascript
   {
     productType: 'VARIANT',
     productId: 789,
     parentId: 456,  // Links to parent
     name: 'T-Shirt - Blue / Large',
     sku: 'TSHIRT-BLUE-L',
     weight: 0.5,
     total: 19.99
   }
   ```

4. **GROUPED**: Bundle of simple products
   ```javascript
   {
     productType: 'GROUPED',
     productId: 999,
     name: 'Starter Pack',
     childIds: [100, 101, 102]  // Simple product IDs
   }
   ```

5. **SUBSCRIPTION**: Recurring product (WooCommerce Subscriptions)
   ```javascript
   {
     productType: 'SUBSCRIPTION',
     productId: 555,
     name: 'Monthly Coffee Subscription',
     sku: 'COFFEE-SUB',
     total: 29.99  // Per billing period
   }
   ```

### SKU Management

**SKU Uniqueness**: SKUs should be unique per store (but not enforced by database)

**SKU Lookup**:
```javascript
async function findProductBySKU(storeUUID, sku) {
  return await ProductsNew.findOne({
    storeUUID,
    sku,
    isActive: true
  });
}
```

**Use Cases**:
- Order line item matching during import
- Inventory updates from store webhooks
- CSV import/export operations

## Product-Order Relationship

### Line Item Matching

**When order imported**, line items reference products:

```javascript
// Order line item
{
  productId: 123,
  variantId: 789,
  sku: 'TSHIRT-BLUE-L',
  name: 'Blue T-Shirt - Large',
  quantity: 2,
  price: 19.99,
  weight: 0  // Initially 0, populated from product
}

// Product lookup during order processing
const product = await ProductsNew.findOne({
  storeUUID: order.storeUUID,
  $or: [
    { productId: lineItem.productId },
    { productId: lineItem.variantId },
    { sku: lineItem.sku }
  ]
});

if (product) {
  // Populate line item with product data
  lineItem.weight = product.weight;
  lineItem.dimensions = {
    length: product.length,
    width: product.width,
    height: product.height
  };
  lineItem.harmonizationCode = product.harmonizationCode;
  lineItem.countryOfManufacture = product.countryOfManufacture;
  lineItem.isDangerousGoodsPresent = product.isDangerousGoodsPresent;
}
```

### Package Weight Calculation

**Total package weight** = sum of line item weights:

```javascript
function calculatePackageWeight(lineItems) {
  let totalWeight = 0;

  for (const item of lineItems) {
    const itemWeight = item.weight || 0;
    totalWeight += itemWeight * item.quantity;
  }

  return totalWeight;
}
```

**Example**:
```
Line Item 1: Blue T-Shirt (0.5 kg) × 2 = 1.0 kg
Line Item 2: Red Hat (0.2 kg) × 1 = 0.2 kg
Package Total Weight = 1.2 kg
```

## Carrier-Specific Product Metadata

### Dangerous Goods Declaration

**Purpose**: Required for shipping hazardous materials (chemicals, batteries, aerosols)

**Common Fields**:
```javascript
dangerousGoods: {
  common: {
    uNCode: 'UN1266',  // UN identification number
    technicalName: 'Perfumery Products',
    classDivision: '3',  // Flammable liquid
    packagingGroup: 'III'  // Low danger
  }
}
```

**FedEx-Specific**:
```javascript
dangerousGoods: {
  [constants.FEDEX_CARRIER_CODE]: {
    regulation: 'IATA',  // International Air Transport Association
    accessibility: 'ACCESSIBLE',
    isCargoAircraftOnly: false,  // Can ship on passenger aircraft
    isBattery: true,
    batteryMaterialType: 'LITHIUM_ION',
    batteryPackingType: 'PACKED_WITH_EQUIPMENT'
  }
}
```

**Use Case**: Label generation includes dangerous goods declaration on shipping label

### Delivery Signature Requirements

**Purpose**: Product-level signature requirements (high-value items, age-restricted)

**Example**: Alcohol product (FedEx)
```javascript
{
  isAlcoholPresent: true,
  isDeliverySignatureRequired: true,
  deliverySignature: {
    [constants.FEDEX_CARRIER_CODE]: {
      optionType: 'ADULT'  // Adult signature required (21+)
    }
  },
  alcohol: {
    [constants.FEDEX_CARRIER_CODE]: {
      recipientType: 'CONSUMER'  // vs 'LICENSEE' for business
    }
  }
}
```

**Automation Integration**:
```javascript
// If ANY line item requires signature, apply to entire order
const requiresSignature = order.line_items.some(item => {
  const product = getProduct(item.productId);
  return product?.isDeliverySignatureRequired;
});

if (requiresSignature) {
  order.signatureConfirmation = { isRequired: true };
}
```

### Dry Ice

**Purpose**: Products shipped with dry ice (perishables, medical)

**Example**:
```javascript
{
  isDryIcePresent: true,
  dryIce: {
    common: {
      weight: '2.5',
      weightUnit: 'kg'
    },
    [constants.UPS_CARRIER_CODE]: {
      regulationSet: 'CFR'  // Code of Federal Regulations
    }
  }
}
```

**Label Generation**: Dry ice weight added to special services request

### Harmonization Codes

**Purpose**: HS codes for customs classification (international shipments)

**Example**:
```javascript
{
  harmonizationCode: '6109.10.00',  // T-shirts, knitted
  countryOfManufacture: 'CN',  // China
  stateOfManufacture: 'Guangdong',
  isTaxable: true
}
```

**Customs Form Integration**:
```javascript
// Commercial invoice line item
{
  description: product.name,
  quantity: lineItem.quantity,
  unitPrice: lineItem.price,
  hsCode: product.harmonizationCode,
  countryOfOrigin: product.countryOfManufacture,
  weight: lineItem.weight
}
```

## Inventory Management

### Stock Tracking

**Inventory Field**:
```javascript
stock: {
  quantity: 50  // Available quantity
}
```

**Inventory Update** (from store webhook):
```javascript
async function updateInventory(storeUUID, productId, newQuantity) {
  await ProductsNew.updateOne(
    { storeUUID, productId },
    { $set: { 'stock.quantity': newQuantity } }
  );
}
```

### Warehouse Integration

**WMS (Warehouse Management System)** uses product inventory for warehouse selection:

**Location**: `server/src/modules/wms/services/WarehouseSelectionContext.js:22-44`

```javascript
async function findWarehousesWithStock({ accountUUID, storeUUID, products }) {
  const query = {
    accountUUID,
    storeUUID,
    channelVariantId: { $in: products.map(({ channelVariantId }) => channelVariantId) },
    quantity: { $gt: 0 }  // Only warehouses with stock
  };

  const inventory = await WarehouseProjections.find(query).lean();

  // Group by warehouse
  const warehouses = {};
  inventory.forEach(({ channelVariantId, quantity, warehouseId }) => {
    warehouses[warehouseId] = warehouses[warehouseId] || { products: {} };
    warehouses[warehouseId].products[channelVariantId] = quantity;
  });

  // Filter warehouses with sufficient stock for ALL products
  const sufficient = Object.values(warehouses).filter(({ products: warehouseProducts }) =>
    products.every(({ channelVariantId, quantity }) =>
      (warehouseProducts[channelVariantId] || 0) >= quantity
    )
  );

  return sufficient.map(({ warehouseId }) => warehouseId);
}
```

See [Warehouse Selection](../warehouses/warehouse-selection.md)

## Product Sync

### Import from Store

**Triggered by**:
- Manual "Import Products" button
- Auto-import schedule (if `productAutoImport: true`)
- Product webhook (real-time)

**Example**: Shopify Product Import

**Location**: `server/src/shared/API/stores/shopify/products/ShopifyProductImportService.js`

```javascript
async function importProduct({ shopifyProduct, store, action = 'create' }) {
  // 1. Map Shopify product to StorePep format
  const mappedProduct = await mapShopifyToStorePepProduct(shopifyProduct, store);

  // 2. Check if product exists
  const existingProduct = await ProductsNew.findOne({
    storeUUID: store.storeUUID,
    productId: shopifyProduct.id
  });

  if (existingProduct) {
    // Update existing
    await ProductsNew.updateOne(
      { _id: existingProduct._id },
      { $set: mappedProduct }
    );
  } else {
    // Create new
    const newProduct = new ProductsNew(mappedProduct);
    await newProduct.save();
  }

  // 3. Import variants
  if (shopifyProduct.variants && shopifyProduct.variants.length > 1) {
    for (const variant of shopifyProduct.variants) {
      const variantMapped = await mapShopifyToStorePepProduct(shopifyProduct, store, variant);
      await importProduct({ shopifyProduct: variantMapped, store, action });
    }
  }
}
```

### Export to Store (Inventory Sync)

**Update store inventory** after fulfillment:

```javascript
async function syncInventoryToStore(product, newQuantity) {
  const store = await Stores.findOne({ storeUUID: product.storeUUID });

  if (store.storeType === constants.SHOPIFY_STORE_CODE) {
    const shopify = new Shopify({ /* credentials */ });

    await shopify.inventoryLevel.set({
      inventory_item_id: product.inventoryItemId,
      location_id: store.defaultLocationId,
      available: newQuantity
    });
  } else if (store.storeType === constants.WOOCOMMERCE_STORE_CODE) {
    const wooCommerce = new WooCommerce({ /* credentials */ });

    await wooCommerce.putAsync(`products/${product.productId}`, {
      stock_quantity: newQuantity
    });
  }

  // Update local inventory
  product.stock.quantity = newQuantity;
  await product.save();
}
```

## API Endpoints

**Location**: `server/src/routes/products.js`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/getallproducts` | POST | List all products for store |
| `/getproductdetails` | POST | Get single product details |
| `/addproduct` | POST | Manually add product |
| `/updateproduct` | POST | Update product attributes |
| `/deleteproduct` | POST | Soft-delete product (isActive = false) |
| `/importproducts` | POST | Trigger product import from store |
| `/syncproducts` | POST | Sync product data with store |
| `/updateinventory` | POST | Update stock quantity |
| `/bulkupdateproducts` | POST | Batch update products |

## Common Patterns

### Create Product

```javascript
const product = new ProductsNew({
  productUUID: generateUUID(),
  storeUUID: 'store-uuid',
  accountUUID: 'account-uuid',
  productType: constants.PRODUCT_TYPE_SIMPLE,
  productId: 123,
  sku: 'TSHIRT-BLUE',
  name: 'Blue T-Shirt',
  weight: 0.5,
  weightUnit: 'kg',
  length: 30,
  width: 25,
  height: 2,
  dimensionsUnit: 'cm',
  total: 19.99,
  currency: 'USD',
  stock: { quantity: 100 },
  harmonizationCode: '6109.10.00',
  countryOfManufacture: 'US',
  isActive: true
});

await product.save();
```

### Add Dangerous Goods Metadata

```javascript
const product = await ProductsNew.findOne({ sku: 'PERFUME-001' });

product.isDangerousGoodsPresent = true;
product.dangerousGoods = {
  common: {
    uNCode: 'UN1266',
    technicalName: 'Perfumery Products',
    classDivision: '3',
    packagingGroup: 'III'
  },
  [constants.FEDEX_CARRIER_CODE]: {
    regulation: 'IATA',
    accessibility: 'ACCESSIBLE',
    isCargoAircraftOnly: false
  }
};

await product.save();
```

### Lookup Product by SKU

```javascript
const product = await ProductsNew.findOne({
  storeUUID: 'store-uuid',
  sku: 'TSHIRT-BLUE-L',
  isActive: true
});

if (product) {
  console.log(`Product: ${product.name}, Weight: ${product.weight}${product.weightUnit}`);
}
```

## Known Issues / Tech Debt

1. **No SKU uniqueness constraint**: Duplicate SKUs possible (should be unique per store)
2. **Complex carrier fields**: Nested carrier-specific objects make schema hard to maintain
3. **No product versioning**: Changes overwrite existing data (no history)
4. **Large schema**: 191-line model with many optional fields
5. **No validation**: Missing weight/dimensions not validated (causes label failures)
6. **fullResponse bloat**: Storing entire store response increases document size
7. **No product relationships**: Grouped products store child IDs but no inverse lookup

## Related Pages

- [Product Import/Export](./product-import-export.md) - CSV import/export and store sync
- [Store Integration Overview](../stores/store-integration-overview.md) - Product sync from stores
- [Warehouse Selection](../warehouses/warehouse-selection.md) - Inventory-based warehouse selection
- [Label Generation](../shipping/label-generation.md) - Uses product metadata for customs
