---
title: Order Update Scenarios (Functional)
category: module
domain: orders
sources: [storepep-react, order-updates, fulfillment-service]
status: complete
last_updated: 2026-06-03
git_reference: 67c396dc9cf012c10487eb4cf39e771646ae049b
---

# Order Update Scenarios — Functional Business Catalog

Exhaustive, business-perspective catalog of every way a Shopify order can change and how that change flows through StorePep. Written for product, QA, and support — describes **what happens and why it matters**, not line-level code.

**Three** systems own order updates (this was "two" before tracking was analysed):

- **order-updates** microservice — the *change detector and router*. Receives Shopify `orders/*` + `fulfillment_orders/*` + `fulfillment_holds/*` webhooks, versions every order, computes a field-level diff against the last-applied version, ranks the change by business priority, and notifies MCSL only when something material changed.
- **MCSL / storepep-react** — the *system of action*. Imports orders, runs automation, generates labels, fulfils, and **writes fulfilment + tracking back to Shopify** — which itself produces new Shopify webhooks (the echo, see [§4](#4-mcsl-app-initiated-scenarios-write-back-to-shopify)).
- **shopify-tracking-app** (separate repo `xadapter-cyd/shopify-tracking-app`) — the *delivery-tracking bridge*. Subscribes to **`fulfillments/create` + `fulfillments/update`** (which order-updates does **not** handle), reads tracking numbers, polls carriers, **writes delivery status back to Shopify** via `fulfillmentEventCreate` and rewrites `tracking_info` with a custom URL, and emails customers on status change. See [§7](#7-tracking--delivery-update-scenarios).

The central business problem this design solves: **Shopify is noisy.** A single merchant click can fire several `orders/updated` webhooks; the app's own write-back fires more. Without versioning, diffing, priority ranking, and locking, MCSL would re-process orders endlessly, relabel shipped orders, and hammer carrier APIs. Every scenario below is ultimately about *acting on real changes once, and ignoring the noise*.

---

## ▶ QA Scenarios (downloadable)

Every scenario below is expressed as a **Given/When/Then QA case** in a downloadable CSV — import into a test-management tool or paste into the regression sheet:

**📥 [order-update-qa-scenarios.csv](order-update-qa-scenarios.csv)** — 97 QA cases incl. **Partial Fulfilment (PF1–PF12)**, **Tracking (T1–T8)** and the **Returns/Refunds gap (S29/S30)** (`ID, Section, Scenario, Given, When, Then, DiffPriority, Trigger, Verification, RegressionCoverage, RegressionRef, Caveat`)

> [!success] Resolved this session (were "verify before trust", now code-checked)
> - **M6 / M8** write-back — **Verified in code** (`ordersSyncEngine.syncCurrentStoreOrders` loops → `syncStore` per order; `fulfillmentOrderUpdatingListener`). Bulk = N write-backs.
> - **Echo loop** — **Verified & corrected**: the MCSL fulfilment echo is *newer* and changes a monitored field, so order-updates does **not** suppress it (the `updated_at` gate only stops not-newer/duplicate webhooks); the tracking-URL echo *is* suppressed via the field-filter. See the echo table in [§4](#4-mcsl-app-initiated-scenarios-write-back-to-shopify).
> - **U1** — **Corrected**: `ordersSyncEngine` has **no pre-check** before `syncStore` (verified); whether real double-fulfilment occurs depends on untraced upstream order-selection. Still a Tier-1 gap.
> - **COD** — **Verified & enriched**: two derivation mechanisms + the "Please Reconfirm" ambiguity (S28).

> [!warning] Two columns carry the trust + coverage signal — read before treating any row as fact
> **`Verification`** — how trustworthy the expected outcome is:
> - **Verified** / **Verified (diff/topics/regression/absence)** — read directly from source this session (`order-diff-definition.json`, `webhooks.js`, regression sheet).
> - **Inferred** — from the subagent exploration, **not line-verified**. Treat as a draft hypothesis.
>
> **`RegressionCoverage`** — checked against the regression sheets `Order_Update`, `Orders Grid`, `Batch Flow`:
> - **Covered** / **Partial** — a regression row exists (see `RegressionRef`).
> - **Not-covered (testable)** — user-facing behavior with no regression row → a real gap to write.
> - **N/A-infra** — internal idempotency/lock/retry behavior a merchant regression plan would never contain → verify by integration test, not regression.

### Gap analysis (answering "what's in the CSV but not in regression")

**Tier 1 — testable gaps (no regression row, but should have one):**
- **S5 / P5 / E2** — archive **age-cutoff** (`ignoreOrdersClosedBeforeDays`): no regression coverage of the drop-vs-process boundary.
- **S7** — authorization **expires** uncaptured.
- **S8** — **deferred / pay-later** order paid on due date.
- **S10 / S11** — **refund** (full/partial) after order — absent from the `Order_Update` sheet entirely.
- **S15** — merchant marks **In progress** (intermediate fulfilment state).
- **S21** — **subscription** scheduled→unfulfilled.
- **U1** — **merchant-vs-operator double-fulfilment** race (highest-risk).
- **U2** — two operators contending on the same order.
- **BF2** — **echo storm**: N write-backs from a bulk fulfil → N inbound echoes all suppressed.

**Tier 2 — N/A to regression by nature (infra; cover with integration tests):** P6, P7, C2–C6, E1, E3–E6, L3, L5, L6 — echo suppression, `order_lock` idempotency, `AppliedVersionNotFound`, SQS redelivery, oversized-payload handling.

> [!note] Separate finding — the `Order_Update` regression sheet is ~96% manual
> Of ~30 inbound order-update scenarios, **only row 7.0 (custom physical product added, touchless) is automated** (`AUTO=YES`). Address, product-add, quantity, tags, cancel, hold/release, external-fulfil, payment-method, and 20+-order bulk update are all **manual-only**. This is an automation gap distinct from coverage — the scenarios exist but aren't automated.

### Reverse gaps — scenarios regression has that the catalog had **missed** (now added)

- **S26 Order note sync** — `note` is **not** a field in `order-diff-definition.json` (confirmed by grep); order-note updates flow through a **separate `order.note.updating.listener`**, not the diff engine. The catalog, built on the diff engine, would have missed note updates entirely.
- **S27 Mark as Unfulfilled in Shopify** → red alert icon in MCSL → on confirm the order returns to **Processing**. The catalog had no "un-fulfil → reprocess" transition.

---

## 1. The Change-Priority Model

order-updates monitors a fixed set of order fields. Each detected change carries a **business priority** (higher = more urgent / more disruptive downstream). When several fields change at once, the highest priority drives the notification.

| Priority | Field | Business meaning of the change |
|---|---|---|
| 50 | `total_outstanding` | Money owed changed — billing/COD impact |
| 49 | `tags` | Tags changed — often drive automation rules (carrier choice, routing) |
| 45 | `financial_status` | Payment state changed (paid, refunded, voided…) |
| 45 | `fulfillment_status` | Fulfilment state changed (partial, fulfilled…) |
| 42 | `fulfillment_status` → null | **All fulfilments cancelled** — special case, fires even with no timestamp change |
| 40 | `line_items` | Order contents edited (qty, add/remove product) |
| 40 | `payment_gateway_names` | Payment method changed (COD detection) |
| 30 | `shipping_address` | Delivery address corrected |
| 1 | (forced) | Fulfilment hold placed / released — bypasses diff entirely |

**Why this matters functionally:** support can reason about "what was urgent" from the priority; QA can assert that a given merchant action produces the expected priority; and the app can choose to act fast on money/fulfilment changes while treating an address tweak as low-stakes.

---

## 2. Shopify-Initiated Scenarios

Changes that *originate with the merchant or customer inside Shopify*. Each entry: merchant action → Shopify webhook → field/priority → MCSL effect.

### Order Creation & Lifecycle

| # | Business scenario | Webhook | Field / Priority | MCSL effect |
|---|---|---|---|---|
| S1 | Customer places a new order | `orders/create` | — | Imported as `INITIAL`; payment type derived (COD vs pre-paid) |
| S2 | Merchant edits a draft/open order | `orders/updated` | varies | Diff computed against last-applied version |
| S3 | Merchant cancels the order | `orders/cancelled` | dedicated topic | Status → `CANCELLED` |
| S4 | Merchant voids an unpaid order | `orders/updated` or `orders/cancelled` | `financial_status` → voided / 45 | Cancel/void recorded |
| S5 | Order archived (manual or auto after fulfilment) | `orders/updated` | `closed_at` set | **Dropped if `closed_at` older than `ignoreOrdersClosedBeforeDays`**; else processed |

### Payment / Financial

| # | Business scenario | Field change | Priority | MCSL effect |
|---|---|---|---|---|
| S6 | Merchant captures an authorized payment | `financial_status`: authorized → paid | 45 | Order becomes eligible for paid-only automation |
| S7 | Authorization expires uncaptured | authorized → expired | 45 | Label automation blocked if it requires paid |
| S8 | Deferred ("pay later") order paid on due date | due → paid, `total_outstanding` → 0 | 45 + 50 | Two diffs; notification uses max (50) |
| S9 | Merchant captures partial payment | → partially_paid, outstanding ↓ | 45 + 50 | Flagged partial; `PARTIAL_COD` if COD gateway |
| S10 | Full refund issued | → refunded | 45 | Maps to `PRE_PAID` (was-paid) |
| S11 | Partial refund issued | → partially_refunded, outstanding ↑ | 45 + 50 | Outstanding + status synced |
| S12 | Payment method switched **to** COD | `payment_gateway_names` incl. "Cash on Delivery (COD)" | 40 | Payment type → `COD` (don't charge upfront) |
| S13 | Payment method switched **away from** COD | gateway no longer COD | 40 | Payment type → `PRE_PAID` |
| S14 | Tip / post-order surcharge / discount changes balance | `total_outstanding` | 50 | Highest-priority notification |

> [!note] COD payment-type derivation (verified in `shopifyToStorepepOrderMapper.getPaymentGatewayViaStatus`)
> Payment type is derived by **two mechanisms**, selected by the `isCodCheckEnabled(accountUUID)` flag:
> 1. **Status + outstanding** (flag on): `pending` & `outstanding > 0` → **COD**; `partially_paid` & `outstanding < total` → **PARTIAL_COD**; `paid`/prepaid & `outstanding === 0` → **PRE_PAID**.
> 2. **Legacy gateway-name** (flag off / fallback): matches `payment_gateway_names` against `config.shopifyPossibleCodValues` (e.g. "Cash on Delivery (COD)").
>
> **S28 — COD ambiguity:** if a COD gateway name matches but the status isn't `pending`, the mapper returns `{ success: false, gateway: COD, message: 'Order Marked as COD. Please Reconfirm.' }` — a reconfirm-required state worth its own QA case. Regression covers COD/Partial-COD/Prepaid transitions (Order_Update 30–32).

### Fulfilment

| # | Business scenario | Field change | Priority | MCSL effect |
|---|---|---|---|---|
| S15 | Merchant starts fulfilment ("In progress") | `fulfillment_status` intermediate | 45 | Status update notification |
| S16 | Merchant fulfils **all** items in Shopify (bypassing MCSL) | → fulfilled | 45 | Status → `EXTERNALLY_FULFILED` *(gated by `orderStatusUpdateEnabledFor`)* |
| S17 | Merchant fulfils **some** items | → partial | 45 | → `PARTIALLY_EXTERNALLY_FULFILED` *(gated by `partial.fulfilment.enabled`)* |
| S18 | Merchant cancels all fulfilments | all `fulfillments[*].status` = cancelled; `fulfillment_status` → null | **42 (special)** | Fires even with unchanged `updated_at`; `OrderFulfillmentCancelled` |
| S19 | Fulfilment placed on hold (manual, or post-purchase upsell) | `fulfillment_orders/placed_on_hold` + `fulfillment_holds/added` | 1 (forced) | Order held from shipping; full order re-fetched from Fulfilment API |
| S20 | Fulfilment hold released | `fulfillment_orders/hold_released` + `fulfillment_holds/released` | 1 (forced) | Order released for shipping |
| S21 | Prepaid subscription reaches fulfilment date | `orders/updated` (scheduled → unfulfilled) | 45 | Becomes active, eligible for automation |

### Contents, Address, Tags, Returns

| # | Business scenario | Field change | Priority | MCSL effect |
|---|---|---|---|---|
| S22 | Merchant edits line items (qty / add / remove) | `line_items` (excl. its own fulfillment_status) | 40 | Re-sync contents; may re-trigger packaging/rate calc |
| S23 | Shipping address corrected before shipment | `shipping_address` | 30 | Address updated; relabel may be needed if label exists |
| S24 | Tags added/removed (manual or by an automation app) | `tags` | 49 | Tags drive StorePep automation rules |
| S25 | Customer requests / progresses a return | `orders/updated` (return status) | varies | Return flow may trigger; see [order-returns.md](order-returns.md) |
| S26 | Merchant adds/edits the **order note** | `orders/updated` + `order.note.updating.listener` | — | Note syncs via a **separate listener, not the diff engine** (`note` is not a diff field) |
| S27 | Merchant marks the order **Unfulfilled** in Shopify | `orders/updated` | 45 | Red alert icon in MCSL; on confirm the order returns to `PROCESSING` |

---

## 3. Orders Updated **After** Fulfilment

The riskiest category: a shipped/fulfilled order changing again. Business goal — **never relabel or re-ship an already-completed order, but still capture legitimate post-ship changes** (refunds, returns, cancellations).

| # | Post-fulfilment scenario | Trigger | Expected behaviour |
|---|---|---|---|
| P1 | Refund issued after shipment | S10/S11 | Financial status synced; **no relabel, no re-fulfil** |
| P2 | Fulfilment cancelled after it was created | S18 | `OrderFulfillmentCancelled`; order may return to a shippable state per business rules |
| P3 | Address edited after label generated | S23 | Address updated on record; existing label is **not** auto-voided — flagged for manual relabel decision |
| P4 | Line items edited after partial fulfilment | S22 | Only unfulfilled items affected; `fulfillment_status` within line items excluded from diff to avoid double-counting with S16/S17 |
| P5 | Order archived after fulfilment | S5 | Within window: processed; outside window: silently ignored (prevents reprocessing ancient orders) |
| P6 | Tracking/fulfilment written back by MCSL re-arrives as a webhook | echo of MCSL action | **Not** suppressed by `updated_at` (echo is newer) — see the corrected echo table in [§4](#4-mcsl-app-initiated-scenarios-write-back-to-shopify) |
| P7 | Duplicate `orders/updated` for an already-fulfilled state | Shopify noise | `updated_at` not newer → skipped; or diff finds no material change → `OrderDiffNotDetected` |

**Key guard (verified in `shouldApplyUpdate`):** diffing is against the **last applied version**, and only fires when the latest version's `updated_at` is **strictly newer** — *except* the all-fulfilments-cancelled case (S18/P2), which is allowed through even on an equal timestamp. This gate stops *duplicate/stale* webhooks, **not** the fulfilment echo (which is genuinely newer).

---

## 4. MCSL-App-Initiated Scenarios (Write-Back to Shopify)

Changes that *originate inside StorePep*, then propagate **outward to Shopify**. These are what make the system bidirectional — and what create the echo loop.

| # | App action | Internal effect | Written back to Shopify? |
|---|---|---|---|
| M1 | Order imported / synced from store | Created as `INITIAL` | No (inbound only) |
| M2 | Automation rule packages an order | `INITIAL` → `PROCESSING` | No |
| M3 | Shipping label generated | `PROCESSING` → `LABEL_CREATED` | No |
| M4 | Label generation fails | `PROCESSING` → `LABEL_FAILURE` (retryable → `PROCESSING`) | No |
| M5 | Shipment confirmed | `LABEL_CREATED` → `SHIPPED` | No |
| M6 | Order marked fulfilled (fulfilment request succeeds) | `SHIPPED` → `FULFILLED`; `OrderFulfillmentStatusUpdated`; shipment-batch fulfilment status set | **Yes — fulfilment + tracking pushed to Shopify** |
| M7 | Fulfilment request fails | `isFulfilled:false` recorded | No |
| M8 | Partial fulfilment from MCSL | batch order fulfilment status `unfulfilled`/`fulfilled` per item | **Yes (partial)** |
| M9 | Return label generated | return flow | Depends on store return config |
| M10 | Order marked not-to-ship | → `NOT_TO_SHIP` | No |

**The echo — corrected after reading the code (`OrderUpdateCalculatingService.shouldApplyUpdate`):** there are **two distinct echo paths with two different suppression mechanisms**, and the MCSL fulfilment echo is *not* suppressed the way earlier drafts claimed.

| Echo source | Webhook fired | Newer `updated_at`? | Monitored field changed? | Suppressed by order-updates? |
|---|---|---|---|---|
| **MCSL fulfilment write-back** (M6/M8) | `orders/updated` (fulfilled) | **Yes** (Shopify bumps it) | Yes (`fulfillment_status`) | **No** — passes the `updated_at` gate *and* diffs to priority 45 → real `OrderUpdateDetected`. The loop is broken on the **MCSL side** (receiving "fulfilled" for an already-`FULFILLED` order is a no-op). *MCSL-side idempotency not verified this session.* |
| **Tracking-app `tracking_info` rewrite** | `fulfillments/update` + `orders/updated` | Yes | **No** (`tracking_info`/`tracking_number` is not a diff field) | **Yes** — `compare()` returns empty → `OrderDiffNotDetected` (the E6 path). |
| **Duplicate / stale / out-of-order webhook** | `orders/updated` | **No** | n/a | **Yes** — `shouldApplyUpdate` returns false: "current version is not newer than last applied" (the P7/C1 path). |

So the **`updated_at` gate suppresses *not-newer* (duplicate/stale) webhooks**, not the fulfilment echo. The fulfilment echo is handled by MCSL-side idempotency; the tracking echo is handled by the field-filter. *Verified:* `shouldApplyUpdate` (newer-OR fulfilment-cancellation-at-equal-timestamp) and `OrderComparator.compare` (monitored-fields-only) in `order-updates`.

> The single-order write-back (M6/M8) is **confirmed by code + regression**: `ordersSyncEngine.syncCurrentStoreOrders` loops orders → `currentStoreAdapter.syncStore(...)` pushes tracking+fulfilment per order; `fulfillmentOrderUpdatingListener` emits `OrderFulfillmentStatusUpdated`. Orders Grid 17.0 asserts "Shopify/Woocommerce order [marked fulfilled]".
>
> **U1 correction (verified):** `ordersSyncEngine` has **no pre-check** against Shopify's current fulfilment state before calling `syncStore`. On the write-back path itself there is no guard; a failed sync is recorded as `isStoreSyncFailed: true`. Whether a genuine double-fulfilment is possible depends on the **upstream order-selection** logic (which orders are eligible to be fulfilled) — *not traced this session*. Treat U1 as an open risk, not a mitigated one.

### Bulk Fulfilment (M6/M8 at scale)

Bulk fulfilment is its own risk surface — one operator action fans out to N orders and N write-backs. Well covered in the `Orders Grid` and `Batch Flow` regression sheets.

| # | Scenario | Origin | Write-back | Regression |
|---|---|---|---|---|
| BF1 | Bulk **Mark As Fulfilled** from grid | MCSL grid (N orders) | N orders fulfilled, **single manifest**, each store order marked fulfilled | Orders Grid 45.0 / 61.0 |
| BF2 | **Echo storm** — N write-backs → N inbound `orders/updated` echoes | echo of BF1 | all echoes suppressed by `updated_at` comparison; none re-process | ❌ **Tier-1 gap** |
| BF3 | Batch label-gen + fulfil across **multiple batches** | MCSL batch | labels + fulfilment across batches | Batch Flow 11 / 14 |
| BF4 | **Parallel batch** processing | MCSL (concurrent) | batches complete in parallel without cross-contamination | Batch Flow (Parallel batch running) |
| BF5 | Bulk fulfil with **partial failures** | MCSL batch | successes fulfil, failures retryable without blocking the batch | Batch Flow (Retry batch) / Orders Grid (Fulfilment Failure) |
| BF6 | Merchant **bulk-marks fulfilled in Shopify** (inbound) | Shopify (N orders) | each → `EXTERNALLY_FULFILED` | Order_Update 20.0 |
| BF7 | **20+ orders** updated in a burst right after import | Shopify burst | all reflect latest after the sync window | Order_Update 23.0 / 24.0 |

---

## 5. Concurrency, Load & Multi-User Scenarios

The hard cases. These are where data integrity is won or lost.

### Concurrency / Race conditions

| # | Scenario | Mechanism | Functional outcome |
|---|---|---|---|
| C1 | Two `orders/updated` webhooks for the same order arrive nearly simultaneously | Each saved as its own **version**; diff always compares **latest vs last-applied** | Intermediate versions are not individually actioned — only the newest state matters; no duplicate processing |
| C2 | MCSL's own write-back echoes back as a webhook while processing continues (M6 → S16) | `updated_at` not-newer comparison | Echo suppressed; no infinite loop |
| C3 | A notification is already in flight for an order when another change lands | **`order_lock`** row (insert-on-conflict) | Second notification silently skipped; relies on next diff/redelivery to catch up |
| C4 | Same lock attempted twice (duplicate event) | `ON CONFLICT DO NOTHING` (idempotent insert) | No error, no double-notify |
| C5 | A version's diff is requested twice | "pending update already exists" guard | No duplicate `order_updates` rows created |
| C6 | Recalculation needed after stale diff | `OrderUpdateRecalculationRequested` deletes existing update rows, recomputes | Clean recompute, no orphan diffs |

### Bulk / Load

| # | Scenario | Mechanism | Functional outcome |
|---|---|---|---|
| L1 | Initial bulk order import for a new store | **`shop_lock`** acquired (`ShopLockedForImport`) | All per-order notifications **deferred** during import — MCSL isn't flooded |
| L2 | `orders/updated` webhooks arrive *during* a bulk import | versions saved but diffs held | After `OrderImportFinished`, diffs **recalculated for every version created during the lock window** — nothing lost |
| L3 | Very large order payload exceeds webhook size limits | Heimdal **LINK** payload — body stored in S3, fetched on demand | Large orders handled without truncation |
| L4 | High webhook throughput | 5 independent SQS-polling workers (webhook / version / update / lock / heimdal), batch polling, 10-msg batches | Horizontal, queue-buffered processing; spikes absorbed by SQS |
| L5 | Downstream MCSL API momentarily down | `AxiosError` caught, `webhook_in_progress` reverted, **no manual retry** | SQS redelivers after visibility timeout (~10s) — eventual consistency |
| L6 | Fulfilment API unavailable during a hold webhook (S19/S20) | fetch fails | SQS redelivery; hold applied once API recovers |

### Multi-user / multi-actor

| # | Scenario | Functional outcome |
|---|---|---|
| U1 | Merchant fulfils in Shopify **while** a StorePep operator generates a label for the same order | Whichever fulfilment lands first wins; the second arrives as a webhook and is reconciled via diff. Risk: **double fulfilment** if MCSL ships an order the merchant already fulfilled externally — mitigated by `EXTERNALLY_FULFILED` status (S16) being set before MCSL acts |
| U2 | Two StorePep operators act on the same order in the grid | Internal MCSL order state is the arbiter; last write wins on internal status. Bulk actions and single actions on the same order can contend — see [order-bulk-actions.md](order-bulk-actions.md) |
| U3 | Merchant edits address (S23) while operator is mid-label | Address diff (priority 30) notifies MCSL; if label already cut, flagged for relabel (P3) rather than silently shipping to the old address |
| U4 | An automation app re-tags orders in bulk (S24) during a busy period | Each tag change is a priority-49 diff; high volume handled by the queue model (L4); tag-driven automation rules re-evaluate |
| U5 | Customer-initiated return (S25) coincides with operator fulfilment | Return status and fulfilment status are independent fields; both sync, return flow proceeds per store config |

---

## 6. Error & Edge Scenarios

| # | Scenario | Behaviour |
|---|---|---|
| E1 | Duplicate order version received | Version UUID already known → silently skipped (idempotent) |
| E2 | Order closed before `ignoreOrdersClosedBeforeDays` | Webhook ignored entirely (no processing) |
| E3 | Last-applied version missing during diff (`AppliedVersionNotFound`) | Logged and swallowed; diff aborts, no update rows written |
| E4 | MCSL apply/notify call fails | webhook_in_progress reverted; SQS redelivery (no in-process retry) |
| E5 | Order-lock conflict | Notification skipped; caught up by next diff cycle |
| E6 | No material change in a noisy webhook | `OrderDiffNotDetected` — explicit no-op event for observability |

---

## 7. Tracking & Delivery Update Scenarios

A **separate** order-update family handled by the **shopify-tracking-app**, not the order-updates microservice. It subscribes to `fulfillments/create` + `fulfillments/update` (fulfilment-level, distinct from `orders/updated`), reads the tracking number, polls carriers, and **writes delivery status back to Shopify**.

**Tracking status state machine** (app → Shopify `FulfillmentEvent`):
```
INITIAL(CONFIRMED) → IN_TRANSIT → OUT_FOR_DELIVERY → DELIVERED
                          ├─► Delivery Exception → ATTEMPTED_DELIVERY
                          ├─► Damaged Exception  → FAILURE
                          └─► Return Exception    → FAILURE
```

| # | Scenario | Trigger | Effect | Write-back to Shopify |
|---|---|---|---|---|
| T1 | Fulfilment created with a tracking number | `fulfillments/create` | tracking number + carrier extracted; order registered for tracking (if carrier supported, status `success`) | Optional: rewrite `tracking_info` with custom URL |
| T2 | Fulfilment updated (tracking number changes / re-evaluated) | `fulfillments/update` | tracking info re-read and synced to tracking service | Optional `tracking_info` rewrite |
| T3 | Carrier reports **In Transit** | carrier poll | status → IN_TRANSIT | `fulfillmentEventCreate` (IN_TRANSIT) |
| T4 | Carrier reports **Out for Delivery** | carrier poll | status → OUT_FOR_DELIVERY | `fulfillmentEventCreate` (OUT_FOR_DELIVERY) |
| T5 | Carrier reports **Delivered** | carrier poll | status → DELIVERED | `fulfillmentEventCreate` (DELIVERED) + customer email |
| T6 | Delivery **exception** (failed attempt / damaged / return) | carrier poll | status → Exception | `fulfillmentEventCreate` (ATTEMPTED_DELIVERY / FAILURE) + email |
| T7 | Custom tracking URL rewrite | T1/T2 (if `enableCustomTrackingUrl`) | `tracking_info.url` → `{shop}/apps/phtracking?...` | **Yes** — and this is the tracking-app echo source (suppressed as `OrderDiffNotDetected`, see §4) |
| T8 | Customer delivery/shipment email notification | any status change | Handlebars email to customer shipping address | No (email only) |

> [!warning] Tracking is a coverage blind spot in the order-update catalog
> The order-updates diff engine has **no tracking field** — delivery status never flows through it. Tracking lives entirely in the separate app and writes back via `fulfillmentEventCreate`. Any QA of "order updates" that only exercises the order-updates service **misses the entire T-series**. These rows are **Inferred** (from a subagent read of the tracking app), not line-verified.

## 8. Returns & Refunds Coverage (genuine gap)

**Shopify Return Management is NOT integrated.** Three separate, non-overlapping layers — verified by grep across all three repos:

| Layer | What exists | Verified |
|---|---|---|
| **Shopify Return Management** — `returns/request`→`approve`→`cancel`→`close`/`reopen`→`update`, `reverse_deliveries/*`, `reverse_fulfillment_orders/*`, Return GraphQL (`returnCreate`, `ReturnInput`) | **Nothing.** No webhook subscription, no GraphQL, `order.returns` never parsed in any repo. | grep: zero hits for any Return-Management topic/API |
| **Refund handling** | One **legacy, flag-gated-OFF** path: `shopifyToStorepepOrderMapper.js:285` reads `order.refunds` *only* when both `partial.fulfilment.enabled` **and** `orderStatusUpdateEnabled` are off — sums refunded qty per variant and **subtracts it from shippable line items** (`:299-300`). Pure quantity correction, not a return flow. | code-read |
| **StorePep return labels** | Operator-initiated reverse **shipping-label** generation via carrier RMA APIs (DHL/FedEx/UPS/EasyPost `ReturnRequest`; `carriers.js` `ReturnLabel`/`rma`). Separate data model: `returnBatchStatus`, `returnCarrierIdSelected`, `returnLabel[]`, `returnPackingSummary[]`. See [order-returns.md](order-returns.md). | code-read + [order-returns.md](order-returns.md) |

- **shopify-tracking-app**: returns appear only as `EXCEPTION_3` ("Return Exception") → `FAILURE`. No RMA, no reverse-logistics tracking.
- **Consequence**: a customer return *in Shopify* never reaches StorePep as a return. It surfaces only indirectly — as a refund (`financial_status`, S10/S11) or unfulfil (S27), where the legacy path may reduce line-item quantities (S29). StorePep "returns" mean *printing a reverse label*, operator-triggered, with **no link to Shopify's return objects**. If Shopify-driven return workflows matter, this is the gap to close.

## 9. Partial Fulfilment (dedicated dimension)

Partial fulfilment is not a single scenario — it is an axis crossing source, flag-state, item-recalculation, and sequencing. **Two code paths** handle it: the diff-driven `internalOrderWebhook` route (`deriveStorePepStatus`) and the `externalFulfilmentEventProcessingListener` (`handlePartialFulfilment`).

**Mechanics (verified):** on a partial event, `OrderProcessingService.process()` **strips already-fulfilled items and recomputes line totals, discounts, tax lines and `money_set`** for the *remaining* items, re-maps via the store adapter, sets `PARTIALLY_EXTERNALLY_FULFILED`, and re-imports. `cancelled_at` takes precedence over partial. When `partial.fulfilment.enabled` is **off**, status is forced to `INITIAL`.

| # | Partial scenario | Effect | Verified |
|---|---|---|---|
| PF1 | Merchant partially fulfils in Shopify (flag **ON**) | remaining items recalculated (totals/tax/money) → re-imported as `PARTIALLY_EXTERNALLY_FULFILED` | `externalFulfilmentEventProcessingListener.handlePartialFulfilment` + `OrderProcessingService` |
| PF2 | Merchant partially fulfils (flag **OFF**) | status **forced to `INITIAL`** — MCSL sees it as fully unfulfilled and may ship already-fulfilled items | `deriveStorePepStatus` — **RISK** |
| PF3 | Operator partially fulfils from MCSL (edit packages, fulfil subset) | per-item write-back to Shopify; `isPartiallyAvailable` set | M8 + ordersSyncEngine |
| PF4 | Hold some items in Shopify, fulfil remaining in MCSL | remaining items fulfilled; batch creation handles held items | Batch Flow r32-33 (regression) |
| PF5 | Multi-vendor (WCFM) sub-orders | `isPartiallyAvailable = completedSubOrders ≠ totalSubOrders`; full only when all sub-orders `SHIPPED` | ordersSyncEngine:113-126 |
| PF6 | Partial → then fulfil the remaining | transitions toward `FULFILLED` / `EXTERNALLY_FULFILED` | end-to-end regression row28 |
| PF7 | Partial → then remaining items cancelled | remaining cancelled; order resolves | **Inferred** — not traced |
| PF8 | Partial externally → then line items edited | recalculation re-runs on next event for remaining items | P4 + OrderProcessingService |
| PF9 | Repeated partial webhooks (idempotency) | each event re-runs `process()` recomputing remaining; should converge, not double-strip | **Inferred** — not traced |
| PF10 | Totals/tax/money correctness after partial | `calculateTotals` + `updateMoneySet` recompute price/discount/tax/`money_set` for remaining items only | `OrderProcessingService` (verified) |
| PF11 | Partial fulfilment + COD outstanding | collectible/outstanding should reflect remaining value (intersects S9/S14) | **Inferred** — not traced |
| PF12 | `cancelled_at` precedence over partial | `CANCELLED` wins even if `fulfillment_status = partial` | `deriveStorePepStatus` (verified) |

> [!warning] Two open partial-fulfilment risks worth tracing
> - **PF2 (flag OFF → INITIAL):** an externally partially-fulfilled order is treated as fully unfulfilled. Confirm whether downstream label/fulfil guards prevent re-shipping the already-fulfilled items.
> - **Double-path:** both `internalOrderWebhook` and `externalFulfilmentEventProcessingListener` react to partial fulfilment. Confirm they don't both re-import/recompute the same event.

## State Machine (MCSL internal)

```
INITIAL ─auto─► PROCESSING ─label gen─► LABEL_CREATED ─ship─► SHIPPED ─sync/writeback─► FULFILLED
                   │                          │
                   │                          └─► LABEL_FAILURE ─retry─► PROCESSING
                   ├─► NOT_TO_SHIP
                   └─► CANCELLED

Any state ─orders/cancelled──────────────► CANCELLED
Any state ─orders/updated (fulfilled)────► EXTERNALLY_FULFILED            (gated: orderStatusUpdateEnabledFor)
Any state ─orders/updated (partial)──────► PARTIALLY_EXTERNALLY_FULFILED  (gated: partial.fulfilment.enabled)
```

---

## Feature Flags Governing Behaviour

| Flag | Controls |
|---|---|
| `orderStatusUpdateEnabledFor(accountUUID)` | Whether external fulfilment (S16) updates internal status |
| `partial.fulfilment.enabled` | Whether partial external fulfilment (S17) is tracked |
| `ignoreOrdersClosedBeforeDays` | Age cutoff for ignoring closed/archived orders (S5/E2) |
| `skipOrderWebhookPostponeEnabled(accountUUID)` | Skip the webhook-processing delay |
| `cancelFulfilmentEnabledFor(accountUUID)` | Enable fulfilment cancellation handling (S18) |

---

## Related Pages

- [Order Lifecycle](order-lifecycle.md) — internal status model
- [Order Bulk Actions](order-bulk-actions.md) — multi-order operations and contention
- [Order Address Management](order-address-management.md) — address change handling
- [Order Returns](order-returns.md) — return flows
- [Features List](../../features.md)

## Sources

- **order-updates** microservice — diff engine, versioning, locks, SQS/SNS workers (`raw/order-updates`)
- **storepep-react** — webhook intake (`server/src/routes/webhooks.js`), internal update endpoints (`server/src/routes/internalOrderWebhook.js`), fulfilment write-back (`server/src/shared/ordersSyncEngine.js`, `modules/fulfillment-request/listeners/fulfillmentOrderUpdatingListener.js`), status constants (`server/src/storePepConstants.js`)
- **Shopify order status docs** — https://help.shopify.com/en/manual/fulfillment/managing-orders/order-status
