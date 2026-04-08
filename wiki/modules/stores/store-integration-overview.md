---
title: Store Integration Overview
category: module
domain: stores
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Store Integration Overview

## Overview

Store integrations are **e-commerce platform connectors** that import orders and products from online stores into StorePep for shipping fulfillment. StorePep supports 7 major e-commerce platforms using an adapter pattern where each platform has a dedicated connector class implementing common interfaces for order/product synchronization and webhook management.

**Supported Platforms**: Shopify, WooCommerce, Magento 2, Magento 1, BigCommerce, PrestaShop, Amazon India (7 platforms)

**Core Purpose**: Bidirectional sync between e-commerce platforms and StorePep
- **Import**: Orders, products, inventory from store → StorePep
- **Export**: Tracking numbers, fulfillment status from StorePep → store

## Architecture

### Store Adapter Pattern

**Location**: `server/src/shared/API/stores/`

**Pattern**: Each platform implements common store interface

```
stores/
├── shopify/
│   ├── ShopifyStore.js          # Main adapter class
│   ├── mapper/                  # Order/product transformers
│   ├── products/                # Product sync logic
│   └── batch/                   # Bulk import handlers
├── woocommerce/
│   ├── WooCommerceStore.js
│   ├── mapper/
│   ├── products/
│   └── batch/
├── magento/
├── magentoOne/
├── bigcommerce/
├── prestaShop/
└── amazonIndia/
```

**Common Interface** (example methods):
```javascript
class StoreAdapter {
  // Order operations
  async fetchOrders(store, options)
  async updateOrderStatus(orderId, status)
  async addTrackingInfo(orderId, trackingNumber, carrier)

  // Product operations
  async fetchProducts(store, options)
  async updateInventory(productId, quantity)

  // Webhook operations
  async registerWebhooks(store)
  async handleOrderCreatedWebhook(payload)
  async handleProductUpdatedWebhook(payload)
}
```

### Data Models

**Store Model**: `server/src/models/stores.js`

**Schema**:
```javascript
{
  accountUUID: String,
  storeUUID: String,
  storeName: String,
  storeType: String,  // SHOPIFY, WOOCOMMERCE, MAGENTO, etc.
  isActive: Boolean,
  status: String,  // IN_USE, ARCHIVED
  currency: String,

  // Common connection fields
  url: String,  // Store URL
  consumerKey: String,  // API key
  consumerSecret: String,  // API secret
  accessToken: String,  // OAuth token

  // Units
  weightUnit: String,  // kg, lb, oz
  dimensionsUnit: String,  // cm, in

  // Sync settings
  oldestOrderDate: Date,
  lastImportedTime: Date,
  lastProductImportedTime: Date,
  productAutoImport: Boolean,
  perPageLimit: Number,

  // Webhooks
  orderCreatedWebhookId: String,
  orderUpdatedWebhookId: String,
  orderCancelledWebhookId: String,
  productCreatedWebhookId: String,
  productUpdateWebhookId: String,

  // Branding
  companyLogo: {
    fileName: String,
    fileSize: Number,
    fileType: String,
    image: String,  // Base64
    key: String  // S3 key
  },
  packingSlipMessage: String,

  // Platform-specific fields
  // Shopify
  password: String,
  defaultLocationId: Number,
  connectionMode: String,  // public, private
  shopifyPlanName: String,

  // WooCommerce
  wcVersion: String,
  forceBasicAuth: Boolean,
  defaultWeight: Number,
  defaultDimensionsInCm: {
    defaultLengthInCm: Number,
    defaultWidthInCm: Number,
    defaultHeightInCm: Number
  },
  wooCommerceOrderStatuses: [String],  // ['processing', 'completed']

  // Magento
  dimensionMapper: {
    length: String,
    width: String,
    height: String
  },
  customAttributesMapper: {
    hsCode: String,
    stateOfManufacture: String
  },

  // BigCommerce
  storeHash: String,
  storeStatus: Object,

  // Amazon India
  marketPlaceId: String,
  merchantId: String,
  mwsAuthToken: String
}
```

**Store Types Enum**:
```javascript
storeType: {
  enum: [
    constants.WOOCOMMERCE_STORE_CODE,      // 'WOOCOMMERCE'
    constants.MAGENTO_STORE_CODE,          // 'MAGENTO'
    constants.MAGENTO_ONE_STORE_CODE,      // 'MAGENTO_ONE'
    constants.SHOPIFY_STORE_CODE,          // 'SHOPIFY'
    constants.BIGCOMMERCE_STORE_CODE,      // 'BIGCOMMERCE'
    constants.PRESTA_SHOP_STORE_CODE,      // 'PRESTA_SHOP'
    constants.AMAZON_INDIA_STORE_CODE      // 'AMAZON_INDIA'
  ]
}
```

## Order Import Flow

### 1. Order Polling/Webhook

**Polling Mode** (scheduled import):
```javascript
// Cron job triggers periodic import
const store = await Stores.findOne({ storeUUID: 'store-uuid' });
const storeAdapter = await getStoreAdapter(store.storeType);

const orders = await storeAdapter.fetchOrders(store, {
  since: store.lastImportedTime,
  limit: store.perPageLimit,
  status: 'processing'
});
```

**Webhook Mode** (real-time):
```javascript
// Webhook endpoint receives order.created event
router.post('/webhooks/shopify/order-created', async (req, res) => {
  const payload = req.body;
  const store = await Stores.findOne({ storeUUID: payload.storeUUID });

  await ShopifyStore.handleOrderCreatedWebhook(payload, store);
  res.sendStatus(200);
});
```

### 2. Order Mapping

**Purpose**: Transform platform-specific order format to StorePep format

**Example**: Shopify → StorePep

**Location**: `server/src/shared/API/stores/shopify/mapper/shopifyToStorepepOrderMapper.js`

```javascript
async function mapShopifyToStorePepOrder(shopifyOrder, store) {
  return {
    // StorePep fields
    subOrderUUID: generateUUID(),
    storeUUID: store.storeUUID,
    accountUUID: store.accountUUID,
    orderId: shopifyOrder.id,
    orderNumber: shopifyOrder.order_number,
    storePepStatus: constants.INITIAL,

    // Customer info
    customer: {
      firstName: shopifyOrder.customer?.first_name,
      lastName: shopifyOrder.customer?.last_name,
      email: shopifyOrder.customer?.email
    },

    // Shipping address
    shipping: {
      firstName: shopifyOrder.shipping_address?.first_name,
      lastName: shopifyOrder.shipping_address?.last_name,
      address1: shopifyOrder.shipping_address?.address1,
      address2: shopifyOrder.shipping_address?.address2,
      city: shopifyOrder.shipping_address?.city,
      stateOrProvinceCode: shopifyOrder.shipping_address?.province_code,
      postalCode: shopifyOrder.shipping_address?.zip,
      countryCode: shopifyOrder.shipping_address?.country_code,
      phoneNumber: shopifyOrder.shipping_address?.phone
    },

    // Line items
    line_items: shopifyOrder.line_items.map(item => ({
      productId: item.product_id,
      variantId: item.variant_id,
      sku: item.sku,
      name: item.name,
      quantity: item.quantity,
      price: item.price,
      weight: item.grams ? item.grams / 1000 : 0  // Convert grams to kg
    })),

    // Totals
    total: parseFloat(shopifyOrder.total_price),
    subtotal: parseFloat(shopifyOrder.subtotal_price),
    totalTax: parseFloat(shopifyOrder.total_tax),
    totalShipping: parseFloat(shopifyOrder.total_shipping),

    // Metadata
    meta_data: shopifyOrder.note_attributes,
    tags: shopifyOrder.tags?.split(','),

    // Full response for reference
    fullResponse: shopifyOrder
  };
}
```

### 3. Order Processing

**After import, order flows through**:
```
1. Order imported → storePepStatus = INITIAL
2. Automation runs → Carrier/service set
3. Rate shopping → Rates fetched
4. Service selection → Cheapest/fastest selected
5. Label generation → storePepStatus = LABEL_GENERATED
6. Fulfillment sync → Tracking pushed to store
```

See [Order Lifecycle](../orders/order-lifecycle.md)

## Product Import Flow

### 1. Product Synchronization

**Modes**:
- **Manual import**: User clicks "Import Products" button
- **Auto import**: `productAutoImport: true` syncs on schedule
- **Webhook sync**: Real-time product updates

**Example**: WooCommerce Product Import

**Location**: `server/src/shared/API/stores/woocommerce/products/WoocommerceProductImportService.js`

```javascript
async function importProduct({ product, store, version = 'wc/v3', action = 'create' }) {
  // 1. Map WooCommerce product to StorePep format
  const mappedProduct = await mapWoocommerceToStorepepProduct(product, store);

  // 2. Check if product already exists
  const existingProduct = await ProductsNew.findOne({
    storeUUID: store.storeUUID,
    productId: product.id
  });

  if (existingProduct) {
    // Update existing product
    await ProductsNew.updateOne(
      { _id: existingProduct._id },
      { $set: mappedProduct }
    );
  } else {
    // Create new product
    const newProduct = new ProductsNew(mappedProduct);
    await newProduct.save();
  }

  // 3. Handle variants (for variable products)
  if (product.variations && product.variations.length > 0) {
    for (const variant of product.variations) {
      await importProduct({
        product: variant,
        store,
        version,
        action
      });
    }
  }
}
```

### 2. Product Mapping

**Example**: Shopify → StorePep

**Location**: `server/src/shared/API/stores/shopify/mapper/shopifyToStorepepProductMapper.js`

```javascript
async function mapShopifyToStorePepProduct(shopifyProduct, store, variant = null) {
  const isVariant = !!variant;

  return {
    // Core fields
    productUUID: generateUUID(),
    storeUUID: store.storeUUID,
    accountUUID: store.accountUUID,
    productId: isVariant ? variant.id : shopifyProduct.id,
    inventoryItemId: isVariant ? variant.inventory_item_id : null,
    parentId: isVariant ? shopifyProduct.id : null,
    productType: isVariant ? constants.PRODUCT_TYPE_VARIANT : constants.PRODUCT_TYPE_SIMPLE,

    // Product details
    name: isVariant ? variant.title : shopifyProduct.title,
    sku: isVariant ? variant.sku : shopifyProduct.variants[0]?.sku,
    total: isVariant ? parseFloat(variant.price) : parseFloat(shopifyProduct.variants[0]?.price),

    // Dimensions/weight
    weight: isVariant ? variant.weight : shopifyProduct.variants[0]?.weight,
    weightUnit: store.weightUnit,
    dimensionsUnit: store.dimensionsUnit,

    // Inventory
    stock: {
      quantity: isVariant ? variant.inventory_quantity : shopifyProduct.variants[0]?.inventory_quantity
    },

    // Metadata
    description: shopifyProduct.body_html,
    tags: shopifyProduct.tags?.split(','),
    productImage: {
      id: shopifyProduct.image?.id,
      src: shopifyProduct.image?.src
    },

    // Customs
    harmonizationCode: isVariant ? variant.harmonized_system_code : null,
    countryOfManufacture: shopifyProduct.country_code_of_origin,

    isActive: true
  };
}
```

See [Product Management](../products/product-management.md)

## Webhook Management

### Webhook Registration

**Purpose**: Real-time event notifications from e-commerce platform

**Supported Events**:
- `orders/create` - New order placed
- `orders/updated` - Order modified
- `orders/cancelled` - Order cancelled
- `products/create` - New product added
- `products/update` - Product modified
- `inventory/update` - Inventory quantity changed

### Shopify Webhooks

**Registration Flow**:

**Location**: `server/src/shared/API/stores/shopify/ShopifyStore.js`

```javascript
async function registerWebhooks(store) {
  const shopify = new Shopify({
    shopName: store.storeName,
    apiKey: store.consumerKey,
    password: store.password
  });

  const webhooks = [
    { topic: 'orders/create', address: `${config.webhookBaseUrl}/webhooks/shopify/order-created` },
    { topic: 'orders/updated', address: `${config.webhookBaseUrl}/webhooks/shopify/order-updated` },
    { topic: 'orders/cancelled', address: `${config.webhookBaseUrl}/webhooks/shopify/order-cancelled` },
    { topic: 'products/create', address: `${config.webhookBaseUrl}/webhooks/shopify/product-created` },
    { topic: 'products/update', address: `${config.webhookBaseUrl}/webhooks/shopify/product-updated` }
  ];

  for (const webhook of webhooks) {
    const created = await shopify.webhook.create(webhook);

    // Store webhook IDs for later deletion
    if (webhook.topic === 'orders/create') {
      store.orderCreatedWebhookId = created.id;
    } else if (webhook.topic === 'products/update') {
      store.productUpdateWebhookId = created.id;
    }
    // ... etc
  }

  await store.save();
}
```

### WooCommerce Webhooks

**Location**: `server/src/shared/API/stores/woocommerce/WooCommerceStore.js`

```javascript
async function registerWebhooks(store) {
  const WooCommerce = require('woocommerce-api');

  const wooCommerce = new WooCommerce({
    url: store.url,
    consumerKey: store.consumerKey,
    consumerSecret: store.consumerSecret,
    wpAPI: true,
    version: 'wc/v3'
  });

  const webhooks = [
    {
      name: 'Order Created',
      topic: 'order.created',
      delivery_url: `${config.webhookBaseUrl}/webhooks/woocommerce/order-created`,
      secret: generateWebhookSecret()
    },
    {
      name: 'Order Updated',
      topic: 'order.updated',
      delivery_url: `${config.webhookBaseUrl}/webhooks/woocommerce/order-updated`
    }
  ];

  for (const webhook of webhooks) {
    const result = await wooCommerce.postAsync('webhooks', webhook);
    const created = JSON.parse(result.body);

    // Store webhook IDs
    if (webhook.topic === 'order.created') {
      store.orderCreatedWebhookId = created.id;
    }
  }

  await store.save();
}
```

### Webhook Processing

**Example**: Shopify Order Created Webhook

```javascript
router.post('/webhooks/shopify/order-created', async (req, res) => {
  try {
    const shopifyOrder = req.body;
    const shopDomain = req.headers['x-shopify-shop-domain'];

    // 1. Find store by domain
    const store = await Stores.findOne({
      storeName: shopDomain,
      storeType: constants.SHOPIFY_STORE_CODE
    });

    if (!store) {
      return res.status(404).json({ error: 'Store not found' });
    }

    // 2. Verify webhook signature (security)
    const hmac = req.headers['x-shopify-hmac-sha256'];
    const verified = verifyShopifyWebhook(req.body, hmac, store.consumerSecret);

    if (!verified) {
      return res.status(401).json({ error: 'Invalid webhook signature' });
    }

    // 3. Map and import order
    const mappedOrder = await mapShopifyToStorePepOrder(shopifyOrder, store);
    const order = new Orders(mappedOrder);
    await order.save();

    // 4. Trigger automation
    await packageAutomation([order], currentUser, store.accountUUID, null, true);

    res.sendStatus(200);
  } catch (error) {
    errorLogger('Shopify webhook error:', error);
    res.sendStatus(500);
  }
});
```

## Fulfillment Sync

### Tracking Number Upload

**After label generation**, tracking info pushed back to store:

**Example**: Shopify Fulfillment

**Location**: `server/src/shared/API/stores/shopify/ShopifyFulfilment.js`

```javascript
async function createFulfillment(order, trackingInfo) {
  const shopify = new Shopify({
    shopName: order.storeName,
    apiKey: store.consumerKey,
    password: store.password
  });

  const fulfillment = await shopify.fulfillment.create(order.orderId, {
    location_id: store.defaultLocationId,
    tracking_number: trackingInfo.trackingNumber,
    tracking_company: trackingInfo.carrierName,
    tracking_url: trackingInfo.trackingUrl,
    notify_customer: true,
    line_items: order.line_items.map(item => ({
      id: item.id,
      quantity: item.quantity
    }))
  });

  // Update order status in StorePep
  order.storePepStatus = constants.LABEL_GENERATED;
  order.fulfillmentId = fulfillment.id;
  await order.save();

  return fulfillment;
}
```

**WooCommerce Fulfillment**:

```javascript
async function updateOrderWithTracking(order, trackingInfo) {
  const WooCommerce = require('woocommerce-api');

  const wooCommerce = new WooCommerce({
    url: store.url,
    consumerKey: store.consumerKey,
    consumerSecret: store.consumerSecret
  });

  // Update order status to completed
  await wooCommerce.putAsync(`orders/${order.orderId}`, {
    status: 'completed'
  });

  // Add tracking note
  await wooCommerce.postAsync(`orders/${order.orderId}/notes`, {
    note: `Tracking Number: ${trackingInfo.trackingNumber}\nCarrier: ${trackingInfo.carrierName}\nTracking URL: ${trackingInfo.trackingUrl}`,
    customer_note: true
  });

  // Update custom meta fields (if tracking plugin installed)
  await wooCommerce.putAsync(`orders/${order.orderId}`, {
    meta_data: [
      { key: '_tracking_number', value: trackingInfo.trackingNumber },
      { key: '_tracking_provider', value: trackingInfo.carrierName }
    ]
  });
}
```

## Authentication Methods

### OAuth 2.0 (Shopify, BigCommerce)

```javascript
// OAuth flow for Shopify
router.get('/auth/shopify', (req, res) => {
  const { shop } = req.query;
  const redirectUri = `${config.appUrl}/auth/shopify/callback`;
  const scopes = 'read_orders,write_orders,read_products,write_fulfillments';

  const authUrl = `https://${shop}/admin/oauth/authorize?client_id=${config.shopifyApiKey}&scope=${scopes}&redirect_uri=${redirectUri}`;

  res.redirect(authUrl);
});

router.get('/auth/shopify/callback', async (req, res) => {
  const { code, shop } = req.query;

  // Exchange code for access token
  const response = await axios.post(`https://${shop}/admin/oauth/access_token`, {
    client_id: config.shopifyApiKey,
    client_secret: config.shopifyApiSecret,
    code
  });

  const { access_token } = response.data;

  // Save store with access token
  const store = new Stores({
    storeName: shop,
    storeType: constants.SHOPIFY_STORE_CODE,
    accessToken: access_token,
    accountUUID: req.user.accountUUID
  });

  await store.save();

  res.redirect('/stores');
});
```

### API Keys (WooCommerce, Magento)

```javascript
// WooCommerce stores API keys in database
const store = new Stores({
  storeType: constants.WOOCOMMERCE_STORE_CODE,
  url: 'https://mystore.com',
  consumerKey: 'ck_xxxxxxxxxxxxx',  // Generated in WooCommerce settings
  consumerSecret: 'cs_xxxxxxxxxxxxx',
  accountUUID: req.user.accountUUID
});

// Test connection
const WooCommerce = require('woocommerce-api');
const wooCommerce = new WooCommerce({
  url: store.url,
  consumerKey: store.consumerKey,
  consumerSecret: store.consumerSecret
});

const result = await wooCommerce.getAsync('system_status');
// If successful, connection is valid
```

### Basic Auth (Magento 1, legacy WooCommerce)

```javascript
const store = new Stores({
  storeType: constants.MAGENTO_ONE_STORE_CODE,
  url: 'https://mymagentostore.com',
  username: 'api_user',
  password: 'api_password',
  basicAuth: true
});
```

## Platform-Specific Details

See [Platform Connectors](./platform-connectors.md) for detailed documentation of each supported platform.

## API Endpoints

**Location**: `server/src/routes/stores.js`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/add` | POST | Add new store connection |
| `/update` | POST | Update store settings |
| `/getallstores` | POST | List all stores for account |
| `/getstoredetails` | POST | Get single store details |
| `/delete` | POST | Remove store connection |
| `/testconnection` | POST | Validate store credentials |
| `/importorders` | POST | Trigger manual order import |
| `/importproducts` | POST | Trigger manual product import |
| `/synctracking` | POST | Push tracking to store |
| `/registerwebhooks` | POST | Setup webhooks |
| `/unregisterwebhooks` | POST | Remove webhooks |

## Configuration

### Store Settings

**Per-store configuration**:
```javascript
{
  isActive: true,  // Enable/disable store
  productAutoImport: true,  // Auto-sync products
  perPageLimit: 100,  // Orders per import batch
  wooCommerceOrderStatuses: ['processing'],  // Which order statuses to import
  trackingLanguage: 'en_US'  // Language for tracking emails
}
```

### Default Values

**For missing product data**:
```javascript
{
  defaultWeight: 0.5,  // kg
  defaultDimensionsInCm: {
    defaultLengthInCm: 10,
    defaultWidthInCm: 10,
    defaultHeightInCm: 10
  }
}
```

## Common Patterns

### Add Store Connection

```javascript
const store = new Stores({
  accountUUID: 'account-uuid',
  storeName: 'myshop.myshopify.com',
  storeType: constants.SHOPIFY_STORE_CODE,
  url: 'https://myshop.myshopify.com',
  consumerKey: 'shopify-api-key',
  password: 'shopify-password',
  accessToken: 'shopify-access-token',
  weightUnit: 'kg',
  dimensionsUnit: 'cm',
  currency: 'USD',
  isActive: true,
  productAutoImport: true,
  perPageLimit: 100
});

await store.save();

// Register webhooks
await registerWebhooks(store);
```

### Import Orders from Store

```javascript
const store = await Stores.findOne({ storeUUID: 'store-uuid' });
const storeAdapter = await getStoreAdapter(store.storeType);

const orders = await storeAdapter.fetchOrders(store, {
  since: store.lastImportedTime || new Date('2024-01-01'),
  limit: 100,
  status: 'processing'
});

for (const order of orders) {
  const mappedOrder = await mapOrderToStorePep(order, store);
  const storepepOrder = new Orders(mappedOrder);
  await storepepOrder.save();

  // Run automation
  await packageAutomation([storepepOrder], currentUser, store.accountUUID);
}

// Update last import time
store.lastImportedTime = new Date();
await store.save();
```

## Known Issues / Tech Debt

1. **No rate limiting**: API calls not throttled, can hit platform limits
2. **Synchronous imports**: Large product catalogs block server during import
3. **No retry logic**: Failed webhook processing not retried
4. **Platform coupling**: Store-specific logic scattered across codebase
5. **No connection pooling**: Each request creates new API client
6. **Limited error handling**: API errors not always surfaced to user
7. **No versioning**: Platform API version changes can break integration

## Related Pages

- [Platform Connectors](./platform-connectors.md) - Detailed platform-specific documentation
- [Product Management](../products/product-management.md) - Product data model
- [Order Lifecycle](../orders/order-lifecycle.md) - Order processing flow
- [Automation Overview](../automation/automation-overview.md) - Post-import automation
