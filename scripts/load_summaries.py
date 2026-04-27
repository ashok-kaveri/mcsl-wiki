#!/usr/bin/env python3
"""
Step 2: Load all current summaries and extract open issues.

Reads all wiki/zendesk/summaries/*.md files and outputs intermediate/current_issues.json
"""

import json
import re
from pathlib import Path
from multiprocessing import Pool


def normalize_title(title):
    """Normalize issue title for duplicate detection."""
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value

    return frontmatter


def extract_open_issues(content):
    """Extract open issues from markdown content."""
    issues = []

    # Find "## Open Issues" section
    open_issues_match = re.search(r'## Open Issues\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)

    if not open_issues_match:
        return issues

    open_issues_text = open_issues_match.group(1)

    # Check for "No open issues" message
    if 'no open issues' in open_issues_text.lower():
        return issues

    # Match numbered list items (1. **Title** — description... Area: `area`. (Comment #N))
    issue_pattern = r'(\d+)\.\s+\*\*(.+?)\*\*\s+—\s+(.*?)(?=\n\d+\.|\Z)'

    for match in re.finditer(issue_pattern, open_issues_text, re.DOTALL):
        title = match.group(2).strip()
        description = match.group(3).strip()

        # Extract area tag
        area_match = re.search(r'Area:\s+`?([^.`]+)`?', description)
        area = area_match.group(1).strip() if area_match else 'other'

        # Extract severity
        severity_match = re.search(r'Severity:\s+([HML])', description)
        severity = severity_match.group(1) if severity_match else 'M'

        # Extract blocked-by
        blocked_match = re.search(r'Blocked:\s+([^.]+)', description)
        blocked_by = blocked_match.group(1).strip() if blocked_match else 'unknown'

        # Extract comment reference
        comment_match = re.search(r'Comment[s]?\s+#(\d+|[\d,\s#]+)', description)
        comment_ref = comment_match.group(1) if comment_match else 'unknown'

        issues.append({
            'title': title,
            'normalized_title': normalize_title(title),
            'area': area,
            'severity': severity,
            'blocked_by': blocked_by,
            'comment_ref': comment_ref
        })

    return issues


def process_summary_file(summary_path):
    """Process a single summary file and return ticket info with issues."""
    try:
        with open(summary_path, 'r') as f:
            content = f.read()

        # Parse frontmatter
        frontmatter = parse_frontmatter(content)

        ticket_id = frontmatter.get('ticket_id', summary_path.stem)
        product = frontmatter.get('product', 'unknown')
        status = frontmatter.get('status', 'unknown')

        # Extract open issues
        issues = extract_open_issues(content)

        return str(ticket_id), {
            'product': product,
            'status': status,
            'issues': issues
        }
    except Exception as e:
        print(f"Error processing {summary_path}: {e}")
        return None


def main():
    # Find all summary files
    summaries_dir = Path(__file__).parent.parent / 'wiki' / 'zendesk' / 'summaries'

    if not summaries_dir.exists():
        print(f"Error: Summaries directory not found: {summaries_dir}")
        return

    summary_files = sorted(summaries_dir.glob('*.md'))

    print(f"Loading {len(summary_files)} summary files...")

    # Process in parallel
    with Pool(8) as pool:
        results = pool.map(process_summary_file, summary_files)

    # Filter out None results and build dictionary
    current_issues = {}
    total_issues = 0

    for result in results:
        if result:
            ticket_id, ticket_info = result
            current_issues[ticket_id] = ticket_info
            total_issues += len(ticket_info['issues'])

    # Write output
    output_dir = Path(__file__).parent.parent / 'intermediate'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / 'current_issues.json'

    with open(output_path, 'w') as f:
        json.dump(current_issues, f, indent=2)

    print(f"✓ Loaded {len(current_issues)} tickets with {total_issues} total issues")
    print(f"✓ Wrote: {output_path}")


if __name__ == '__main__':
    main()
