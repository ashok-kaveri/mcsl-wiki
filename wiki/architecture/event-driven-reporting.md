---
title: Event-Driven Reporting Architecture
category: architecture
sources: [reporting]
status: complete
last_updated: 2026-04-27
git_reference: 4728b3d692a83006cf44c6a40c57b06574e49639
---

# Event-Driven Reporting Architecture

## Overview

The reporting service implements an event-driven architecture for asynchronous order data aggregation and report generation. This pattern decouples the reporting workload from the main StorePep system, enabling scalable, on-demand report generation without impacting transaction processing performance.

## Architecture Pattern

### Components

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  StorePep Main  │  Event  │  Message Queue  │  Poll   │    Reporting    │
│     System      ├────────>│     (SQS)       ├────────>│    Service      │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                   │
                                  ┌────────────────────────────────┤
                                  │                                │
                            ┌─────▼─────┐                   ┌─────▼─────┐
                            │ Reporting  │                   │    S3     │
                            │    DB      │                   │  Storage  │
                            └────────────┘                   └───────────┘
```

### Event Flow

1. **Event Emission**: Main system emits domain events (OrderUpdated, OrderCreated, etc.)
2. **Queue Delivery**: Events published to SQS queues (order, job, bulk)
3. **Scheduled Polling**: Reporting service polls queues on schedule (configurable interval)
4. **Event Processing**: Listeners handle events, update denormalized data, trigger workflows
5. **Async Execution**: Long-running tasks (CSV export, email delivery) run asynchronously

## Queue Structure

| Queue Type | Purpose | Processor | Polling Frequency |
|------------|---------|-----------|-------------------|
| **Order** | Order lifecycle events (create, update, delete) | `OrderMessageProcessor` | Per schedule (default: 30s) |
| **Job** | Report job status events (created, updated) | `JobMessageProcessor` | Per schedule (default: 30s) |
| **Bulk** | Bulk operations (batch imports, mass updates) | `BulkMessageProcessor` | Per schedule (default: 30s) |

## Event Bus Pattern

Uses `@phivejs/eventing` — a custom event bus library for internal event handling.

**Publisher pattern**:
```typescript
@AfterInsert()
private publishCreated() {
  EventPublisher.emit(new JobCreated(this));
}
```

**Listener pattern**:
```typescript
addListenerTo({
  JobCreated,
}, listener(on, service, factory), 'Manage exports on job changes');
```

**Listeners registered**:
- `JobCreated` → `orderExporter.ts` — triggers CSV export
- `JobCreated` → `jobStatsSync.ts` — syncs job stats
- `JobUpdated` → `emailer.ts` — sends email on completion
- `OrderReportRequested` → `reportScheduler.ts` — schedules new report job

## Data Denormalization Strategy

**Problem**: Generating reports from the main normalized DB requires complex joins across 10+ tables, slowing down report queries.

**Solution**: Maintain a denormalized order snapshot table in the reporting DB.

**Order entity** (`infrastructure/order/entities/Order.ts`):
- **36 fields** — flattened from relational model
- **Updated on every order change** — synced via `OrderUpdated` events
- **Optimized for reads** — no joins needed for report generation
- **Soft deletes** — `deleted` flag for audit trail

**Trade-offs**:
- ✅ **Fast queries** — single table scan for reports
- ✅ **Independent scaling** — reporting DB can scale separately
- ✅ **Historical accuracy** — captures order state at reporting time
- ❌ **Eventual consistency** — slight lag between main system and reporting view
- ❌ **Storage overhead** — duplicate data

## Async Report Generation Flow

### 1. Request Phase
```
User → API → OrderReportRequested event → SQS
```

### 2. Job Scheduling Phase
```
OrderReportRequested listener → ReportScheduler → Job entity (status: pending)
```

### 3. Export Phase
```
JobCreated event → OrderExporter → OrderExportUnitaryService
→ Stream orders from DB → Transform to CSV → Upload to S3
→ Update Job (status: completed, reportPath: s3://...)
```

### 4. Notification Phase
```
JobUpdated event → Emailer → Nodemailer → Email with S3 link
```

**Streaming pattern**: Uses `pg-query-stream` for large datasets to avoid memory issues.

```typescript
// Pseudo-code from OrderExportUnitaryService
const queryStream = await connection.stream(sql);
queryStream
  .pipe(new CSVTransform())
  .pipe(s3UploadStream);
```

## Configuration Management

**AWS SSM Parameter Store** — centralized config for multi-environment deployments.

**RemoteConfig pattern** (`modules/app/config/RemoteConfig.ts`):
- Loads config from SSM on bootstrap
- Caches config in memory
- Environment-specific paths: `/mcsl/{env}/reporting/{key}`

**Config keys**:
- Queue URLs (SQS)
- DB connection strings
- S3 bucket names
- Email SMTP settings
- Polling intervals

## Deployment Architecture

**Serverless deployment** via AWS Lambda + API Gateway:
- **Lambda handler**: `@vendia/serverless-express` wraps Express app
- **Cold start mitigation**: `bootstrap.ts` pre-loads config
- **Multi-env**: QA, Prod (managed via Terraform + Ansible)

**Database migrations**: `node-pg-migrate` — versioned schema evolution.

## Benefits of This Pattern

1. **Decoupling**: Reporting workload isolated from transactional workload
2. **Scalability**: Can scale reporting service independently (more Lambda instances, larger DB)
3. **Resilience**: Failures in reporting don't affect order processing
4. **Flexibility**: Easy to add new report types without changing main system
5. **Auditability**: Full event log for debugging report issues

## Known Limitations

1. **Eventual consistency**: Reports may lag behind real-time state (typically <30s)
2. **Queue backlog**: Large event bursts can cause processing delays
3. **S3 link expiry**: Pre-signed URLs expire after TTL (requires re-generation)
4. **No real-time reports**: All reports are async (no instant download)

## Related Patterns

- [CQRS (Command Query Responsibility Segregation)](https://martinfowler.com/bliki/CQRS.html) — reporting DB is the "query" side
- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) — lite version (events for sync, not full history)
- [Materialized View](https://en.wikipedia.org/wiki/Materialized_view) — denormalized order table is a materialized view

## Related Pages

- [Reporting Module](../modules/reporting/reporting.md) — implementation details
