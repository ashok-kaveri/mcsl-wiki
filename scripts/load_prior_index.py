#!/usr/bin/env python3
"""
Step 3: Load prior ZI assignments from the previous daily index.

Reads wiki/zendesk/2026-04-20.md and outputs intermediate/prior_zi_assignments.json
"""

import json
import re
from pathlib import Path


def normalize_title(title):
    """Normalize issue title for duplicate detection."""
    title = title.lower()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def parse_prior_index(index_path):
    """Parse prior daily index and extract ZI assignments."""
    with open(index_path, 'r') as f:
        content = f.read()

    # Find "## Issue Index" section
    issue_index_match = re.search(r'## Issue Index\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)

    if not issue_index_match:
        print("Error: Could not find '## Issue Index' section")
        return {}

    issue_index_text = issue_index_match.group(1)

    # Parse markdown table
    # Format: | ID | Issue | Ticket | Product | Area |
    # Example: | ZI-136 | Variant SKU search not supported | [218195](summaries/218195.md) | unknown | product-management |

    zi_assignments = {}

    # Skip header row and separator row
    lines = issue_index_text.strip().split('\n')[2:]

    for line in lines:
        if not line.strip() or not line.startswith('|'):
            continue

        # Split by | and clean
        parts = [p.strip() for p in line.split('|')]

        if len(parts) < 6:  # Need at least 6 parts (empty, ID, Issue, Ticket, Product, Area, empty)
            continue

        zi_id = parts[1].strip()
        title = parts[2].strip()
        ticket_link = parts[3].strip()
        product = parts[4].strip()
        area = parts[5].strip()

        # Extract ticket_id from link [218195](summaries/218195.md)
        ticket_match = re.search(r'\[(\d+)\]', ticket_link)
        if not ticket_match:
            # Try alternative format
            ticket_match = re.search(r'(\d+)', ticket_link)

        ticket_id = ticket_match.group(1) if ticket_match else 'unknown'

        # Validate ZI format
        if not zi_id.startswith('ZI-'):
            continue

        zi_assignments[zi_id] = {
            'ticket_id': ticket_id,
            'title': title,
            'normalized_title': normalize_title(title),
            'product': product,
            'area': area,
            'referenced': False  # Track if this ZI is referenced in new issues
        }

    return zi_assignments


def main():
    # Load prior index
    prior_index_path = Path(__file__).parent.parent / 'wiki' / 'zendesk' / '2026-04-20.md'

    if not prior_index_path.exists():
        print(f"Error: Prior index not found: {prior_index_path}")
        return

    print(f"Loading prior index: {prior_index_path}")

    prior_zis = parse_prior_index(prior_index_path)

    # Validate
    if not prior_zis:
        print("Error: No ZI assignments found in prior index")
        return

    # Find highest ZI number
    max_zi = max(int(zi.split('-')[1]) for zi in prior_zis.keys())

    # Write output
    output_dir = Path(__file__).parent.parent / 'intermediate'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / 'prior_zi_assignments.json'

    with open(output_path, 'w') as f:
        json.dump(prior_zis, f, indent=2)

    print(f"✓ Loaded {len(prior_zis)} prior ZI assignments")
    print(f"✓ Highest ZI: ZI-{max_zi}")
    print(f"✓ Next ZI will be: ZI-{max_zi + 1}")
    print(f"✓ Wrote: {output_path}")


if __name__ == '__main__':
    main()
