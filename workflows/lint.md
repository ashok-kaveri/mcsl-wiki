# Lint Workflow

**Trigger**: "Lint the wiki", "health-check the KB", "check for stale pages"

## Checks

### 1. Staleness
- Compare page metadata (`last_updated`, `git_reference`) with current git state
- Flag pages referencing old commits or marked outdated

### 2. Completeness
- Find pages marked `status: partial` or `status: needs-update`
- Identify major features/modules in the codebase not yet documented

### 3. Consistency
- Find orphan pages (no inbound links)
- Find broken links
- Check for contradictions between pages

### 4. Coverage Suggestions
- Important concepts that lack dedicated pages
- Missing cross-references

## Output

Summary report with actionable items grouped by check. Log in `wiki/log.md`:

```markdown
## [YYYY-MM-DD HH:MM] lint | Wiki health check
- Flagged N pages as potentially stale
- Identified N orphan pages
- Suggested N new topics to document
```
