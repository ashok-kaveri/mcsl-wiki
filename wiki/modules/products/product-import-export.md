---
title: Product Import/Export
category: module
domain: products
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Product Import/Export

## Overview

Product import/export enables **bulk product management** through CSV files and automated store synchronization. Merchants can import products from e-commerce platforms (Shopify, WooCommerce, Magento), export product catalogs for offline editing, and update StorePep product metadata in batch operations.

**Core Features**:
- CSV import/export for bulk product management
- Store-to-StorePep product synchronization
- Batch product updates
- Variant handling for variable products
- Inventory sync between store and StorePep

**Location**: `server/src/shared/products/`, `server/src/shared/API/stores/*/products/`

## Import Methods

### 1. Store Sync Import

**Purpose**: Import products from connected e-commerce store

**Trigger Points**:
- Manual "Import Products" button
- Auto-import schedule (cron job)
- Product webhook (real-time)

#### Shopify Import

**Location**: `server/src/shared/API/stores/shopify/products/ShopifyProductImportService.js`

**Flow**:
```javascript
async function importProductsFromShopify(store, options = {}) {
  const shopify = new Shopify({
    shopName: store.storeName,
    apiKey: store.consumerKey,
    password: store.password
  });

  // 1. Fetch products from Shopify
  let page = 1;
  let hasMore = true;
  const allProducts = [];

  while (hasMore) {
    const products = await shopify.product.list({
      limit: 250,
      page,
      fields: 'id,title,variants,body_html,images,tags,product_type'
    });

    allProducts.push(...products);

    if (products.length < 250) {
      hasMore = false;
    } else {
      page++;
    }
  }

  // 2. Process each product
  for (const shopifyProduct of allProducts) {
    // Map parent product
    const mappedProduct = await mapShopifyToStorePepProduct(shopifyProduct, store);

    // Save or update product
    await upsertProduct(mappedProduct);

    // Import variants
    if (shopifyProduct.variants && shopifyProduct.variants.length > 1) {
      for (const variant of shopifyProduct.variants) {
        const variantMapped = await mapShopifyToStorePepProduct(
          shopifyProduct,
          store,
          variant
        );
        await upsertProduct(variantMapped);
      }
    }
  }

  // 3. Update last import time
  store.lastProductImportedTime = new Date();
  await store.save();

  return { imported: allProducts.length };
}
```

**GraphQL Bulk Import** (for large catalogs):

**Location**: `server/src/shared/API/stores/shopify/batch/ShopifyProductImport.js`

```javascript
async function bulkImportProducts(store) {
  const shopifyGraphQLClient = new ShopifyClient({
    shop: store.storeName,
    accessToken: store.accessToken
  });

  // 1. Initiate bulk operation
  const mutation = `
    mutation {
      bulkOperationRunQuery(
        query: """
        {
          products {
            edges {
              node {
                id
                title
                descriptionHtml
                variants {
                  edges {
                    node {
                      id
                      sku
                      price
                      inventoryQuantity
                      weight
                      weightUnit
                    }
                  }
                }
              }
            }
          }
        }
        """
      ) {
        bulkOperation {
          id
          status
        }
      }
    }
  `;

  const result = await shopifyGraphQLClient.mutate({ mutation });
  const operationId = result.bulkOperationRunQuery.bulkOperation.id;

  // 2. Poll for completion
  let completed = false;
  while (!completed) {
    const statusQuery = `
      query {
        node(id: "${operationId}") {
          ... on BulkOperation {
            id
            status
            url
          }
        }
      }
    `;

    const status = await shopifyGraphQLClient.query({ query: statusQuery });

    if (status.node.status === 'COMPLETED') {
      completed = true;

      // 3. Download JSONL file
      const response = await axios.get(status.node.url);
      const lines = response.data.split('\n');

      // 4. Process each product
      for (const line of lines) {
        if (!line) continue;

        const product = JSON.parse(line);
        const mapped = await mapShopifyToStorePepProduct(product, store);
        await upsertProduct(mapped);
      }
    } else if (status.node.status === 'FAILED') {
      throw new Error('Bulk import failed');
    } else {
      await sleep(5000);  // Wait 5 seconds
    }
  }
}
```

#### WooCommerce Import

**Location**: `server/src/shared/API/stores/woocommerce/products/WoocommerceProductImportService.js`

```javascript
async function importProductsFromWooCommerce(store, options = {}) {
  const WooCommerce = require('woocommerce-api');

  const wooCommerce = new WooCommerce({
    url: store.url,
    consumerKey: store.consumerKey,
    consumerSecret: store.consumerSecret,
    wpAPI: true,
    version: 'wc/v3'
  });

  // 1. Fetch products (paginated)
  let page = 1;
  let hasMore = true;
  const allProducts = [];

  while (hasMore) {
    const result = await wooCommerce.getAsync('products', {
      per_page: 100,
      page
    });

    const products = JSON.parse(result.body);
    allProducts.push(...products);

    if (products.length < 100) {
      hasMore = false;
    } else {
      page++;
    }
  }

  // 2. Process each product
  for (const wcProduct of allProducts) {
    const mappedProduct = await mapWoocommerceToStorepepProduct(wcProduct, store);
    await upsertProduct(mappedProduct);

    // Import variations
    if (wcProduct.type === 'variable') {
      const variationsResult = await wooCommerce.getAsync(
        `products/${wcProduct.id}/variations`,
        { per_page: 100 }
      );

      const variations = JSON.parse(variationsResult.body);

      for (const variation of variations) {
        const variantMapped = await mapWoocommerceToStorepepProduct(
          variation,
          store,
          wcProduct  // Parent product
        );
        await upsertProduct(variantMapped);
      }
    }
  }

  store.lastProductImportedTime = new Date();
  await store.save();

  return { imported: allProducts.length };
}
```

### 2. CSV Import

**Purpose**: Bulk import products from CSV file

**CSV Format**:
```csv
sku,name,weight,weightUnit,length,width,height,dimensionsUnit,price,currency,stock,harmonizationCode,countryOfManufacture
TSHIRT-BLUE,Blue T-Shirt,0.5,kg,30,25,2,cm,19.99,USD,100,6109.10.00,US
HAT-RED,Red Hat,0.2,kg,20,20,10,cm,14.99,USD,50,6505.00.90,CN
```

**Implementation**:
```javascript
async function importProductsFromCSV(file, storeUUID, accountUUID) {
  const csv = require('csv-parser');
  const fs = require('fs');

  const products = [];

  return new Promise((resolve, reject) => {
    fs.createReadStream(file.path)
      .pipe(csv())
      .on('data', (row) => {
        products.push({
          productUUID: generateUUID(),
          storeUUID,
          accountUUID,
          productType: constants.PRODUCT_TYPE_SIMPLE,
          sku: row.sku,
          name: row.name,
          weight: parseFloat(row.weight),
          weightUnit: row.weightUnit,
          length: parseFloat(row.length),
          width: parseFloat(row.width),
          height: parseFloat(row.height),
          dimensionsUnit: row.dimensionsUnit,
          total: parseFloat(row.price),
          currency: row.currency,
          stock: { quantity: parseInt(row.stock) },
          harmonizationCode: row.harmonizationCode,
          countryOfManufacture: row.countryOfManufacture,
          isActive: true
        });
      })
      .on('end', async () => {
        // Batch insert
        await ProductsNew.insertMany(products);
        resolve({ imported: products.length });
      })
      .on('error', reject);
  });
}
```

**API Endpoint**:
```javascript
router.post('/importcsv', upload.single('file'), async (req, res) => {
  try {
    const { storeUUID, accountUUID } = req.body;
    const result = await importProductsFromCSV(req.file, storeUUID, accountUUID);

    res.json({
      success: true,
      message: `Imported ${result.imported} products`,
      data: result
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});
```

## Export Methods

### 1. CSV Export

**Purpose**: Export product catalog for offline editing

**CSV Generation**:
```javascript
async function exportProductsToCSV(storeUUID) {
  const products = await ProductsNew.find({
    storeUUID,
    isActive: true
  }).lean();

  const csvStringifier = require('csv-stringify/sync');

  const csvData = products.map(product => ({
    sku: product.sku,
    name: product.name,
    weight: product.weight,
    weightUnit: product.weightUnit,
    length: product.length,
    width: product.width,
    height: product.height,
    dimensionsUnit: product.dimensionsUnit,
    price: product.total,
    currency: product.currency,
    stock: product.stock?.quantity || 0,
    harmonizationCode: product.harmonizationCode,
    countryOfManufacture: product.countryOfManufacture,
    productType: product.productType,
    parentSku: product.parentId ? getParentSKU(product.parentId) : ''
  }));

  const csv = csvStringifier.stringify(csvData, {
    header: true,
    columns: [
      'sku', 'name', 'weight', 'weightUnit', 'length', 'width', 'height',
      'dimensionsUnit', 'price', 'currency', 'stock', 'harmonizationCode',
      'countryOfManufacture', 'productType', 'parentSku'
    ]
  });

  return csv;
}
```

**API Endpoint**:
```javascript
router.post('/exportcsv', async (req, res) => {
  try {
    const { storeUUID } = req.body;
    const csv = await exportProductsToCSV(storeUUID);

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=products.csv');
    res.send(csv);
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});
```

### 2. Export to Store

**Purpose**: Push product updates back to e-commerce store

**Shopify Export**:
```javascript
async function updateProductInShopify(product, store) {
  const shopify = new Shopify({
    shopName: store.storeName,
    apiKey: store.consumerKey,
    password: store.password
  });

  await shopify.product.update(product.productId, {
    variants: [{
      id: product.inventoryItemId,
      price: product.total,
      weight: product.weight,
      weight_unit: product.weightUnit
    }]
  });
}
```

**WooCommerce Export**:
```javascript
async function updateProductInWooCommerce(product, store) {
  const WooCommerce = require('woocommerce-api');

  const wooCommerce = new WooCommerce({
    url: store.url,
    consumerKey: store.consumerKey,
    consumerSecret: store.consumerSecret
  });

  await wooCommerce.putAsync(`products/${product.productId}`, {
    regular_price: product.total.toString(),
    weight: product.weight.toString(),
    stock_quantity: product.stock?.quantity
  });
}
```

## Batch Operations

### Batch Product Update

**Purpose**: Update multiple products at once

**Implementation**:
```javascript
async function batchUpdateProducts(updates) {
  const bulkOps = updates.map(update => ({
    updateOne: {
      filter: { productUUID: update.productUUID },
      update: { $set: update.fields }
    }
  }));

  const result = await ProductsNew.bulkWrite(bulkOps);

  return {
    modified: result.modifiedCount,
    matched: result.matchedCount
  };
}
```

**API Endpoint**:
```javascript
router.post('/bulkupdate', async (req, res) => {
  try {
    const { updates } = req.body;
    // updates = [
    //   { productUUID: 'uuid-1', fields: { weight: 0.6, total: 21.99 } },
    //   { productUUID: 'uuid-2', fields: { stock: { quantity: 75 } } }
    // ]

    const result = await batchUpdateProducts(updates);

    res.json({
      success: true,
      message: `Updated ${result.modified} products`,
      data: result
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});
```

## Variant Handling

### Import Variable Products

**WooCommerce Variant Iterator**:

**Location**: `server/src/shared/API/stores/woocommerce/products/variantIterator.js`

```javascript
async function getVariants({ product, store, accountUUID }) {
  if (product.type !== 'variable' && product.type !== 'variable-subscription') {
    return [];
  }

  const WooCommerce = require('woocommerce-api');

  const wooCommerce = new WooCommerce({
    url: store.url,
    consumerKey: store.consumerKey,
    consumerSecret: store.consumerSecret
  });

  // Fetch all variations
  const result = await wooCommerce.getAsync(
    `products/${product.id}/variations`,
    { per_page: 100 }
  );

  const variations = JSON.parse(result.body);

  return variations;
}
```

**Shopify Variant Import**:
```javascript
async function importShopifyVariants(shopifyProduct, store) {
  if (!shopifyProduct.variants || shopifyProduct.variants.length <= 1) {
    return;
  }

  for (const variant of shopifyProduct.variants) {
    const mappedVariant = {
      productUUID: generateUUID(),
      productType: constants.PRODUCT_TYPE_VARIANT,
      parentId: shopifyProduct.id,
      productId: variant.id,
      inventoryItemId: variant.inventory_item_id,
      storeUUID: store.storeUUID,
      accountUUID: store.accountUUID,

      // Variant-specific
      name: `${shopifyProduct.title} - ${variant.title}`,
      sku: variant.sku,
      total: parseFloat(variant.price),
      weight: variant.weight,
      weightUnit: variant.weight_unit,

      // Variant options
      option1: variant.option1,  // e.g., 'Blue'
      option2: variant.option2,  // e.g., 'Large'
      option3: variant.option3,

      // Inventory
      stock: { quantity: variant.inventory_quantity }
    };

    await ProductsNew.findOneAndUpdate(
      { storeUUID: store.storeUUID, productId: variant.id },
      { $set: mappedVariant },
      { upsert: true }
    );
  }
}
```

## Inventory Sync

### Store to StorePep

**Shopify Inventory Webhook**:
```javascript
router.post('/webhooks/shopify/inventory-update', async (req, res) => {
  try {
    const { inventory_item_id, available } = req.body;

    // Find product by inventory item ID
    const product = await ProductsNew.findOne({
      inventoryItemId: inventory_item_id
    });

    if (product) {
      product.stock.quantity = available;
      await product.save();
    }

    res.sendStatus(200);
  } catch (error) {
    errorLogger('Inventory webhook error:', error);
    res.sendStatus(500);
  }
});
```

### StorePep to Store

**After order fulfillment**, sync inventory back:
```javascript
async function syncInventoryAfterFulfillment(order) {
  const store = await Stores.findOne({ storeUUID: order.storeUUID });

  for (const lineItem of order.line_items) {
    const product = await ProductsNew.findOne({
      storeUUID: order.storeUUID,
      productId: lineItem.product_id
    });

    if (!product) continue;

    // Decrease local stock
    product.stock.quantity -= lineItem.quantity;
    await product.save();

    // Update store inventory
    if (store.storeType === constants.SHOPIFY_STORE_CODE) {
      await updateShopifyInventory(product, product.stock.quantity);
    } else if (store.storeType === constants.WOOCOMMERCE_STORE_CODE) {
      await updateWooCommerceInventory(product, product.stock.quantity);
    }
  }
}
```

## Auto-Import Scheduling

**Cron Job** for automatic product sync:

**Location**: `server/src/jobs/productAutoImport.js`

```javascript
const cron = require('node-cron');

// Run every 6 hours
cron.schedule('0 */6 * * *', async () => {
  const stores = await Stores.find({
    isActive: true,
    productAutoImport: true
  });

  for (const store of stores) {
    try {
      infoLogger(`Auto-importing products for store: ${store.storeName}`);

      if (store.storeType === constants.SHOPIFY_STORE_CODE) {
        await importProductsFromShopify(store);
      } else if (store.storeType === constants.WOOCOMMERCE_STORE_CODE) {
        await importProductsFromWooCommerce(store);
      }

      infoLogger(`Completed auto-import for store: ${store.storeName}`);
    } catch (error) {
      errorLogger(`Auto-import failed for store ${store.storeName}:`, error);
    }
  }
});
```

## Deduplication

**Feature**: Prevent duplicate products during import

**Location**: `server/src/shared/API/stores/shopify/products/featureLoader.js`

```javascript
async function isProductImportDeduplicationEnabled(accountUUID) {
  return await features.isEnabled('product-import-deduplication', accountUUID);
}
```

**Implementation**:
```javascript
async function upsertProduct(mappedProduct) {
  if (await isProductImportDeduplicationEnabled(mappedProduct.accountUUID)) {
    // Check for existing product
    const existing = await ProductsNew.findOne({
      storeUUID: mappedProduct.storeUUID,
      $or: [
        { productId: mappedProduct.productId },
        { sku: mappedProduct.sku }
      ]
    });

    if (existing) {
      // Update existing product
      await ProductsNew.updateOne(
        { _id: existing._id },
        { $set: mappedProduct }
      );
      return { action: 'updated', productUUID: existing.productUUID };
    }
  }

  // Create new product
  const product = new ProductsNew(mappedProduct);
  await product.save();
  return { action: 'created', productUUID: product.productUUID };
}
```

## Common Patterns

### Upsert Product

```javascript
async function upsertProduct(mappedProduct) {
  const filter = {
    storeUUID: mappedProduct.storeUUID,
    productId: mappedProduct.productId
  };

  const result = await ProductsNew.findOneAndUpdate(
    filter,
    { $set: mappedProduct },
    { upsert: true, new: true }
  );

  return result;
}
```

### Batch Insert Products

```javascript
async function batchInsertProducts(products) {
  const bulkOps = products.map(product => ({
    insertOne: { document: product }
  }));

  const result = await ProductsNew.bulkWrite(bulkOps, { ordered: false });

  return { inserted: result.insertedCount };
}
```

## Known Issues / Tech Debt

1. **No import validation**: Invalid data (missing SKU, negative weight) not validated
2. **Slow CSV import**: Large CSV files block server during processing
3. **No progress tracking**: Long imports provide no progress feedback
4. **Duplicate handling**: Deduplication logic inconsistent across platforms
5. **No rollback**: Failed batch import leaves partial data
6. **Memory issues**: Large product catalogs loaded entirely into memory
7. **No delta sync**: Full import each time (no incremental updates)

## Related Pages

- [Product Management](./product-management.md) - Product data model and structure
- [Store Integration Overview](../stores/store-integration-overview.md) - Store sync architecture
- [Platform Connectors](../stores/platform-connectors.md) - Platform-specific import details
