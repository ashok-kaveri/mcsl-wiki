---
title: "Release MCSL 382"
category: product-release
tag: "MCSL 382"
tag_slug: mcsl-382
board_id: 63e1e0414b6026c45be1087c
lane_filter: "SL MCSL 382: Iteration backlog"
status: shipped
last_synced: 2026-06-26 12:51:35 UTC
shipped_at: 2026-06-26
git_reference: d74c967ff04c2c7841722af1a872248abcd04e74
tickets_delta_on_last_sync: 0
cards_total: 26
cards_shipped: 0
cards_ready_to_ship: 18
cards_high_risk: 0
cards_support_closed: 3
cards_unsupported_partnership: 0
cards_carrier_platform_issues: 0
cards_bug_reported: 0
cards_open: 0
cards_spill_over: 0
cards_traded_off: 2
---

# Release MCSL 382

> **Status**: SHIPPED 2026-06-26 · **Last synced**: 2026-06-26 12:51 UTC · **Board**: [ph-WIP](https://trello.com/b/63e1e0414b6026c45be1087c)

## Summary

| State | Count |
|-------|-------|
| Shipped | 0 |
| Ready To Ship | 18 |
| ⚠️ High Risk | 0 |
| Support Closed | 3 |
| Unsupported Partnership | 0 |
| Carrier Platform Issues | 0 |
| BUG REPORTED | 0 |
| QA READY | 0 |
| DEV | 3 |
| Open (not started) | 0 |
| Spill Over | 0 |
| Traded Off | 2 |
| **Total** | **26** |

**Note:** 26 unique cards (23 from the MCSL 382 lane + 3 from the MCSL 382p patch). The 3 patch cards are in-flight (DEV) hotfixes deployed on top of the shipped 382 release — tracked under *MCSL 382p — Patch Cards* and folded into the DEV bucket below (Source = `382p`).

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

## Ad-hoc Cards (3)

*Cards tagged for this release but not mirrored from a ZI issue — typically dev-initiated work (refactors, infra, platform changes).*

### PostNord UK (Direct Link) Integration

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/y8vhOmoA](https://trello.com/c/y8vhOmoA)

PR: [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3102](https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3102 "smartCard-inline")

### Migrate FedEx REST DG, Alcohol, and Battery shipment support from C2 to C39 and Implemented ORM_D dg shipment

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/U02MSYJq](https://trello.com/c/U02MSYJq)

PR - [https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3133](https://bitbucket.org/xadapter-cyd/storepep-react/pull-requests/3133 "smartCard-inline")

### Iteration 2: FedEx REST DG Close Manifest – Show Confirmation Modal Indicating Manifest Will Be Generated for All FedEx Ground Closed Label Orders

**State:** Ready To Ship  ·  **Card:** [https://trello.com/c/cPWaVpoL](https://trello.com/c/cPWaVpoL)

‌


## MCSL 382p — Patch Cards (3)

*Patch cards tagged `SL: MCSL 382p`, living in the MCSL 383 lane. Post-382 hotfixes deployed on top of the 382 release; folded into the DEV bucket below with Source = `382p`.*

### ZI-640 — FedEx REST: EU de minimis product identifiers [#396854]

**State:** DEV  ·  **Card:** [https://trello.com/c/yYU2DWPl](https://trello.com/c/yYU2DWPl)

EU de minimis exemption ends **2026-07-01**. FedEx REST now requires, per-commodity for EU B2C shipments (regardless of value): Merchant Product Identifier, Non-standardized Manufacturer Product Identifier, and Standardized Manufacturer Product Identifier (only if it exists). Lands in `storepepSAAS/server/src/shared/API/carriers/fedExRest/requestBuilder.js` → `commoditiesFor()` (L518-547), gated to EU ship-to; flows into `getCustomsClearanceDetailFor{Rates,Label}`. **Blocker:** exact FedEx REST field keys pending FedEx (Veena).

**Sources:** [Zendesk #396854](../../zendesk/summaries/396854.md) (ZI-640) · [Slack requirement](https://pluginhive.slack.com/archives/C0AREH9HNFQ/p1782713740039489)

### Amazon Shipping India — 30% Partner Discount Plans

**State:** DEV  ·  **Card:** [https://trello.com/c/VCSQGRaP](https://trello.com/c/VCSQGRaP)

Apply 30% discount on $29/$49/$99 plans for Amazon-referred partner stores. Discount applied at the Shopify charge layer in `shopify-multicarrier-app` — no storepep-react changes. Partner store allowlist via env var. *(Reassigned from MCSL 383 to the 382p patch.)*

**Sources:** [Requirement](https://pluginhive.slack.com/archives/C0AREH9HNFQ/p1782289838018159) · [Refund trigger — #396499](https://pluginhive.slack.com/archives/C02E15X8X0C/p1782298655255439)

### ZI-644 — FedEx REST registration fails for countries without zip codes [#396159]

**State:** DEV  ·  **Card:** [https://trello.com/c/cxuQOXYr](https://trello.com/c/cxuQOXYr)

FedEx REST carrier registration fails for ~65 countries where postal code is suppressed (`post: 'NONE'`). Two issues: (1) `Country.js:12` defines `DEFAULT_POST_CODE = 99999` as a number literal — carrier-registration-api JSON schema requires string, causing validation error; (2) Kuwait incorrectly marked as no-postal-code country. Fix: `String(zipCode)` coercion in `carrierRegistrationService.js:142` + remove `post: 'NONE'` from Kuwait in `countries.js:141`. *(Reassigned from MCSL 383 to the 382p patch.)*

**Sources:** [Zendesk #396159](../../zendesk/summaries/396159.md) (ZI-644) · [Story card](../stories/ZI-644.md)

## Shipped (0)

*No cards in this state*
## Ready To Ship (18)

| ZI | Ticket | Card |
|----|--------|------|
| None | N/A | [Link](https://trello.com/c/y8vhOmoA) |
| None | N/A | [Link](https://trello.com/c/U02MSYJq) |
| None | N/A | [Link](https://trello.com/c/cPWaVpoL) |
| ZI-564 | [#277997](../../zendesk/summaries/277997.md) | [Link](https://trello.com/c/LAMSPjle) |
| ZI-565 | [#277997](../../zendesk/summaries/277997.md) | [Link](https://trello.com/c/Ru0KCBpe) |
| ZI-566 | [#389467](../../zendesk/summaries/389467.md) | [Link](https://trello.com/c/QjX9VGza) |
| ZI-567 | [#392107](../../zendesk/summaries/392107.md) | [Link](https://trello.com/c/Tq9glgfV) |
| ZI-568 | [#389508](../../zendesk/summaries/389508.md) | [Link](https://trello.com/c/gao3uv58) |
| ZI-570 | [#391779](../../zendesk/summaries/391779.md) | [Link](https://trello.com/c/y7WZOyyq) |
| ZI-571 | [#389228](../../zendesk/summaries/389228.md) | [Link](https://trello.com/c/4C0YrEax) |
| ZI-574 | [#391952](../../zendesk/summaries/391952.md) | [Link](https://trello.com/c/ku0XyzRY) |
| ZI-575 | [#368959](../../zendesk/summaries/368959.md) | [Link](https://trello.com/c/edxRPQIk) |
| ZI-576 | [#391628](../../zendesk/summaries/391628.md) | [Link](https://trello.com/c/NpGp3YGF) |
| ZI-577 | [#390510](../../zendesk/summaries/390510.md) | [Link](https://trello.com/c/orILX1VP) |
| ZI-578 | [#388157](../../zendesk/summaries/388157.md) | [Link](https://trello.com/c/wKY8tIdq) |
| ZI-579 | [#389953](../../zendesk/summaries/389953.md) | [Link](https://trello.com/c/vUBfAgZv) |
| ZI-580 | [#379796](../../zendesk/summaries/379796.md) | [Link](https://trello.com/c/jrUM4aUB) |
| ZI-583 | [#381046](../../zendesk/summaries/381046.md) | [Link](https://trello.com/c/I8eVHiKr) |
## Support Closed (3)

| ZI | Ticket | Reason | Card |
|----|--------|--------|------|
| ZI-569 | [#389508](../../zendesk/summaries/389508.md) | pending | [Link](https://trello.com/c/8pvBqtrE) |
| ZI-572 | [#389228](../../zendesk/summaries/389228.md) | pending | [Link](https://trello.com/c/DHqqu0p0) |
| ZI-573 | [#391952](../../zendesk/summaries/391952.md) | pending | [Link](https://trello.com/c/Rg646lBM) |
## Unsupported Partnership (0)

*No cards in this state*
## Carrier Platform Issues (0)

*No cards in this state*
## BUG REPORTED (0)

*No cards in this state*

## Spill Over (0)

*No cards in this state*

## Traded Off (2)

| ZI | Ticket | Card |
|----|--------|------|
| ZI-581 | [#391159](../../zendesk/summaries/391159.md) | [Link](https://trello.com/c/dJYpGyep) |
| ZI-582 | [#375738](../../zendesk/summaries/375738.md) | [Link](https://trello.com/c/8MoVg84b) |

## Still Open (3)

### QA READY (0)

*No cards in this state*

### DEV (3)

| ZI | Ticket | Card | Source |
|----|--------|------|--------|
| ZI-640 | [#396854](../../zendesk/summaries/396854.md) | [Link](https://trello.com/c/yYU2DWPl) | 382p |
| ZI-644 | [#396159](../../zendesk/summaries/396159.md) | [Link](https://trello.com/c/cxuQOXYr) | 382p |
| — | Amazon Shipping India — 30% Partner Discount Plans | [Link](https://trello.com/c/VCSQGRaP) | 382p |

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
