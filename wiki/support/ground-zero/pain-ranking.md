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

**Trello Board**: [PH WIP](https://trello.com/b/PWKHwiCI/ph-wip) — lanes reflect card position as of 2026-04-10.

---

## 🔴 TIER 1 — BLOCKING / HIGH PAIN

### Category A: International Shipping / Customs / Invoices
**Pain Score: 10/10** | **14 issues** | Blocks international merchants entirely; compliance risk

> **Pattern**: Data not appearing — or appearing incorrectly — on customs documents (Commercial Invoices, CN22 forms, HS codes, declarations). Affects UPS, FedEx, PostNord, DHL. Fixing the CI/customs pipeline once resolves ~20% of the entire backlog.

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#383043](../../../../raw/zendesk/shopify/383043.json) | Custom description field capped at 30 chars on label | WooCommerce | Handled | — no card |
| [#380784](../../../../raw/zendesk/shopify/380784.json) | Print declarationStatement on Commercial Invoice | Shopify | Yet to pick | [— no MCSL tag](https://trello.com/c/3DpR40jp) |
| [#374851](../../../../raw/zendesk/shopify/374851.json) | Incorrect decimal printed on invoice | Shopify | Yet to pick | [DevNeeded Cards](https://trello.com/c/Y0HKgDp0) |
| [#382694](../../../../raw/zendesk/shopify/382694.json) | Country of origin fix for CN22 PostNord | Shopify | **Dev completed** ✅ | [Ready For QA MCSL 376](https://trello.com/c/wF8Q05oX) |
| [#377795](../../../../raw/zendesk/shopify/377795.json) | UPS: Full product description not printed on invoice | Shopify | In discussion | — no card |
| [#379784](../../../../raw/zendesk/shopify/379784.json) | Print CN22 and label on same page (PostNord) | Shopify | Contacted PostNord | — no card |
| [#380339](../../../../raw/zendesk/shopify/380339.json) | Edit HS Code at shipment level | Shopify | To discuss | [Cards to Groom](https://trello.com/c/dvXHxVhu) |
| [#373991](../../../../raw/zendesk/shopify/373991.json) | Display box name on tax invoice | Shopify | Yet to pick | [Planning Lane](https://trello.com/c/OIA5Rtyn) |
| [#374022](../../../../raw/zendesk/shopify/374022.json) | Discounted value not printed on CI (UPS) | Shopify | Yet to pick | [Planning Lane](https://trello.com/c/anU1cUOT) |
| [#381261](../../../../raw/zendesk/shopify/381261.json) | Avoid passing export declaration for DHL | Shopify | Yet to pick | — no card |
| #376223 | PostNord discounted value in CI | BigCommerce | Yet to pick | — no card |
| [#377217](../../../../raw/zendesk/shopify/377217.json) | Different export reasons for forward vs return shipments | Shopify | Yet to pick | [L3 Dev Ready](https://trello.com/c/JtONFSnJ) |
| [#366630](../../../../raw/zendesk/shopify/366630.json) | DPD NL services (international) | Shopify | Yet to pick | [L3 Dev Ready](https://trello.com/c/hm95at6L) |
| [#378511](../../../../raw/zendesk/shopify/378511.json) | Pass product description in UPS reference field | Shopify | Yet to pick | [L3 Dev Ready](https://trello.com/c/oESb1Zcx) |

---

### Category B: Product Import / Variant Handling
**Pain Score: 9/10** | **11 issues** | Merchants with large catalogs cannot use the app

> **Pattern**: Hard limits on variant counts block scaling merchants. Variant search has been open since June 2023. Bundled/composite product support missing across both WooCommerce and Shopify.

| Ticket | Issue | App | Dev Status | Age | Trello Lane |
|--------|-------|-----|-----------|-----|-------------|
| [#379214](../../../../raw/zendesk/shopify/379214.json) | Variant import fails when count > 100 | Shopify | Fixed ✅ | 3 weeks | — no card |
| [#381087](../../../../raw/zendesk/shopify/381087.json) | Variant import fails when count > 100 (2nd merchant) | Shopify | Fixed ✅ | 2 weeks | — no card |
| [#378513](../../../../raw/zendesk/shopify/378513.json) | Variant import fails when count > 100 (3rd — recurring!) | Shopify | Fixed ✅ | 1 month | [Ready For QA MCSL 375p_3](https://trello.com/c/GveSDv1T) |
| [#365042](../../../../raw/zendesk/shopify/365042.json) | Support more than 250 variants | Shopify | Yet to pick | 4 months | [Planning Lane](https://trello.com/c/tCzg2BA5) |
| [#370966](../../../../raw/zendesk/shopify/370966.json) | Delay in product import | Shopify | Yet to discuss | 2.5 months | [Cards to Groom](https://trello.com/c/Dhxvv3iL) |
| [#372492](../../../../raw/zendesk/shopify/372492.json) | Incorrect product count for bundled product | Shopify | Yet to pick | 2 months | [L3 Dev Ready](https://trello.com/c/6M3cbv7i) |
| [#277997](../../../../raw/zendesk/shopify/277997.json) | Variant search functionality | Shopify | Yet to pick | **21 months** | [L3 Dev Ready](https://trello.com/c/iuoLrBbC) |
| [#218195](../../../../raw/zendesk/shopify/218195.json) | Variant search (oldest ticket) | Shopify | Yet to pick | **34 months** | [L3 Dev Ready](https://trello.com/c/iuoLrBbC) |
| [#351838](../../../../raw/zendesk/shopify/351838.json) | Composite product compatibility | WooCommerce | Yet to pick | 6 months | — no card |
| [#350796](../../../../raw/zendesk/shopify/350796.json) | Composite product compatibility (2nd) | WooCommerce | Yet to pick | 6 months | — no card |
| [#260001](../../../../raw/zendesk/shopify/260001.json) | Bundled product compatibility | WooCommerce | Yet to pick | **25 months** | — no card |

---

### Category C: Carrier Integration & Migration
**Pain Score: 8/10** | **15 issues** | API deadlines create urgency; merchants can't use preferred carriers

> **Pattern**: Each carrier API change generates 3-6 tickets. Australia Post security update is urgent (2 merchants forwarded the notice on the same day). PostNord and Royal Mail service updates pending. USPS has multiple service gaps.

| Ticket | Issue | App | Dev Status | Urgency | Trello Lane |
|--------|-------|-----|-----------|---------|-------------|
| [#382780](../../../../raw/zendesk/shopify/382780.json) | Australia Post security update | Shopify | To discuss | 🚨 External deadline | — no card |
| [#383002](../../../../raw/zendesk/shopify/383002.json) | Australia Post security update (2nd merchant same day) | Shopify | To discuss | 🚨 External deadline | — no card |
| [#373200](../../../../raw/zendesk/shopify/373200.json) | PostNord discontinued/updated services | Shopify | Yet to pick | High | [Cards to Groom](https://trello.com/c/veBBlL23) |
| [#379963](../../../../raw/zendesk/shopify/379963.json) | Include new Royal Mail services | Shopify | Yet to pick | Medium | — no card |
| [#376856](../../../../raw/zendesk/shopify/376856.json) | UPS WorldEase integration | Shopify | To discuss | Medium | — no card |
| [#348049](../../../../raw/zendesk/shopify/348049.json) | USPS Scanform / EOD manifest | Shopify | Yet to pick | Medium | [Planning Lane](https://trello.com/c/u2tYCGmn) |
| [#299137](../../../../raw/zendesk/shopify/299137.json) | USPS Ground Advantage Cubic service | Shopify | Yet to pick | Medium | [Planning Lane](https://trello.com/c/fIdUwi8i) |
| [#369556](../../../../raw/zendesk/shopify/369556.json) | DHL Return service integration | Shopify | Yet to pick | Medium | [In Dev](https://trello.com/c/FK4lGtNX) |
| #381046 | Delivro carrier integration | WooCommerce | Yet to pick | Low | — no card |
| #379378 | Canpar eCommerce integration listing | WooCommerce | Open | Low | — no card |
| #377088 | FedEx REST package edit functionality | WooCommerce | Open | Medium | — no card |
| #364411 | USPS Flat Rate Box dimensions | WooCommerce | In progress | Medium | — no card |
| #302656 | Media Mail integration | WooCommerce | Backlog | Low | — no card |
| #379796 | PostNL service update | Magento | Yet to pick | High | — no card |
| [#306141](../../../../raw/zendesk/shopify/306141.json) | Avoid Saturday delivery when not available | Shopify | Yet to pick | Low | [Planning Lane](https://trello.com/c/gSSuSgsQ) |

---

## 🟠 TIER 2 — SIGNIFICANT PAIN

### Category D: FedEx-Specific Issues
**Pain Score: 7/10** | **6 issues** | REST migration aftermath; ongoing edge-case stream

> **Pattern**: FedEx REST migration generated a long tail of edge cases. Post-upload failures are FedEx-side but customers blame the app. Each issue requires careful FedEx API coordination.

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#382188](../../../../raw/zendesk/shopify/382188.json) | FedEx REST post upload failure | Shopify | FedEx-side issue | — no card |
| [#379042](../../../../raw/zendesk/shopify/379042.json) | FedEx post upload failure (2nd merchant) | Shopify | FedEx-side issue | [Cards to Groom](https://trello.com/c/fDPNIIsr) |
| [#382425](../../../../raw/zendesk/shopify/382425.json) | FedEx REST: Avoid One Rate | Shopify | **Dev completed** ✅ | — no card |
| [#382009](../../../../raw/zendesk/shopify/382009.json) | Dimensions not passed when FedEx box selected | Shopify | To discuss | — no card |
| [#379098](../../../../raw/zendesk/shopify/379098.json) | Update FedEx REST signature option via CSV | Shopify | Yet to pick | [L3 Dev Ready](https://trello.com/c/HELulhS7) |
| [#369144](../../../../raw/zendesk/shopify/369144.json) | Minimum value handling for FedEx | Shopify | Yet to pick | [Cards to Groom](https://trello.com/c/Vu9WCUzZ) |

---

### Category E: Order Management
**Pain Score: 7/10** | **3 issues** | Data integrity issues erode trust fastest

> ⚠️ **#382961 is the single most dangerous ticket in the entire list** — orders silently changing to "not to ship" state. Even if edge-case, data integrity issues are the fastest path to churn. **Note: Trello card has no labels at all — needs MCSL tag and prioritisation.**

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#382961](../../../../raw/zendesk/shopify/382961.json) | ⚠️ Orders disappearing (not-to-ship state) — upsell trigger | Shopify | Fix needed | [⚠️ No labels](https://trello.com/c/iHqyyqoC) |
| #375662 | Shipping address changes not syncing from WooCommerce | WooCommerce | Open | — no card |
| [#304193](../../../../raw/zendesk/shopify/304193.json) | Update order note in imported order | Shopify | Yet to pick | [Planning Lane](https://trello.com/c/V0HHCMiw) |

---

### Category F: Label Generation & Management
**Pain Score: 6/10** | **3 issues** | Core workflow disruption

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#381380](../../../../raw/zendesk/shopify/381380.json) | Can't clean up / delete USPS label | Shopify | Yet to fix | [Cards to Groom](https://trello.com/c/h0S55hOR) |
| #368959 | Manifest enhancement | WooCommerce | **Dev completed** ✅ | — no card |
| [#361776](../../../../raw/zendesk/shopify/361776.json) | Edit package not showing adjusted value | Shopify | Yet to pick | [L3 Dev Ready](https://trello.com/c/yaXvKdU9) |

---

## 🟡 TIER 3 — MODERATE PAIN

### Category G: Reporting & Data Export
**Pain Score: 5/10** | **2 issues**

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#354696](../../../../raw/zendesk/shopify/354696.json) | Include Ship To address in report | Shopify | Yet to pick | [Planning Lane](https://trello.com/c/VXJbbgIK) |
| [#360396](../../../../raw/zendesk/shopify/360396.json) | Include carrier scan time in report | Shopify | In progress | [L3 Dev Ready](https://trello.com/c/NaexGMn2) |

---

### Category H: Returns
**Pain Score: 5/10** | **2 issues**

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#377217](../../../../raw/zendesk/shopify/377217.json) | Return label failing / different export reasons | Shopify | Yet to pick | [L3 Dev Ready](https://trello.com/c/JtONFSnJ) |
| [#369556](../../../../raw/zendesk/shopify/369556.json) | DHL Return service integration | Shopify | Yet to pick | [In Dev](https://trello.com/c/FK4lGtNX) |

---

### Category I: Rate Shopping & Pricing
**Pain Score: 4/10** | **3 issues**

| Ticket | Issue | App | Dev Status | Trello Lane |
|--------|-------|-----|-----------|-------------|
| [#383024](../../../../raw/zendesk/shopify/383024.json) | Rates unavailable | Shopify | Handled | — no card |
| [#378176](../../../../raw/zendesk/shopify/378176.json) | UPS Hazmat rate discrepancy | Shopify | Needs UPS assistance | [— MCSL (diff board)](https://trello.com/c/0vyY6mAt) |
| #309068 | Currency switcher compatibility | WooCommerce | Yet to pick | — no card |

---

## 🟢 TIER 4 — LOW PAIN / HANDLED

### Category J: Onboarding & Installation (8 tickets)

Mostly handled by support team. Logged for volume tracking only.

| Ticket | Issue | App | Status | Trello Lane |
|--------|-------|-----|--------|-------------|
| [#383243](../../../../raw/zendesk/shopify/383243.json) | Installation — call scheduled | Shopify | Handled | — no card |
| #383036 | Onboarding scheduled | WooCommerce | Handled | — no card |
| #383119 | Welcome follow-up | WooCommerce | Open | — no card |
| [#383103](../../../../raw/zendesk/shopify/383103.json) | UPS Digital Connections inquiry | Shopify | Handled | — no card |
| #383148 | Onboarding | Shopify | Handled | — no card |
| #383093 | Onboarding (2 problems) | Shopify | Handled | — no card |
| [#382795](../../../../raw/zendesk/shopify/382795.json) | Bluedart label failure (account eligibility) | Shopify | Handled | — no card |
| [#382820](../../../../raw/zendesk/shopify/382820.json) | Bluedart pickup zone auth | Shopify | Handled | — no card |

### Category K: Billing / Misc (8 tickets)

| Ticket | Issue | App | Status | Trello Lane |
|--------|-------|-----|--------|-------------|
| #383244 | App uninstalled / churn signal | Shopify | Signal | — no card |
| [#377113](../../../../raw/zendesk/shopify/377113.json) | Churn prevention / USPS buffer time for delivery | Shopify | Yet to pick | [Cards to Groom](https://trello.com/c/l5RzUNwU) |
| #381496 | Payment dispute | WooCommerce | Billing | — no card |
| [#381931](../../../../raw/zendesk/shopify/381931.json) | Amazon Shipping onboarding / custom plan needed | Shopify | Billing | [Cards to Groom](https://trello.com/c/I2JzgMHB) |
| [#338603](../../../../raw/zendesk/shopify/338603.json) | Change subscription error on Safari | Shopify | Yet to pick | [Planning Lane](https://trello.com/c/KqyWcCcB) |
| #370219 | Payment type filter update | Shopify | Yet to pick | [Cards to Groom](https://trello.com/c/rhEXNvk4) |
| #376463 | Incorrect value in fulfillment request | BigCommerce | Yet to pick | — no card |
| #345572 | Display delivery date with service | BigCommerce FedEx | Yet to pick | — no card |

---

## Trello Lane Summary

| Lane | Cards (MCSL) | Notes |
|------|-------------|-------|
| Cards to Groom | 10 | Groomed but not yet in a sprint — needs triage priority |
| Planning Lane | 9 | Accepted into roadmap, awaiting sprint slot |
| L3 Dev Ready | 8 | Dev spec done, ready to be picked up |
| DevNeeded Cards | 1 | Confirmed needs dev but not groomed yet |
| In Dev | 1 | Actively being developed |
| Ready For QA MCSL 375p_3 | 1 | In QA |
| Ready For QA MCSL 376 | 1 | In QA |
| ⚠️ No card / No MCSL tag | 3 | #382961 (P0 orders bug), #380784 (CI declaration), #378176 (UPS Hazmat) |
| — No Trello card at all | 34 | Tickets with no linked Trello card — no dev action tracked |

---

## Related Pages

- [Ground Zero Index](index.md)
- [By App](by-app.md)
- [Insights](insights.md)
- [Sprint Views](sprint-views.md)
