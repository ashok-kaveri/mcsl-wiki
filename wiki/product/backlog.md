---
title: Product Backlog
category: product
sources: [zendesk, zendesk-zi-extraction-2026-04-13, regression-scenarios, storepep-react, mcsl-test-automation]
status: complete
last_updated: 2026-04-13
git_reference: 5058f2c24d90fbaf9741d9279b8bdc8428a4af5e
---

# Product Backlog

## Scoring Framework

| Dimension | Scale | Description |
|-----------|-------|-------------|
| Impact | 1-5 | Customer pain (ticket volume, severity) + revenue potential |
| Effort | 1-5 | Code complexity + test coverage needed (1=easy, 5=hard) |
| Confidence | 1-5 | How well we understand the problem (data quality) |
| Priority Score | (Impact x Confidence) / Effort | Higher = do first |

**Status values**: proposed -> accepted -> in-progress -> shipped -> closed

> **Last synced**: ZI extraction 2026-04-13 -- 93 issues from 66 Zendesk tickets clustered into 14 backlog items.

---

## Active Backlog

### Shopify Multi Carrier Shipping Label App

| # | Item | Issues | Tickets | Impact | Effort | Confidence | Score | Key Sources | Feature Story | Status |
|---|------|--------|---------|--------|--------|------------|-------|-------------|---------------|--------|
| 1 | Label generation & packing reliability | 17 | 12 | 5 | 4 | 5 | **6.3** | ZI-016, ZI-024, ZI-025, ZI-027, ZI-029, ZI-030, ZI-032, ZI-033, ZI-035, ZI-041, ZI-043, ZI-052, ZI-058, ZI-067, ZI-071, ZI-073, ZI-081 -- [#377526](../../raw/zendesk/shopify/377526.json), [#382393](../../raw/zendesk/shopify/382393.json), [#370219](../../raw/zendesk/shopify/370219.json), [#372492](../../raw/zendesk/shopify/372492.json), [#373991](../../raw/zendesk/shopify/373991.json), [#374851](../../raw/zendesk/shopify/374851.json), [#380339](../../raw/zendesk/shopify/380339.json), [#381380](../../raw/zendesk/shopify/381380.json), [#382009](../../raw/zendesk/shopify/382009.json), [#379042](../../raw/zendesk/shopify/379042.json), [#361776](../../raw/zendesk/shopify/361776.json), [#382987](../../raw/zendesk/shopify/382987.json) | -- | proposed |
| 2 | Onboarding & setup flow | 11 | 9 | 4 | 3 | 5 | **6.7** | ZI-010, ZI-050, ZI-066, ZI-068, ZI-077, ZI-078, ZI-082, ZI-086, ZI-088, ZI-091, ZI-093 -- [#338603](../../raw/zendesk/shopify/338603.json), [#378513](../../raw/zendesk/shopify/378513.json), [#381283](../../raw/zendesk/shopify/381283.json), [#381931](../../raw/zendesk/shopify/381931.json), [#382795](../../raw/zendesk/shopify/382795.json), [#382935](../../raw/zendesk/shopify/382935.json), [#382999](../../raw/zendesk/shopify/382999.json), [#383103](../../raw/zendesk/shopify/383103.json), [#383148](../../raw/zendesk/shopify/383148.json) | -- | proposed |
| 3 | Carrier configuration & service availability | 11 | 9 | 4 | 4 | 4 | **4.0** | ZI-008, ZI-018, ZI-022, ZI-023, ZI-031, ZI-037, ZI-057, ZI-061, ZI-076, ZI-083, ZI-090 -- [#306141](../../raw/zendesk/shopify/306141.json), [#366630](../../raw/zendesk/shopify/366630.json), [#369556](../../raw/zendesk/shopify/369556.json), [#373200](../../raw/zendesk/shopify/373200.json), [#377113](../../raw/zendesk/shopify/377113.json), [#379963](../../raw/zendesk/shopify/379963.json), [#380339](../../raw/zendesk/shopify/380339.json), [#382780](../../raw/zendesk/shopify/382780.json), [#383002](../../raw/zendesk/shopify/383002.json) | -- | proposed |
| 4 | International shipping & customs | 10 | 8 | 4 | 4 | 4 | **4.0** | ZI-015, ZI-019, ZI-021, ZI-034, ZI-055, ZI-060, ZI-062, ZI-063, ZI-065, ZI-075 -- [#361776](../../raw/zendesk/shopify/361776.json), [#366630](../../raw/zendesk/shopify/366630.json), [#369144](../../raw/zendesk/shopify/369144.json), [#374022](../../raw/zendesk/shopify/374022.json), [#379784](../../raw/zendesk/shopify/379784.json), [#380339](../../raw/zendesk/shopify/380339.json), [#380784](../../raw/zendesk/shopify/380784.json), [#381261](../../raw/zendesk/shopify/381261.json) | -- | proposed |
| 5 | Order management & data integrity | 10 | 7 | 4 | 3 | 4 | **5.3** | ZI-007, ZI-011, ZI-013, ZI-028, ZI-039, ZI-040, ZI-044, ZI-046, ZI-079, ZI-089 -- [#304193](../../raw/zendesk/shopify/304193.json), [#338603](../../raw/zendesk/shopify/338603.json), [#354696](../../raw/zendesk/shopify/354696.json), [#370966](../../raw/zendesk/shopify/370966.json), [#377526](../../raw/zendesk/shopify/377526.json), [#377574](../../raw/zendesk/shopify/377574.json), [#382961](../../raw/zendesk/shopify/382961.json) | -- | proposed |
| 6 | FedEx REST API migration | 9 | 7 | 5 | 5 | 5 | **5.0** | ZI-051, ZI-052, ZI-053, ZI-054, ZI-069, ZI-070, ZI-072, ZI-074, ZI-080 -- [#379042](../../raw/zendesk/shopify/379042.json), [#379098](../../raw/zendesk/shopify/379098.json), [#382009](../../raw/zendesk/shopify/382009.json), [#382188](../../raw/zendesk/shopify/382188.json), [#382425](../../raw/zendesk/shopify/382425.json), [#382982](../../raw/zendesk/shopify/382982.json), [#381380](../../raw/zendesk/shopify/381380.json) | [carrier-migration-fedex-rest](features/carrier-migration-fedex-rest.md) | proposed |
| 7 | Product & variant sync | 9 | 5 | 4 | 4 | 5 | **5.0** | ZI-001, ZI-002, ZI-003, ZI-004, ZI-005, ZI-017, ZI-049, ZI-064, ZI-092 -- [#218195](../../raw/zendesk/shopify/218195.json), [#277997](../../raw/zendesk/shopify/277997.json), [#365042](../../raw/zendesk/shopify/365042.json), [#381087](../../raw/zendesk/shopify/381087.json), [#383437](../../raw/zendesk/shopify/383437.json) | -- | proposed |
| 8 | Rate shopping reliability | 6 | 4 | 3 | 4 | 3 | **2.3** | ZI-006, ZI-020, ZI-047, ZI-084, ZI-085, ZI-087 -- [#299137](../../raw/zendesk/shopify/299137.json), [#366630](../../raw/zendesk/shopify/366630.json), [#378176](../../raw/zendesk/shopify/378176.json), [#383093](../../raw/zendesk/shopify/383093.json) | -- | proposed |
| 9 | Australia Post TLS deprecation & integration | 3 | 3 | 4 | 3 | 5 | **6.7** | ZI-058, ZI-076, ZI-083 -- [#380339](../../raw/zendesk/shopify/380339.json), [#382780](../../raw/zendesk/shopify/382780.json), [#383002](../../raw/zendesk/shopify/383002.json) | -- | proposed |
| 10 | Returns label support | 2 | 2 | 3 | 3 | 3 | **3.0** | ZI-038, ZI-056 -- [#377217](../../raw/zendesk/shopify/377217.json), [#379784](../../raw/zendesk/shopify/379784.json) | -- | proposed |
| 11 | Tracking & reporting | 2 | 2 | 2 | 3 | 3 | **2.0** | ZI-014, ZI-059 -- [#360396](../../raw/zendesk/shopify/360396.json), [#380339](../../raw/zendesk/shopify/380339.json) | -- | proposed |

**Sorted by Priority Score** (highest first): #2 Onboarding (6.7) = #9 Australia Post TLS (6.7) > #1 Label Gen (6.3) > #5 Order Mgmt (5.3) > #6 FedEx REST (5.0) = #7 Product Sync (5.0) > #3 Carrier Config (4.0) = #4 International (4.0) > #10 Returns (3.0) > #8 Rate Shopping (2.3) > #11 Tracking (2.0)

---

### Cluster Details

#### #1 Label generation & packing reliability (17 issues, 12 tickets)

The largest cluster, spanning label creation errors, packing logic, tax invoice formatting, and UI gaps.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-016 | No product-to-box mapping rules | [#361776](../../raw/zendesk/shopify/361776.json) | label-generation |
| ZI-024 | Incorrect declared value for 0-price items | [#370219](../../raw/zendesk/shopify/370219.json) | label-generation |
| ZI-025 | Shipping charges not included in declared value | [#370219](../../raw/zendesk/shopify/370219.json) | label-generation |
| ZI-027 | Multiple Tracking IDs per order (Bluedart Dart Plus) | [#370219](../../raw/zendesk/shopify/370219.json) | label-generation |
| ZI-029 | Bundle product support missing | [#372492](../../raw/zendesk/shopify/372492.json) | label-generation |
| ZI-030 | Package size auto-selection too large | [#372492](../../raw/zendesk/shopify/372492.json) | label-generation |
| ZI-032 | Tax invoice printing on multiple pages | [#373991](../../raw/zendesk/shopify/373991.json) | label-generation |
| ZI-033 | Box name on tax invoice or pick-list | [#373991](../../raw/zendesk/shopify/373991.json) | label-generation |
| ZI-035 | Decimal precision on custom packing slip prices | [#374851](../../raw/zendesk/shopify/374851.json) | label-generation |
| ZI-041 | USPS address validation causing label failures | [#377526](../../raw/zendesk/shopify/377526.json) | label-generation |
| ZI-043 | Packing slip sort helper | [#377526](../../raw/zendesk/shopify/377526.json) | label-generation |
| ZI-052 | Label stock 4x6 not available in REST | [#379042](../../raw/zendesk/shopify/379042.json) | label-generation |
| ZI-058 | eParcel bulk label generation delay (8+ sec consistently) | [#380339](../../raw/zendesk/shopify/380339.json) | label-generation |
| ZI-067 | Cleanup button missing in new UI | [#381380](../../raw/zendesk/shopify/381380.json) | label-generation |
| ZI-071 | Packing slip does not show selected package size | [#382009](../../raw/zendesk/shopify/382009.json) | label-generation |
| ZI-073 | Can product details (qty, SKU, description) be shown on shipping labels? | [#382393](../../raw/zendesk/shopify/382393.json) | label-generation |
| ZI-081 | "Amount is a required field" error on order #18501 | [#382987](../../raw/zendesk/shopify/382987.json) | label-generation |

#### #2 Onboarding & setup flow (11 issues, 9 tickets)

Onboarding calls pending, plan creation issues, Safari bugs, and carrier account creation blockers.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-010 | Subscription plans page error on Safari | [#338603](../../raw/zendesk/shopify/338603.json) | onboarding |
| ZI-050 | USPS integration blocked by plan limit | [#378513](../../raw/zendesk/shopify/378513.json) | onboarding |
| ZI-066 | Customer unable to create BlueDart account | [#381283](../../raw/zendesk/shopify/381283.json) | onboarding |
| ZI-068 | Custom plan ($150/year, 4000 shipments) not yet created | [#381931](../../raw/zendesk/shopify/381931.json) | onboarding |
| ZI-077 | Blue Dart label generation failing | [#382795](../../raw/zendesk/shopify/382795.json) | onboarding |
| ZI-078 | Onboarding call pending | [#382935](../../raw/zendesk/shopify/382935.json) | onboarding |
| ZI-082 | Onboarding call pending | [#382999](../../raw/zendesk/shopify/382999.json) | onboarding |
| ZI-086 | Demo call scheduling for 2026-04-14 | [#383103](../../raw/zendesk/shopify/383103.json) | onboarding |
| ZI-088 | Onboarding call pending | [#383148](../../raw/zendesk/shopify/383148.json) | onboarding |
| ZI-091 | Onboarding call and UPS setup | [#383273](../../raw/zendesk/shopify/383273.json) | onboarding |
| ZI-093 | Churn investigation for high-volume customer | [#383729](../../raw/zendesk/shopify/383729.json) | onboarding |

#### #3 Carrier configuration & service availability (11 issues, 9 tickets)

Missing services, incorrect service mappings, PostNord updates, DHL address format, metafield integrations, and TLS compliance.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-008 | Automatic day-of-week Saturday Delivery handling | [#306141](../../raw/zendesk/shopify/306141.json) | carrier-config |
| ZI-018 | DPD services not appearing via EasyPost | [#366630](../../raw/zendesk/shopify/366630.json) | carrier-config |
| ZI-022 | DHL Freight Sweden Return Service not available | [#369556](../../raw/zendesk/shopify/369556.json) | carrier-config |
| ZI-023 | DHL label address format | [#369556](../../raw/zendesk/shopify/369556.json) | carrier-config |
| ZI-031 | PostNord service updates for May 2026 | [#373200](../../raw/zendesk/shopify/373200.json) | carrier-config |
| ZI-037 | Pre-packed box metafield/Shopify Flow integration | [#377113](../../raw/zendesk/shopify/377113.json) | carrier-config |
| ZI-057 | RoyalMail48ParcelDailyRateService missing from app | [#379963](../../raw/zendesk/shopify/379963.json) | carrier-config |
| ZI-061 | Set Service vs Add Service rule behavior | [#380339](../../raw/zendesk/shopify/380339.json) | carrier-config |
| ZI-076 | Australia Post TLS 1.0/1.1 deprecation compliance | [#382780](../../raw/zendesk/shopify/382780.json) | carrier-config |
| ZI-083 | Australia Post TLS 1.0/1.1 deprecation compliance | [#383002](../../raw/zendesk/shopify/383002.json) | carrier-config |
| ZI-090 | Second pre-call issue | [#383243](../../raw/zendesk/shopify/383243.json) | carrier-config |

#### #4 International shipping & customs (10 issues, 8 tickets)

Customs declarations, HS codes, dangerous goods surcharges, commercial invoice fields, and shipment classification.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-015 | Declared/insured value resets after manual package edit | [#361776](../../raw/zendesk/shopify/361776.json) | international |
| ZI-019 | FedEx ETD save setting unclear | [#366630](../../raw/zendesk/shopify/366630.json) | international |
| ZI-021 | Enhancement: minimum customs value floor | [#369144](../../raw/zendesk/shopify/369144.json) | international |
| ZI-034 | Discounted price not reflected on commercial invoice | [#374022](../../raw/zendesk/shopify/374022.json) | international |
| ZI-055 | Country-specific HS codes | [#379784](../../raw/zendesk/shopify/379784.json) | international |
| ZI-060 | HS code editing at package level | [#380339](../../raw/zendesk/shopify/380339.json) | international |
| ZI-062 | Shipment type classification per order | [#380339](../../raw/zendesk/shopify/380339.json) | international |
| ZI-063 | Custom declaration statement on FedEx commercial invoice not available | [#380784](../../raw/zendesk/shopify/380784.json) | international |
| ZI-065 | DHL Export Declaration Surcharge incorrectly applied for Japan shipments | [#381261](../../raw/zendesk/shopify/381261.json) | international |
| ZI-075 | App prints incorrect Country of Manufacture on CN22 customs documents | [#382694](../../raw/zendesk/shopify/382694.json) | international |

#### #5 Order management & data integrity (10 issues, 7 tickets)

Order sync issues, draft order handling, report gaps, OCU post-purchase upsell conflicts, and filter requests.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-007 | Order notes not synced after import | [#304193](../../raw/zendesk/shopify/304193.json) | order-management |
| ZI-011 | COD payment type shown as Manual | [#338603](../../raw/zendesk/shopify/338603.json) | order-management |
| ZI-013 | Ship To Address City missing from Order Report | [#354696](../../raw/zendesk/shopify/354696.json) | order-management |
| ZI-028 | Product variant import failure | [#370966](../../raw/zendesk/shopify/370966.json) | order-management |
| ZI-039 | Externally fulfilled orders appearing in open queue | [#377526](../../raw/zendesk/shopify/377526.json) | order-management |
| ZI-040 | Draft orders ineligible for label generation | [#377526](../../raw/zendesk/shopify/377526.json) | order-management |
| ZI-044 | Order report for historical data | [#377574](../../raw/zendesk/shopify/377574.json) | order-management |
| ZI-046 | Payment status filter | [#377574](../../raw/zendesk/shopify/377574.json) | order-management |
| ZI-079 | Orders move to "Not to Ship" on refresh when OCU post-purchase upsell modifies the order | [#382961](../../raw/zendesk/shopify/382961.json) | order-management |
| ZI-089 | Order page integration issue | [#383243](../../raw/zendesk/shopify/383243.json) | order-management |

#### #6 FedEx REST API migration (9 issues, 7 tickets)

Post-migration defects: declared value limits, label stock, document upload, rate mismatches, box dimensions, PO Box rules, and registration failures.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-051 | FedEx REST declared value exceeds limit | [#379042](../../raw/zendesk/shopify/379042.json) | carrier-migration |
| ZI-053 | Auto-upload documents failing in REST | [#379042](../../raw/zendesk/shopify/379042.json) | carrier-migration |
| ZI-054 | Post-migration FedEx REST stabilization | [#379098](../../raw/zendesk/shopify/379098.json) | carrier-migration |
| ZI-069 | FedEx box dimensions not printed on labels after REST migration | [#382009](../../raw/zendesk/shopify/382009.json) | carrier-migration |
| ZI-070 | PO Box automation rule behavior after migration | [#382009](../../raw/zendesk/shopify/382009.json) | carrier-migration |
| ZI-072 | FedEx `/documents/v1/etds/multiupload` endpoint failing in production | [#382188](../../raw/zendesk/shopify/382188.json) | carrier-migration |
| ZI-074 | FedEx One Rate returned instead of negotiated rates after REST migration | [#382425](../../raw/zendesk/shopify/382425.json) | carrier-migration |
| ZI-080 | FedEx REST API registration failing | [#382982](../../raw/zendesk/shopify/382982.json) | carrier-migration |
| ZI-052 | Label stock 4x6 not available in REST | [#379042](../../raw/zendesk/shopify/379042.json) | label-generation |

Note: ZI-052 is cross-listed (label-generation defect caused by REST migration).

#### #7 Product & variant sync (9 issues, 5 tickets)

Variant SKU search, deletion sync, 250-variant import limit, 100+ variant loss, and shipping class sync.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-001 | Variant SKU search not supported | [#218195](../../raw/zendesk/shopify/218195.json) | product-management |
| ZI-002 | Product sync with Shopify | [#218195](../../raw/zendesk/shopify/218195.json) | product-management |
| ZI-003 | Variant SKU search not working | [#277997](../../raw/zendesk/shopify/277997.json) | product-management |
| ZI-004 | Deleted Shopify products persist in PluginHive | [#277997](../../raw/zendesk/shopify/277997.json) | product-management |
| ZI-005 | Product name/variant changes create duplicates | [#277997](../../raw/zendesk/shopify/277997.json) | product-management |
| ZI-017 | 250-variant import limit | [#365042](../../raw/zendesk/shopify/365042.json) | product-management |
| ZI-049 | Products with 100+ variants losing sync | [#378513](../../raw/zendesk/shopify/378513.json) | product-management |
| ZI-064 | Product variants added after initial setup not auto-imported | [#381087](../../raw/zendesk/shopify/381087.json) | product-management |
| ZI-092 | Shipping class/product category sync failure | [#383437](../../raw/zendesk/shopify/383437.json) | product-management |

#### #8 Rate shopping reliability (6 issues, 4 tickets)

Missing services, rate mismatches, item quantity limits, and DG surcharge gaps.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-006 | USPS Ground Advantage Cubic service not implemented | [#299137](../../raw/zendesk/shopify/299137.json) | rate-shopping |
| ZI-020 | Rate comparison logic questions unanswered | [#366630](../../raw/zendesk/shopify/366630.json) | rate-shopping |
| ZI-047 | UPS Dangerous Goods rates not reflecting DG surcharge | [#378176](../../raw/zendesk/shopify/378176.json) | rate-shopping |
| ZI-084 | Shipping rates not displaying at checkout | [#383093](../../raw/zendesk/shopify/383093.json) | rate-shopping |
| ZI-085 | 350-item quantity limit too low | [#383093](../../raw/zendesk/shopify/383093.json) | rate-shopping |
| ZI-087 | FedEx rate mismatch between app and FedEx portal | [#383114](../../raw/zendesk/shopify/383114.json) | rate-shopping |

#### #9 Australia Post TLS deprecation & integration (3 issues, 3 tickets)

Time-sensitive: TLS 1.0/1.1 deprecation affecting Australia Post API connectivity, plus eParcel performance.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-058 | eParcel bulk label generation delay (8+ sec consistently) | [#380339](../../raw/zendesk/shopify/380339.json) | label-generation |
| ZI-076 | Australia Post TLS 1.0/1.1 deprecation compliance | [#382780](../../raw/zendesk/shopify/382780.json) | carrier-config |
| ZI-083 | Australia Post TLS 1.0/1.1 deprecation compliance | [#383002](../../raw/zendesk/shopify/383002.json) | carrier-config |

Note: ZI-076 and ZI-083 are duplicate reports from separate customers, confirming urgency. ZI-058 is cross-listed under Label Gen (#1).

#### #10 Returns label support (2 issues, 2 tickets)

DHL "reason for return" field and PostNord return product codes.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-038 | DHL Express "reason for return" field not supported | [#377217](../../raw/zendesk/shopify/377217.json) | returns |
| ZI-056 | PostNord return label product codes | [#379784](../../raw/zendesk/shopify/379784.json) | returns |

#### #11 Tracking & reporting (2 issues, 2 tickets)

Pickup date/time in reports, Australia Post international tracking sync.

| ZI | Title | Ticket | Area |
|----|-------|--------|------|
| ZI-014 | Pickup date/time not available in order report | [#360396](../../raw/zendesk/shopify/360396.json) | tracking |
| ZI-059 | Australia Post international tracking not syncing to Shopify | [#380339](../../raw/zendesk/shopify/380339.json) | tracking |

---

## Parking Lot -- Feature Requests

Low urgency, customer-requested enhancements not yet scored.

| ZI | Ticket | Date | Request | Notes |
|----|--------|------|---------|-------|
| ZI-009 | [#306141](../../raw/zendesk/shopify/306141.json) | 2024-12-30 | Per-order Saturday Delivery toggle | Nice-to-have UX improvement |
| ZI-012 | [#348049](../../raw/zendesk/shopify/348049.json) | 2025-09-08 | End of Day manifest / SCAN sheet generation | Repeated ask, useful for carriers |
| ZI-026 | [#370219](../../raw/zendesk/shopify/370219.json) | 2026-01-22 | Payment Type Filter (Prepaid/COD) | Filtering enhancement |
| ZI-036 | [#376856](../../raw/zendesk/shopify/376856.json) | 2026-03-02 | UPS WorldEase integration | New carrier service request |
| ZI-042 | [#377526](../../raw/zendesk/shopify/377526.json) | 2026-03-04 | Address suggestion feature | Would reduce USPS validation failures (see ZI-041) |
| ZI-045 | [#377574](../../raw/zendesk/shopify/377574.json) | 2026-03-05 | BlueDart pickup token enhancement | Carrier-specific improvement |
| ZI-048 | [#378511](../../raw/zendesk/shopify/378511.json) | 2026-03-12 | UPS domestic label Reference field enhancement | Label customization request |

---

## Stale / Back-log

Long-open tickets (2023-2024 vintage). May need closure review or re-triage.

| Ticket | Open Since | ZI Issues | Summary |
|--------|-----------|-----------|---------|
| [#218195](../../raw/zendesk/shopify/218195.json) | 2023-06-08 | ZI-001, ZI-002 | Variant SKU search not supported; product sync with Shopify -- oldest open ticket |
| [#277997](../../raw/zendesk/shopify/277997.json) | 2024-07-05 | ZI-003, ZI-004, ZI-005 | Variant SKU search, deleted products persist, name changes create duplicates |
| [#299137](../../raw/zendesk/shopify/299137.json) | 2024-10-15 | ZI-006 | USPS Ground Advantage Cubic service not implemented |
| [#304193](../../raw/zendesk/shopify/304193.json) | 2024-12-16 | ZI-007 | Order notes not synced after import |
| [#306141](../../raw/zendesk/shopify/306141.json) | 2024-12-30 | ZI-008, ZI-009 | Saturday Delivery handling and per-order toggle |
| [#338603](../../raw/zendesk/shopify/338603.json) | 2025-07-07 | ZI-010, ZI-011 | Safari subscription page error; COD shown as Manual |

---

## Scoring Rationale

| # | Item | Impact rationale | Effort rationale | Confidence rationale |
|---|------|-----------------|------------------|---------------------|
| 1 | Label generation & packing | 5 -- 17 issues across 12 tickets; core revenue workflow | 4 -- touches packing engine, declared values, UI, multiple carriers | 5 -- many issues well-documented with comment threads |
| 2 | Onboarding & setup | 4 -- 11 issues across 9 tickets; direct churn risk | 3 -- mostly process/config, some Safari bug | 5 -- pattern is clear: pending calls, plan limits, account creation |
| 3 | Carrier config & services | 4 -- 11 issues across 9 tickets; blocks shipping for affected carriers | 4 -- carrier-specific work, service mapping, TLS upgrade | 4 -- multi-carrier signals confirm pattern but each carrier is different |
| 4 | International & customs | 4 -- 10 issues across 8 tickets; critical for international merchants | 4 -- customs logic, HS codes, document generation, multi-carrier | 4 -- well-documented but complex domain |
| 5 | Order management | 4 -- 10 issues across 7 tickets; data integrity affects all workflows | 3 -- mostly data mapping and filter logic | 4 -- clear patterns (draft orders, external fulfillment, OCU conflicts) |
| 6 | FedEx REST migration | 5 -- 9 issues across 7 tickets; FedEx is a top carrier, migration is mandatory | 5 -- deep API integration, multiple endpoints, rate logic | 5 -- all post-migration, root causes well understood |
| 7 | Product & variant sync | 4 -- 9 issues across 5 tickets; affects product data foundation | 4 -- sync engine, import limits, deletion propagation | 5 -- long-standing issues (2023+), very well documented |
| 8 | Rate shopping | 3 -- 6 issues across 4 tickets; checkout impact but narrower scope | 4 -- rate engine, carrier-specific service mappings | 3 -- some issues lack detail (single-ticket, no comment counts) |
| 9 | Australia Post TLS | 4 -- 3 issues across 3 tickets; time-sensitive deprecation deadline | 3 -- TLS upgrade is well-scoped | 5 -- duplicate reports confirm, carrier-mandated deadline |
| 10 | Returns | 3 -- 2 issues across 2 tickets; important but low volume | 3 -- carrier-specific field additions | 3 -- limited data, two different carriers |
| 11 | Tracking & reporting | 2 -- 2 issues across 2 tickets; non-critical reporting gaps | 3 -- report field additions, tracking sync | 3 -- limited data |

---

## Issue Coverage Summary

| Category | ZI Issues | Count |
|----------|-----------|-------|
| Active Backlog (items #1-#11) | ZI-001 through ZI-093 (excluding parking lot) | 86 |
| Parking Lot | ZI-009, ZI-012, ZI-026, ZI-036, ZI-042, ZI-045, ZI-048 | 7 |
| **Total** | | **93** |

Cross-listed issues: ZI-052 (Label Gen + FedEx REST), ZI-058 (Label Gen + Australia Post), ZI-076/ZI-083 (Carrier Config + Australia Post).

---

## Related Pages

- [Product Insights](insights.md) - Signal aggregation from all sources
- [Customer Metrics](metrics.md) - Per-feature health scores and pain index
- [Features & Test Coverage](../features.md) - Automation status
- [System Features Analysis](../system-features-analysis.md) - Code complexity and coverage gaps
- [Zendesk Issue Extraction 2026-04-13](../zendesk/2026-04-13.md) - Source ZI issue extraction from 66 tickets
- [Ground Zero Sprint Views](../support/ground-zero/sprint-views.md) - 6 priority queues spanning all apps
- [Ground Zero Pain Ranking](../support/ground-zero/pain-ranking.md) - Full 68-ticket cross-app ranked list

---

## Shipped in MCSL 377 — 2026-04-28 (re-shipped)

**Release Summary**: 29 cards total (18 Ready To Ship, 2 Support Closed, 2 Unsupported Partnership, 2 Carrier Platform Issues, 1 BUG REPORTED, 1 QA READY, 2 Open, 1 Spill Over)

**Shipped/Closed**: 24 cards (18 Ready To Ship + 2 Support Closed + 2 Unsupported Partnership + 2 Carrier Platform Issues)

**⚠️ Non-terminal at re-ship**: 5 cards (1 BUG REPORTED, 1 QA READY, 2 Open, 1 Spill Over)

| ZI | Status | Ticket | Card |
|----|--------|--------|------|
| ZI-007 | Ready To Ship | [#304193](../zendesk/summaries/304193.md) | [Link](https://trello.com/c/5MHzHTHX) |
| ZI-012 | Ready To Ship | [#348049](../zendesk/summaries/348049.md) | [Link](https://trello.com/c/4O2qtG5a) |
| ZI-013 | Ready To Ship | [#354696](../zendesk/summaries/354696.md) | [Link](https://trello.com/c/eS4A1leH) |
| ZI-015 | Ready To Ship | [#361776](../zendesk/summaries/361776.md) | [Link](https://trello.com/c/PkYyotgd) |
| ZI-021 | Ready To Ship | [#369144](../zendesk/summaries/369144.md) | [Link](https://trello.com/c/f7opk5j4) |
| ZI-022 | Ready To Ship | [#369556](../zendesk/summaries/369556.md) | [Link](https://trello.com/c/xGKh9VxZ) |
| ZI-032 | Ready To Ship | [#373991](../zendesk/summaries/373991.md) | [Link](https://trello.com/c/YMDkiZpi) |
| ZI-033 | Ready To Ship | [#373991](../zendesk/summaries/373991.md) | [Link](https://trello.com/c/vxt5hVgw) |
| ZI-035 | Ready To Ship | [#374851](../zendesk/summaries/374851.md) | [Link](https://trello.com/c/5IrdjdB5) |
| ZI-039 | Ready To Ship | [#377526](../zendesk/summaries/377526.md) | [Link](https://trello.com/c/SUyCh7kL) |
| ZI-041 | Ready To Ship | [#377526](../zendesk/summaries/377526.md) | [Link](https://trello.com/c/gvXEqh1o) |
| ZI-046 | Ready To Ship | [#377574](../zendesk/summaries/377574.md) | [Link](https://trello.com/c/6d6xn2el) |
| ZI-048 | Ready To Ship | [#378511](../zendesk/summaries/378511.md) | [Link](https://trello.com/c/XOMzbVqD) |
| ZI-049 | Ready To Ship | [#378513](../zendesk/summaries/378513.md) | [Link](https://trello.com/c/2xiIZROW) |
| ZI-060 | Ready To Ship | [#380339](../zendesk/summaries/380339.md) | [Link](https://trello.com/c/vqCI9275) |
| ZI-067 | Ready To Ship | [#381380](../zendesk/summaries/381380.md) | [Link](https://trello.com/c/IroRLJ0E) |
| ZI-071 | Ready To Ship | [#382009](../zendesk/summaries/382009.md) | [Link](https://trello.com/c/Nad1fC51) |
| ZI-263 | Ready To Ship | [#384408](../zendesk/summaries/384408.md) | [Link](https://trello.com/c/DJn4GJCG) |
| ZI-023 | Support Closed | [#369556](../zendesk/summaries/369556.md) | [Link](https://trello.com/c/v6cIPFyE) |
| ZI-051 | Support Closed | [#379042](../zendesk/summaries/379042.md) | [Link](https://trello.com/c/xuBZ7old) |
| ZI-018 | Unsupported Partnership | [#366630](../zendesk/summaries/366630.md) | [Link](https://trello.com/c/NJ7hg2Oi) |
| ZI-057 | Unsupported Partnership | [#379963](../zendesk/summaries/379963.md) | [Link](https://trello.com/c/DxVXh1CF) |
| ZI-008 | Carrier Platform Issues | [#306141](../zendesk/summaries/306141.md) | [Link](https://trello.com/c/9rdDqCiL) |
| ZI-069 | Carrier Platform Issues | [#382009](../zendesk/summaries/382009.md) | [Link](https://trello.com/c/IDjBgyhh) |

---

## Shipped in MCSL 381 — 2026-06-16

| ZI | Title | Ticket | Card | Source |
|----|-------|--------|------|--------|
| ZI-523 | Amazon Shipping label-failure error message fix | [#387563](../zendesk/summaries/387563.md) | [SL](https://trello.com/c/Gvyyzmdl) | 381 |
| ZI-524 | Amazon Shipping estimated delivery days in grid | [#387563](../zendesk/summaries/387563.md) | [SL](https://trello.com/c/Cr6MYVVL) | 381 |
| ZI-530 | Welcome-email overhaul | [#387845](../zendesk/summaries/387845.md) | [SL](https://trello.com/c/m9W9Cblq) | 381 |
| ZI-531 | TForce carrier integration | [#389467](../zendesk/summaries/389467.md) | [SL](https://trello.com/c/zZlGsCnW) | 381 |
| ZI-538 | AusPost: sanitise null recipient phone | [#390097](../zendesk/summaries/390097.md) | [SL](https://trello.com/c/br0i86eK) | 381 |
| ZI-540 | NZ Post Enhancements: SOv2 + Label upgrades | [#390108](../zendesk/summaries/390108.md) | [SL](https://trello.com/c/l1oRHe2L) | 381 |
| ZI-544 | Love of India: large-batch UX, retry-state, print mismatch | [#390510](../zendesk/summaries/390510.md) | [SL](https://trello.com/c/qaq1crm5) | 381 |
| ZI-552 | Block tracking-notification emails when SMTP not configured | [#390467](../zendesk/summaries/390467.md) | [SL](https://trello.com/c/nIGCc0JC) | 381 |
| ZI-583 | Delivro post-integration: shipment field defaults | [#381046](../zendesk/summaries/381046.md) | [SL](https://trello.com/c/I8eVHiKr) | 381p |
| ZI-094 | UPS custom description (Support Closed) | [#377795](../zendesk/summaries/377795.md) | [SL](https://trello.com/c/UpgWKbYK) | 381 |
| ZI-103 | Commercial invoice EUR currency (Support Closed) | [#383757](../zendesk/summaries/383757.md) | [SL](https://trello.com/c/iQu7hqb9) | 381 |
| ZI-534 | Plan-tier product-count limits (Carrier Platform) | [#389897](../zendesk/summaries/389897.md) | [SL](https://trello.com/c/GlcjLhTe) | 381 |
| ZI-542 | MyNZPB SMB integration (Carrier Platform) | [#390108](../zendesk/summaries/390108.md) | [SL](https://trello.com/c/WddCGKuY) | 381 |
| — | Carrier Integration India Post | — | [ph-WIP](https://trello.com/c/WOth7i6s) | 381 ad-hoc |
| — | Carrier Integration DHL Express | — | [ph-WIP](https://trello.com/c/LsmHAIIj) | 381 ad-hoc |
| — | WSS: flat rate adjustment fix (ZD #394137) | — | [ph-WIP](https://trello.com/c/NLqXsEv7) | 381 ad-hoc |
| — | FedEx REST Ground Close Manifest | — | [ph-WIP](https://trello.com/c/LzjcrcUr) | 381 ad-hoc |
| — | Shopify Billing Compliance and Trial Extension | — | [ph-WIP](https://trello.com/c/AH1WgQnW) | 381p |
| — | Delivro: Flat Rate Zeroed fix | — | [ph-WIP](https://trello.com/c/7hF2HxYq) | 381p (ZI-583) |
| — | Delivro: BOITE fallback | — | [ph-WIP](https://trello.com/c/TuoIk6Ik) | 381p (ZI-583) |
| — | Release Label Batches | — | [ph-WIP](https://trello.com/c/FSugx3SX) | 381p |
