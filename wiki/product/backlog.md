---
title: Product Backlog
category: product
sources: [zendesk, regression-scenarios, storepep-react, mcsl-test-automation]
status: partial
last_updated: 2026-04-08
git_reference: 635bf855126e7e91768e410f0432f56fd3216491
---

# Product Backlog

## Scoring Framework

| Dimension | Scale | Description |
|-----------|-------|-------------|
| Impact | 1-5 | Customer pain (ticket volume, severity) + revenue potential |
| Effort | 1-5 | Code complexity + test coverage needed (1=easy, 5=hard) |
| Confidence | 1-5 | How well we understand the problem (data quality) |
| Priority Score | (Impact × Confidence) / Effort | Higher = do first |

**Status values**: proposed → accepted → in-progress → shipped → closed

> **Last synced**: `git diff b367ffe..635bf85 -- raw/zendesk/shopify/` — processed all 54 tickets on disk.

---

## Active Backlog

### Shopify Multi Carrier Shipping Label App

| # | Item | Tickets | Impact | Effort | Confidence | Score | Key Sources | Feature Story | Status |
|---|------|---------|--------|--------|------------|-------|-------------|---------------|--------|
| 1 | Onboarding flow improvement | 10 | 4 | 3 | 5 | **6.7** | [#382935](../../raw/zendesk/shopify/382935.json), [#382795](../../raw/zendesk/shopify/382795.json), [#382393](../../raw/zendesk/shopify/382393.json), [#381283](../../raw/zendesk/shopify/381283.json), [#382999](../../raw/zendesk/shopify/382999.json) + 5 more | — | proposed |
| 2 | FedEx REST API migration | 5 | 5 | 4 | 5 | **6.3** | [#382982](../../raw/zendesk/shopify/382982.json), [#382425](../../raw/zendesk/shopify/382425.json), [#382188](../../raw/zendesk/shopify/382188.json), [#379042](../../raw/zendesk/shopify/379042.json), [#379098](../../raw/zendesk/shopify/379098.json) | [carrier-migration-fedex-rest](features/carrier-migration-fedex-rest.md) | proposed |
| 3 | Label generation reliability | 6 | 4 | 3 | 5 | **6.7** | [#381380](../../raw/zendesk/shopify/381380.json), [#372492](../../raw/zendesk/shopify/372492.json), [#370966](../../raw/zendesk/shopify/370966.json), [#374851](../../raw/zendesk/shopify/374851.json), [#373991](../../raw/zendesk/shopify/373991.json), [#338603](../../raw/zendesk/shopify/338603.json) | — | proposed |
| 4 | Carrier config & setup | 7 | 4 | 4 | 3 | **3.0** | [#381931](../../raw/zendesk/shopify/381931.json), [#379784](../../raw/zendesk/shopify/379784.json), [#377526](../../raw/zendesk/shopify/377526.json), [#376856](../../raw/zendesk/shopify/376856.json), [#373200](../../raw/zendesk/shopify/373200.json), [#365042](../../raw/zendesk/shopify/365042.json), [#306141](../../raw/zendesk/shopify/306141.json) | — | proposed |
| 5 | Australia Post API security update | 2 | 4 | 3 | 4 | **5.3** | [#383002](../../raw/zendesk/shopify/383002.json), [#382780](../../raw/zendesk/shopify/382780.json) | — | proposed |
| 6 | International / Dangerous goods | 3 | 3 | 4 | 3 | **2.3** | [#382694](../../raw/zendesk/shopify/382694.json), [#378176](../../raw/zendesk/shopify/378176.json), [#366630](../../raw/zendesk/shopify/366630.json) | — | proposed |
| 7 | Rate shopping reliability | 2 | 3 | 4 | 3 | **2.3** | [#379963](../../raw/zendesk/shopify/379963.json), [#374022](../../raw/zendesk/shopify/374022.json) | — | proposed |
| 8 | Order data / validation errors | 2 | 3 | 3 | 3 | **3.0** | [#382987](../../raw/zendesk/shopify/382987.json), [#379214](../../raw/zendesk/shopify/379214.json) | — | proposed |
| 9 | Return label failures | 1 | 3 | 3 | 4 | **4.0** | [#377217](../../raw/zendesk/shopify/377217.json) | — | proposed |
| 10 | Tracking status sync to Shopify | 1 | 2 | 3 | 3 | **2.0** | [#377574](../../raw/zendesk/shopify/377574.json) | — | proposed |

**Sorted by Priority Score** (highest first): #1 Onboarding (6.7) = #3 Label Gen (6.7) > #2 FedEx Migration (6.3) > #5 Australia Post (5.3) > #9 Returns (4.0) > #4/#8 Carrier/Order (3.0) > #6/#7 (2.3) > #10 (2.0)

---

## Uncategorized / Needs Triage

11 tickets with ambiguous subjects or multi-issue content. Review individually to assign to a backlog item.

| Ticket | Date | Subject | Tags |
|--------|------|---------|------|
| [#382009](../../raw/zendesk/shopify/382009.json) | 2026-04-01 | "I did the merge yesterday over a zoom call..." | high_agent_replies, system_email_notification_failure |
| [#381261](../../raw/zendesk/shopify/381261.json) | 2026-03-28 | "The app is almost setup. Could you call us..." | dev_needed, high_agent_replies, system_email_notification_failure |
| [#381087](../../raw/zendesk/shopify/381087.json) | 2026-03-26 | "Hi PH MultiCarrier Support Team, I am reaching out..." | dev_needed, high_agent_replies, system_email_notification_failure |
| [#380784](../../raw/zendesk/shopify/380784.json) | 2026-03-25 | "Please allow me to ask one more question..." | l3, web_widget |
| [#380339](../../raw/zendesk/shopify/380339.json) | 2026-03-23 | "Re: Just Checking In — How's Your Shipping Experience?" | other |
| [#378513](../../raw/zendesk/shopify/378513.json) | 2026-03-12 | "AGAIN ISSUES" | high_agent_replies, l3 |
| [#372492](../../raw/zendesk/shopify/372492.json) | 2026-02-04 | "Order 11622 - 20 items in total..." | dev_needed, other |
| [#369144](../../raw/zendesk/shopify/369144.json) | 2026-01-15 | "#112295" | dev_needed |
| [#361776](../../raw/zendesk/shopify/361776.json) | 2025-11-27 | "Re: We haven't heard from you since 48 hours" | dev_needed, high_agent_replies |
| [#360396](../../raw/zendesk/shopify/360396.json) | 2025-11-19 | "Could you please advise whether there is..." | dev_needed, in_progress |
| [#277997](../../raw/zendesk/shopify/277997.json) | 2024-07-05 | "I would like to follow up with regarding the status..." | back-log, dev_needed |

---

## Parking Lot — Feature Requests

Low urgency, customer-requested features not yet scored.

| Ticket | Date | Request | Notes |
|--------|------|---------|-------|
| [#348049](../../raw/zendesk/shopify/348049.json) | 2025-09-08 | End of Day manifest generation | Repeated ask, useful for carriers |
| [#354696](../../raw/zendesk/shopify/354696.json) | 2025-10-16 | Export large volume of tracking data | Data export feature |
| [#304193](../../raw/zendesk/shopify/304193.json) | 2024-12-16 | Roadmap feature suggestion (details in ticket) | Unread detail |

---

## Stale / Back-log

Long-open tickets (tagged `back-log`). May need closure review.

| Ticket | Open Since | Subject |
|--------|-----------|---------|
| [#218195](../../raw/zendesk/shopify/218195.json) | 2023-06-08 | Product Excel import issue |
| [#277997](../../raw/zendesk/shopify/277997.json) | 2024-07-05 | Follow-up on status (unclear) |
| [#306141](../../raw/zendesk/shopify/306141.json) | 2024-12-30 | Carrier config — app worked, now issue |

---

## Related Pages

- [Product Insights](insights.md) - Signal aggregation from all sources
- [Customer Metrics](metrics.md) - Per-feature health scores and pain index
- [Features & Test Coverage](../features.md) - Automation status
- [System Features Analysis](../system-features-analysis.md) - Code complexity and coverage gaps
