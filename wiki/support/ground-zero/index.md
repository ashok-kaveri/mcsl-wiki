---
title: Ground Zero Support Triage
category: support
sources: [stage-zero-analysis, zendesk]
status: complete
last_updated: 2026-04-10
git_reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
---

# Ground Zero Support Triage

Cross-app analysis of **68 open Zendesk tickets** from the [stage-zero-analysis sheet](../../../raw/sheets/stage-zero-analysis.xlsx), covering all StorePep products. This is a one-time deep triage establishing the full pain landscape before sprint planning.

> **Source**: `raw/sheets/stage-zero-analysis.xlsx` (synced 2026-04-10)
> **Scope**: All apps — Shopify, WooCommerce, BigCommerce, Magento
> **Distinct from**: `raw/zendesk/shopify/` (Shopify-only, agent-filtered tickets from API)

---

## Ticket Inventory by App

| App | Tickets | % of Total |
|-----|---------|-----------|
| Shopify Multi Carrier Shipping Label App | 49 | 72% |
| WooCommerce Shipping Services | 15 | 22% |
| BigCommerce Multi Carrier / FedEx | 3 | 4.5% |
| Magento Multi Carrier Shipping Label App | 1 | 1.5% |
| **Total** | **68** | |

---

## Issue Categories at a Glance

| Tier | Category | Count | Pain Score |
|------|----------|-------|-----------|
| 🔴 Tier 1 | International Shipping / Customs / Invoices | 14 | 10/10 |
| 🔴 Tier 1 | Carrier Integration & Migration | 15 | 8/10 |
| 🔴 Tier 1 | Product Import / Variant Handling | 11 | 9/10 |
| 🟠 Tier 2 | FedEx-Specific Issues | 6 | 7/10 |
| 🟠 Tier 2 | Order Management | 3 | 7/10 |
| 🟠 Tier 2 | Label Generation & Management | 3 | 6/10 |
| 🟡 Tier 3 | Reporting & Data Export | 2 | 5/10 |
| 🟡 Tier 3 | Returns | 2 | 5/10 |
| 🟡 Tier 3 | Rate Shopping & Pricing | 3 | 4/10 |
| 🟢 Tier 4 | Onboarding / Support (handled) | 8 | 2/10 |
| 🟢 Tier 4 | Billing / Misc | 8 | 2/10 |

---

## Key Stats

| Metric | Value |
|--------|-------|
| Total open tickets | 68 |
| Tickets "yet to be picked" | 26 (38%) |
| Tickets with dev-completed but unshipped | 4 |
| Oldest open ticket | #218195 (June 2023 — 3 years) |
| Apps affected | 4 |
| Issue categories | 10 |
| Sprint views proposed | 6 |

---

## Sub-Pages

| Page | Description |
|------|-------------|
| [Pain Ranking](pain-ranking.md) | All 68 tickets in 4 tiers, ranked most → least painful |
| [By App](by-app.md) | Per-app breakdown with cross-app patterns |
| [Insights](insights.md) | 7 key insights + aging backlog risk analysis |
| [Sprint Views](sprint-views.md) | 6 actionable priority queues for sprint planning |

---

## Related Pages

- [Product Insights](../../product/insights.md) - Shopify-only signal aggregation (from Zendesk API)
- [Product Backlog](../../product/backlog.md) - Scored, prioritized Shopify work items
- [Customer Metrics](../../product/metrics.md) - Per-feature health scorecard
