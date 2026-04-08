---
title: Customer Metrics
category: product
sources: [zendesk, regression-scenarios, mcsl-test-automation]
status: partial
last_updated: 2026-04-08
git_reference: b367ffe7e91f3fe5ccc496676bbfee860ed8c003
---

# Customer Metrics

Per-feature health metrics for **Shopify Multi Carrier Shipping Label App**.

**Data source**: Zendesk API (status < pending, support_type = agent, product = shopify_multi_carrier_shipping_label_app)
**Total open tickets**: 52
**Last synced**: 2026-04-08

---

## Feature Health Scorecard

| Feature Area | Tickets | Trend | Top Issue | Automation | Regression Coverage | Health |
|-------------|---------|-------|-----------|-----------|-------------------|--------|
| Onboarding | 9 | -> | Installation / setup confusion | ~40% | TBD | 🔴 At Risk |
| Carrier Configuration | 8 | -> | Multi-carrier setup complexity | 7% | TBD | 🔴 At Risk |
| Label Generation | 6 | -> | Label creation failures, return labels | 100% | 85% | 🟡 Watch |
| Carrier Migration (FedEx) | 4 | up | FedEx SOAP->REST migration | 0% | 0% | 🔴 At Risk |
| Order Management | 3 | -> | Missing line items, validation errors | 58% | TBD | 🟡 Watch |
| Australia Post API | 2 | up | Security API update | 0% | 0% | 🔴 At Risk |
| International / DG | 2 | -> | Country of manufacture, DG API gaps | ~80% | TBD | 🟡 Watch |
| Rate Shopping | 2 | -> | Rate fetch failures, rate rules | 0% | 40% | 🔴 At Risk |
| Tracking | 1 | -> | Shopify status sync | 7% | TBD | 🟡 Watch |
| Feature Requests | 1 | -> | Various | - | - | - |
| Other / Multi-issue | 14 | -> | Mixed (see insights) | - | - | - |

**Health criteria**:
- 🟢 Healthy: < 2 tickets AND automation > 70%
- 🟡 Watch: 2-5 tickets OR automation 20-70%
- 🔴 At Risk: > 5 tickets OR automation < 20% OR trending up

---

## Ticket Volume by Feature Area

| Feature Area       | Total Open | With `dev_needed` | With `high_agent_replies` | With `l3` (escalated) | With `to-do` |
| ------------------ | ---------- | ----------------- | ------------------------- | --------------------- | ------------ |
| Onboarding         | 9          | 3                 | 1                         | 0                     | 3            |
| Carrier Config     | 8          | 5                 | 3                         | 2                     | 2            |
| Label Generation   | 6          | 5                 | 2                         | 0                     | 3            |
| Carrier Migration  | 4          | 2                 | 2                         | 2                     | 0            |
| Order Management   | 3          | 2                 | 0                         | 0                     | 1            |
| Australia Post     | 2          | 2                 | 0                         | 0                     | 0            |
| International / DG | 2          | 0                 | 1                         | 1                     | 0            |
| Rate Shopping      | 2          | 2                 | 1                         | 0                     | 1            |
| Tracking           | 1          | 0                 | 0                         | 1                     | 0            |
| Other              | 14         | 11                | 8                         | 1                     | 5            |
| **Total**          | **52**     | **34**            | **18**                    | **7**                 | **15**       |

---

## Customer Pain Index

Composite score: `(ticket_volume x severity_weight) / automation_confidence`

Severity weights: `dev_needed` = 2, `high_agent_replies` = 1.5, `l3` = 3, `to-do` = 1

| Feature Area       | Raw Pain | Automation Factor | Pain Index | Action Priority                 |
| ------------------ | -------- | ----------------- | ---------- | ------------------------------- |
| Carrier Config     | 26.0     | / 0.07 =          | **371**    | P0 - Immediate                  |
| Carrier Migration  | 17.0     | / 0.01 =          | **1700**   | P0 - Immediate (time-sensitive) |
| Onboarding         | 14.0     | / 0.40 =          | **35**     | P1 - High                       |
| Label Generation   | 16.5     | / 1.00 =          | **17**     | P2 - Medium                     |
| Rate Shopping      | 7.5      | / 0.01 =          | **750**    | P1 - High                       |
| Order Management   | 5.0      | / 0.58 =          | **9**      | P3 - Low                        |
| Australia Post     | 6.0      | / 0.01 =          | **600**    | P1 - High (emerging)            |
| International / DG | 5.5      | / 0.80 =          | **7**      | P3 - Low                        |
| Tracking           | 3.0      | / 0.07 =          | **43**     | P2 - Medium                     |

**Top 3 by Pain Index**: Carrier Migration (1700), Rate Shopping (750), Australia Post (600)

---

## New vs Recurring Issues

| Category | New (last 7 days) | Recurring (> 30 days old) | Oldest Open |
|----------|-------------------|--------------------------|-------------|
| Onboarding | 2 (#382935, #382795) | 3 (#369556, #370219, #299137) | 2024-11-18 |
| Carrier Config | 2 (#383002, #381087) | 2 (#306141, #373200) | 2024-12-30 |
| Label Generation | 0 | 3 (#370966, #374851, #338603) | 2025-07-16 |
| Carrier Migration | 1 (#382425) | 0 | 2026-03-12 |
| Other | 2 | 7 | 2023-06-08 (#218195) |

**Stale tickets** (> 6 months old): 7 tickets, oldest from 2023-06-08. These may need triage for closure or escalation.

---

## Ticket Age Distribution

| Age Bucket | Count | % |
|-----------|-------|---|
| < 7 days | 8 | 15% |
| 7-30 days | 18 | 35% |
| 30-90 days | 11 | 21% |
| 90-180 days | 6 | 12% |
| > 180 days | 9 | 17% |

**Median ticket age**: ~30 days
**Mean ticket age**: ~75 days (skewed by 9 stale tickets)

---

## Related Pages

- [Product Insights](insights.md) - Qualitative signal analysis
- [Product Backlog](backlog.md) - Prioritized action items
- [Features & Test Coverage](../features.md) - Automation percentages used in health calculations
- [System Features Analysis](../system-features-analysis.md) - Code complexity data
