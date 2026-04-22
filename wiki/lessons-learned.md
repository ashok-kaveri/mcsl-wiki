# Lessons Learned

This page captures lessons learned during wiki development and maintenance.

## 2026-04-22: yq available for YAML parsing

**Context**: While implementing the sl-iteration snapshot workflow, discovered that Python's `yaml` module is not available in the Claude Code environment.

**Lesson**: Use `yq` command-line tool for parsing YAML frontmatter instead of Python's yaml module.

**Example**:
```bash
# Extract frontmatter block first (markdown files have content after ---)
awk '/^---$/{if(++c==2) exit} c==1' wiki/product/releases/mcsl-377.md | \
  yq eval -o json '{"git_reference": .git_reference, "status": .status, "shipped_at": .shipped_at}'

# Or extract a single field
awk '/^---$/{if(++c==2) exit} c==1' wiki/product/releases/mcsl-377.md | \
  yq eval '.git_reference'
```

**Application**: All Python scripts that need to read/write YAML frontmatter in wiki markdown files should use subprocess calls to `yq` rather than importing yaml.
