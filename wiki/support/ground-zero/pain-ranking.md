---
title: Ground Zero — Pain Ranking
category: support
sources: [stage-zero-analysis, zendesk]
status: complete
last_updated: 2026-04-10
git_reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
---

# Pain Ranking — All 68 Tickets

All tickets from `raw/sheets/stage-zero-analysis.xlsx` categorized and ranked from most to least painful. Multi-issue tickets are split into discrete problems. Tickets with local JSON are linked.

---

## 🔴 TIER 1 — BLOCKING / HIGH PAIN

### Category A: International Shipping / Customs / Invoices
**Pain Score: 10/10** | **14 issues** | Blocks international merchants entirely; compliance risk

> **Pattern**: Data not appearing — or appearing incorrectly — on customs documents (Commercial Invoices, CN22 forms, HS codes, declarations). Affects UPS, FedEx, PostNord, DHL. Fixing the CI/customs pipeline once resolves ~20% of the entire backlog.

| Ticket | Issue | App | Dev Status |
|--------|-------|-----|-----------|
| [#383043](../../../../raw/zendesk/shopify/383043.json) | Custom description field capped at 30 chars on label | WooCommerce | Handled |
| [#380784](../../../../raw/zendesk/shopify/380784.json) | Print declarationStatement on Commercial Invoice | Shopify | Yet to pick |
| [#374851](../../../../raw/zendesk/shopify/374851.json) | Incorrect decimal printed on invoice | Shopify | Yet to pick |
| [#382694](../../../../raw/zendesk/shopify/382694.json) | Country of origin fix for CN22 PostNord | Shopify | **Dev completed** ✅ |
| [#377795](../../../../raw/zendesk/shopify/377795.json) | UPS: Full product description not printed on invoice | Shopify | In discussion |
| [#379784](../../../../raw/zendesk/shopify/379784.json) | Print CN22 and label on same page (PostNord) | Shopify | Contacted PostNord |
| [#380339](../../../../raw/zendesk/shopify/380339.json) | Edit HS Code at shipment level | Shopify | To discuss |
| [#373991](../../../../raw/zendesk/shopify/373991.json) | Display box name on tax invoice | Shopify | Yet to pick |
| [#374022](../../../../raw/zendesk/shopify/374022.json) | Discounted value not printed on CI (UPS) | Shopify | Yet to pick |
| [#381261](../../../../raw/zendesk/shopify/381261.json) | Avoid passing export declaration for DHL | Shopify | Yet to pick |
| #376223 | PostNord discounted value in CI | BigCommerce | Yet to pick |
| [#377217](../../../../raw/zendesk/shopify/377217.json) | Different export reasons for forward vs return shipments | Shopify | Yet to pick |
| [#366630](../../../../raw/zendesk/shopify/366630.json) | DPD NL services (international) | Shopify | Yet to pick |
| [#378511](../../../../raw/zendesk/shopify/378511.json) | Pass product description in UPS reference field | Shopify | Yet to pick |

---

### Category B: Product Import / Variant Handling
**Pain Score: 9/10** | **11 issues** | Merchants with large catalogs cannot use the app

> **Pattern**: Hard limits on variant counts block scaling merchants. Variant search has been open since June 2023. Bundled/composite product support missing across both WooCommerce and Shopify.

| Ticket | Issue | App | Dev Status | Age |
|--------|-------|-----|-----------|-----|
| [#379214](../../../../raw/zendesk/shopify/379214.json) | Variant import fails when count > 100 | Shopify | Fixed ✅ | 3 weeks |
| [#381087](../../../../raw/zendesk/shopify/381087.json) | Variant import fails when count > 100 (2nd merchant) | Shopify | Fixed ✅ | 2 weeks |
| [#378513](../../../../raw/zendesk/shopify/378513.json) | Variant import fails when count > 100 (3rd — recurring!) | Shopify | Fixed ✅ | 1 month |
| [#365042](../../../../raw/zendesk/shopify/365042.json) | Support more than 250 variants | Shopify | Yet to pick | 4 months |
| [#370966](../../../../raw/zendesk/shopify/370966.json) | Delay in product import | Shopify | Yet to discuss | 2.5 months |
| [#372492](../../../../raw/zendesk/shopify/372492.json) | Incorrect product count for bundled product | Shopify | Yet to pick | 2 months |
| [#277997](../../../../raw/zendesk/shopify/277997.json) | Variant search functionality | Shopify | Yet to pick | **21 months** |
| [#218195](../../../../raw/zendesk/shopify/218195.json) | Variant search (oldest ticket) | Shopify | Yet to pick | **34 months** |
| [#351838](../../../../raw/zendesk/shopify/351838.json) | Composite product compatibility | WooCommerce | Yet to pick | 6 months |
| [#350796](../../../../raw/zendesk/shopify/350796.json) | Composite product compatibility (2nd) | WooCommerce | Yet to pick | 6 months |
| [#260001](../../../../raw/zendesk/shopify/260001.json) | Bundled product compatibility | WooCommerce | Yet to pick | **25 months** |

---

### Category C: Carrier Integration & Migration
**Pain Score: 8/10** | **15 issues** | API deadlines create urgency; merchants can't use preferred carriers

> **Pattern**: Each carrier API change generates 3-6 tickets. Australia Post security update is urgent (2 merchants forwarded the notice on the same day). PostNord and Royal Mail service updates pending. USPS has multiple service gaps.

| Ticket | Issue | App | Dev Status | Urgency |
|--------|-------|-----|-----------|---------|
| [#382780](../../../../raw/zendesk/shopify/382780.json) | Australia Post security update | Shopify | To discuss | 🚨 External deadline |
| [#383002](../../../../raw/zendesk/shopify/383002.json) | Australia Post security update (2nd merchant same day) | Shopify | To discuss | 🚨 External deadline |
| [#373200](../../../../raw/zendesk/shopify/373200.json) | PostNord discontinued/updated services | Shopify | Yet to pick | High |
| [#379963](../../../../raw/zendesk/shopify/379963.json) | Include new Royal Mail services | Shopify | Yet to pick | Medium |
| [#376856](../../../../raw/zendesk/shopify/376856.json) | UPS WorldEase integration | Shopify | To discuss | Medium |
| [#348049](../../../../raw/zendesk/shopify/348049.json) | USPS Scanform / EOD manifest | Shopify | Yet to pick | Medium |
| [#299137](../../../../raw/zendesk/shopify/299137.json) | USPS Ground Advantage Cubic service | Shopify | Yet to pick | Medium |
| [#369556](../../../../raw/zendesk/shopify/369556.json) | DHL Return service integration | Shopify | Yet to pick | Medium |
| #381046 | Delivro carrier integration | WooCommerce | Yet to pick | Low |
| #379378 | Canpar eCommerce integration listing | WooCommerce | Open | Low |
| #377088 | FedEx REST package edit functionality | WooCommerce | Open | Medium |
| #364411 | USPS Flat Rate Box dimensions | WooCommerce | In progress | Medium |
| #302656 | Media Mail integration | WooCommerce | Backlog | Low |
| #379796 | PostNL service update | Magento | Yet to pick | High |
| [#306141](../../../../raw/zendesk/shopify/306141.json) | Avoid Saturday delivery when not available | Shopify | Yet to pick | Low |

---

## 🟠 TIER 2 — SIGNIFICANT PAIN

### Category D: FedEx-Specific Issues
**Pain Score: 7/10** | **6 issues** | REST migration aftermath; ongoing edge-case stream

> **Pattern**: FedEx REST migration generated a long tail of edge cases. Post-upload failures are FedEx-side but customers blame the app. Each issue requires careful FedEx API coordination.

| Ticket                                                 | Issue                                         | App     | Dev Status          |
| ------------------------------------------------------ | --------------------------------------------- | ------- | ------------------- |
| [#382188](../../../../raw/zendesk/shopify/382188.json) | FedEx REST post upload failure                | Shopify | FedEx-side issue    |
| [#379042](../../../../raw/zendesk/shopify/379042.json) | FedEx post upload failure (2nd merchant)      | Shopify | FedEx-side issue    |
| [#382425](../../../../raw/zendesk/shopify/382425.json) | FedEx REST: Avoid One Rate                    | Shopify | **Dev completed** ✅ |
| [#382009](../../../../raw/zendesk/shopify/382009.json) | Dimensions not passed when FedEx box selected | Shopify | To discuss          |
| [#379098](../../../../raw/zendesk/shopify/379098.json) | Update FedEx REST signature option via CSV    | Shopify | Yet to pick         |
| [#369144](../../../../raw/zendesk/shopify/369144.json) | Minimum value handling for FedEx              | Shopify | Yet to pick         |

---

### Category E: Order Management
**Pain Score: 7/10** | **3 issues** | Data integrity issues erode trust fastest

> ⚠️ **#382961 is the single most dangerous ticket in the entire list** — orders silently changing to "not to ship" state. Even if edge-case, data integrity issues are the fastest path to churn.

| Ticket | Issue | App | Dev Status |
|--------|-------|-----|-----------|
| [#382961](../../../../raw/zendesk/shopify/382961.json) | ⚠️ Orders disappearing (not-to-ship state) — upsell trigger | Shopify | Fix needed |
| #375662 | Shipping address changes not syncing from WooCommerce | WooCommerce | Open |
| [#304193](../../../../raw/zendesk/shopify/304193.json) | Update order note in imported order | Shopify | Yet to pick |

---

### Category F: Label Generation & Management
**Pain Score: 6/10** | **3 issues** | Core workflow disruption

| Ticket | Issue | App | Dev Status |
|--------|-------|-----|-----------|
| [#381380](../../../../raw/zendesk/shopify/381380.json) | Can't clean up / delete USPS label | Shopify | Yet to fix |
| #368959 | Manifest enhancement | WooCommerce | **Dev completed** ✅ |
| [#361776](../../../../raw/zendesk/shopify/361776.json) | Edit package not showing adjusted value | Shopify | Yet to pick |

---

## 🟡 TIER 3 — MODERATE PAIN

### Category G: Reporting & Data Export
**Pain Score: 5/10** | **2 issues**

| Ticket | Issue | App | Dev Status |
|--------|-------|-----|-----------|
| [#354696](../../../../raw/zendesk/shopify/354696.json) | Include Ship To address in report | Shopify | Yet to pick |
| [#360396](../../../../raw/zendesk/shopify/360396.json) | Include carrier scan time in report | Shopify | In progress |

---

### Category H: Returns
**Pain Score: 5/10** | **2 issues**

| Ticket | Issue | App | Dev Status |
|--------|-------|-----|-----------|
| [#377217](../../../../raw/zendesk/shopify/377217.json) | Return label failing / different export reasons | Shopify | Yet to pick |
| [#369556](../../../../raw/zendesk/shopify/369556.json) | DHL Return service integration | Shopify | Yet to pick |

---

### Category I: Rate Shopping & Pricing
**Pain Score: 4/10** | **3 issues**

| Ticket | Issue | App | Dev Status |
|--------|-------|-----|-----------|
| [#383024](../../../../raw/zendesk/shopify/383024.json) | Rates unavailable | Shopify | Handled |
| [#378176](../../../../raw/zendesk/shopify/378176.json) | UPS Hazmat rate discrepancy | Shopify | Needs UPS assistance |
| #309068 | Currency switcher compatibility | WooCommerce | Yet to pick |

---

## 🟢 TIER 4 — LOW PAIN / HANDLED

### Category J: Onboarding & Installation (8 tickets)

Mostly handled by support team. Logged for volume tracking only.

| Ticket | Issue | App | Status |
|--------|-------|-----|--------|
| [#383243](../../../../raw/zendesk/shopify/383243.json) | Installation — call scheduled | Shopify | Handled |
| #383036 | Onboarding scheduled | WooCommerce | Handled |
| #383119 | Welcome follow-up | WooCommerce | Open |
| [#383103](../../../../raw/zendesk/shopify/383103.json) | UPS Digital Connections inquiry | Shopify | Handled |
| #383148 | Onboarding | Shopify | Handled |
| #383093 | Onboarding (2 problems) | Shopify | Handled |
| [#382795](../../../../raw/zendesk/shopify/382795.json) | Bluedart label failure (account eligibility) | Shopify | Handled |
| [#382820](../../../../raw/zendesk/shopify/382820.json) | Bluedart pickup zone auth | Shopify | Handled |

### Category K: Billing / Misc (8 tickets)

| Ticket | Issue | App | Status |
|--------|-------|-----|--------|
| #383244 | App uninstalled / churn signal | Shopify | Signal |
| [#377113](../../../../raw/zendesk/shopify/377113.json) | Churn prevention / USPS buffer time for delivery | Shopify | Yet to pick |
| #381496 | Payment dispute | WooCommerce | Billing |
| [#381931](../../../../raw/zendesk/shopify/381931.json) | Amazon Shipping onboarding / custom plan needed | Shopify | Billing |
| [#338603](../../../../raw/zendesk/shopify/338603.json) | Change subscription error on Safari | Shopify | Yet to pick |
| #370219 | Payment type filter update | Shopify | Yet to pick |
| #376463 | Incorrect value in fulfillment request | BigCommerce | Yet to pick |
| #345572 | Display delivery date with service | BigCommerce FedEx | Yet to pick |

---

## Related Pages

- [Ground Zero Index](index.md)
- [By App](by-app.md)
- [Insights](insights.md)
- [Sprint Views](sprint-views.md)
