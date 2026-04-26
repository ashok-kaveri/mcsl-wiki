## Blast Radius

- A single conceptual change should touch as few files as possible
- If a change requires edits in more than 3-4 files, first ask:
  "Is there a missing abstraction that would centralize this?"
- Prefer changing one owner over changing many consumers
- Shared logic belongs in utils/, config/, or middleware/ — not duplicated at call sites
- If adding a feature requires copy-pasting the same pattern in multiple places,
  create the abstraction first, then use it once

## When wide changes are acceptable
- Mechanical renames (variable, function, config key) with no logic change
- Automated reformatting or linting fixes
- Dependency upgrades that touch import paths
These are wide but low-risk. The rule targets logic duplication, not mechanical edits.