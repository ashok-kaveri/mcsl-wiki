---
title: "Royal Mail Integration Requires 3PI Approval"
category: product-decision
status: proposed
date: 2026-04-15
git_reference: current
sources: [slack, zendesk]
---

# Royal Mail Integration Requires 3PI Approval

## Context

ZI-057 ([Ticket #379963](../../zendesk/summaries/379963.md)) reported that `RoyalMail48ParcelDailyRateService` is missing from the app. When the team investigated what's needed to test and ship a fix, they discovered significant integration constraints.

**Trigger**: QA team needed Royal Mail configured in EasyPost to test [Trello card #4129](https://trello.com/c/DxVXh1CF/4129).

## Finding

Royal Mail cannot be integrated directly via EasyPost. The integration path requires:

1. **OBA (Online Business Account)** — merchant must have an active OBA account with Royal Mail
2. **Posting Location ID** — specific to the merchant's account
3. **Rates Card** — merchant shares their OBA rates card with EasyPost team
4. **Royal Mail Approval** — EasyPost contacts Royal Mail to get approval and uploads the rates card

For **software providers** (like PluginHive/StorePep):
- Direct API access is **not freely available**
- Integration requires becoming an approved **3PI (Third Party Integrator)** or going through an approved partner like **Intersoft**
- No free production-ready API exists for multi-carrier SaaS platforms
- Applies to both **BYOA** (Bring Your Own Account) and **Reseller** models

**Previous attempt**: EasyPost was contacted in the past for test credentials but was unable to help.

## Decision

Explore the EasyPost route to access Royal Mail for testing. **Abhilash S** will contact EasyPost to request a test account and cc **Keerthi**.

## Alternatives Considered

| Option | Feasibility | Notes |
|--------|------------|-------|
| Direct Royal Mail API | ❌ Not viable | Requires 3PI approval, no free access |
| Intersoft partner route | ❓ Unknown | Approved partner infrastructure, needs investigation |
| EasyPost test account | 🔄 In progress | Previously declined, trying again |
| Mock/stub for testing | ⚠️ Partial | Could unblock QA but won't validate real integration |

## Signals

- **Zendesk**: [Ticket #379963](../../zendesk/summaries/379963.md) — customer (Billy, a90e3a-59.myshopify.com) blocked on RoyalMail48ParcelDailyRateService, SLA breached by 21+ days
- **ZI Issue**: ZI-057 — carrier-config area, pain 8/10
- **Trello**: [Card #4129](https://trello.com/c/DxVXh1CF/4129)
- **Slack**: [2026-04-15 discussion](../../../raw/slack/2026-04-15-royal-mail-easypost-integration.md)

## Consequences

1. **QA is blocked** — cannot test Royal Mail until EasyPost provides test credentials
2. **Customer resolution delayed** — ZI-057 fix cannot be validated without test environment
3. **May need partnership escalation** — if EasyPost can't help, Intersoft or direct Royal Mail 3PI approval required
4. **Architectural note** — Royal Mail integration is more complex than typical EasyPost carriers; onboarding docs should reflect this

## Related

- **ZI Story**: [ZI-057](../stories/ZI-057.md) — RoyalMail48ParcelDailyRateService missing
- **Backlog**: [Product Backlog](../backlog.md) — carrier-config cluster
- **Module**: [Carrier Configuration](../../modules/shipping/carrier-configuration.md)
- **Carrier List**: [Carrier Integrations](../../modules/shipping/carrier-integrations.md)
