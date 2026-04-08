---
title: "Establish Product Management Layer in Wiki"
category: product-decision
status: accepted
date: 2026-04-08
git_reference: b367ffe7e91f3fe5ccc496676bbfee860ed8c003
---

# Establish Product Management Layer in Wiki

## Context

The wiki had 45 pages covering architecture, modules, patterns, and operations, plus test coverage analysis (95 features, 58 Playwright tests). Raw sources included 24+ Zendesk tickets and a 24-sheet regression matrix. However, there was no structured way to:
- Synthesize signals from tickets, test gaps, and code complexity into priorities
- Track customer metrics per feature area
- Write feature stories with acceptance criteria linked to evidence
- Record product decisions with traceability

## Decision

Add a **source-driven product management layer** (`wiki/product/`) with:
1. **backlog.md** — scored work items with impact/effort/confidence framework
2. **insights.md** — aggregated signals from Zendesk themes, test gaps, code hotspots
3. **metrics.md** — customer health scorecard with pain index per feature area
4. **features/** — feature stories with user stories, acceptance criteria, cross-links
5. **decisions/** — this format, for recording product decisions
6. **releases/** — release notes with before/after metrics

**Delta-aware resync**: All pages use `git_reference` in frontmatter. On resync, `git diff <ref>..HEAD -- raw/` detects new tickets, changed tests, or updated sheets — only the delta is processed.

**Ticket categorization**: Tickets are grouped by product (e.g., Shopify MCSL) and feature area (onboarding, carrier-config, label-generation, etc.).

## Alternatives Considered

1. **Lightweight (backlog + release notes only)** — Rejected: doesn't leverage existing Zendesk/test data
2. **Full PM suite (roadmap, OKRs, epics, ceremonies)** — Deferred: can grow into this later, too heavy for initial setup
3. **External tool (Linear, Jira)** — Not chosen: loses the cross-linking advantage of having everything in one wiki

## Signals

- 52 open Zendesk tickets with 65% needing dev work (`dev_needed` tag)
- 0% test automation for Rate Shopping, Product Management, Carrier Migration
- FedEx migration creating time-sensitive pressure (4 tickets, trending up)
- 15 tickets tagged `to-do` representing acknowledged but unacted debt

## Consequences

- CLAUDE.md updated with PM workflows (triage, feature story, metrics refresh, release)
- New `wiki/product/` directory with 6 initial files
- Every resync now processes raw/ delta and updates product pages
- Ticket categorization by product enables future multi-product support
- Cross-linking rules ensure traceability between signals and decisions

## Related

- Backlog: [Product Backlog](../backlog.md)
- Insights: [Product Insights](../insights.md)
- Metrics: [Customer Metrics](../metrics.md)
- Feature: [FedEx REST Migration](../features/carrier-migration-fedex-rest.md)
