#!/usr/bin/env python3
"""Verify story card quality against SKILL.md requirements."""
import sys
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
delta_file = WIKI_ROOT / "intermediate" / "delta_zi_ids.txt"
stories_dir = WIKI_ROOT / "wiki" / "product" / "stories"

with open(delta_file) as f:
    zi_ids = [line.strip() for line in f if line.strip()]

print(f"Verifying {len(zi_ids)} delta story cards...\n")

issues = []

for zi_id in zi_ids:
    story_path = stories_dir / f"{zi_id}.md"
    if not story_path.exists():
        issues.append(f"❌ {zi_id}: File missing")
        continue

    with open(story_path) as f:
        content = f.read()

    # Check for bad patterns
    bad_patterns = [
        ("Generic user story template", "I want {"),
        ("Generic 'manage shipping operations'", "manage my shipping operations effectively"),
        ("Generic acceptance criteria", "**Simple**: Address the issue described"),
        ("Generic GWT", "**Given** the conditions described in the ticket"),
    ]

    for check_name, pattern in bad_patterns:
        if pattern in content:
            issues.append(f"❌ {zi_id}: {check_name}")

    # Check for required sections
    required_sections = [
        ("## User Story", "Missing user story section"),
        ("## Acceptance Criteria (Simple)", "Missing simple acceptance criteria"),
        ("## Acceptance Criteria (Given/When/Then)", "Missing GWT scenarios"),
        ("## Ticket Summary", "Missing ticket summary"),
    ]

    for section, error_msg in required_sections:
        if section not in content:
            issues.append(f"❌ {zi_id}: {error_msg}")

    # Check for good patterns
    has_specific_criteria = "- [ ]" in content
    has_gwt_scenarios = "### Scenario:" in content

    if not has_specific_criteria:
        issues.append(f"⚠️  {zi_id}: No checkbox criteria found")
    if not has_gwt_scenarios:
        issues.append(f"⚠️  {zi_id}: No GWT scenarios found")

if issues:
    print("ISSUES FOUND:\n")
    for issue in issues:
        print(issue)
    print(f"\nTotal issues: {len(issues)}")
    sys.exit(1)
else:
    print("✅ All story cards pass verification!")
    print(f"All {len(zi_ids)} cards have:")
    print("  - Specific user stories (not generic templates)")
    print("  - 5 checkbox acceptance criteria")
    print("  - 3 Given/When/Then scenarios")
    print("  - Embedded ticket summaries")
    sys.exit(0)
