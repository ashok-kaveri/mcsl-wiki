# Decision Record Template

Use for `wiki/product/decisions/YYYY-MM-DD-<slug>.md`.

```markdown
---
title: "<Decision Title>"
category: product-decision
status: <proposed|accepted|superseded>
date: YYYY-MM-DD
git_reference: <commit hash>
---

# <Decision Title>

## Context
What prompted this decision?

## Decision
What did we decide?

## Alternatives Considered
What else was on the table?

## Signals
- Zendesk: [ticket links]
- Slack: `raw/slack/YYYY-MM-DD-<slug>.md` (if applicable)
- Test gaps: [coverage data]
- Code complexity: [hotspot data]

## Consequences
What changes as a result?

## Related
- Feature: [link]
- Backlog: [link]
- Module: [link]
```
