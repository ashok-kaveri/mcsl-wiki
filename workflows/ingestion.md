# Ingestion Workflow

**Trigger**: "Ingest X", "document the Y module", "add the Z feature to the wiki"

## Steps

### 1. Read
Use Glob/Grep/Read to explore the specified files/directories.
- For a feature domain, read: routes, models, services, actions, reducers, components
- Start with main files, then follow into dependencies

### 2. Discuss
Before creating pages, share findings with the user:
- Core functionality?
- Complexity (LOC, file count)?
- Main dependencies?
- Surprises or interesting patterns?
- Any clarifying questions

### 3. Create/Update Pages
- Create new module pages or update existing ones (use `@templates/page.md`)
- Update architecture/pattern pages if affected
- Include `file:line` references for key code locations
- Record the git commit: `cd raw/<source> && git rev-parse HEAD`

### 4. Cross-link
- Add "Dependencies" linking to other modules
- Update "Referenced By" sections in dependent pages
- Link to relevant pattern/architecture pages

### 5. Update Index
Add new pages to `wiki/index.md` with one-line summaries.

### 6. Log
Append to `wiki/log.md`:

```markdown
## [YYYY-MM-DD HH:MM] ingest | <Feature/Module Name>
- Created: `path/to/new/page.md`
- Updated: `path/to/existing/page.md`
- Git reference: <commit-hash>
- Summary: Brief description of what was ingested
```

## Test Coverage Follow-up

After initial ingestion, ask: "Should I analyze test coverage for this module?" If yes, switch to @workflows/test-coverage.md and add a Test Coverage section to the module page.

## Example

See @workflows/examples.md — "Ingesting a Module with Test Coverage".
