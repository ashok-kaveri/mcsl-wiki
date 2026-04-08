---
title: Product Backlog
category: product
sources: [zendesk, regression-scenarios, storepep-react, mcsl-test-automation]
status: partial
last_updated: 2026-04-08
git_reference: b367ffe7e91f3fe5ccc496676bbfee860ed8c003
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

## Active Backlog

### Shopify Multi Carrier Shipping Label App

| # | Item | Impact | Effort | Confidence | Score | Source | Feature | Status |
|---|------|--------|--------|------------|-------|--------|---------|--------|
| 1 | FedEx REST API migration support | 5 | 4 | 5 | 6.3 | zendesk: [#382425](../../raw/zendesk/382425.json), [#379042](../../raw/zendesk/379042.json), [#382188](../../raw/zendesk/382188.json), [#379098](../../raw/zendesk/379098.json) | [carrier-migration](features/carrier-migration.md) | proposed |
| 2 | Onboarding flow improvement | 4 | 3 | 5 | 6.7 | zendesk: 9 tickets (mcsl-installation tag) | - | proposed |
| 3 | Label generation error handling | 4 | 3 | 4 | 5.3 | zendesk: [#381380](../../raw/zendesk/381380.json), [#377217](../../raw/zendesk/377217.json), [#370966](../../raw/zendesk/370966.json) + 3 more | [label-generation](features/label-generation.md) | proposed |
| 4 | Carrier config & setup issues | 4 | 4 | 3 | 3.0 | zendesk: 8 tickets (carrier-config area) | - | proposed |
| 5 | Australia Post API security update | 4 | 3 | 4 | 5.3 | zendesk: [#382780](../../raw/zendesk/382780.json), [#383002](../../raw/zendesk/383002.json) | - | proposed |
| 6 | Dangerous goods / international compliance | 3 | 4 | 3 | 2.3 | zendesk: [#382694](../../raw/zendesk/382694.json), [#378176](../../raw/zendesk/378176.json) | - | proposed |
| 7 | Rate shopping reliability | 3 | 4 | 3 | 2.3 | zendesk: [#379963](../../raw/zendesk/379963.json), 0% test automation | - | proposed |
| 8 | Order data / line items issues | 3 | 3 | 3 | 3.0 | zendesk: [#382987](../../raw/zendesk/382987.json), [#379214](../../raw/zendesk/379214.json), [#372492](../../raw/zendesk/372492.json) | - | proposed |
| 9 | Return label failures | 3 | 3 | 4 | 4.0 | zendesk: [#377217](../../raw/zendesk/377217.json) | - | proposed |
| 10 | Tracking status sync to Shopify | 2 | 3 | 3 | 2.0 | zendesk: [#377574](../../raw/zendesk/377574.json), 7% test automation | - | proposed |

## Parking Lot

Items not yet scored or low-priority feature requests.

| Item | Source | Notes |
|------|--------|-------|
| Export large volume of tracking data | zendesk: [#354696](../../raw/zendesk/354696.json) | Feature request |
| Suggest feature: [details TBD] | zendesk: [#304193](../../raw/zendesk/304193.json) | Feature request |
| End of Day manifest generation | zendesk: [#348049](../../raw/zendesk/348049.json) | Feature request |

## Related Pages

- [Product Insights](insights.md) - Signal aggregation from all sources
- [Customer Metrics](metrics.md) - Per-feature health scores
- [Features & Test Coverage](../features.md) - Automation status
- [System Features Analysis](../system-features-analysis.md) - Code complexity and coverage gaps
