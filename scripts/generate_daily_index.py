#!/usr/bin/env python3
"""
Step 5: Generate daily index with 6-column schema.

Reads intermediate/zi_assignments.json and generates wiki/zendesk/2026-04-27.md
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def get_git_head():
    """Get current git HEAD commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return 'unknown'


def truncate_title(title, max_length=80):
    """Truncate title for readability and escape special characters."""
    # Replace newlines with spaces
    title = title.replace('\n', ' ').replace('\r', ' ')
    # Collapse multiple spaces
    title = ' '.join(title.split())
    # Escape pipe characters that would break markdown tables
    title = title.replace('|', '\\|')

    if len(title) <= max_length:
        return title
    return title[:max_length - 3] + '...'


def generate_daily_index(zi_assignments, output_date):
    """Generate daily index markdown content."""
    git_ref = get_git_head()

    # Aggregate statistics
    total_issues = len(zi_assignments)
    tickets_with_issues = len(set(a['ticket_id'] for a in zi_assignments))

    # Count by product
    by_product = defaultdict(lambda: {'issues': 0, 'tickets': set()})
    for assignment in zi_assignments:
        product = assignment['product']
        by_product[product]['issues'] += 1
        by_product[product]['tickets'].add(assignment['ticket_id'])

    # Count by area
    by_area = defaultdict(lambda: {'issues': 0, 'tickets': set()})
    for assignment in zi_assignments:
        area = assignment['area']
        by_area[area]['issues'] += 1
        by_area[area]['tickets'].add(assignment['ticket_id'])

    # Start building markdown
    lines = []

    # Frontmatter
    lines.append('---')
    lines.append(f'title: Zendesk Issue Extraction — {output_date}')
    lines.append('category: support')
    lines.append('sources: [zendesk]')
    lines.append('status: complete')
    lines.append(f'last_updated: {output_date}')
    lines.append(f'git_reference: {git_ref}')
    lines.append('---')
    lines.append('')

    # Title
    lines.append(f'# Zendesk Issue Extraction — {output_date}')
    lines.append('')
    lines.append(f'**Tickets with open issues**: {tickets_with_issues}')
    lines.append(f'**Total active issues**: {total_issues}')
    lines.append('')

    # Summary by Product
    lines.append('## Summary by Product')
    lines.append('| Product | Issues | Tickets |')
    lines.append('|---|---|---|')
    for product in sorted(by_product.keys()):
        stats = by_product[product]
        lines.append(f'| {product} | {stats["issues"]} | {len(stats["tickets"])} |')
    lines.append('')

    # Summary by Feature Area
    lines.append('## Summary by Feature Area')
    lines.append('| Feature Area | Issues | Tickets |')
    lines.append('|---|---|---|')
    for area in sorted(by_area.keys()):
        stats = by_area[area]
        lines.append(f'| {area} | {stats["issues"]} | {len(stats["tickets"])} |')
    lines.append('')

    # Issue Index (6-column schema with Duplicate Of)
    lines.append('## Issue Index')
    lines.append('| ID | Issue | Ticket | Product | Area | Duplicate Of |')
    lines.append('|---|---|---|---|---|---|')

    for assignment in zi_assignments:
        zi = assignment['zi']
        title = truncate_title(assignment['title'], 80)
        ticket_id = assignment['ticket_id']
        product = assignment['product']
        area = assignment['area']
        duplicate_of = assignment.get('duplicate_of') or ''

        ticket_link = f'[{ticket_id}](summaries/{ticket_id}.md)'

        lines.append(f'| {zi} | {title} | {ticket_link} | {product} | {area} | {duplicate_of} |')

    lines.append('')

    # Issues by Feature Area (6-column tables)
    lines.append('## Issues by Feature Area')
    lines.append('')

    for area in sorted(by_area.keys()):
        area_issues = [a for a in zi_assignments if a['area'] == area]

        lines.append(f'### {area} ({len(area_issues)} issues)')
        lines.append('')
        lines.append('| ID | Issue | Ticket | Product | Area | Duplicate Of |')
        lines.append('|---|---|---|---|---|---|')

        for assignment in area_issues:
            zi = assignment['zi']
            title = truncate_title(assignment['title'], 60)
            ticket_id = assignment['ticket_id']
            product = assignment['product']
            area_val = assignment['area']
            duplicate_of = assignment.get('duplicate_of') or ''

            ticket_link = f'[{ticket_id}](summaries/{ticket_id}.md)'

            lines.append(f'| {zi} | {title} | {ticket_link} | {product} | {area_val} | {duplicate_of} |')

        lines.append('')

    return '\n'.join(lines)


def main():
    # Load ZI assignments
    intermediate_dir = Path(__file__).parent.parent / 'intermediate'
    zi_assignments_path = intermediate_dir / 'zi_assignments.json'

    if not zi_assignments_path.exists():
        print(f"Error: {zi_assignments_path} not found. Run assign_zi_ids.py first.")
        return

    with open(zi_assignments_path, 'r') as f:
        zi_assignments = json.load(f)

    output_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Generating daily index for {output_date}...")
    print(f"Total issues: {len(zi_assignments)}")

    # Generate markdown
    markdown = generate_daily_index(zi_assignments, output_date)

    # Write output
    output_dir = Path(__file__).parent.parent / 'wiki' / 'zendesk'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f'{output_date}.md'

    with open(output_path, 'w') as f:
        f.write(markdown)

    print(f"✓ Generated: {output_path}")
    print(f"✓ Schema: 6-column with 'Duplicate Of' column")

    # Count duplicates
    duplicates = sum(1 for a in zi_assignments if a.get('duplicate_of'))
    print(f"✓ Duplicates tracked: {duplicates}")


if __name__ == '__main__':
    main()
