---
title: "ZI Area Coupling Map"
category: support
sources: [zendesk, storepep-react]
status: complete
last_updated: 2026-04-28
git_reference: c40664e6
tickets_analyzed: 16
zi_issues_analyzed: 22
---

# ZI Area Coupling Map

Areas that co-appear in the same Zendesk ticket or backlog cluster signal coupled surfaces in user-reported failures — even if no direct import exists between them. Code co-change counts from [`coupling-map.md`](../architecture/coupling-map.md) confirm whether the coupling is also visible in git history.

**Tickets analyzed**: 16 | **ZI issues**: 22 | **As of**: 2026-04-28

---

## Area Co-Occurrence (by ticket)

Pairs ranked by frequency. Threshold: ≥2 co-occurring tickets.

| Pair | Co-Occurrences | Strength | Code Co-Changes | Sample Tickets | Sample ZIs |
|------|----------------|----------|-----------------|----------------|-----------|
| label-generation ↔ rate-shopping | 3 | 🟢 Weak | — | #[#385094](summaries/385094.md), #[#385211](summaries/385211.md), #[#385906](summaries/385906.md) | ZI-339, ZI-357, ZI-341 |

---

## Area Overlap by Backlog Cluster

Which areas appear together in the same cluster — indicates the engineering footprint spans both surfaces.

| Backlog Item | Areas in Cluster | ZI Count |
|---|---|---|
| (No cluster pairs found) | — | — |

---

## Blast-Radius Lookup

> If your card touches area X, also review area Y.

| If you touch… | Also check… | Evidence | Code co-changes |
|---|---|---|---|
| label-generation | rate-shopping | 🟢 Weak (3 tickets) | no code overlap detected |
| rate-shopping | label-generation | 🟢 Weak (3 tickets) | no code overlap detected |

---

## How to Read This

- **Co-Occurrences**: how many Zendesk tickets had open issues in *both* areas simultaneously
- **Code Co-Changes**: from [`coupling-map.md`](../architecture/coupling-map.md) — total co-change weight across the relevant code domains for that area pair. High = confirmed code coupling.
- **Strength**: 🔴 Strong ≥8 tickets · 🟡 Medium 4-7 · 🟢 Weak 2-3
- **A pair with high ticket co-occurrence AND high code co-changes** is a blast-radius risk: changes in one area almost certainly require reviewing the other.

---

## Related

- [Backlog](../product/backlog.md)
- [Code Co-Change Coupling Map](../architecture/coupling-map.md)
- [Daily ZI Index](2026-04-27.md)
