#!/usr/bin/env python3
"""
Story Card Quality Validator

Validates story cards against objective quality criteria.
Returns exit code 0 if valid, 1 if validation fails.

Usage:
    python validate_story_card.py wiki/product/stories/ZI-475.md
"""

import sys
import re
from pathlib import Path


class ValidationError(Exception):
    """Raised when a validation check fails"""
    pass


def read_card(path):
    """Read story card markdown file"""
    with open(path, 'r') as f:
        return f.read()


def extract_section(content, section_name):
    """Extract a section from the markdown content"""
    # Use word boundary or space after ## to avoid matching ### scenario headers
    pattern = rf'## {re.escape(section_name)}(.*?)(?=^## |\n---\n|\Z)'
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else None


def validate_simple_ac(content):
    """Validate Simple Acceptance Criteria"""
    simple_ac = extract_section(content, 'Acceptance Criteria (Simple)')

    if not simple_ac:
        raise ValidationError("Missing 'Acceptance Criteria (Simple)' section")

    # Extract all checkbox items
    items = re.findall(r'- \[ \] (.+)', simple_ac)

    if len(items) < 3:
        raise ValidationError(f"Simple AC has {len(items)} items, requires at least 3")

    # Forbidden patterns (vague/generic criteria)
    forbidden = [
        (r'\bcustomer verified\b', "Customer verified"),
        (r'\broot cause fixed\b', "Root cause fixed"),
        (r'\bissue resolved\b', "Issue resolved"),
        (r'\bprevention added\b', "Prevention added"),
        (r'\bworks correctly\b', "works correctly"),
        (r'\bfixed\b(?!.*\w{20,})', "fixed (without sufficient context)"),
        (r'^.{1,20}$', "too brief (< 20 chars)"),
    ]

    violations = []
    for item in items:
        for pattern, msg in forbidden:
            if re.search(pattern, item, re.IGNORECASE):
                violations.append(f"  - '{item}' → {msg}")
                break

    if violations:
        raise ValidationError("Simple AC contains forbidden patterns:\n" + "\n".join(violations))


def validate_gwt_scenarios(content):
    """Validate Given/When/Then scenarios"""
    gwt = extract_section(content, 'Acceptance Criteria (Given/When/Then)')

    if not gwt:
        raise ValidationError("Missing 'Acceptance Criteria (Given/When/Then)' section")

    # Count scenarios
    scenarios = re.findall(r'### Scenario:', gwt)
    if len(scenarios) < 3:
        raise ValidationError(f"Found {len(scenarios)} GWT scenarios, requires minimum 3")

    # Extract each scenario
    scenario_blocks = re.split(r'### Scenario:', gwt)[1:]  # Skip before first scenario

    violations = []
    for i, scenario in enumerate(scenario_blocks, 1):
        # Check for Given/When/Then structure
        has_given = re.search(r'- \*\*Given\*\*(.+)', scenario)
        has_when = re.search(r'- \*\*When\*\*(.+)', scenario)
        has_then = re.search(r'- \*\*Then\*\*(.+)', scenario)

        if not has_given:
            violations.append(f"  Scenario {i}: Missing 'Given'")
        if not has_when:
            violations.append(f"  Scenario {i}: Missing 'When'")
        if not has_then:
            violations.append(f"  Scenario {i}: Missing 'Then'")

        # Check for forbidden generic patterns
        forbidden_patterns = [
            (r'conditions described in the ticket', "references ticket instead of being specific"),
            (r'the issue no longer occurs', "too vague - what specific behavior?"),
            (r'the fix is deployed', "deployment is not a user action"),
            (r'given the system', "generic system reference"),
            (r'given precondition', "placeholder text"),
        ]

        scenario_text = scenario.lower()
        for pattern, msg in forbidden_patterns:
            if re.search(pattern, scenario_text):
                violations.append(f"  Scenario {i}: {msg} ('{pattern}')")

        # Check minimum length for Given/When/Then
        if has_given and len(has_given.group(1).strip()) < 30:
            violations.append(f"  Scenario {i}: 'Given' clause too brief (< 30 chars)")
        if has_when and len(has_when.group(1).strip()) < 20:
            violations.append(f"  Scenario {i}: 'When' clause too brief (< 20 chars)")
        if has_then and len(has_then.group(1).strip()) < 30:
            violations.append(f"  Scenario {i}: 'Then' clause too brief (< 30 chars)")

    if violations:
        raise ValidationError("GWT scenarios have quality issues:\n" + "\n".join(violations))


def validate_user_story(content):
    """Validate User Story quality"""
    user_story = extract_section(content, 'User Story')

    if not user_story:
        raise ValidationError("Missing 'User Story' section")

    # Check for forbidden generic patterns
    violations = []

    forbidden = [
        (r'as a store owner\b', "Too generic - specify their situation (volume, plan, constraints)"),
        (r'as a merchant\b(?!.*\w{30,})', "Too generic - add context about their specific situation"),
        (r'as a user\b', "Way too generic - who specifically?"),
        (r'i want.*to be available', "Restates the feature, not the underlying need"),
        (r'i want.*to work', "Too vague - what capability do they actually need?"),
        (r'i want.*the bug fixed', "Not a user story - what's the underlying need?"),
        (r'so that.*uninterrupted', "Generic outcome - what specific consequence do they feel?"),
    ]

    for pattern, msg in forbidden:
        if re.search(pattern, user_story, re.IGNORECASE):
            violations.append(f"  - {msg}")

    # Check minimum length (good user stories explain context)
    if len(user_story) < 150:
        violations.append(f"  - User story too brief ({len(user_story)} chars, expect 150+)")

    if violations:
        raise ValidationError("User Story quality issues:\n" + "\n".join(violations))


def validate_title(content):
    """Validate card title from frontmatter"""
    # Extract title from YAML frontmatter
    title_match = re.search(r'^title:\s*["\'](.+?)["\']', content, re.MULTILINE)
    if not title_match:
        title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)

    if not title_match:
        raise ValidationError("Missing title in frontmatter")

    title = title_match.group(1).strip()

    violations = []

    # Check for question marks (titles shouldn't be questions)
    if '?' in title:
        violations.append("  - Title is a question (should be a statement)")

    # Check for generic wording
    generic_patterns = [
        (r'\bissue with\b', "Too generic - be specific about what's broken"),
        (r'\bproblem with\b', "Too generic - be specific"),
        (r'\bcustomer wants\b', "Not actionable - what needs to be done?"),
    ]

    for pattern, msg in generic_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            violations.append(f"  - {msg}")

    # Check length
    if len(title) > 120:
        violations.append(f"  - Title too long ({len(title)} chars, keep under 120)")

    if violations:
        raise ValidationError("Title quality issues:\n" + "\n".join(violations))


def validate_card(path):
    """Run all validation checks on a story card"""
    content = read_card(path)

    checks = [
        ("Title", validate_title),
        ("User Story", validate_user_story),
        ("Simple Acceptance Criteria", validate_simple_ac),
        ("Given/When/Then Scenarios", validate_gwt_scenarios),
    ]

    failed = []
    for check_name, check_fn in checks:
        try:
            check_fn(content)
            print(f"✓ {check_name}")
        except ValidationError as e:
            print(f"✗ {check_name}")
            print(f"  {e}")
            failed.append(check_name)

    return len(failed) == 0


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_story_card.py <path_to_card.md>")
        sys.exit(2)

    card_path = Path(sys.argv[1])

    if not card_path.exists():
        print(f"Error: File not found: {card_path}")
        sys.exit(2)

    print(f"\nValidating: {card_path.name}")
    print("=" * 60)

    is_valid = validate_card(card_path)

    print("=" * 60)
    if is_valid:
        print("✓ PASS - Card meets quality standards")
        sys.exit(0)
    else:
        print("✗ FAIL - Card has quality issues")
        sys.exit(1)


if __name__ == '__main__':
    main()
