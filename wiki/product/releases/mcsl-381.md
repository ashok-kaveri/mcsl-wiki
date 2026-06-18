---
title: "Release MCSL 381"
category: product-release
tag: "MCSL 381"
tag_slug: mcsl-381
board_id: 63e1e0414b6026c45be1087c
lane_filter: "SL MCSL 381: Iteration backlog"
status: shipped
last_synced: 2026-06-18 02:35:06 UTC
shipped_at: 2026-06-16
git_reference: 09a6ae74c525274493b48801fb2832ca41335f48
tickets_delta_on_last_sync: 0
cards_total: 21
cards_shipped: 0
cards_ready_to_ship: 17
cards_high_risk: 0
cards_support_closed: 2
cards_unsupported_partnership: 0
cards_carrier_platform_issues: 2
cards_bug_reported: 0
cards_open: 0
cards_spill_over: 0
cards_traded_off: 0
---

# Release MCSL 381

> **Status**: SHIPPED 2026-06-16 · **Last synced**: 2026-06-18 02:35 UTC · **Board**: [ph-WIP](https://trello.com/b/63e1e0414b6026c45be1087c)

## Summary

| State | Count |
|-------|-------|
| Shipped | 0 |
| Ready To Ship | 17 |
| ⚠️ High Risk | 0 |
| Support Closed | 2 |
| Unsupported Partnership | 0 |
| Carrier Platform Issues | 2 |
| BUG REPORTED | 0 |
| QA READY | 0 |
| DEV | 0 |
| Open (not started) | 0 |
| Spill Over | 0 |
| Traded Off | 0 |
| **Total** | **21** |

**Note:** 21 unique cards (16 from MCSL 381 lane + 5 from MCSL 381p patch).

## Legend

- **Shipped** — deployed to production (ph-WIP SHIPPED or PROD label)
- **Ready To Ship** — QA verified, ready to deploy (ph-WIP QA_VERIFIED label)
- **⚠️ High Risk** — cards with `QA_VERIFIED` AND (`SL: Carrier Platform Issues` OR `Unsupported Partnership`) labels (possible use of customer credentials for verification; requires special care before shipping)
- **Support Closed** — StoryLab card has `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label; closed without code via support action
- **Unsupported Partnership** — StoryLab card has `Unsupported Partnership For Carrier` label (case-insensitive); unsupported carrier/partnership
- **Carrier Platform Issues** — external carrier/platform environment issues we cannot solve (ph-WIP `SL: Carrier Platform Issues` label)
- **BUG REPORTED** — code is in QA, bug has been reported (ph-WIP BUG REPORTED label)
- **QA READY** — code complete, in QA (ph-WIP Dev Done, Ready for QA, or QA Reported labels — NOT yet verified)
- **DEV** — active development (ph-WIP DEV label)
- **Open (not started)** — in product backlog but dev hasn't started (no ph-WIP state label)
- **Spill Over** — cards that could not be completed in the current iteration and were moved out (ph-WIP `Spill Over` label)
- **Traded Off** — cards intentionally dropped from this iteration to make room for new cards brought in (ph-WIP `Traded Off` label)

## Ad-hoc Cards (4)

*Cards tagged for this release but not mirrored from a ZI issue — typically dev-initiated work (refactors, infra, platform changes).*

### Carrier Integration India Post

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/WOth7i6s](https://trello.com/c/WOth7i6s)

PR (storepep):  [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3105](https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3105 "smartCard-inline")
PR (registration): [https://bitbucket.org/xadapter-cyd/carrier-registration-api/pull-requests/6](https://bitbucket.org/xadap…

### Carrier Integration DHL Express

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/LsmHAIIj](https://trello.com/c/LsmHAIIj)

PR (storepep): [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3107](https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3107 "smartCard-inline")
PR (registration): [https://bitbucket.org/xadapter-cyd/carrier-registration-api/pull-requests/5](https://bitbucket.org/xadapt…

### WSS: Add flat rate adjustment shown when carrier rates fail (ZD #394137)

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/NLqXsEv7](https://trello.com/c/NLqXsEv7)

PR: [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3092](https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3092 "smartCard-inline")

### MCSL- Fedex Rest Ground Close Manifest

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/LzjcrcUr](https://trello.com/c/LzjcrcUr)

PR - [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3115](https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3115 "‌")
PR(proxy) - [https://bitbucket.org/xadapter-cyd/ship-rate-track/pull-requests/7](https://bitbucket.org/xadapter-cyd/ship-rate-track/pull-requests/7 "s…


## MCSL 381p — Patch Cards (5)

*Patch cards tagged `SL: MCSL 381p`, living in the MCSL 382 lane. Included as part of the 381 release.*

### Shopify Billing Compliance and Trial Extension

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/AH1WgQnW](https://trello.com/c/AH1WgQnW)

### ZI-583 — Delivro post-integration: shipment field defaults [#381046]

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/I8eVHiKr](https://trello.com/c/I8eVHiKr)

*Includes sub-tasks:*
- Flat Rate Action Skipped When Carrier Rate Zeroed By Prior Adjustment — [https://trello.com/c/7hF2HxYq](https://trello.com/c/7hF2HxYq) (QA_VERIFIED)
- Delivro: Fall Back to BOITE when No Predefined Box is Selected — [https://trello.com/c/TuoIk6Ik](https://trello.com/c/TuoIk6Ik) (QA_VERIFIED)

### Release Label Batches

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/FSugx3SX](https://trello.com/c/FSugx3SX)

---

## Shipped (0)

*No cards in this state*
## Ready To Ship (17)

| ZI | Ticket | Card | Source |
|----|--------|------|--------|
| ZI-523 | [#387563](../../zendesk/summaries/387563.md) | [Link](https://trello.com/c/Gvyyzmdl) | 381 |
| ZI-524 | [#387563](../../zendesk/summaries/387563.md) | [Link](https://trello.com/c/Cr6MYVVL) | 381 |
| ZI-530 | [#387845](../../zendesk/summaries/387845.md) | [Link](https://trello.com/c/m9W9Cblq) | 381 |
| ZI-531 | [#389467](../../zendesk/summaries/389467.md) | [Link](https://trello.com/c/zZlGsCnW) | 381 |
| ZI-538 | [#390097](../../zendesk/summaries/390097.md) | [Link](https://trello.com/c/br0i86eK) | 381 |
| ZI-540 | [#390108](../../zendesk/summaries/390108.md) | [Link](https://trello.com/c/l1oRHe2L) | 381 |
| ZI-544 | [#390510](../../zendesk/summaries/390510.md) | [Link](https://trello.com/c/qaq1crm5) | 381 |
| ZI-552 | [#390467](../../zendesk/summaries/390467.md) | [Link](https://trello.com/c/nIGCc0JC) | 381 |
| — | India Post integration | [Link](https://trello.com/c/WOth7i6s) | 381 ad-hoc |
| — | DHL Express integration | [Link](https://trello.com/c/LsmHAIIj) | 381 ad-hoc |
| — | WSS flat rate fix (ZD #394137) | [Link](https://trello.com/c/NLqXsEv7) | 381 ad-hoc |
| — | FedEx REST Ground Close Manifest | [Link](https://trello.com/c/LzjcrcUr) | 381 ad-hoc |
| — | Shopify Billing Compliance | [Link](https://trello.com/c/AH1WgQnW) | 381p |
| — | Delivro: Flat Rate Zeroed fix | [Link](https://trello.com/c/7hF2HxYq) | 381p (ZI-583) |
| — | Delivro: BOITE fallback | [Link](https://trello.com/c/TuoIk6Ik) | 381p (ZI-583) |
| ZI-583 | Delivro post-integration [#381046](../../zendesk/summaries/381046.md) | [Link](https://trello.com/c/I8eVHiKr) | 381p |
| — | Release Label Batches | [Link](https://trello.com/c/FSugx3SX) | 381p |
## Support Closed (2)

| ZI | Ticket | Reason | Card |
|----|--------|--------|------|
| ZI-094 | [#377795](../../zendesk/summaries/377795.md) | pending | [Link](https://trello.com/c/UpgWKbYK) |
| ZI-103 | [#383757](../../zendesk/summaries/383757.md) | pending | [Link](https://trello.com/c/iQu7hqb9) |
## Unsupported Partnership (0)

*No cards in this state*
## Carrier Platform Issues (2)

| ZI | Ticket | Carriers | Card |
|----|--------|----------|------|
| ZI-534 | [#389897](../../zendesk/summaries/389897.md) | N/A | [Link](https://trello.com/c/GlcjLhTe) |
| ZI-542 | [#390108](../../zendesk/summaries/390108.md) | N/A | [Link](https://trello.com/c/WddCGKuY) |
## BUG REPORTED (0)

*No cards in this state*

## Spill Over (0)

*No cards in this state*

## Traded Off (0)

*No cards in this state*

## Still Open (0)

### QA READY (0)

*No cards in this state*

### DEV (0)

*No cards in this state*

### Open / not started (0)

*No cards in this state*

## Notes

- Cards missing `[close-reason: ...]` comment: TBD
- Cards with no ph-WIP correlation: 0 (all cards are on ph-WIP board)
- Cards dropped since last snapshot: 0
- Warnings: None

## Cross-Links

- [Backlog](../backlog.md)
- [Latest Zendesk daily index](../../zendesk/)
