---
title: Backend Architecture
category: architecture
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Backend Architecture

## Overview

The StorePep backend is a Node.js application built on Express.js, providing RESTful APIs for the frontend and webhook endpoints for external integrations. It follows a layered architecture with clear separation between routes, business logic, and data access.

**Location**: `server/src/`
**Entry Points**:
- `server/src/index.js` - Standard single-process mode
- `server/src/index-cluster.js` - Cluster mode for production (multi-core)

## Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Node.js | 14+ (.nvmrc) | Runtime |
| Express.js | 4.15.3 | Web framework |
| Mongoose | 4.11.10 | MongoDB ODM |
| Socket.io | 2.0.4 | Real-time communication |
| Redis | 2.8.0 | Caching layer |
| Cron | 1.3.0 | Scheduled jobs |
| JWT | 7.4.1 | Authentication |
| Winston | 3.3.4 | Logging |
| Puppeteer | 13.5.2 | PDF generation & screenshots |
| EasyPost | 5.6.1 | Multi-carrier shipping API |

See [Technology Stack](./technology-stack.md) for complete dependency list.

## Directory Structure

```
server/src/
├── index.js                    # Application entry point (single process)
├── index-cluster.js            # Cluster mode entry (production)
├── dbConnector.js              # MongoDB connection setup
├── storepepConfig.js           # Application configuration
├── storePepConstants.js        # Constants and enums
│
├── routes/                     # API route handlers (82 files)
│   ├── orders.js               # Order management (2139 lines!)
│   ├── products.js             # Product catalog
│   ├── carriers.js             # Carrier configuration
│   ├── shipments.js            # Shipment processing
│   ├── manifest.js             # Manifest generation
│   ├── labels.js               # Label generation
│   ├── pickup.js               # Pickup scheduling
│   ├── payment.js              # Payment processing
│   ├── subscription.js         # Subscription management
│   ├── automation.js           # Automation rules
│   ├── ratesApi.js             # Rate shopping
│   └── ... (71 more routes)
│
├── models/                     # MongoDB models (92 files)
│   ├── orders.js               # Order schema
│   ├── products.js             # Product schema
│   ├── carriers.js             # Carrier configuration schema
│   ├── packages.js             # Package tracking schema
│   ├── manifest.js             # Manifest schema
│   ├── batch.js                # Batch processing schema
│   ├── subscriptions.js        # Subscription schema
│   ├── storepepTransactions.js # Transaction schema
│   └── ... (84 more models)
│
├── shared/                     # Business logic layer (40+ modules)
│   ├── order/
│   │   ├── OrderProcessingService.js
│   │   └── ...
│   ├── products/
│   │   ├── ProductImportService.js
│   │   └── ...
│   ├── label/                  # Label generation logic
│   ├── manifest/               # Manifest generation logic
│   ├── pickup/                 # Pickup scheduling logic
│   ├── batch/                  # Batch processing logic
│   ├── payment/                # Payment processing logic
│   ├── subscription/           # Subscription logic
│   ├── ratesApi/               # Rate shopping logic
│   ├── shopify/                # Shopify integration
│   ├── API/                    # External API integrations
│   │   ├── carriers/           # Carrier API clients
│   │   │   ├── fedex/
│   │   │   ├── ups/
│   │   │   ├── dhl/
│   │   │   ├── canadapost/
│   │   │   ├── usps/
│   │   │   └── ... (10+ more)
│   │   └── stores/             # Store platform clients
│   │       ├── shopify/
│   │       ├── woocommerce/
│   │       ├── magento/
│   │       └── ...
│   ├── cache/                  # Caching utilities
│   ├── notifications/          # Email/webhook notifications
│   ├── documents/              # PDF/document generation
│   ├── cronJob/                # Cron job definitions
│   ├── errorHandler/           # Error handling utilities
│   └── ... (30+ more modules)
│
├── modules/                    # Domain modules (27 folders)
│   ├── order/
│   ├── order-presets/
│   ├── orderFulfilmentSummary/
│   ├── orderHistory/
│   ├── subscription/
│   ├── product-custom-value/
│   ├── reporting/
│   ├── tracking/
│   ├── trackingOrder/
│   ├── wms/                    # Warehouse management
│   ├── workflow/               # Automation workflows
│   └── ... (17 more)
│
├── middlewares/                # Express middleware
│   ├── authenticate.js         # JWT authentication
│   ├── authorise.js            # Role-based authorization
│   ├── subscriptionValidator.js # Subscription tier validation
│   ├── ratesApiAuthentication.js # Rates API key auth
│   └── ...
│
├── ACL/                        # Access Control Lists
│   └── ... (permission definitions)
│
├── db-migrations/              # Database migrations (106+ files)
│   ├── migrate-mongo-config.js
│   └── migrations/
│       ├── 20200101120000-initial.js
│       └── ... (105+ more)
│
└── supportScripts/             # Maintenance & utility scripts
    ├── createStorepepAdmin.js
    ├── createStorepepPlans.js
    ├── cleanUpStorepepAccount.js
    └── ... (data migration, testing scripts)
```

## Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP Requests                         │
│              (REST API, Webhooks, Socket.io)            │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Middleware Layer                        │
│  ┌───────────┐  ┌───────────┐  ┌────────────────────┐  │
│  │   CORS    │  │   Helmet  │  │  Body Parser       │  │
│  └───────────┘  └───────────┘  └────────────────────┘  │
│  ┌───────────┐  ┌───────────┐  ┌────────────────────┐  │
│  │   Auth    │  │ Authz/ACL │  │  Subscription Val  │  │
│  └───────────┘  └───────────┘  └────────────────────┘  │
│  ┌───────────┐  ┌───────────┐  ┌────────────────────┐  │
│  │  Logging  │  │   Error   │  │  Rate Limiting     │  │
│  └───────────┘  └───────────┘  └────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Route Handlers                         │
│        (82 route files - thin controllers)              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Request validation, parameter extraction          │  │
│  │  Delegate to service layer                         │  │
│  │  Format response, handle errors                    │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                          │
│     (shared/ modules - business logic encapsulation)    │
│  ┌────────────────┐  ┌───────────────────────────────┐  │
│  │ OrderProcessing│  │  ProductImportService         │  │
│  │    Service     │  └───────────────────────────────┘  │
│  └────────────────┘                                     │
│  ┌────────────────┐  ┌───────────────────────────────┐  │
│  │ LabelGenerator │  │  ManifestService              │  │
│  └────────────────┘  └───────────────────────────────┘  │
│  ┌────────────────┐  ┌───────────────────────────────┐  │
│  │  CarrierAPI    │  │  StoreIntegration             │  │
│  │   Clients      │  │     Handlers                  │  │
│  └────────────────┘  └───────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Access Layer                      │
│            (Mongoose models - 92 schemas)               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Schema definition, validation, hooks           │    │
│  │  CRUD operations, queries                       │    │
│  └─────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│                      MongoDB                             │
│                  (Database Layer)                        │
└─────────────────────────────────────────────────────────┘
```

## Key Architectural Patterns

### 1. Service Layer Pattern

Business logic is extracted into reusable service classes in `shared/`:

```javascript
// shared/order/OrderProcessingService.js
class OrderProcessingService {
  async processOrder(orderId, userId) {
    // 1. Fetch order from DB
    const order = await Order.findById(orderId);

    // 2. Apply business rules
    const shippingDetails = await this.calculateShipping(order);

    // 3. Update order state
    order.status = 'Processing';
    await order.save();

    // 4. Trigger side effects (notifications, webhooks)
    await this.notifyCustomer(order);

    return order;
  }
}
```

**Benefits**:
- Reusable across multiple routes
- Testable in isolation
- Centralized business logic
- Easier to maintain

### 2. Middleware Chain Pattern

Express middleware provides cross-cutting concerns:

```javascript
// Typical route setup
router.post('/orders',
  authenticate,           // Verify JWT
  authorise(['merchant']), // Check role
  subscriptionValidator,  // Check subscription tier
  validateRequest,        // Validate request body
  asyncHandler(async (req, res) => {
    // Route logic here
  })
);
```

### 3. Repository Pattern (via Mongoose)

Mongoose models act as repositories:

```javascript
// models/orders.js
const orderSchema = new Schema({
  orderNumber: String,
  customer: Object,
  items: [itemSchema],
  status: String,
  // ...
});

// Instance methods
orderSchema.methods.markAsShipped = function() {
  this.status = 'Shipped';
  this.shippedAt = new Date();
};

// Static methods (query builders)
orderSchema.statics.findPendingOrders = function(userId) {
  return this.find({ userId, status: 'Pending' });
};

module.exports = mongoose.model('Order', orderSchema);
```

### 4. Event Sourcing (Partial)

Event sourcing support via `@phivejs/eventsourcing-support`:
- Audit trail for critical operations
- Order state transitions logged as events
- Replay capability for debugging

### 5. Feature Toggle Pattern

Runtime feature control via `@phivejs/feature-switch`:

```javascript
const featureSwitch = require('@phivejs/feature-switch');

if (featureSwitch.isEnabled('advanced_automation', userId)) {
  // Enable advanced automation features
}
```

**Configuration**: `server/featureToggles.json` (62KB)

## Request/Response Flow

### Typical API Request Flow

1. **Client sends HTTP request** (e.g., POST /api/orders)
2. **Express receives request**
3. **Middleware chain executes**:
   - CORS check
   - Helmet security headers
   - Body parser (JSON)
   - Authentication (JWT verification)
   - Authorization (role/ACL check)
   - Subscription validation (tier check)
   - Request logging
4. **Route handler invoked**:
   - Validate request parameters
   - Call service layer method
5. **Service layer processes**:
   - Business logic execution
   - External API calls (if needed)
   - Database operations via Mongoose
6. **Response formatted and sent**:
   - Success: `res.json({ success: true, data: ... })`
   - Error: Error handler middleware formats error response
7. **Response logging** (Winston)

## Database Layer

### MongoDB Connection

**File**: `server/src/dbConnector.js`

```javascript
mongoose.connect(mongoURL, {
  useNewUrlParser: true,
  useUnifiedTopology: true
});
```

### Schema Organization

92 Mongoose models organized by domain:
- **Core Entities**: orders, products, packages, carriers
- **Fulfillment**: manifest, batch, pickups, labels
- **Integration**: stores, carrierAccounts, webhooks
- **Billing**: subscriptions, transactions, invoices
- **Configuration**: settings, automation, workflows
- **User Management**: users, teams, permissions

### Migration Strategy

**Tool**: `migrate-mongo` (106+ migrations)

**Location**: `server/src/db-migrations/migrations/`

Migrations track schema changes:
- Adding new fields
- Removing deprecated fields
- Data transformations
- Index creation

**Run migrations**:
```bash
npx migrate-mongo up   # Apply pending migrations
npx migrate-mongo down # Rollback last migration
```

## External Integrations

### 1. Shipping Carrier APIs

**Location**: `server/src/shared/API/carriers/`

Supported carriers (15+):
- FedEx (SOAP API)
- UPS (REST API)
- DHL (XML API)
- Canada Post
- USPS (via EasyPost)
- Australia Post
- Stamps.com
- TNT, Aramex, and more

**Multi-carrier abstraction**: EasyPost API (`@easypost/api` 5.6.1) provides unified interface for many carriers.

### 2. E-commerce Platform APIs

**Location**: `server/src/shared/API/stores/`

Supported platforms:
- **Shopify**: `@phivejs/shopify-api` 0.1.14 (custom wrapper)
- **WooCommerce**: `woocommerce-api` 1.4.2
- **Magento**: Custom SOAP/REST client
- **BigCommerce**: REST API
- **PrestaShop**: Custom integration

**Integration flow**:
1. Merchant connects store via OAuth
2. Webhook registered for order events
3. Orders automatically imported on creation/update
4. Product catalog synced periodically

### 3. Payment Gateway APIs

**Location**: `server/src/shared/payment/`

- **Stripe**: `stripe` 8.156.0 - Subscriptions, one-time payments
- **PayPal**: `paypal-rest-sdk` 1.8.1 - Subscription management
- **Razorpay**: `razorpay` 2.0.4 - India-specific payments

### 4. Monitoring & Observability

- **Sentry**: Error tracking (`@sentry/node`)
- **New Relic**: APM monitoring (`newrelic` 8.7.1)
- **Prometheus**: Metrics collection (`prom-client` 11.1.2)
- **Winston**: Structured logging with Syslog transport

## Background Jobs (Cron)

**Location**: `server/src/shared/cronJob/`

Scheduled tasks using `cron` package:

- **Tracking updates**: Poll carrier APIs for tracking information (every 30 min)
- **Subscription renewals**: Check and process subscription renewals (daily)
- **Order sync**: Sync orders from connected stores (configurable frequency)
- **Manifest reminders**: Send reminders for un-manifested shipments (daily)
- **Data cleanup**: Archive old data, remove expired sessions (weekly)

**Configuration**: Cron expressions in `storepepConfig.js`

## Real-Time Communication (Socket.io)

**Setup**: `server/src/index.js` (Socket.io server initialization)

**Namespaces**:
- `/` - Default namespace for general updates
- `/orders` - Order-specific events
- `/tracking` - Tracking updates

**Event Types**:
- `order:updated` - Order status change
- `label:generated` - Label creation completed
- `batch:completed` - Batch processing finished
- `tracking:updated` - New tracking info available

**Authentication**: Socket connections authenticated via JWT token in handshake.

## Caching Strategy (Redis)

**Client**: `redis` 2.8.0, `node-cache` 5.1.2

**Use cases**:
1. **Rate shopping cache**: Store carrier rate quotes (TTL: 15 min)
2. **Session storage**: User sessions and temporary data
3. **Feature toggles**: Cache feature flag state
4. **API response cache**: Cache expensive computations
5. **Webhook deduplication**: Track processed webhook IDs

**Pattern**:
```javascript
const cachedData = await redis.get(`rates:${cacheKey}`);
if (cachedData) {
  return JSON.parse(cachedData);
}

const freshData = await fetchRatesFromCarrier();
await redis.set(`rates:${cacheKey}`, JSON.stringify(freshData), 'EX', 900); // 15 min TTL
return freshData;
```

## Document Generation

### PDF Generation

**Libraries**:
- `puppeteer` 13.5.2 - Screenshots, HTML to PDF
- `html-pdf` 3.0.1 - Simple HTML to PDF
- `handlebars` 4.7.7 - Template rendering

**Use cases**:
- Shipping labels (4x6 thermal labels)
- Packing slips
- Invoices
- Manifests
- Commercial invoices (international)

**Process**:
1. Render Handlebars template with data
2. Convert HTML to PDF via Puppeteer
3. Upload PDF to S3 (if needed)
4. Return PDF URL or base64 data

### Image Processing

**Library**: `jimp` 0.2.28

**Use cases**:
- Resize product images
- Generate thumbnails
- Add watermarks to labels

## Error Handling

### Error Handler Middleware

**Location**: `server/src/shared/errorHandler/`

Centralized error handling:
- Catches all errors from routes/services
- Formats error response consistently
- Logs error details to Winston
- Sends error to Sentry
- Returns appropriate HTTP status code

**Example**:
```javascript
app.use((err, req, res, next) => {
  logger.error(err.message, { stack: err.stack, url: req.url });
  Sentry.captureException(err);

  res.status(err.statusCode || 500).json({
    success: false,
    error: err.message || 'Internal Server Error'
  });
});
```

## Authentication & Authorization

### Authentication (JWT)

**Middleware**: `server/src/middlewares/authenticate.js`

1. Extract JWT from `Authorization` header
2. Verify signature using secret key
3. Decode payload to get user ID and account ID
4. Attach user object to `req.user`

**JWT Libraries**: `jsonwebtoken` 7.4.1, `jwks-rsa` 3.0.1 (for Auth0 OAuth)

### Authorization (ACL)

**Middleware**: `server/src/middlewares/authorise.js`

Role-based and permission-based checks:
- `merchant` - Regular merchant user
- `storepepTeam` - StorePep admin
- `ratesApi` - API key access for rates API

**ACL Definitions**: `server/src/ACL/`

### Subscription Validation

**Middleware**: `server/src/middlewares/subscriptionValidator.js`

Checks if user's subscription tier allows access to feature:
- `Lite` - Basic features
- `Advanced` - Additional automation
- `Pro` - All features unlocked

**Feature gating**: If feature requires Pro but user has Lite, return 403 Forbidden.

## Logging

**Library**: `winston` 3.3.4 with transports:
- Console (development)
- File rotation (`winston-logrotate`)
- Syslog (`winston-syslog`) for centralized logging

**Log Levels**: error, warn, info, debug

**Structured Logging**:
```javascript
logger.info('Order processed', {
  orderId: order._id,
  userId: req.user.id,
  carrier: 'FedEx',
  duration: processingTime
});
```

## Configuration Management

**File**: `server/src/storepepConfig.js`

Environment-based configuration:
- Database connection strings
- API keys (Stripe, PayPal, EasyPost, etc.)
- Feature toggle defaults
- Cron job schedules
- Email settings (Mailgun)
- S3 bucket names
- Redis connection

**Environment Variables**: Loaded via `dotenv` from `.env` files.

## Deployment Modes

### Single Process Mode

**Entry**: `server/src/index.js`

Standard Node.js single process:
```bash
npm start  # Runs nodemon src/index.js
```

### Cluster Mode

**Entry**: `server/src/index-cluster.js`

Multi-core utilization for production:
```bash
npm run cluster  # Spawns workers per CPU core
```

**Benefits**:
- Better CPU utilization
- Fault tolerance (worker restart on crash)
- Load balancing across cores

## Dependencies

- [Overview](./overview.md) - High-level system architecture
- [Technology Stack](./technology-stack.md) - Complete dependency listing
- [Data Flow](./data-flow.md) - Request/response cycles (to be created)
- [Database Migrations](../operations/database-migrations.md) (to be created)

## Referenced By

- All backend module pages (orders, shipping, products, etc.)
- [API Conventions](../patterns/api-conventions.md) (to be created)
- [Error Handling Patterns](../patterns/error-handling.md) (to be created)

## Known Issues / Tech Debt

1. **Mongoose Version**: 4.11.10 is very old - modern version is 7+
2. **Express Version**: 4.15.3 is outdated - current is 4.18+
3. **Large Route Files**: `orders.js` is 2139 lines - needs refactoring into smaller modules
4. **Callback Hell**: Some older code uses callbacks instead of async/await
5. **Error Handling**: Inconsistent error handling across different modules
6. **Testing**: Limited test coverage (Jest configured but minimal tests)
7. **Security**: Several dependencies have known vulnerabilities (need updates)

## Related Pages

- [Frontend Architecture](./frontend-architecture.md)
- [Deployment Pipeline](./deployment-pipeline.md) (to be created)
- [Service Layer Patterns](../patterns/service-layer.md) (to be created)
