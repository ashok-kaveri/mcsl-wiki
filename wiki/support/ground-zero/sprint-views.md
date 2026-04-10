---
title: Ground Zero — Sprint Views
category: support
sources: [stage-zero-analysis, zendesk]
status: complete
last_updated: 2026-04-10
git_reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
---

# Sprint Views — 6 Priority Queues

Six actionable views for prioritizing the 68-ticket backlog. Each view is a ready-to-use sprint input — pick a view, assign it, ship it.

---

## View 1: Sprint Zero — Ship What's Built
**Effort**: 1-2 days | **Impact**: Immediate customer relief, zero dev effort

Dev is done. These fixes exist in code but haven't reached merchants. The only work is deployment and closing the ticket.

| Ticket | Fix Ready | App | Merchant Waiting Since |
|--------|-----------|-----|----------------------|
| [#382694](../../../../raw/zendesk/shopify/382694.json) | Country of origin fix for CN22 PostNord | Shopify | Apr 6, 2026 |
| [#382425](../../../../raw/zendesk/shopify/382425.json) | FedEx REST: Avoid One Rate | Shopify | Apr 4, 2026 |
| #368959 | Manifest enhancement | WooCommerce | Jan 14, 2026 |
| #345572 | Display delivery date with service | BigCommerce | Aug 26, 2025 |

**Action**: Deploy, close tickets, notify merchants. Done.

---

## View 2: Fire Drill — External Deadlines
**Effort**: 3-5 days | **Impact**: Prevents service outages; carrier-imposed deadlines cannot slip

These are not optional. Carriers set the deadline.

| Ticket | Issue | Urgency | Action |
|--------|-------|---------|--------|
| [#382780](../../../../raw/zendesk/shopify/382780.json) | Australia Post security update | 🚨 Carrier deadline | Implement API security changes immediately |
| [#383002](../../../../raw/zendesk/shopify/383002.json) | Australia Post security update (2nd merchant) | 🚨 Carrier deadline | Same fix, verify both merchants resolved |
| [#373200](../../../../raw/zendesk/shopify/373200.json) | PostNord discontinued services | High — services already changing | Update service list, deprecate removed services |
| #379796 | PostNL service update (Magento) | High | Sync with PostNord changes if shared code |

**Note**: Australia Post fix likely handles both #382780 and #383002 in one deployment.

---

## View 3: Trust Restorers — Data Integrity & Core Bugs
**Effort**: 1 sprint | **Impact**: Prevents churn from the merchants most at risk of leaving

These issues directly erode trust in the app's reliability.

| Ticket | Issue | Why It's Critical |
|--------|-------|------------------|
| [#382961](../../../../raw/zendesk/shopify/382961.json) | ⚠️ Orders disappearing (not-to-ship state) | Data integrity = P0. Merchant has reported this multiple times. |
| [#381380](../../../../raw/zendesk/shopify/381380.json) | Can't delete / clean up USPS label | Stuck labels block re-shipment workflow entirely |
| [#361776](../../../../raw/zendesk/shopify/361776.json) | Edit package shows wrong adjusted value | Confusing UX; merchant can't trust what they see |
| #376463 | Incorrect value in BigCommerce fulfillment request | Wrong data sent to carrier — potential compliance issue |
| #375662 | Shipping address changes not syncing from WooCommerce | Orders ship to wrong address |

**Root cause to investigate for #382961**: One Click Upsell post-purchase flow interacts badly with order state machine. Check how post-purchase upsell events update order status in the app.

---

## View 4: International Shipping Sprint — CI/Customs Batch Fix
**Effort**: 2-3 sprints | **Impact**: Closes ~14 tickets; unblocks all international merchants

The single highest-leverage body of work. These 11 tickets share the same underlying commercial invoice and customs document pipeline. Fix it once, close many.

**Recommended approach**: Audit the full CI generation flow before assigning individual tickets. Many of these are the same pipeline issue presenting differently per carrier.

| Ticket | Issue | Carrier |
|--------|-------|---------|
| [#380784](../../../../raw/zendesk/shopify/380784.json) | Print declarationStatement on CI | DHL / general |
| [#374851](../../../../raw/zendesk/shopify/374851.json) | Incorrect decimal on invoice | General |
| [#377795](../../../../raw/zendesk/shopify/377795.json) | Full product description on UPS invoice | UPS |
| [#373991](../../../../raw/zendesk/shopify/373991.json) | Box name on tax invoice | General |
| [#374022](../../../../raw/zendesk/shopify/374022.json) | Discounted value not on CI | UPS |
| #376223 | PostNord discounted value in CI | PostNord / BigCommerce |
| [#378511](../../../../raw/zendesk/shopify/378511.json) | Product description in UPS reference field | UPS |
| [#380339](../../../../raw/zendesk/shopify/380339.json) | Edit HS Code at shipment level | General |
| [#381261](../../../../raw/zendesk/shopify/381261.json) | Skip export declaration for DHL | DHL |
| [#377217](../../../../raw/zendesk/shopify/377217.json) | Different export reasons for forward vs return | General |
| [#379784](../../../../raw/zendesk/shopify/379784.json) | CN22 + label on same page | PostNord |

**Also include** (related, lower effort):
- #383043 (WooCommerce custom description 30-char limit) — likely a single field length config change

---

## View 5: Scale Unlockers — Product Import Improvements
**Effort**: 2 sprints | **Impact**: Enables larger merchants; addresses the oldest open tickets

Unblocks the segment of merchants the app is currently unable to serve.

| Ticket | Issue | Age | App |
|--------|-------|-----|-----|
| [#218195](../../../../raw/zendesk/shopify/218195.json) | Variant search | **34 months** | Shopify |
| [#277997](../../../../raw/zendesk/shopify/277997.json) | Variant search (follow-up) | **21 months** | Shopify |
| [#365042](../../../../raw/zendesk/shopify/365042.json) | Support >250 variants | 4 months | Shopify |
| [#372492](../../../../raw/zendesk/shopify/372492.json) | Incorrect product count (bundled) | 2 months | Shopify |
| [#370966](../../../../raw/zendesk/shopify/370966.json) | Delay in product import | 2.5 months | Shopify |
| #260001 | Bundled product compatibility | **25 months** | WooCommerce |
| #351838 | Composite product compatibility | 6 months | WooCommerce |
| #350796 | Composite product compatibility (2nd) | 6 months | WooCommerce |

**Sequencing suggestion**:
1. Variant search (closes 2 tickets, highest ask age)
2. >250 variant limit (unblocks large-catalog merchants)
3. Bundled/composite product support (WooCommerce + Shopify together if shared logic)

---

## View 6: Carrier Expansion — New Integrations
**Effort**: Quarterly planning | **Impact**: New carrier coverage; mostly feature requests, lower urgency

Queue these for roadmap planning, not immediate sprints. Each requires carrier API onboarding.

| Ticket | Integration | App | Status |
|--------|------------|-----|--------|
| [#376856](../../../../raw/zendesk/shopify/376856.json) | UPS WorldEase | Shopify | To discuss |
| [#348049](../../../../raw/zendesk/shopify/348049.json) | USPS Scanform / EOD manifest | Shopify | Yet to pick |
| [#299137](../../../../raw/zendesk/shopify/299137.json) | USPS Ground Advantage Cubic service | Shopify | Yet to pick |
| [#369556](../../../../raw/zendesk/shopify/369556.json) | DHL Return service | Shopify | Yet to pick |
| [#379963](../../../../raw/zendesk/shopify/379963.json) | Royal Mail new services | Shopify | Yet to pick |
| #381046 | Delivro carrier | WooCommerce | Yet to pick |
| #379378 | Canpar listing | WooCommerce | Open |
| #302656 | Media Mail | WooCommerce | Backlog |
| [#306141](../../../../raw/zendesk/shopify/306141.json) | Avoid Saturday delivery (UPS) | Shopify | Yet to pick |

---

## Overflow: Misc / Feature Requests

Lower priority items to review during roadmap planning.

| Ticket | Issue | App |
|--------|-------|-----|
| [#354696](../../../../raw/zendesk/shopify/354696.json) | Include Ship To address in report | Shopify |
| [#360396](../../../../raw/zendesk/shopify/360396.json) | Carrier scan time in report (in progress) | Shopify |
| [#304193](../../../../raw/zendesk/shopify/304193.json) | Update order note in imported order | Shopify |
| #370219 | Payment type filter update | Shopify |
| [#338603](../../../../raw/zendesk/shopify/338603.json) | Subscription error on Safari | Shopify |
| [#377526](../../../../raw/zendesk/shopify/377526.json) | USPS address correction feature | Shopify |
| [#377113](../../../../raw/zendesk/shopify/377113.json) | USPS delivery buffer time | Shopify |
| #345572 | Delivery date display (BC FedEx) | BigCommerce |
| [#379098](../../../../raw/zendesk/shopify/379098.json) | FedEx REST signature option via CSV | Shopify |
| #309068 | Currency switcher compatibility | WooCommerce |

---

## Summary: Recommended Sequence

```
Week 1:   View 1 (Sprint Zero)  — deploy what's built, close 4 tickets
Week 1-2: View 2 (Fire Drill)   — AusPost + PostNord, deadline-driven
Sprint 1: View 3 (Trust)        — orders disappearing + data integrity
Sprint 2-4: View 4 (International) — CI/customs pipeline batch
Sprint 5-6: View 5 (Scale)      — variant search + bundled products
Quarterly: View 6 (Carriers)    — new integrations, roadmap planning
```

---

## Related Pages

- [Ground Zero Index](index.md)
- [Pain Ranking](pain-ranking.md)
- [By App](by-app.md)
- [Insights](insights.md)
- [Product Backlog](../../product/backlog.md) - Shopify-specific scored backlog
