---
title: Reporting Service
category: module
domain: reporting
sources: [reporting]
status: complete
last_updated: 2026-04-27
git_reference: 4728b3d692a83006cf44c6a40c57b06574e49639
---

# Reporting Service

## Overview

Standalone microservice for asynchronous order data aggregation and customizable report generation. Implements event-driven architecture to decouple reporting workload from the main StorePep system, enabling scalable, on-demand CSV exports without impacting transaction processing.

**Repository**: `raw/reporting` (git submodule)
**Type**: TypeScript + Node.js + Express (Serverless Lambda deployment)
**Size**: 111 TypeScript files, ~3,800 LOC

## Key Capabilities

1. **Order Data Sync** — Listens to order events, maintains denormalized snapshot table
2. **Filtered CSV Export** — Async report generation with flexible filter criteria
3. **Email Delivery** — Uploads reports to S3, emails pre-signed download links
4. **Job Status Tracking** — Tracks report progress (pending → completed/failed)

## Architecture

See [Event-Driven Reporting Architecture](../../architecture/event-driven-reporting.md) for full pattern details.

**Event flow**:
```
OrderReportRequested → ReportScheduler → Job (pending)
→ JobCreated → OrderExporter → CSV generation → S3 upload
→ Job (completed) → JobUpdated → Emailer → Send email
```

## Key Components

### 1. Order Sync (`modules/app/order`)

**Purpose**: Keeps reporting DB in sync with main system order state.

**OrderImportUnitaryService** (`order/service/OrderImportUnitaryService.ts`):
- Receives `OrderUpdated` events from SQS
- Transforms external order format to internal `Order` entity
- Upserts denormalized order snapshot (36 fields)
- Handles soft deletes via `deleted` flag

**OrderTransformer** (`order/service/OrderTransformer.ts`):
- Maps main system order model to reporting model
- Flattens nested objects (customer, address, products)
- Normalizes field names for consistency

**Order entity** (`infrastructure/order/entities/Order.ts:1-138`):
- **36 fields**: storeId, accountId, orderId, orderDisplayId, status, tracking, customer info (name/email/phone), shipping address (5 fields), carrier, financials (7 fields), dates (6 fields), products, tags, SKU
- **Indexes**: (not visible in entity, likely on orderId, storeId, status, shippingDate)
- **Soft deletes**: `deleted: boolean`

### 2. Report Generation (`modules/app/reporting`)

**ReportScheduler** (`reporting/service/ReportScheduler.ts`):
- Creates `Job` entities with filter criteria
- Persists job to DB (status: pending)
- Emits `JobCreated` event

**OrderExportUnitaryService** (`order/service/OrderExportUnitaryService.ts`):
- Streams orders from DB matching filter criteria
- Transforms to CSV rows via `CSVTransform`
- Uploads to S3 bucket
- Updates job with `reportPath` and `status: completed`

**Streaming implementation**:
```typescript
// Uses pg-query-stream for large datasets
const queryStream = await connection.stream(sql);
queryStream
  .pipe(new CSVTransform())      // Transform order → CSV row
  .pipe(new RowCountingTransform()) // Track progress
  .pipe(s3UploadStream);           // Upload to S3
```

**CSV structure** (inferred from tests):
- Headers: orderId, orderDisplayId, status, carrier, trackingIds, customerName, customerEmail, shippingAddress, shippingTotal, carrierShippingCost, orderCreatedAt, shippingDate, etc.
- Encoding: UTF-8
- Delimiter: comma

**Job entity** (`infrastructure/reporting/entities/Job.ts:1-98`):
- **Fields**: jobId (UUID), storeId, accountId, payload (JSON filter), completed, total, contacts (CSV), externalReference, status, reportPath, tries
- **Status values**: `pending`, `completed`, `failed`
- **Events**: Emits `JobCreated` (AfterInsert), `JobUpdated` (AfterUpdate)

### 3. Filter System (`modules/app/reporting/service`)

**Composable filter pattern** — build complex queries from simple predicates.

**Filter types**:
- **EqualsFilter** (`EqualsFilter.ts`) — exact match (status = 'fulfilled')
- **LikeFilter** (`LikeFilter.ts`) — partial match (customerName LIKE '%John%')
- **RangeFilter** (`RangeFilter.ts`) — between values (shippingDate BETWEEN '2026-01-01' AND '2026-01-31')
- **CompositeFilter** (`CompositeFilter.ts`) — AND/OR logic (status = 'fulfilled' AND carrier = 'FedEx')

**DateRange** (`DateRange.ts`):
- Convenience wrapper for date-based ranges
- Handles timezone conversion (all dates stored in UTC)

**FilterFactory** (`FilterFactoryImpl.ts`):
- Deserializes JSON filter payloads to typed filter objects
- Validates filter structure against schema

**Example filter payload** (JSON):
```json
{
  "app": "shopify",
  "account": "acct_123",
  "store": "store_456",
  "filter": {
    "type": "composite",
    "operator": "AND",
    "filters": [
      { "type": "range", "field": "shippingDate", "from": "2026-01-01", "to": "2026-01-31" },
      { "type": "equals", "field": "status", "value": "fulfilled" }
    ]
  }
}
```

### 4. Event Listeners (`modules/app/reporting/listener`)

**orderExporter.ts**:
- Listens to: `JobCreated`
- Action: Triggers `OrderExportUnitaryService.export()`
- Error handling: Catches exceptions, logs, returns `null` (non-blocking)

**emailer.ts**:
- Listens to: `JobUpdated`
- Action: Sends email with S3 pre-signed URL when `job.status === 'completed'`
- Uses: Nodemailer (SMTP client)
- Contacts: Parsed from `job.contacts` (CSV string)

**reportScheduler.ts**:
- Listens to: `OrderReportRequested`
- Action: Creates `Job` entity, persists to DB

**jobStatsSync.ts**:
- Listens to: `JobCreated`
- Action: Syncs job stats to external system (likely main StorePep dashboard)

**orderReportRequestStatusChecker.ts**:
- Listens to: Internal event (periodic)
- Action: Checks for stale jobs, retries failed jobs (up to `job.tries` limit)

### 5. Message Processing (`modules/app/messaging`)

**MessageProcessor** (interface):
- `process()` — poll queue, deserialize messages, emit events

**Implementations**:
- `BulkMessageProcessor` — processes bulk SQS queue
- `OrderMessageProcessor` — processes order SQS queue
- `JobMessageProcessor` — processes job SQS queue

**Scheduler** (`modules/app/job/Scheduler.ts`):
- `schedule(callback)` — registers callback for periodic execution
- Used in `index.ts:11-24` to poll queues on interval

**Bootstrap sequence** (`index.ts:27-35`):
```typescript
await Context.init();               // DI container setup
initAPI();                          // Express app
schedule(scheduler, BulkProcessor, 'BULK');
schedule(scheduler, OrderProcessor, 'ORDER');
schedule(scheduler, JobProcessor, 'JOB');
```

## Configuration

**RemoteConfig** (`modules/app/config/RemoteConfig.ts`):
- Loads config from AWS SSM Parameter Store
- Called in `bootstrap.ts:6` before app initialization

**Config keys** (inferred):
- `QUEUE_URL_BULK` — SQS queue for bulk operations
- `QUEUE_URL_ORDER` — SQS queue for order events
- `QUEUE_URL_JOB` — SQS queue for job events
- `S3_BUCKET_REPORTS` — S3 bucket for report storage
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` — Email delivery
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` — Postgres connection
- `POLL_INTERVAL_MS` — Queue polling frequency (default: 30000)

## Data Flow

### Order Sync Flow
```
1. Main System → Order event → SQS Order Queue
2. OrderMessageProcessor polls queue → deserializes event
3. OrderImportUnitaryService.import(externalOrder)
4. OrderTransformer.transform(externalOrder) → Order entity
5. Upsert to reporting DB
```

### Report Generation Flow
```
1. API Request → POST /reports (filter criteria, contacts)
2. OrderReportRequested event → SQS Job Queue
3. JobMessageProcessor polls → ReportScheduler.scheduleOrderReport()
4. Create Job entity (status: pending) → DB
5. JobCreated event → OrderExporter listener
6. OrderExportUnitaryService.export(criteria, jobId)
7. Stream orders → CSV → S3 upload
8. Update Job (status: completed, reportPath: s3://...)
9. JobUpdated event → Emailer listener
10. Send email with pre-signed S3 URL
```

## Test Coverage

**Test suite**:
- **46 test files** (~4,822 LOC) — 1.27:1 test-to-code ratio
- **6 integration tests** — DB operations, streaming exports
- **40 unit tests** — services, filters, transformers, listeners

**Tested scenarios**:

| Component | Tests | Coverage |
|-----------|-------|----------|
| **OrderImportUnitaryService** | Unit + Integration | ✅ Full |
| **OrderExportUnitaryService** | Unit + Integration | ✅ Full |
| **Filter system** | 10 unit tests (all filter types + factory) | ✅ Full |
| **Event listeners** | 5 unit tests (all listeners) | ✅ Full |
| **Job entity** | Integration test | ✅ Full |
| **Order entity** | Integration test | ✅ Full |
| **ReportScheduler** | Unit test | ✅ Full |
| **OrderTransformer** | Unit test | ✅ Full |
| **OrderLookupUnitaryService** | Unit test | ✅ Full |

**Test organization**:
- `test/modules/app/order/` — order sync tests
- `test/modules/app/reporting/` — report generation tests
- `test/modules/infrastructure/` — entity integration tests
- `test/migration.test.ts` — DB migration validation

**Coverage tools**:
- `jest` (unit + integration)
- `nyc` (istanbul) for coverage reporting
- Separate configs: `jest.config.unit.cjs`, `jest.config.integration.cjs`

## Database Schema

**Migrations** (`modules/app/migrations/*.ts`):
- 12 migrations tracked
- Managed by `node-pg-migrate`

**Key migrations**:
- `1744279008604-create-order.ts` — Initial order table
- `1744366552633-create-job.ts` — Initial job table
- `1745127312773-add-account-order.ts` — Add accountId to order
- `1745220345172-rename-platform-app-order.ts` — Rename platform → app
- `1745856682204-add-totals-products.ts` — Add financial totals, products JSON
- `1745900823238-add-package-dimensions.ts` — Add packageDimensions field
- `1746618727473-add-tries-job.ts` — Add retry counter to job
- `1746765556637-add-deleted-order.ts` — Add soft delete flag
- `1750000000001-add-timezone-to-all-order-dates.ts` — Normalize dates to UTC
- `1764158323558-add-filter-columns-to-order.ts` — Add indexed filter columns (tags, sku, lineItemsQty, shippingMethod)

**Current schema** (inferred from entities + migrations):

**Order table**:
```sql
CREATE TABLE "order" (
  id SERIAL PRIMARY KEY,
  store_id VARCHAR NOT NULL,
  account_id VARCHAR NOT NULL,
  app VARCHAR NOT NULL,
  order_id VARCHAR NOT NULL UNIQUE,
  order_display_id VARCHAR,
  status VARCHAR,
  tracking_ids TEXT,
  tracking_status VARCHAR,
  shipping_date TIMESTAMP WITH TIME ZONE,
  customer_name VARCHAR,
  customer_email VARCHAR,
  customer_phone VARCHAR,
  shipping_address TEXT,
  shipping_address_state VARCHAR,
  shipping_address_country VARCHAR,
  shipping_address_city VARCHAR,
  shipping_address_postal_code VARCHAR,
  carrier VARCHAR,
  shipping_total DECIMAL(10,2),
  carrier_shipping_cost DECIMAL(10,2),
  cancelled_at TIMESTAMP WITH TIME ZONE,
  label_created_at TIMESTAMP WITH TIME ZONE,
  fulfilled_at TIMESTAMP WITH TIME ZONE,
  order_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  order_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
  total_order_value DECIMAL(10,2),
  sub_total DECIMAL(10,2),
  shipping_tax DECIMAL(10,2),
  products JSONB,
  package_dimensions JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(6),
  deleted BOOLEAN DEFAULT FALSE,
  error TEXT,
  tags TEXT,
  sku TEXT,
  line_items_qty INTEGER,
  shipping_method VARCHAR
);

-- Indexes (likely):
CREATE INDEX idx_order_store_id ON "order"(store_id);
CREATE INDEX idx_order_account_id ON "order"(account_id);
CREATE INDEX idx_order_status ON "order"(status);
CREATE INDEX idx_order_shipping_date ON "order"(shipping_date);
CREATE INDEX idx_order_created_at ON "order"(order_created_at);
```

**Job table**:
```sql
CREATE TABLE "job" (
  id SERIAL PRIMARY KEY,
  job_id VARCHAR NOT NULL UNIQUE,
  store_id VARCHAR NOT NULL,
  account_id VARCHAR,
  payload JSONB NOT NULL,
  completed INTEGER DEFAULT 0,
  total INTEGER DEFAULT 0,
  contacts TEXT,
  external_reference VARCHAR,
  status VARCHAR DEFAULT 'pending',
  report_path VARCHAR,
  tries INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(6)
);
```

## Dependencies

**Upstream** (main system → reporting):
- `storepep-react` — emits OrderUpdated, OrderCreated, OrderDeleted events

**Downstream** (reporting → external):
- AWS S3 — report storage
- Email (SMTP) — report delivery
- Main system dashboard — job stats sync (optional)

**Internal libraries**:
- `@phivejs/eventing` — event bus (custom library, likely internal to phive)
- `typeorm` — ORM for Postgres
- `express` + `@vendia/serverless-express` — HTTP server (Lambda wrapper)
- `pg-query-stream` — streaming queries for large datasets
- `nodemailer` — email delivery
- `axios` — HTTP client
- `inversify` / `typedi` — DI containers

## Deployment

**Infrastructure as Code**:
- `terraform/` — AWS resources (Lambda, SQS, S3, RDS, SSM params)
- `deploy/` — Ansible playbooks for config promotion

**Deployment steps** (from README):
1. Build: `npm run build` → compiles TS to `dist/`
2. Package: Zip `dist/` + `node_modules/` → Lambda artifact
3. Deploy via Ansible: `ansible-playbook deploy_config.yml` (per API type: job, bulk, order)
4. Terraform apply: `tflocal apply` (local), `terraform apply` (QA/Prod)

**Environments**:
- Local: Localstack (mocked AWS services)
- QA: `mcsl-qa01` (AWS account `phive-workload-qa01`)
- Prod: `mcsl-prod02` (AWS account `phive-workload-prod02`)

**Lambda configuration**:
- Runtime: Node.js 18.19 (Volta-managed)
- Handler: `dist/src/bootstrap.js`
- Timeout: (not specified, likely 900s for long exports)
- Memory: (not specified, likely 1024MB+)

## Known Issues / Tech Debt

1. **No pagination on large exports** — streams entire result set (memory risk for 100k+ orders)
2. **No resume on failure** — if export fails mid-stream, must restart from beginning
3. **No incremental sync** — always full upsert on order events (no delta detection)
4. **S3 link expiry** — pre-signed URLs expire after TTL (users must download promptly)
5. **No real-time reports** — all reports async (no instant download UI)
6. **Queue backlog monitoring** — no alerting on queue depth (could miss processing delays)
7. **No compression** — CSV files not gzipped (large files slow to download)

## Related Pages

- [Event-Driven Reporting Architecture](../../architecture/event-driven-reporting.md) — architectural pattern
- [Order Management](../orders/order-lifecycle.md) — upstream order events (TODO)
- [Test Coverage](../../features.md) — automated test mapping (TODO)
