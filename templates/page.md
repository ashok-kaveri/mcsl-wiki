# Standard Wiki Page Template

Use for pages in `wiki/architecture/`, `wiki/modules/`, `wiki/patterns/`, `wiki/operations/`.

```markdown
---
title: <Page Title>
category: <architecture|module|pattern|operation>
domain: <orders|shipping|products|etc.>   # if category=module
sources: [storepep-react, mcsl-test-automation]   # keys from sources.yaml
status: <complete|partial|needs-update>
last_updated: <YYYY-MM-DD>
git_reference: <commit hash or "current">
---

# <Page Title>

## Overview

Brief description of what this is and why it exists.

## Key Components

### Component/File 1
- **Location**: `path/to/file.js:123-456`
- **Purpose**: What it does
- **Key exports/APIs**: Main functions, classes, components

### Component/File 2
...

## Data Flow

How data moves through this module. Diagrams welcome (mermaid, ascii).

## Dependencies

This module depends on:
- [Module Name](../path/to/module.md) — why/how
- [External Package](link) — version, purpose

## Referenced By

This module is used by:
- [Module Name](../path/to/module.md) — how it's used

## Configuration

Environment variables, feature toggles, settings relevant to this module.

## Common Patterns

Typical usage, code examples if useful.

## Test Coverage

**Automated E2E Tests**: X Playwright tests covering this module

### Tested Features

| Feature | Test File | Status |
|---------|-----------|--------|
| Feature Name | `path/to/test.spec.ts` | ✅ Passing |

**Coverage**: X/Y features tested (Z%)

**Tested Scenarios**:
- ✅ Scenario 1
- ✅ Scenario 2

**Untested Scenarios**:
- ❌ Scenario 3

**Test Suite Location**: `raw/mcsl-test-automation/tests/<domain>/`
**Documentation**: See [Features List](../../features.md)

## Known Issues / Tech Debt

Areas for improvement, known bugs, planned refactoring.

## Related Pages

- [Related Topic](../path/to/topic.md)
- [Features List](../../features.md)
```
