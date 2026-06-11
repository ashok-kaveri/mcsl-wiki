---
title: Product CSV Export for Large Catalogs
category: product-feature
domain: products
sources: [zendesk, storepep-react]
status: proposed
last_updated: 2026-06-11
git_reference: 01898b83a15a8ca9495bf890bcdb47a745792c0d
---

# Product CSV Export for Large Catalogs

## Problem Statement

The product CSV export (`GET /api/products/export`) silently never completes for stores with large catalogs. The merchant clicks Export, waits, and no document ever arrives — no error, no progress, nothing.

- **Evidence**: [Zendesk #394571](https://pluginhive.zendesk.com/agent/tickets/394571) (original: #389897) — Biomatik (`ez90xj-ps.myshopify.com`, ~78k products) attempted export 14 times on 2026-06-10 (12:13–14:08 UTC); zero completions in `mcsl-imports-01` logs. A 12-product store exported in 119 ms in the same window. Ops incident: `ops-wiki/wiki/04_Incidents/Incident - 2026-06-10 - MCSL Product CSV Export Hangs for Large Catalogs.md`.
- **Affected users**: any merchant with a catalog large enough to exceed the ~30 s LB timeout; reported by 1 strategic customer (agreed to upgrade $29 Popular → $99 Enterprise once the app works for their catalog — upsell blocked on this).
- **Impact**: Revenue (blocked Enterprise upgrade) + reliability — the export loop **blocks the Node event loop on the MCSL imports server**, stalling all merchants' import/export traffic while it runs; each retry stacks another multi-hour job.

### Root Cause

`server/src/routes/products.js:498` → `server/src/shared/products/productsHelperFunctions.js:354` (`getCSVData`):

1. `db.product.findWithLean(query)` loads the entire catalog into memory — no cursor, pagination, or projection.
2. O(n²) row assembly: `valuesArray += productCSVArray.values` coerces the accumulator to a string and re-copies it every iteration, and `valuesCSV = valuesArray.toString()` also runs inside the loop. At 78k rows that's ~10¹² byte copies — hours of blocked CPU.
3. Fully synchronous request/response: even a successful build couldn't beat the ~30 s gateway timeout with a multi-MB JSON body.

## User Stories

### Story 1: As a merchant with a large catalog, I want product CSV export to run as a background job, so that I reliably get my export file regardless of catalog size

**Acceptance Criteria**:
- [ ] Given a store with 78k+ products, when the merchant initiates an export, then the request returns immediately with a job acknowledgement (no long-held HTTP request)
- [ ] Given a running export job, when it completes, then the merchant is notified (socket event and/or email) with a download link to the generated CSV
- [ ] Given the generated file, when the merchant edits it and re-imports via the existing product CSV upload, then it is accepted — header and 35-column row format identical to the current export
- [ ] Given an export job in progress, when other merchants use import/export, then their requests are unaffected (no event-loop blocking on the imports server)

### Story 2: As the platform, I want the CSV build to be streaming and linear-time, so that export cost scales with catalog size

**Acceptance Criteria**:
- [ ] Given any catalog size, when the CSV is built, then products are read via a query cursor with a projection (no full-collection load into memory)
- [ ] Given row assembly, when rows are accumulated, then they are joined once after iteration (array + single `join`) — no string re-concatenation per row
- [ ] Given a 78k-product store, when export runs, then it completes in minutes with bounded memory (verify on QA with a seeded catalog)

### Story 3: As a support engineer, I want a server-side export script, so that I can deliver a CSV to a blocked merchant without waiting for the product fix

**Acceptance Criteria**:
- [x] Given a storeUUID, when running `node src/supportScripts/exportProductsToCSV.js <storeUUID> [--active] [--out file.csv]` on the imports server, then a CSV identical in format to the app export is written (streaming cursor, Node v10 + mongoose 4.x compatible)
- [ ] Given ZD #394571, when the script is run for storeUUID `f4d8c084-f83f-43f8-8020-aedb67cf12b0` with `--active`, then the file is delivered to the merchant

### Story 4 (guardrail): As the platform, I want oversized synchronous exports rejected, so that the legacy path can never block the imports server again

**Acceptance Criteria**:
- [ ] Given a synchronous export request for a store above a product-count threshold, when the request is received, then it is routed to the async job path (or rejected with a clear message until async ships)

## Cross-Links

| Type | Link | Relationship |
|------|------|-------------|
| Wiki Module | [Product Import/Export](../../modules/products/product-import-export.md) | Export implementation, CSV format |
| Code | `server/src/routes/products.js:498`, `server/src/shared/products/productsHelperFunctions.js:354` | Broken sync export path |
| Code | `server/src/supportScripts/exportProductsToCSV.js` | Support workaround script (new) |
| Zendesk | [#394571](https://pluginhive.zendesk.com/agent/tickets/394571), #389897 | Customer report (Biomatik) |
| Ops Incident | `ops-wiki` → Incident - 2026-06-10 - MCSL Product CSV Export Hangs for Large Catalogs | Log evidence, server impact |
| Slack | [L3 thread](https://pluginhive.slack.com/archives/C02E15X8X0C/p1781129632547599?thread_ts=1778793143.446829&cid=C02E15X8X0C) | Escalation |

## Customer Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| Related tickets (30d) | 1 (#394571, strategic — Enterprise upgrade blocked) | → |
| Automation confidence | 🔴 None — no automated export test for large catalogs | |

## Acceptance Sign-off

| Criteria | Status | Verified By |
|----------|--------|-------------|
| Support workaround delivered (Story 3) | ⬜ | |
| Async export shipped (Story 1) | ⬜ | |
| Streaming/linear CSV build (Story 2) | ⬜ | |
| Guardrail threshold (Story 4) | ⬜ | |
| Regression: exported CSV re-imports cleanly | ⬜ | |
