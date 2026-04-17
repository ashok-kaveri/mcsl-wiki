---
title: "Release MCSL 377"
category: product-release
tag: "MCSL 377"
tag_slug: MCSL-377
board_id: 69dd9134576a26fcb79b670d
delivery_board_id: 63e1e0414b6026c45be1087c
status: draft
last_synced: 2026-04-17T00:42:18Z
shipped_at: null
git_reference: 35f62ec0d649571624bfcdef66a88401c1b3af82
tickets_delta_on_last_sync: 0
cards_total: 28
cards_shipped: 0
cards_support_closed: 1
cards_open: 27
---

# Release MCSL 377

> **Status**: draft · **Last synced**: 2026-04-17 00:42 UTC · **Planning board**: [StoryLab](https://trello.com/b/d1xk25XH/storylab) · **Delivery board**: [ph-WIP](https://trello.com/b/PWKHwiCI)

## Summary

| State | Count |
|-------|-------|
| PROD (shipped) | 0 |
| Support Closed | 1 |
| QA READY | 16 |
| DEV | 10 |
| Open (not started) | 1 |
| **Total** | **28** |

## Legend (ph-WIP label → release state)

| State | ph-WIP label(s) |
|-------|-----------------|
| **PROD** | `SHIPPED`, `PROD` |
| **QA READY** | `QA_VERIFIED`, `QA Reported`, `Ready for QA`, `Dev Done` |
| **DEV** | `DEV` |
| **Open (not started)** | no state label on any matching ph-WIP card |
| **Support Closed** | StoryLab card has `SL: HANDLED_BY_SUPPORT` (overrides ph-WIP state) |

Classification uses the HIGHEST-precedence ph-WIP label across all ph-WIP cards matching the ticket. SL-copies in `SL <tag>: Iteration backlog` lanes are excluded unless they're the only match.

## Shipped (0)

_No shipped cards yet._

## Support Closed (1)

| ZI | Title | Ticket | Reason | Detail | Card |
|----|-------|--------|--------|--------|------|
| ZI-023 | DHL label address format | [#369556](../../zendesk/summaries/369556.md) | `—` | _(missing close-reason comment)_ | [SL](https://trello.com/c/UbjjIcB4) |

## Still Open (27)

### QA READY (16)

| ZI | Title | Ticket | Theme | ph-WIP Label | ph-WIP Lane | Card |
|----|-------|--------|-------|--------------|-------------|------|
| ZI-008 | Automatic day-of-week Saturday Delivery handling | [#306141](../../zendesk/summaries/306141.md) | Carrier Platform | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/8d4uLUZQ) |
| ZI-012 | End of Day manifest / SCAN sheet not available | [#348049](../../zendesk/summaries/348049.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/pjjqzZe4) |
| ZI-022 | DHL Freight Sweden Return Service not available | [#369556](../../zendesk/summaries/369556.md) | Carrier Platform | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/ecEn741m) |
| ZI-032 | Tax invoice printing on multiple pages | [#373991](../../zendesk/summaries/373991.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/mbUahMod) |
| ZI-033 | Box name on tax invoice or pick-list | [#373991](../../zendesk/summaries/373991.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/pjYyxlUE) |
| ZI-035 | Decimal precision on custom packing slip prices | [#374851](../../zendesk/summaries/374851.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/UguO3HAQ) |
| ZI-039 | Externally fulfilled orders appearing in open queue | [#377526](../../zendesk/summaries/377526.md) | Order & Product Data | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/kJXO8BHG) |
| ZI-041 | USPS address validation causing label failures | [#377526](../../zendesk/summaries/377526.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/A7C9e1aV) |
| ZI-043 | Packing slip sort helper | [#377526](../../zendesk/summaries/377526.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/fNuSAO9L) |
| ZI-048 | UPS domestic label Reference field enhancement | [#378511](../../zendesk/summaries/378511.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/fcGYo2Pp) |
| ZI-049 | Products with 100+ variants losing sync | [#378513](../../zendesk/summaries/378513.md) | Order & Product Data | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/z1RZJ6Gl) |
| ZI-051 | FedEx REST declared value exceeds limit | [#379042](../../zendesk/summaries/379042.md) | Carrier Platform | `QA_VERIFIED` | Ready For QA MCSL 376 | [SL](https://trello.com/c/YDKHYezv) |
| ZI-057 | RoyalMail48ParcelDailyRateService missing from app | [#379963](../../zendesk/summaries/379963.md) | Carrier Platform | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/BAxlyYd9) |
| ZI-067 | Cleanup button missing in new UI | [#381380](../../zendesk/summaries/381380.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/8VZqA06r) |
| ZI-069 | FedEx box dimensions not printed on labels after REST migration | [#382009](../../zendesk/summaries/382009.md) | Carrier Platform | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/uVkbgbro) |
| ZI-071 | Packing slip does not show selected package size | [#382009](../../zendesk/summaries/382009.md) | Label & Document Quality | `Dev Done` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/7CigGQwW) |

### DEV (10)

| ZI | Title | Ticket | Theme | ph-WIP Label | ph-WIP Lane | Card |
|----|-------|--------|-------|--------------|-------------|------|
| ZI-007 | Order notes not synced after import | [#304193](../../zendesk/summaries/304193.md) | Order & Product Data | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/fSyJAktE) |
| ZI-013 | Ship To Address City missing from Order Report | [#354696](../../zendesk/summaries/354696.md) | Order & Product Data | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/J4Uo4FUu) |
| ZI-015 | Declared/insured value resets after manual package edit | [#361776](../../zendesk/summaries/361776.md) | International & Customs | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/0tXMF3PT) |
| ZI-021 | Enhancement: minimum customs value floor | [#369144](../../zendesk/summaries/369144.md) | International & Customs | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/npsdp7FI) |
| ZI-024 | Incorrect declared value for 0-price items | [#370219](../../zendesk/summaries/370219.md) | Label & Document Quality | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/gTtIp8Lb) |
| ZI-025 | Shipping charges not included in declared value | [#370219](../../zendesk/summaries/370219.md) | Label & Document Quality | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/X5MCfc5O) |
| ZI-046 | Payment status filter | [#377574](../../zendesk/summaries/377574.md) | Order & Product Data | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/Kan6dYQ9) |
| ZI-058 | eParcel bulk label generation delay (8+ sec consistently) | [#380339](../../zendesk/summaries/380339.md) | Label & Document Quality | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/twgeW1TL) |
| ZI-060 | HS code editing at package level | [#380339](../../zendesk/summaries/380339.md) | International & Customs | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/BvWit7vw) |
| ZI-079 | Orders move to "Not to Ship" on refresh when OCU post-purchase upsell modifies t | [#382961](../../zendesk/summaries/382961.md) | Order & Product Data | `DEV` | SL MCSL 377: Iteration backlog | [SL](https://trello.com/c/DhGRTFDI) |

### Open (not started) (1)

| ZI | Title | Ticket | Theme | ph-WIP Lane (ref only) | Card |
|----|-------|--------|-------|-----------------------|------|
| ZI-018 | DPD services not appearing via EasyPost | [#366630](../../zendesk/summaries/366630.md) | Carrier Platform | (no ph-WIP match) | [SL](https://trello.com/c/lAs3ZtSn) |

## Notes

- Cards missing `[close-reason: ...]` comment: 1
- Cards with no ph-WIP correlation: 0
- Cards with multiple ph-WIP matches (picked highest-precedence state label): 27
- Cards Support Closed while also present on ph-WIP: 1

## Cross-Links

- [Backlog](../backlog.md)
- [Stories directory](../stories/)
- [Zendesk daily index 2026-04-16](../../zendesk/2026-04-16.md)
