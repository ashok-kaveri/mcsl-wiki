---
title: Ground Zero — Insights
category: support
sources: [stage-zero-analysis, zendesk]
status: complete
last_updated: 2026-04-10
git_reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
---

# Key Insights

Derived from the full 68-ticket cross-app triage. These patterns repeat across apps and carriers — fixing the underlying system issues addresses multiple tickets at once.

---

## Insight 1: International Shipping is the #1 Pain Cluster

**14 tickets (~20% of the backlog)** are about customs documents, commercial invoices, and CN22 forms.

**Common thread**: Data not appearing — or appearing incorrectly — on international documents. Affects UPS, FedEx, PostNord, DHL. This is not a per-carrier problem; it's a shared document generation pipeline problem.

**Specific gaps**:
- Decimal formatting errors on invoices (#374851)
- Missing declaration statements (#380784)
- Missing product descriptions on UPS invoice (#377795) and reference field (#378511)
- Discounted value not passed to CI (#374022, #376223)
- Box name not on invoice (#373991)
- Export declaration control per direction (forward vs return) (#377217, #381261)
- HS Code not editable at shipment level (#380339)
- CN22 + label on same physical page (#379784)

**Fix leverage**: Addressing the CI/customs document pipeline once would close or significantly progress ~8 tickets across 3 apps.

---

## Insight 2: Product Import Has a Scaling Ceiling

**11 tickets** about variant limits and product compatibility — the app cannot grow with merchants.

**Timeline of neglect**:
- **June 2023**: Variant search first requested (#218195) — **34 months** open
- **July 2024**: Bundled products (WooCommerce, #260001) — **25 months** open
- **July 2024**: Variant search follow-up (#277997) — **21 months** open
- **Dec 2024**: >250 variant limit requested (#365042)
- **Mar 2026**: >100 variant bug hit by 3 separate merchants (#378513, #381087, #379214) — now fixed, but root limit (250) remains

**Growth blocker**: Merchants who scale to larger catalogs hit hard limits. The app is self-selecting for small merchants by not fixing these.

**WooCommerce specifically**: Composite and bundled product compatibility missing — 3 tickets, 0 progress for 2+ years.

---

## Insight 3: Carrier API Migrations Create Recurring Fire Drills

Each major carrier API change generates **3-6 support tickets** and often a backlog of months.

**Historical pattern**:
- FedEx SOAP→REST: 6 tickets, still generating edge cases months later
- Australia Post security update: 2 tickets in a **single day** (Apr 7-8) — could escalate like FedEx if widespread
- PostNord service discontinuation: 2 tickets (Shopify + Magento)

**What's missing**: A proactive carrier migration playbook. Currently the team reacts ticket-by-ticket instead of shipping a coordinated migration flow before the carrier deadline hits.

**Upcoming risks**: Australia Post (urgent), PostNord (service changes), Royal Mail (new services needed).

---

## Insight 4: 38% of Tickets Are "Yet to Be Picked" — Accumulating Trust Debt

**26 of 68 tickets** have status "yet to be picked up." Many are feature requests that never get prioritized. This creates a compounding trust problem:

- Merchants who filed tickets months or years ago and got no resolution quietly churn
- Support agents re-explain why things aren't built, eroding confidence
- The queue grows faster than it resolves (new tickets arrive weekly, backlog doesn't shrink)

See [Aging Backlog](#aging-backlog) section below.

---

## Insight 5: Shopify Dominates But WooCommerce Has Distinct Gaps

- **72% of tickets are Shopify MCSL** — expected given install base
- **WooCommerce is 22%** but has a completely different pain profile: product compatibility (composite, bundled) and carrier coverage holes (Delivro, Canpar, Media Mail) that don't exist in Shopify
- **BigCommerce and Magento are quiet** at 4.5% and 1.5% — but may be underreported; small install base means merchants may not bother filing tickets

**Implication**: WooCommerce needs its own sprint view. The backlog is not just a Shopify backlog.

---

## Insight 6: "Orders Disappearing" is the Most Dangerous Single Ticket

**Ticket #382961**: Orders silently flip to "not to ship" state when a upsell product is purchased via One Click Upsell (post-purchase). Merchant has reported this happening multiple times ("again" in subject).

Even if this is an edge case affecting a small percentage of orders, **data integrity bugs are existential**. A merchant who loses orders through the app cannot trust it for their business.

**Treatment**: P0 regardless of frequency. Should be in the very next fix cycle.

---

## Insight 7: Dev-Completed Items Are Sitting Unshipped

**4 tickets** have "dev completed" status but remain open — their fixes exist in code but haven't reached merchants:

| Ticket | Fix | App |
|--------|-----|-----|
| [#382694](../../../../raw/zendesk/shopify/382694.json) | Country of origin fix for CN22 PostNord | Shopify |
| [#382425](../../../../raw/zendesk/shopify/382425.json) | FedEx REST: Avoid One Rate | Shopify |
| #368959 | Manifest enhancement | WooCommerce |
| #345572 | Display delivery date with service | BigCommerce |

These are **free wins** — zero additional dev effort required. The bottleneck is deployment or release coordination, not engineering.

---

## Aging Backlog

Tickets open longer than 12 months flagged as **trust risk**. These represent merchants waiting years for resolution.

| Ticket | Open Since | Issue | App | Age |
|--------|-----------|-------|-----|-----|
| [#218195](../../../../raw/zendesk/shopify/218195.json) | Jun 2023 | Variant search | Shopify | **34 months** |
| #260001 | Mar 2024 | Bundled product compatibility | WooCommerce | **25 months** |
| [#277997](../../../../raw/zendesk/shopify/277997.json) | Jul 2024 | Variant search (follow-up) | Shopify | **21 months** |
| #302656 | Dec 2024 | Media Mail integration | WooCommerce | **16 months** |
| [#304193](../../../../raw/zendesk/shopify/304193.json) | Dec 2024 | Update order note | Shopify | **16 months** |
| [#299137](../../../../raw/zendesk/shopify/299137.json) | Nov 2024 | USPS Ground Advantage Cubic | Shopify | **17 months** |
| [#306141](../../../../raw/zendesk/shopify/306141.json) | Dec 2024 | Avoid Saturday delivery | Shopify | **16 months** |

**Recommended action**: For each aging ticket, decide one of:
1. **Schedule** — assign to a sprint and commit to a fix date
2. **Close with explanation** — if won't build, tell the merchant why and close
3. **Feature request log** — move to a public roadmap item and close the ticket

Leaving them open indefinitely is the worst outcome for trust.

---

## Related Pages

- [Ground Zero Index](index.md)
- [Pain Ranking](pain-ranking.md)
- [By App](by-app.md)
- [Sprint Views](sprint-views.md)
- [Product Insights](../../product/insights.md) - Shopify-specific signals from Zendesk API
