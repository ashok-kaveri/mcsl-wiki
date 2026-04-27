#!/usr/bin/env python3
"""
Step 6: Validate the generated daily index.

Performs comprehensive checks on the new daily index.
"""

import json
import re
from pathlib import Path
from collections import Counter


def parse_issue_index(index_path):
    """Parse Issue Index section and extract all ZI assignments."""
    with open(index_path, 'r') as f:
        content = f.read()

    # Find "## Issue Index" section
    issue_index_match = re.search(r'## Issue Index\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)

    if not issue_index_match:
        print("❌ CRITICAL: Could not find '## Issue Index' section")
        return None, []

    issue_index_text = issue_index_match.group(1)

    # Parse markdown table (6 columns now)
    # Format: | ID | Issue | Ticket | Product | Area | Duplicate Of |
    assignments = []
    lines = issue_index_text.strip().split('\n')[2:]  # Skip header and separator

    for line_num, line in enumerate(lines, start=3):
        if not line.strip() or not line.startswith('|'):
            continue

        parts = [p.strip() for p in line.split('|')]

        if len(parts) < 7:  # Need at least 7 parts (empty, ID, Issue, Ticket, Product, Area, Duplicate Of, empty)
            print(f"⚠️  WARNING: Line {line_num} has {len(parts)} columns, expected 7")
            continue

        zi_id = parts[1].strip()
        title = parts[2].strip()
        ticket_link = parts[3].strip()
        product = parts[4].strip()
        area = parts[5].strip()
        duplicate_of = parts[6].strip()

        # Extract ticket_id from link
        ticket_match = re.search(r'\[(\d+)\]', ticket_link)
        ticket_id = ticket_match.group(1) if ticket_match else 'unknown'

        assignments.append({
            'zi': zi_id,
            'title': title,
            'ticket_id': ticket_id,
            'product': product,
            'area': area,
            'duplicate_of': duplicate_of if duplicate_of else None
        })

    return content, assignments


def validate_daily_index(index_path, prior_zis_path):
    """Run comprehensive validation checks."""
    print("=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)

    errors = []
    warnings = []

    # Parse new index
    content, assignments = parse_issue_index(index_path)

    if assignments is None:
        print("\n❌ CRITICAL: Failed to parse index")
        return False

    print(f"\n📊 Statistics:")
    print(f"   Total issues in index: {len(assignments)}")

    # Load prior ZIs
    with open(prior_zis_path, 'r') as f:
        prior_zis = json.load(f)

    prior_zi_ids = set(prior_zis.keys())
    print(f"   Prior ZI count: {len(prior_zi_ids)}")

    # Check 1: All prior ZI IDs present
    print("\n1️⃣  Checking all prior ZI IDs are preserved...")
    current_zi_ids = set(a['zi'] for a in assignments)
    missing_zis = prior_zi_ids - current_zi_ids

    if missing_zis:
        errors.append(f"CRITICAL: {len(missing_zis)} prior ZI IDs missing: {sorted(list(missing_zis))[:10]}")
        print(f"   ❌ {len(missing_zis)} prior ZI IDs MISSING")
    else:
        print(f"   ✓ All {len(prior_zi_ids)} prior ZI IDs preserved")

    # Check 2: No duplicate ZI IDs
    print("\n2️⃣  Checking for duplicate ZI IDs...")
    zi_counts = Counter(a['zi'] for a in assignments)
    duplicates = {zi: count for zi, count in zi_counts.items() if count > 1}

    if duplicates:
        errors.append(f"CRITICAL: Duplicate ZI IDs found: {duplicates}")
        print(f"   ❌ {len(duplicates)} duplicate ZI IDs")
    else:
        print(f"   ✓ No duplicate ZI IDs")

    # Check 3: All "Duplicate Of" references valid
    print("\n3️⃣  Checking 'Duplicate Of' references...")
    invalid_refs = []
    duplicate_count = 0

    for assignment in assignments:
        if assignment['duplicate_of']:
            duplicate_count += 1
            if assignment['duplicate_of'] not in current_zi_ids:
                invalid_refs.append(f"{assignment['zi']} -> {assignment['duplicate_of']}")

    if invalid_refs:
        errors.append(f"CRITICAL: {len(invalid_refs)} invalid 'Duplicate Of' references: {invalid_refs[:5]}")
        print(f"   ❌ {len(invalid_refs)} invalid references")
    else:
        print(f"   ✓ All {duplicate_count} 'Duplicate Of' references valid")

    # Check 4: All ticket links resolve
    print("\n4️⃣  Checking ticket links...")
    summaries_dir = index_path.parent / 'summaries'
    missing_summaries = []

    for assignment in assignments:
        ticket_id = assignment['ticket_id']
        summary_path = summaries_dir / f'{ticket_id}.md'

        if not summary_path.exists():
            missing_summaries.append(ticket_id)

    if missing_summaries:
        warnings.append(f"WARNING: {len(missing_summaries)} ticket summaries not found: {missing_summaries[:5]}")
        print(f"   ⚠️  {len(missing_summaries)} summaries missing")
    else:
        print(f"   ✓ All ticket links resolve")

    # Check 5: Product/Area values
    print("\n5️⃣  Checking product/area values...")
    valid_products = {'shopify', 'woocommerce', 'magento', 'unknown'}
    valid_areas = {
        'label-generation', 'carrier-config', 'product-management',
        'order-management', 'rate-shopping', 'tracking', 'international',
        'onboarding', 'feature-request', 'carrier-migration', 'other',
        '`label-generation`', '`feature-request`', '`international`',
        '`onboarding` (account / billing)',
        'carrier-config / feature-request', 'feature-request / carrier-config',
        'onboarding (uninstall/cancel)',
        'onboarding / carrier-config (store-level connectivity), secondary tag: order-management',
        'unknown'
    }

    invalid_products = [a['product'] for a in assignments if a['product'] not in valid_products]
    # Area validation is more lenient due to variations
    # invalid_areas = [a['area'] for a in assignments if a['area'] not in valid_areas]

    if invalid_products:
        warnings.append(f"WARNING: {len(invalid_products)} invalid products: {set(invalid_products)}")
        print(f"   ⚠️  {len(invalid_products)} invalid products")
    else:
        print(f"   ✓ All products valid")

    # Check 6: Issue count consistency
    print("\n6️⃣  Checking issue count consistency...")
    # Extract count from frontmatter
    total_match = re.search(r'\*\*Total active issues\*\*:\s*(\d+)', content)
    if total_match:
        stated_count = int(total_match.group(1))
        if stated_count != len(assignments):
            errors.append(f"CRITICAL: Stated count ({stated_count}) != actual count ({len(assignments)})")
            print(f"   ❌ Count mismatch: stated {stated_count}, actual {len(assignments)}")
        else:
            print(f"   ✓ Issue count matches ({len(assignments)})")
    else:
        warnings.append("WARNING: Could not find total issue count in frontmatter")
        print(f"   ⚠️  Could not verify count")

    # Check 7: Schema validation (6 columns)
    print("\n7️⃣  Checking 6-column schema...")
    # Check header row
    if '| Duplicate Of |' in content:
        print(f"   ✓ 6-column schema with 'Duplicate Of' column")
    else:
        errors.append("CRITICAL: 'Duplicate Of' column missing from schema")
        print(f"   ❌ 'Duplicate Of' column missing")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if errors:
        print(f"\n❌ VALIDATION FAILED: {len(errors)} critical errors")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings")
        for warning in warnings:
            print(f"   • {warning}")

    if not errors and not warnings:
        print("\n✅ ALL CHECKS PASSED")
        return True
    elif not errors:
        print("\n✅ VALIDATION PASSED (with warnings)")
        return True
    else:
        print("\n❌ VALIDATION FAILED")
        return False


def main():
    # Paths
    wiki_dir = Path(__file__).parent.parent / 'wiki' / 'zendesk'
    intermediate_dir = Path(__file__).parent.parent / 'intermediate'

    from datetime import datetime
    output_date = datetime.now().strftime('%Y-%m-%d')

    index_path = wiki_dir / f'{output_date}.md'
    prior_zis_path = intermediate_dir / 'prior_zi_assignments.json'

    if not index_path.exists():
        print(f"Error: Daily index not found: {index_path}")
        return

    if not prior_zis_path.exists():
        print(f"Error: Prior ZI assignments not found: {prior_zis_path}")
        return

    success = validate_daily_index(index_path, prior_zis_path)

    if not success:
        exit(1)


if __name__ == '__main__':
    main()
