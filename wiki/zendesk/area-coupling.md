---
title: "ZI Area Coupling Map"
category: support
sources: [zendesk, storepep-react]
status: complete
last_updated: 2026-04-22
git_reference: 33ccc9c03bf518934340d3ee546fb0927edb5cbb
tickets_analyzed: 10
zi_issues_analyzed: 25
---

# ZI Area Coupling Map

Areas that co-appear in the same Zendesk ticket or backlog cluster signal coupled surfaces in user-reported failures — even if no direct import exists between them. Code co-change counts from [`coupling-map.md`](../architecture/coupling-map.md) confirm whether the coupling is also visible in git history.

**Tickets analyzed**: 10 | **ZI issues**: 25 | **As of**: 2026-04-22

---

## Area Co-Occurrence (by ticket)

Pairs ranked by frequency. Threshold: ≥2 co-occurring tickets.

| Pair | Co-Occurrences | Strength | Code Co-Changes | Sample Tickets | Sample ZIs |
|------|----------------|----------|-----------------|----------------|-----------|
| carrier-config ↔ feature-request | 2 | 🟢 Weak | — | #306141, #381046 | ZI-143, ZI-144, ZI-206 |

---

## Area Overlap by Backlog Cluster

Which areas appear together in the same cluster — indicates the engineering footprint spans both surfaces.

| Backlog Item | Areas in Cluster | ZI Count |
|---|---|---|
| — | — | — |

*No multi-area clusters found in backlog.*

---

## Blast-Radius Lookup

> If your card touches area X, also review area Y.

| If you touch… | Also check… | Evidence | Code co-changes |
|---|---|---|---|
| carrier-config | feature-request | 🟢 Weak (2 tickets) | no code overlap detected |
| carrier-config | international | 🟢 Weak (1 tickets) | no code overlap detected |
| carrier-config | rate-shopping | 🟢 Weak (1 tickets) | no code overlap detected |
| carrier-config | label-generation | 🟢 Weak (1 tickets) | no code overlap detected |
| feature-request | carrier-config | 🟢 Weak (2 tickets) | no code overlap detected |
| feature-request | label-generation | 🟢 Weak (1 tickets) | no code overlap detected |
| international | label-generation | 🟢 Weak (1 tickets) | no code overlap detected |
| international | carrier-config | 🟢 Weak (1 tickets) | no code overlap detected |
| international | rate-shopping | 🟢 Weak (1 tickets) | no code overlap detected |
| label-generation | international | 🟢 Weak (1 tickets) | no code overlap detected |
| label-generation | carrier-config | 🟢 Weak (1 tickets) | no code overlap detected |
| label-generation | feature-request | 🟢 Weak (1 tickets) | no code overlap detected |
| onboarding | order-management | 🟢 Weak (1 tickets) | no code overlap detected |
| onboarding | tracking | 🟢 Weak (1 tickets) | no code overlap detected |
| order-management | onboarding | 🟢 Weak (1 tickets) | no code overlap detected |
| order-management | other | 🟢 Weak (1 tickets) | no code overlap detected |
| order-management | unknown | 🟢 Weak (1 tickets) | no code overlap detected |
| other | order-management | 🟢 Weak (1 tickets) | no code overlap detected |
| rate-shopping | carrier-config | 🟢 Weak (1 tickets) | no code overlap detected |
| rate-shopping | international | 🟢 Weak (1 tickets) | no code overlap detected |
| tracking | onboarding | 🟢 Weak (1 tickets) | no code overlap detected |
| unknown | order-management | 🟢 Weak (1 tickets) | no code overlap detected |

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
- [Daily ZI Index](./2026-04-20.md)
