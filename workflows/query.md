# Query Workflow

**Trigger**: User asks a question about the codebase.

## Steps

1. **Search index** — Read `wiki/index.md` to find relevant pages
2. **Read pages** — Read the relevant wiki pages
3. **Check source** — If the wiki info is insufficient or potentially stale, read the actual source files in `raw/`
4. **Answer** — Provide answer with citations (link to wiki pages and source files)
5. **File (optional)** — If the answer is substantial and reusable, ask user: "Should I file this as a wiki page?"

## Logging

Log substantive queries in `wiki/log.md`:

```markdown
## [YYYY-MM-DD HH:MM] query | <Question summary>
- Read: `path/to/relevant-page.md`
- Result: Brief answer summary with citation
- Pages created: <if applicable>
```
