---
title: Product Insights
category: product
sources: [zendesk, regression-scenarios, storepep-react, mcsl-test-automation]
status: partial
last_updated: 2026-04-08
git_reference: 635bf855126e7e91768e410f0432f56fd3216491
---

# Product Insights

Aggregated signals from Zendesk tickets, test coverage gaps, and code complexity. Updated on each resync via git delta detection.

---

## Zendesk Themes

### Shopify Multi Carrier Shipping Label App

**Source**: 54 tickets on disk (status < pending, support_type = agent) in `raw/zendesk/shopify/`
**Last synced**: 2026-04-08 (git_reference: 635bf85, processed via `git diff b367ffe..HEAD -- raw/zendesk/shopify/`)

| Theme | Ticket Count | Key Tickets | Affected Feature Area | Severity | Trend |
|-------|-------------|-------------|----------------------|----------|-------|
| Onboarding / Installation | 10 | [#382935](../../raw/zendesk/shopify/382935.json), [#382795](../../raw/zendesk/shopify/382795.json), [#382393](../../raw/zendesk/shopify/382393.json), [#382999](../../raw/zendesk/shopify/382999.json), [#381283](../../raw/zendesk/shopify/381283.json) + 5 more | [Platform Connectors](../modules/stores/platform-connectors.md) | High | -> |
| Carrier configuration & setup | 7 | [#381931](../../raw/zendesk/shopify/381931.json), [#379784](../../raw/zendesk/shopify/379784.json), [#377526](../../raw/zendesk/shopify/377526.json), [#376856](../../raw/zendesk/shopify/376856.json), [#373200](../../raw/zendesk/shopify/373200.json) + 2 more | [Carrier Configuration](../modules/shipping/carrier-configuration.md) | High | -> |
| Label generation failures | 6 | [#381380](../../raw/zendesk/shopify/381380.json), [#372492](../../raw/zendesk/shopify/372492.json), [#370966](../../raw/zendesk/shopify/370966.json), [#374851](../../raw/zendesk/shopify/374851.json), [#373991](../../raw/zendesk/shopify/373991.json), [#338603](../../raw/zendesk/shopify/338603.json) | [Label Generation](../modules/shipping/label-generation.md) | High | -> |
| FedEx REST API migration | 5 | [#382982](../../raw/zendesk/shopify/382982.json), [#382425](../../raw/zendesk/shopify/382425.json), [#382188](../../raw/zendesk/shopify/382188.json), [#379042](../../raw/zendesk/shopify/379042.json), [#379098](../../raw/zendesk/shopify/379098.json) | [Carrier Configuration](../modules/shipping/carrier-configuration.md) | Critical | up |
| International / Dangerous goods | 3 | [#382694](../../raw/zendesk/shopify/382694.json), [#378176](../../raw/zendesk/shopify/378176.json), [#366630](../../raw/zendesk/shopify/366630.json) | [Label Generation](../modules/shipping/label-generation.md) | Medium | -> |
| Order data / validation | 2 | [#382987](../../raw/zendesk/shopify/382987.json), [#379214](../../raw/zendesk/shopify/379214.json) | [Order Lifecycle](../modules/orders/order-lifecycle.md) | Medium | -> |
| Rate shopping problems | 2 | [#379963](../../raw/zendesk/shopify/379963.json), [#374022](../../raw/zendesk/shopify/374022.json) | [Rate Shopping](../modules/shipping/rate-shopping.md) | Medium | -> |
| Australia Post API changes | 2 | [#382780](../../raw/zendesk/shopify/382780.json), [#383002](../../raw/zendesk/shopify/383002.json) | [Carrier Configuration](../modules/shipping/carrier-configuration.md) | High | up (new) |
| Feature requests | 3 | [#348049](../../raw/zendesk/shopify/348049.json), [#354696](../../raw/zendesk/shopify/354696.json), [#304193](../../raw/zendesk/shopify/304193.json) | Various | Low | -> |
| Return label failures | 1 | [#377217](../../raw/zendesk/shopify/377217.json) | [Label Generation](../modules/shipping/label-generation.md) | Medium | -> |
| Tracking sync to Shopify | 1 | [#377574](../../raw/zendesk/shopify/377574.json) | [Shipment Tracking](../modules/shipping/shipment-tracking.md) | Low | -> |
| Product import | 1 | [#218195](../../raw/zendesk/shopify/218195.json) | [Product Management](../modules/products/product-management.md) | Low | -> (stale 2023) |
| Uncategorised / needs triage | 11 | [#382009](../../raw/zendesk/shopify/382009.json), [#381261](../../raw/zendesk/shopify/381261.json), [#381087](../../raw/zendesk/shopify/381087.json), [#378513](../../raw/zendesk/shopify/378513.json) + 7 more | Various | Varies | -> |

### Tag Distribution (operational signals)

| Tag | Count | Meaning |
|-----|-------|---------|
| `dev_needed` | 34 | Requires development work — 65% of open tickets need code changes |
| `high_agent_replies` | 18 | High back-and-forth — complex or poorly understood issues |
| `web_widget` | 18 | Submitted via web widget (not email) |
| `issues_with_setting_up_the_plugin` | 15 | Setup-related — overlaps heavily with onboarding theme |
| `to-do` | 15 | Acknowledged but not yet acted on |
| `l3` | 7 | Escalated to L3 support — needs engineering |
| `system_email_notification_failure` | 6 | Email notification system failing for these tickets |
| `back-log` | 3 | Explicitly backlogged |

### Key Signals

1. **65% of open tickets need dev work** (`dev_needed` on 34/52 tickets) — the support queue is not self-resolving; most issues require code changes
2. **Onboarding is the #1 volume driver** (9 tickets) — new customers are struggling with setup
3. **FedEx migration is time-sensitive** (4 tickets, trending up) — external deadline pressure from FedEx deprecating SOAP API
4. **Australia Post API security update is emerging** (2 tickets in last 2 days) — new external pressure
5. **35% of tickets have high agent replies** — indicates complex issues or knowledge gaps
6. **15 tickets tagged `to-do`** — acknowledged debt accumulating in the support queue

---

## Test Coverage Gaps (High Risk)

Features with low automation and high customer impact. Cross-referenced from [features.md](../features.md) and [system-features-analysis.md](../system-features-analysis.md).

| Feature               | Automation %  | Code Complexity                         | Zendesk Tickets      | Risk        | Recommended Action                     |
| --------------------- | ------------- | --------------------------------------- | -------------------- | ----------- | -------------------------------------- |
| Rate Shopping         | 0%            | High (300+ LOC)                         | 2 open               | 🔴 Critical | Automate core rate fetch flow          |
| Product Management    | 0%            | High (191-line model)                   | 2 open               | 🔴 Critical | Automate CRUD + import                 |
| Carrier Configuration | 7% (UPS only) | Very High (487-line model, 43 carriers) | 8 open + 4 migration | 🔴 Critical | Expand beyond UPS, add migration tests |
| Tracking              | 7% (1 test)   | Very High (6800 LOC mapper)             | 1 open               | 🟡 Watch    | Add status mapping + cron tests        |
| Auto Import           | 0%            | High                                    | 0 open               | 🟡 Watch    | Automate Shopify/WooCommerce import    |
| Bulk Actions          | 30% (12/40+)  | Very High (2500+ LOC)                   | 0 directly           | 🟡 Watch    | Expand action coverage                 |
| Reports               | 0%            | Medium                                  | 0 open               | 🟠 Low      | Defer unless tickets increase          |

---

## Code Hotspots

Files with high complexity that intersect with open tickets.

| File | LOC | Feature Area | Open Tickets | Last Wiki Update |
|------|-----|-------------|-------------|-----------------|
| `orders.js` (routes) | 2,139 | Order Management | 3 | 2026-04-07 |
| `storepepMappedTrackingStatus.js` | 6,800 | Tracking | 1 | 2026-04-08 |
| `bulkactionHelper.js` | 2,500+ | Bulk Actions | 0 | 2026-04-07 |
| FedEx request builder | 1,800+ | Label Generation | 4 (migration) | 2026-04-07 |
| Carrier model | 487 | Carrier Config | 8 | 2026-04-07 |

---

## Emerging Patterns

Signals too early to categorize but worth watching.

- **Australia Post API deprecation** — 2 tickets in 2 days (Apr 7-8). May escalate like FedEx migration if widespread.
- **PostNord service changes** — [#373200](../../raw/zendesk/shopify/373200.json) reports discontinued services. Could affect Nordic customers.
- **Email notification failures** — 6 tickets tagged `system_email_notification_failure`. May indicate a systemic infrastructure issue, not a feature bug.

---

## Related Pages

- [Product Backlog](backlog.md) - Prioritized work items derived from these insights
- [Customer Metrics](metrics.md) - Quantitative health scores per feature
- [Features & Test Coverage](../features.md) - Automation status
- [System Features Analysis](../system-features-analysis.md) - Complexity and scenario estimates
- [Ground Zero Triage](../support/ground-zero/index.md) - Cross-app view: 68 tickets across all StorePep products (Shopify + WooCommerce + BigCommerce + Magento)
- [Ground Zero Insights](../support/ground-zero/insights.md) - 7 cross-app insights including international shipping pain cluster and aging backlog risk
