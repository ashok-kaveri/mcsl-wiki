---
title: Ground Zero — By App
category: support
sources: [stage-zero-analysis, zendesk]
status: complete
last_updated: 2026-04-10
git_reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
---

# Tickets by App

Same 68 tickets from [Pain Ranking](pain-ranking.md) re-cut by product. Useful for sprint planning when work is scoped per app team.

---

## Shopify Multi Carrier Shipping Label App — 49 tickets (72%)

The dominant surface area. All 10 issue categories are represented.

| Category | Count | Top Pain |
|----------|-------|----------|
| International / Customs / Invoices | 11 | CI data accuracy, HS codes, declarations, CN22 |
| Carrier Integration & Migration | 9 | AusPost security deadline, PostNord updates, USPS gaps |
| Product Import / Variants | 8 | >250 variant limit, variant search (3 years!), bundled products |
| FedEx Specific | 6 | REST post-upload, dimensions, signature options |
| Onboarding / Support | 6 | Mostly handled by support team |
| Billing / Misc | 5 | Subscription error, churn, Amazon Shipping plan |
| Order Management | 2 | Orders disappearing (P0!), order notes |
| Reporting | 2 | Ship-to address, scan time in reports |
| Returns | 2 | Return label failures, DHL returns |
| Label Management | 2 | Can't delete USPS label, edit package adjusted value |
| Rate Shopping | 2 | Rates unavailable, UPS Hazmat discrepancy |

### Shopify Tickets — Full List

| Ticket | Category | Issue | Dev Status |
|--------|----------|-------|-----------|
| [#383244](../../../../raw/zendesk/shopify/383244.json) | Billing/Churn | App uninstalled | Signal |
| [#383243](../../../../raw/zendesk/shopify/383243.json) | Onboarding | Installation — call scheduled | Handled |
| [#383103](../../../../raw/zendesk/shopify/383103.json) | Onboarding | UPS Digital Connections inquiry | Handled |
| [#383024](../../../../raw/zendesk/shopify/383024.json) | Rate Shopping | Rates unavailable | Handled |
| [#383002](../../../../raw/zendesk/shopify/383002.json) | Carrier Migration | Australia Post security update | To discuss |
| [#382961](../../../../raw/zendesk/shopify/382961.json) | Order Management | ⚠️ Orders disappearing (not-to-ship) | Fix needed |
| [#382820](../../../../raw/zendesk/shopify/382820.json) | Onboarding | Bluedart pickup zone auth | Handled |
| [#382795](../../../../raw/zendesk/shopify/382795.json) | Onboarding | Bluedart label failure (account) | Handled |
| [#382780](../../../../raw/zendesk/shopify/382780.json) | Carrier Migration | Australia Post security update | To discuss |
| [#382694](../../../../raw/zendesk/shopify/382694.json) | International | Country of origin CN22 PostNord | Dev completed ✅ |
| [#382425](../../../../raw/zendesk/shopify/382425.json) | FedEx | Avoid One Rate | Dev completed ✅ |
| [#382188](../../../../raw/zendesk/shopify/382188.json) | FedEx | REST post upload failure | FedEx-side |
| [#382009](../../../../raw/zendesk/shopify/382009.json) | FedEx | Dimensions not passed with FedEx box | To discuss |
| [#381931](../../../../raw/zendesk/shopify/381931.json) | Billing | Amazon Shipping / custom plan | Billing |
| [#381380](../../../../raw/zendesk/shopify/381380.json) | Label Management | Can't delete USPS label | Yet to fix |
| [#381261](../../../../raw/zendesk/shopify/381261.json) | International | Avoid export declaration for DHL | Yet to pick |
| [#381087](../../../../raw/zendesk/shopify/381087.json) | Product Import | Variant import fails >100 | Fixed ✅ |
| #383148 | Onboarding | Onboarding | Handled |
| #383093 | Onboarding | Onboarding (2 problems) | Handled |
| [#380784](../../../../raw/zendesk/shopify/380784.json) | International | Print declarationStatement on CI | Yet to pick |
| [#380339](../../../../raw/zendesk/shopify/380339.json) | International | Edit HS Code at shipment level | To discuss |
| [#379963](../../../../raw/zendesk/shopify/379963.json) | Carrier Integration | New Royal Mail services | Yet to pick |
| [#379784](../../../../raw/zendesk/shopify/379784.json) | International | Print CN22 + label on same page | Contacted PostNord |
| [#379214](../../../../raw/zendesk/shopify/379214.json) | Product Import | Variant import fails >100 | Fixed ✅ |
| [#379098](../../../../raw/zendesk/shopify/379098.json) | FedEx | Signature option via CSV | Yet to pick |
| [#379042](../../../../raw/zendesk/shopify/379042.json) | FedEx | REST post upload failure | FedEx-side |
| [#378513](../../../../raw/zendesk/shopify/378513.json) | Product Import | Variant import fails >100 (3rd!) | Fixed ✅ |
| [#378511](../../../../raw/zendesk/shopify/378511.json) | International | Product description in UPS reference | Yet to pick |
| [#378176](../../../../raw/zendesk/shopify/378176.json) | Rate Shopping | UPS Hazmat rate discrepancy | Needs UPS help |
| [#377795](../../../../raw/zendesk/shopify/377795.json) | International | Full description on UPS invoice | In discussion |
| [#377526](../../../../raw/zendesk/shopify/377526.json) | Carrier Integration | USPS address correction feature | To discuss |
| [#377217](../../../../raw/zendesk/shopify/377217.json) | Returns | Return label failing / export reasons | Yet to pick |
| [#377113](../../../../raw/zendesk/shopify/377113.json) | Billing/Churn | USPS delivery buffer time | Yet to pick |
| [#376856](../../../../raw/zendesk/shopify/376856.json) | Carrier Integration | UPS WorldEase integration | To discuss |
| [#374851](../../../../raw/zendesk/shopify/374851.json) | International | Incorrect decimal on invoice | Yet to pick |
| [#374022](../../../../raw/zendesk/shopify/374022.json) | International | Discounted value not on CI (UPS) | Yet to pick |
| [#373991](../../../../raw/zendesk/shopify/373991.json) | International | Box name on tax invoice | Yet to pick |
| [#373200](../../../../raw/zendesk/shopify/373200.json) | Carrier Migration | PostNord discontinued services | Yet to pick |
| [#372492](../../../../raw/zendesk/shopify/372492.json) | Product Import | Incorrect product count (bundled) | Yet to pick |
| [#370966](../../../../raw/zendesk/shopify/370966.json) | Product Import | Delay in product import | Yet to discuss |
| [#370219](../../../../raw/zendesk/shopify/370219.json) | Billing/Misc | Payment type filter update | Yet to pick |
| [#369556](../../../../raw/zendesk/shopify/369556.json) | Returns | DHL Return service integration | Yet to pick |
| [#369144](../../../../raw/zendesk/shopify/369144.json) | FedEx | Minimum value handling | Yet to pick |
| [#366630](../../../../raw/zendesk/shopify/366630.json) | International | DPD NL services | Yet to pick |
| [#365042](../../../../raw/zendesk/shopify/365042.json) | Product Import | Support >250 variants | Yet to pick |
| [#361776](../../../../raw/zendesk/shopify/361776.json) | Label Management | Edit package adjusted value wrong | Yet to pick |
| [#360396](../../../../raw/zendesk/shopify/360396.json) | Reporting | Carrier scan time in report | In progress |
| [#354696](../../../../raw/zendesk/shopify/354696.json) | Reporting | Ship to address in report | Yet to pick |
| [#348049](../../../../raw/zendesk/shopify/348049.json) | Carrier Integration | USPS Scanform / EOD manifest | Yet to pick |
| [#338603](../../../../raw/zendesk/shopify/338603.json) | Billing | Subscription error on Safari | Yet to pick |
| [#306141](../../../../raw/zendesk/shopify/306141.json) | Carrier Integration | Avoid Saturday delivery | Yet to pick |
| [#304193](../../../../raw/zendesk/shopify/304193.json) | Order Management | Update order note | Yet to pick |
| [#299137](../../../../raw/zendesk/shopify/299137.json) | Carrier Integration | USPS Ground Advantage Cubic | Yet to pick |
| [#277997](../../../../raw/zendesk/shopify/277997.json) | Product Import | Variant search | Yet to pick |
| [#218195](../../../../raw/zendesk/shopify/218195.json) | Product Import | Variant search (oldest ticket) | Yet to pick |

---

## WooCommerce Shipping Services — 15 tickets (22%)

Distinct pain profile from Shopify. Dominated by product compatibility gaps and carrier coverage holes.

| Category | Count | Top Pain |
|----------|-------|----------|
| Product Compatibility | 4 | Composite, bundled products, currency switcher |
| Carrier Integration | 4 | Delivro, Canpar, FedEx REST edit, Media Mail |
| Carrier Config | 2 | USPS Flat Rate boxes, FedEx package edit |
| Onboarding | 2 | Installation, welcome follow-up |
| International | 1 | Customs description length (30-char limit) |
| Order Management | 1 | Address changes not syncing |
| Label / Manifest | 1 | Manifest enhancement (dev completed) |

### WooCommerce Tickets — Full List

| Ticket | Category | Issue | Dev Status |
|--------|----------|-------|-----------|
| #383119 | Onboarding | Welcome follow-up | Open |
| #383036 | Onboarding | Installation — onboarding scheduled | Handled |
| #383043 | International | Custom description 30-char limit | Handled |
| #381496 | Billing | Payment dispute | Billing |
| #381046 | Carrier Integration | Delivro carrier integration | Yet to pick |
| #379378 | Carrier Integration | Canpar eCommerce listing | Open |
| #377088 | Carrier Config | FedEx REST new package edit | Open |
| #375662 | Order Management | Shipping address changes from WC | Open |
| #368959 | Label / Manifest | Manifest enhancement | Dev completed ✅ |
| #364411 | Carrier Config | USPS Flat Rate Box dimensions | In progress |
| #351838 | Product Compatibility | Composite product compatibility | Yet to pick |
| #350796 | Product Compatibility | Composite product compatibility (2nd) | Yet to pick |
| #309068 | Rate Shopping | Currency switcher compatibility | Yet to pick |
| #302656 | Carrier Integration | Media Mail integration | Backlog |
| #260001 | Product Compatibility | Bundled product compatibility | Yet to pick |

---

## BigCommerce — 3 tickets (4.5%)

Small but telling — international data accuracy and fulfillment correctness issues mirror Shopify patterns.

| Ticket | Category | Issue | Dev Status |
|--------|----------|-------|-----------|
| #376463 | Order Management | Incorrect value in fulfillment request | Yet to pick |
| #376223 | International | PostNord discounted value in CI | Yet to pick |
| #345572 | Feature Request | Display delivery date with service | Yet to pick |

**Cross-app signal**: PostNord CI value issue (#376223) mirrors Shopify's #374022 — likely same underlying data pipeline.

---

## Magento Multi Carrier — 1 ticket (1.5%)

| Ticket | Category | Issue | Dev Status |
|--------|----------|-------|-----------|
| #379796 | Carrier Migration | PostNL service update | Yet to pick |

---

## Cross-App Patterns

Issues that span multiple apps, indicating shared infrastructure problems:

| Pattern | Apps Affected | Tickets |
|---------|--------------|---------|
| PostNord CI / customs data | Shopify + BigCommerce | #374022, #376223, #382694, #379784 |
| Customs document accuracy | Shopify + WooCommerce + BigCommerce | Multiple (see Category A) |
| Product compatibility gaps | Shopify + WooCommerce | Variants, bundled, composite |
| Carrier service updates (PostNord, AusPost) | Shopify + Magento | Multiple |
| FedEx REST migration edge cases | Shopify + WooCommerce | Multiple |

---

## Related Pages

- [Ground Zero Index](index.md)
- [Pain Ranking](pain-ranking.md)
- [Insights](insights.md)
- [Sprint Views](sprint-views.md)
