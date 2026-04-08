---
title: Platform Connectors
category: module
domain: stores
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Platform Connectors

## Overview

Platform connectors are **platform-specific adapter implementations** for each supported e-commerce platform. Each connector handles authentication, API communication, data mapping, and webhook management according to the platform's unique API structure and requirements.

**Supported Platforms**: 7 connectors

## Shopify Connector

**Store Type**: `SHOPIFY`

**Location**: `server/src/shared/API/stores/shopify/`

**API**: REST API + GraphQL API

**Authentication**: OAuth 2.0 + API password (private apps)

### Connection Modes

**Public App** (OAuth 2.0):
```javascript
{
  storeType: 'SHOPIFY',
  storeName: 'myshop.myshopify.com',
  consumerKey: 'shopify_api_key',  // App API key
  accessToken: 'shpat_xxxxxxxxxxxxx',  // OAuth token
  connectionMode: 'public'
}
```

**Private App** (API Password):
```javascript
{
  storeType: 'SHOPIFY',
  storeName: 'myshop.myshopify.com',
  consumerKey: 'api_key',
  password: 'password',  // Admin API password
  connectionMode: 'private'
}
```

### Shopify-Specific Fields

```javascript
{
  defaultLocationId: Number,  // Inventory location ID
  shopifyPlanName: String,  // 'basic', 'shopify_plus', etc.
  isShopClosed: Boolean,  // Shop temporarily closed
  ianaTimezone: String,  // 'America/New_York'
}
```

### Order Import

**API Endpoint**: `GET /admin/api/2024-01/orders.json`

**Implementation**: `ShopifyStore.js`

```javascript
async function fetchOrders(store, options = {}) {
  const shopify = new Shopify({
    shopName: store.storeName,
    apiKey: store.consumerKey,
    password: store.password || store.accessToken
  });

  const params = {
    status: options.status || 'any',
    created_at_min: options.since?.toISOString(),
    limit: options.limit || 250,
    fields: 'id,order_number,created_at,updated_at,customer,line_items,shipping_address,total_price'
  };

  const orders = await shopify.order.list(params);

  return orders.map(order => mapShopifyToStorePepOrder(order, store));
}
```

### Product Import

**REST API** (legacy):
```javascript
const products = await shopify.product.list({ limit: 250 });
```

**GraphQL API** (preferred for bulk operations):
```javascript
const query = `
  query {
    products(first: 250) {
      edges {
        node {
          id
          title
          variants {
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
`;

const result = await shopifyGraphQLClient.query({ query });
```

**Location**: `ShopifyStore.js`, `ShopifyGraphql.js`

### Webhooks

**Supported Topics**:
- `orders/create`
- `orders/updated`
- `orders/cancelled`
- `products/create`
- `products/update`
- `inventory_levels/update`
- `shop/update`

**Webhook Verification**:
```javascript
function verifyShopifyWebhook(data, hmac, secret) {
  const message = JSON.stringify(data);
  const generatedHash = crypto
    .createHmac('sha256', secret)
    .update(message, 'utf8')
    .digest('base64');

  return generatedHash === hmac;
}
```

### Fulfillment

**API**: `POST /admin/api/2024-01/orders/{order_id}/fulfillments.json`

**Implementation**: `ShopifyFulfilment.js`

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
    tracking_company: mapCarrierToShopifyName(trackingInfo.carrierType),
    tracking_url: trackingInfo.trackingUrl,
    notify_customer: true,
    line_items: order.line_items.map(item => ({
      id: item.id,
      quantity: item.quantity
    }))
  });

  return fulfillment;
}
```

**Carrier Mapping** (Shopify recognizes specific carrier names):
```javascript
const carrierMapping = {
  'C1': 'FedEx',
  'C3': 'UPS',
  'C2': 'USPS',
  'C4': 'DHL Express',
  'C5': 'Canada Post'
};
```

### Known Issues

- **GraphQL rate limits**: 1000 points per second (complex queries consume more points)
- **Webhook retries**: Shopify retries failed webhooks for 48 hours
- **Variant limits**: Max 100 variants per product

---

## WooCommerce Connector

**Store Type**: `WOOCOMMERCE`

**Location**: `server/src/shared/API/stores/woocommerce/`

**API**: WooCommerce REST API (v3)

**Authentication**: Consumer Key/Secret (OAuth1)

### Connection Configuration

```javascript
{
  storeType: 'WOOCOMMERCE',
  url: 'https://mystore.com',
  consumerKey: 'ck_xxxxxxxxxxxxx',  // Generated in WooCommerce > Settings > Advanced > REST API
  consumerSecret: 'cs_xxxxxxxxxxxxx',
  wcVersion: '3.0',  // WooCommerce version
  forceBasicAuth: false,  // Force Basic Auth over HTTPS
  basicAuth: false,  // Use Basic Auth (username/password)
  username: 'api_user',  // If basicAuth = true
  password: 'api_password'
}
```

### WooCommerce-Specific Fields

```javascript
{
  wordPressSiteUrl: String,  // WordPress site URL (if different from WooCommerce)
  defaultWeight: Number,  // Default weight if product has no weight
  defaultDimensionsInCm: {
    defaultLengthInCm: Number,
    defaultWidthInCm: Number,
    defaultHeightInCm: Number
  },
  wooCommerceOrderStatuses: [String],  // Which statuses to import ['processing', 'completed']
  subscriptionPluginEnabled: Boolean,  // WooCommerce Subscriptions plugin detected
  subscriptionPluginName: [String],  // ['woocommerce-subscriptions']
  allowCustomStatusOrders: Boolean  // Import custom order statuses
}
```

### Order Import

**API Endpoint**: `GET /wp-json/wc/v3/orders`

**Implementation**: `WooCommerceStore.js`

```javascript
async function fetchOrders(store, options = {}) {
  const WooCommerce = require('woocommerce-api');

  const wooCommerce = new WooCommerce({
    url: store.url,
    consumerKey: store.consumerKey,
    consumerSecret: store.consumerSecret,
    wpAPI: true,
    version: 'wc/v3'
  });

  const params = {
    status: store.wooCommerceOrderStatuses.join(','),  // 'processing,completed'
    after: options.since?.toISOString(),
    per_page: options.limit || 100,
    orderby: 'date',
    order: 'desc'
  };

  const result = await wooCommerce.getAsync('orders', params);
  const orders = JSON.parse(result.body);

  return orders.map(order => mapWoocommerceToStorePepOrder(order, store));
}
```

### Product Import

**API Endpoint**: `GET /wp-json/wc/v3/products`

**Handling Variants**:
```javascript
async function fetchProducts(store) {
  const wooCommerce = new WooCommerce({ /* config */ });

  // 1. Fetch parent products
  const productsResult = await wooCommerce.getAsync('products', { per_page: 100 });
  const products = JSON.parse(productsResult.body);

  for (const product of products) {
    // 2. Map parent product
    await importProduct({ product, store });

    // 3. Fetch variations for variable products
    if (product.type === 'variable') {
      const variationsResult = await wooCommerce.getAsync(
        `products/${product.id}/variations`,
        { per_page: 100 }
      );
      const variations = JSON.parse(variationsResult.body);

      for (const variation of variations) {
        await importProduct({
          product: { ...variation, parent: product },
          store,
          action: 'create'
        });
      }
    }
  }
}
```

**Location**: `WoocommerceProductImportService.js`, `products/variantIterator.js`

### Webhooks

**API Endpoint**: `POST /wp-json/wc/v3/webhooks`

**Webhook Creation**:
```javascript
async function registerWebhooks(store) {
  const wooCommerce = new WooCommerce({ /* config */ });

  const webhooks = [
    {
      name: 'StorePep Order Created',
      topic: 'order.created',
      delivery_url: `${config.webhookBaseUrl}/webhooks/woocommerce/order-created`,
      secret: generateWebhookSecret()
    },
    {
      name: 'StorePep Order Updated',
      topic: 'order.updated',
      delivery_url: `${config.webhookBaseUrl}/webhooks/woocommerce/order-updated`
    },
    {
      name: 'StorePep Product Updated',
      topic: 'product.updated',
      delivery_url: `${config.webhookBaseUrl}/webhooks/woocommerce/product-updated`
    }
  ];

  for (const webhook of webhooks) {
    const result = await wooCommerce.postAsync('webhooks', webhook);
    const created = JSON.parse(result.body);

    // Store webhook ID
    if (webhook.topic === 'order.created') {
      store.orderCreatedWebhookId = created.id;
    }
  }

  await store.save();
}
```

### Tracking Update

**Method 1**: Order Notes
```javascript
async function addTrackingNote(order, trackingInfo) {
  const wooCommerce = new WooCommerce({ /* config */ });

  await wooCommerce.postAsync(`orders/${order.orderId}/notes`, {
    note: `Shipment tracking number: ${trackingInfo.trackingNumber}\nCarrier: ${trackingInfo.carrierName}\nTracking URL: ${trackingInfo.trackingUrl}`,
    customer_note: true  // Visible to customer
  });
}
```

**Method 2**: Order Meta (with tracking plugin)
```javascript
async function updateOrderMeta(order, trackingInfo) {
  const wooCommerce = new WooCommerce({ /* config */ });

  await wooCommerce.putAsync(`orders/${order.orderId}`, {
    status: 'completed',
    meta_data: [
      { key: '_tracking_provider', value: trackingInfo.carrierName },
      { key: '_tracking_number', value: trackingInfo.trackingNumber },
      { key: '_date_shipped', value: new Date().toISOString() }
    ]
  });
}
```

### Known Issues

- **Slow API**: WooCommerce API slower than Shopify (no bulk operations)
- **Pagination limits**: Max 100 products per page
- **Webhook reliability**: Depends on WordPress cron, may miss events

---

## Magento 2 Connector

**Store Type**: `MAGENTO`

**Location**: `server/src/shared/API/stores/magento/`

**API**: Magento REST API

**Authentication**: Token-based (bearer token)

### Connection Configuration

```javascript
{
  storeType: 'MAGENTO',
  url: 'https://mymagentostore.com',
  consumerKey: 'integration_consumer_key',
  consumerSecret: 'integration_consumer_secret',
  accessToken: 'access_token',  // Generated via integration
  dimensionMapper: {
    length: 'custom_length',  // Map custom attributes to dimensions
    width: 'custom_width',
    height: 'custom_height'
  },
  customAttributesMapper: {
    hsCode: 'hs_code',  // Harmonization code attribute
    stateOfManufacture: 'state_of_manufacture'
  },
  isMagentoCustomStatusRequired: false,
  magentoCustomStatusList: ['processing', 'pending']
}
```

### Order Import

**API Endpoint**: `GET /rest/V1/orders`

```javascript
async function fetchOrders(store, options = {}) {
  const axios = require('axios');

  const params = {
    'searchCriteria[filterGroups][0][filters][0][field]': 'status',
    'searchCriteria[filterGroups][0][filters][0][value]': 'processing',
    'searchCriteria[filterGroups][0][filters][0][conditionType]': 'eq',
    'searchCriteria[pageSize]': options.limit || 100
  };

  const response = await axios.get(`${store.url}/rest/V1/orders`, {
    params,
    headers: {
      'Authorization': `Bearer ${store.accessToken}`,
      'Content-Type': 'application/json'
    }
  });

  return response.data.items.map(order => magentoToStorePepOrderMapper(order, store));
}
```

### Product Import

**Custom Attribute Mapping**:
```javascript
async function mapMagentoProduct(magentoProduct, store) {
  const customAttributes = {};

  magentoProduct.custom_attributes.forEach(attr => {
    customAttributes[attr.attribute_code] = attr.value;
  });

  return {
    productUUID: generateUUID(),
    storeUUID: store.storeUUID,
    name: magentoProduct.name,
    sku: magentoProduct.sku,
    weight: magentoProduct.weight,

    // Map custom dimension attributes
    length: customAttributes[store.dimensionMapper.length],
    width: customAttributes[store.dimensionMapper.width],
    height: customAttributes[store.dimensionMapper.height],

    // Map customs attributes
    harmonizationCode: customAttributes[store.customAttributesMapper.hsCode],
    stateOfManufacture: customAttributes[store.customAttributesMapper.stateOfManufacture]
  };
}
```

### Known Issues

- **Complex attribute system**: Custom attributes require mapping configuration
- **Performance**: Large catalogs slow to sync
- **Authentication complexity**: OAuth 1.0a flow for integrations

---

## Magento 1 Connector

**Store Type**: `MAGENTO_ONE`

**Location**: `server/src/shared/API/stores/magentoOne/`

**API**: Magento SOAP API (XML-RPC)

**Authentication**: Username/Password or API Key

### Connection Configuration

```javascript
{
  storeType: 'MAGENTO_ONE',
  url: 'https://mymagentostore.com',
  userName: 'api_user',  // Magento API user
  consumerKey: 'api_key'  // API key from Magento admin
}
```

### SOAP API Call

```javascript
const soap = require('soap');

async function fetchOrders(store, options = {}) {
  const wsdlUrl = `${store.url}/api/v2_soap?wsdl=1`;

  const client = await soap.createClientAsync(wsdlUrl);

  // Login to get session ID
  const sessionId = await client.loginAsync({
    username: store.userName,
    apiKey: store.consumerKey
  });

  // Fetch orders
  const result = await client.salesOrderListAsync({
    sessionId: sessionId[0],
    filters: {
      status: { key: 'status', value: 'processing' }
    }
  });

  const orders = result[0];

  return orders.map(order => magentoOneToStorepepOrderMapper(order, store));
}
```

### Known Issues

- **Legacy API**: SOAP/XML-RPC slower than REST
- **Limited support**: Magento 1 end-of-life (use with caution)

---

## BigCommerce Connector

**Store Type**: `BIGCOMMERCE`

**Location**: `server/src/shared/API/stores/bigcommerce/`

**API**: BigCommerce REST API v2/v3

**Authentication**: API credentials (Client ID + Access Token)

### Connection Configuration

```javascript
{
  storeType: 'BIGCOMMERCE',
  url: 'https://api.bigcommerce.com/stores/{store_hash}',
  storeHash: 'abc123def',  // Store hash from BigCommerce
  consumerKey: 'client_id',
  accessToken: 'access_token'
}
```

### Order Import

**API Endpoint**: `GET /v2/orders`

```javascript
async function fetchOrders(store, options = {}) {
  const axios = require('axios');

  const response = await axios.get(`${store.url}/v2/orders`, {
    params: {
      status_id: 11,  // Awaiting Fulfillment
      min_date_created: options.since?.toISOString(),
      limit: options.limit || 250
    },
    headers: {
      'X-Auth-Client': store.consumerKey,
      'X-Auth-Token': store.accessToken,
      'Content-Type': 'application/json'
    }
  });

  return response.data.map(order => bigcommerceToStorePepOrderMapper(order, store));
}
```

### Webhooks

**API Endpoint**: `POST /v3/hooks`

```javascript
async function registerWebhooks(store) {
  const axios = require('axios');

  const webhooks = [
    {
      scope: 'store/order/created',
      destination: `${config.webhookBaseUrl}/webhooks/bigcommerce/order-created`,
      is_active: true
    },
    {
      scope: 'store/product/updated',
      destination: `${config.webhookBaseUrl}/webhooks/bigcommerce/product-updated`
    }
  ];

  for (const webhook of webhooks) {
    const response = await axios.post(`${store.url}/v3/hooks`, webhook, {
      headers: {
        'X-Auth-Client': store.consumerKey,
        'X-Auth-Token': store.accessToken
      }
    });

    // Store webhook ID
    if (webhook.scope === 'store/order/created') {
      store.orderCreatedWebhookId = response.data.id;
    }
  }
}
```

---

## PrestaShop Connector

**Store Type**: `PRESTA_SHOP`

**Location**: `server/src/shared/API/stores/prestaShop/`

**API**: PrestaShop Web Service API (REST)

**Authentication**: API Key

### Connection Configuration

```javascript
{
  storeType: 'PRESTA_SHOP',
  url: 'https://myprestashop.com',
  consumerKey: 'prestashop_api_key'  // Generated in PrestaShop admin
}
```

### Order Import

**API Endpoint**: `GET /api/orders`

```javascript
async function fetchOrders(store, options = {}) {
  const axios = require('axios');

  const response = await axios.get(`${store.url}/api/orders`, {
    params: {
      'filter[current_state]': '[2,3]',  // Order states
      'display': 'full',
      'limit': options.limit || 100
    },
    auth: {
      username: store.consumerKey,
      password: ''  // PrestaShop API uses key as username, empty password
    }
  });

  // Parse XML response
  const xml2js = require('xml2js');
  const parser = new xml2js.Parser();
  const result = await parser.parseStringPromise(response.data);

  return result.prestashop.orders.order.map(order =>
    prestaToStorepepOrderMapper(order, store)
  );
}
```

### Known Issues

- **XML responses**: PrestaShop API returns XML (not JSON)
- **Complex filtering**: Limited query capabilities
- **No webhooks**: Must poll API for changes

---

## Amazon India Connector

**Store Type**: `AMAZON_INDIA`

**Location**: `server/src/shared/API/stores/amazonIndia/`

**API**: Amazon MWS (Marketplace Web Service)

**Authentication**: MWS Auth Token + Merchant ID

### Connection Configuration

```javascript
{
  storeType: 'AMAZON_INDIA',
  url: 'https://mws.amazonservices.in',
  marketPlaceId: 'A21TJRUUN4KGV',  // Amazon India marketplace ID
  merchantId: 'seller_merchant_id',
  consumerKey: 'aws_access_key_id',
  consumerSecret: 'aws_secret_access_key',
  mwsAuthToken: 'mws_auth_token',
  reportRequestId: String,  // Current report request
  reportId: String  // Generated report ID
}
```

### Order Import (Report-Based)

**Amazon MWS uses report generation** instead of direct API calls:

```javascript
async function fetchOrders(store, options = {}) {
  const mws = require('amazon-mws');

  // 1. Request order report
  const reportRequest = await mws.reports.submit({
    MarketplaceIdList: [store.marketPlaceId],
    ReportType: '_GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_',
    StartDate: options.since?.toISOString()
  });

  store.reportRequestId = reportRequest.ReportRequestId;
  await store.save();

  // 2. Poll for report completion (may take 15+ minutes)
  let reportReady = false;
  while (!reportReady) {
    const reportStatus = await mws.reports.getRequestStatus({
      ReportRequestIdList: [store.reportRequestId]
    });

    if (reportStatus.ReportProcessingStatus === '_DONE_') {
      store.reportId = reportStatus.GeneratedReportId;
      reportReady = true;
    } else {
      await sleep(60000);  // Wait 1 minute
    }
  }

  // 3. Download report
  const reportData = await mws.reports.get({
    ReportId: store.reportId
  });

  // 4. Parse CSV report
  const csv = require('csv-parser');
  const orders = [];

  return new Promise((resolve, reject) => {
    reportData
      .pipe(csv())
      .on('data', (row) => {
        orders.push(amazonIndiaToStorepepOrderMapper(row, store));
      })
      .on('end', () => {
        resolve(orders);
      });
  });
}
```

### Known Issues

- **Report delays**: Order reports take 15+ minutes to generate
- **CSV format**: Must parse CSV (not JSON)
- **Complex authentication**: Requires AWS signature calculation
- **Rate limiting**: Strict API throttling

---

## Platform Comparison

| Feature | Shopify | WooCommerce | Magento 2 | BigCommerce | PrestaShop |
|---------|---------|-------------|-----------|-------------|------------|
| **API Type** | REST + GraphQL | REST | REST | REST | REST (XML) |
| **Auth** | OAuth 2.0 | OAuth1 | Token | Token | API Key |
| **Webhooks** | Yes | Yes | Yes | Yes | No |
| **Real-time Sync** | Yes | Yes | Yes | Yes | No (polling) |
| **Bulk Operations** | Yes (GraphQL) | No | Limited | No | No |
| **Rate Limits** | 2 req/sec | Varies | Varies | Varies | Varies |
| **Order Import Speed** | Fast | Medium | Slow | Fast | Slow |
| **Product Variants** | Native | Native | Configurable | Native | Combinations |

## Test Coverage

**Automated E2E Tests**: 3 Playwright tests covering store integration

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| **Onboarding** | | |
| Create Store & Install App | `onboardingFlow/createStoreAndInstallApp.spec.ts` | ✅ Passing |
| Manage Subscription | `onboardingFlow/manageSubscription.spec.ts` | ✅ Passing |
| **Shopify Integration** | | |
| Shopify Checkout | `shopifyUI/shopifyCheckout.spec.ts` | ✅ Passing |
| **External Fulfillment** | | |
| Fulfill from Shopify | `externallyFulfilled/fulfillOrderFromShopify.spec.ts` | ✅ Passing |
| Partially Externally Fulfilled | `externallyFulfilled/partiallyExternallyFulfilled.spec.ts` | ✅ Passing |

**Test Coverage**: 5 integration workflows tested

**Tested Platforms**: Shopify

**Untested Platforms**: WooCommerce, Magento 2, Magento 1, BigCommerce, PrestaShop, Amazon India

**Test Suite Location**: `mcsl-test-automation/tests/onboardingFlow/`, `mcsl-test-automation/tests/shopifyUI/`, `mcsl-test-automation/tests/externallyFulfilled/`

**Documentation**: See [Features List](../../features.md) for complete test coverage

## Related Pages

- [Store Integration Overview](./store-integration-overview.md) - Architecture and common patterns
- [Product Management](../products/product-management.md) - Product data model
- [Order Lifecycle](../orders/order-lifecycle.md) - Order processing
