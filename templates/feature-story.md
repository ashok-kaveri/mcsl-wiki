# Feature Story Template

Use for `wiki/product/features/<slug>.md`.

```markdown
---
title: <Feature Name>
category: product-feature
domain: <orders|shipping|etc.>
sources: [zendesk, regression-scenarios, storepep-react, mcsl-test-automation]
status: <proposed|accepted|in-progress|shipped>
last_updated: YYYY-MM-DD
git_reference: <commit hash>
---

# <Feature Name>

## Problem Statement

What problem does this solve? Who experiences it? How do we know?
- **Evidence**: [Ticket #XXXXX](../../zendesk/summaries/XXXXX.md) (ZI-001, ZI-002), ...
- **Affected users**: X customers reported this
- **Impact**: Revenue / reliability / UX

## User Stories

### Story 1: As a [role], I want [goal], so that [benefit]

**Acceptance Criteria**:
- [ ] Given [context], when [action], then [outcome]

**Regression Scenarios** (from regression matrix):
- Sheet row/scenario → maps to this story

### Story 2: ...

## Cross-Links

| Type | Link | Relationship |
|------|------|-------------|
| Wiki Module | [Module](../../modules/...) | Implementation details |
| Test Coverage | [Features](../../features.md#section) | Automation status |
| Zendesk Summary | [#XXXXX](../../zendesk/summaries/XXXXX.md) | Customer report |
| ZI Issues | ZI-001, ZI-002 | Open issues from daily index |
| Regression | Sheet rows | Manual test scenarios |
| Backlog | [Item](../backlog.md) | Prioritization |
| Decision | [Record](../decisions/...) | Why this approach |

## Customer Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| Related tickets (30d) | X | ↑/→/↓ |
| Automation confidence | 🟠 X% | |
| Regression coverage | X% | |

## Acceptance Sign-off

| Criteria | Status | Verified By |
|----------|--------|-------------|
| All stories implemented | ⬜ | |
| Regression scenarios pass | ⬜ | |
| No open P1/P2 tickets | ⬜ | |
| Automation confidence ≥ 70% | ⬜ | |
```
