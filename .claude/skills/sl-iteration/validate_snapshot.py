#!/usr/bin/env python3
"""
Validation script for sl-iteration snapshot command.

Verifies that the generated release file matches actual Trello state.
Run this after snapshot to catch state detection bugs.

Usage:
  python3 validate_snapshot.py MCSL-377
  python3 validate_snapshot.py "MCSL 377"

Exit codes:
  0 - All validations passed
  1 - Validation failures found
  2 - Error (missing file, API failure, etc.)
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

# Constants
PH_WIP_BOARD = "63e1e0414b6026c45be1087c"
TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")
TRELLO_TOKEN = os.environ.get("TRELLO_TOKEN")
BASE_URL = "https://api.trello.com/1"

# State label names in precedence order
STATE_LABEL_NAMES = [
    "SHIPPED",
    "PROD",
    "QA_VERIFIED",
    "QA Reported",
    "Ready for QA",
    "Dev Done",
    "DEV",
    "BUG REPORTED"
]

# State expectations
STATE_EXPECTATIONS = {
    'Shipped': ['SHIPPED', 'PROD'],
    'Ready To Ship': ['QA_VERIFIED'],
    'Support Closed': ['Closed by Support', 'Closed By Support', 'SL: Closed by Support', 'SL: Closed By Support'],
    'Unsupported Partnership': ['Unsupported Partnership For Carrier'],
    'QA READY': ['Dev Done', 'Ready for QA', 'QA Reported'],
    'DEV': ['DEV'],
    'BUG REPORTED': ['BUG REPORTED'],
    'Open (not started)': []  # No state labels
}

def fetch_json(url):
    """Fetch JSON from Trello API using curl."""
    auth = f"key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    full_url = f"{url}?{auth}" if "?" not in url else f"{url}&{auth}"
    result = subprocess.run(
        ["curl", "-s", full_url],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)

def parse_release_file(tag_slug):
    """Parse the release file and extract counts and cards."""
    release_file = Path(f"wiki/product/releases/{tag_slug}.md")

    if not release_file.exists():
        raise Exception(f"Release file not found: {release_file}")

    with open(release_file) as f:
        content = f.read()

    # Extract frontmatter
    if not content.startswith('---\n'):
        raise Exception("Invalid release file: missing frontmatter")

    end_marker = content.find('\n---\n', 4)
    if end_marker == -1:
        raise Exception("Invalid release file: malformed frontmatter")

    frontmatter_text = content[4:end_marker]
    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Extract state counts from frontmatter
    counts_from_fm = {
        'cards_total': int(frontmatter.get('cards_total', 0)),
        'cards_shipped': int(frontmatter.get('cards_shipped', 0)),
        'cards_ready_to_ship': int(frontmatter.get('cards_ready_to_ship', 0)),
        'cards_support_closed': int(frontmatter.get('cards_support_closed', 0)),
        'cards_unsupported_partnership': int(frontmatter.get('cards_unsupported_partnership', 0)),
        'cards_bug_reported': int(frontmatter.get('cards_bug_reported', 0)),
        'cards_open': int(frontmatter.get('cards_open', 0)),
    }

    # Extract state counts from Summary table
    summary_match = re.search(r'## Summary\n\n.*?\n((?:\|.*?\n)+)', content, re.DOTALL)
    if not summary_match:
        raise Exception("Could not find Summary table in release file")

    summary_table = summary_match.group(1)
    counts_from_table = {}

    for line in summary_table.split('\n'):
        if '|' in line and 'State' not in line and '---' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 2:
                state = parts[0].replace('*', '').strip()  # Remove bold markers from state name
                count_str = parts[1].replace('*', '').strip()  # Remove bold markers from count
                try:
                    count = int(count_str)
                    counts_from_table[state] = count
                except ValueError:
                    pass

    # Extract card URLs from each section
    cards_by_state = defaultdict(list)

    # Parse each state section
    sections = [
        ('Shipped', r'## Shipped \(\d+\)(.*?)(?=##|$)'),
        ('Ready To Ship', r'## Ready To Ship \(\d+\)(.*?)(?=##|$)'),
        ('Support Closed', r'## Support Closed \(\d+\)(.*?)(?=##|$)'),
        ('Unsupported Partnership', r'## Unsupported Partnership \(\d+\)(.*?)(?=##|$)'),
        ('BUG REPORTED', r'## BUG REPORTED \(\d+\)(.*?)(?=##|$)'),
        ('QA READY', r'### QA READY \(\d+\)(.*?)(?=###|##|$)'),
        ('DEV', r'### DEV \(\d+\)(.*?)(?=###|##|$)'),
        ('Open (not started)', r'### Open / not started \(\d+\)(.*?)(?=###|##|$)'),
    ]

    for state, pattern in sections:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section_text = match.group(1)
            # Extract Trello URLs
            urls = re.findall(r'https://trello\.com/c/([a-zA-Z0-9]+)', section_text)
            cards_by_state[state].extend(urls)

    return {
        'frontmatter': frontmatter,
        'counts_fm': counts_from_fm,
        'counts_table': counts_from_table,
        'cards_by_state': cards_by_state,
        'board_id': frontmatter.get('board_id'),
        'lane_filter': frontmatter.get('lane_filter', 'null').strip('"')
    }

def fetch_labels_from_board(board_id):
    """Fetch all labels from a board."""
    url = f"{BASE_URL}/boards/{board_id}/labels"
    params = "fields=name,color,id&limit=1000"
    return fetch_json(f"{url}?{params}")

def build_state_label_map(labels):
    """Build {state_name: set(label_ids)} map."""
    state_label_map = {}

    for state_name in STATE_LABEL_NAMES:
        matching_labels = [
            lbl for lbl in labels
            if lbl['name'].strip().lower() == state_name.lower()
        ]
        label_ids = {lbl['id'] for lbl in matching_labels}
        state_label_map[state_name] = label_ids

    return state_label_map

def fetch_card_details(card_shortlink):
    """Fetch full card details including labels."""
    url = f"{BASE_URL}/cards/{card_shortlink}"
    params = "fields=name,idLabels,labels,shortUrl"
    return fetch_json(f"{url}?{params}")

def detect_state_from_labels(card_labels, state_label_map):
    """Detect state from card's labels."""
    card_label_ids = {lbl['id'] for lbl in card_labels}
    card_label_names = {lbl['name'] for lbl in card_labels}

    # Walk state precedence order
    for state_name in STATE_LABEL_NAMES:
        label_ids = state_label_map.get(state_name, set())
        if card_label_ids & label_ids:
            # Found a matching state label
            # Coarsen to report bucket
            if state_name in ['SHIPPED', 'PROD']:
                return 'Shipped', state_name, card_label_names
            elif state_name == 'QA_VERIFIED':
                return 'Ready To Ship', state_name, card_label_names
            elif state_name in ['QA Reported', 'Ready for QA', 'Dev Done']:
                return 'QA READY', state_name, card_label_names
            elif state_name == 'DEV':
                return 'DEV', state_name, card_label_names
            elif state_name == 'BUG REPORTED':
                return 'BUG REPORTED', state_name, card_label_names

    return 'Open (not started)', None, card_label_names

def validate_snapshot(tag):
    """Main validation function."""
    print("=" * 70)
    print(f"VALIDATE SNAPSHOT: {tag}")
    print("=" * 70)

    # Convert tag to slug
    tag_slug = tag.replace(' ', '-')

    # Step 1: Parse release file
    print(f"\nStep 1: Parsing release file wiki/product/releases/{tag_slug}.md...")
    try:
        release_data = parse_release_file(tag_slug)
        print(f"  ✓ Release file parsed")
        print(f"  ✓ Board: {release_data['board_id']}")
        print(f"  ✓ Lane filter: {release_data['lane_filter']}")
        print(f"  ✓ Total cards in file: {release_data['counts_fm']['cards_total']}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return 2

    # Step 2: Fetch labels from board
    print(f"\nStep 2: Fetching labels from board {release_data['board_id']}...")
    try:
        labels = fetch_labels_from_board(release_data['board_id'])
        state_label_map = build_state_label_map(labels)
        print(f"  ✓ Fetched {len(labels)} labels")

        # Validate critical labels exist
        critical_missing = []
        for state in ['SHIPPED', 'PROD', 'QA_VERIFIED', 'Dev Done', 'DEV']:
            if not state_label_map.get(state):
                critical_missing.append(state)

        if critical_missing:
            print(f"  ❌ CRITICAL: Missing state labels: {critical_missing}")
            return 2
        else:
            print(f"  ✓ All critical state labels found")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return 2

    # Step 3: Sample cards and verify against Trello
    print(f"\nStep 3: Verifying sample cards against live Trello state...")

    mismatches = []
    total_checked = 0

    for state, card_shortlinks in release_data['cards_by_state'].items():
        if not card_shortlinks:
            continue

        # Check up to 3 cards from each state
        sample = card_shortlinks[:3]

        for shortlink in sample:
            total_checked += 1
            try:
                card = fetch_card_details(shortlink)
                detected_state, detected_label, label_names = detect_state_from_labels(
                    card['labels'], state_label_map
                )

                if detected_state != state:
                    mismatches.append({
                        'card_name': card['name'][:60],
                        'card_url': card['shortUrl'],
                        'expected_state': state,
                        'actual_state': detected_state,
                        'actual_labels': list(label_names)
                    })
                    print(f"  ❌ {shortlink}: Expected {state}, got {detected_state}")
                    print(f"     Labels: {list(label_names)}")
                else:
                    print(f"  ✓ {shortlink}: {state} (label: {detected_label})")
            except Exception as e:
                print(f"  ⚠️  {shortlink}: Could not fetch - {e}")

    # Step 4: Validate count consistency
    print(f"\nStep 4: Validating count consistency...")

    count_mismatches = []

    # Compare frontmatter counts vs table counts
    fm_shipped = release_data['counts_fm']['cards_shipped']
    fm_ready = release_data['counts_fm']['cards_ready_to_ship']
    fm_support_closed = release_data['counts_fm']['cards_support_closed']
    fm_unsupported = release_data['counts_fm']['cards_unsupported_partnership']
    fm_total = release_data['counts_fm']['cards_total']

    table_shipped = release_data['counts_table'].get('Shipped', 0)
    table_ready = release_data['counts_table'].get('Ready To Ship', 0)
    table_support_closed = release_data['counts_table'].get('Support Closed', 0)
    table_unsupported = release_data['counts_table'].get('Unsupported Partnership', 0)
    table_total = release_data['counts_table'].get('Total', 0)

    if fm_shipped != table_shipped:
        count_mismatches.append(f"Shipped: frontmatter={fm_shipped}, table={table_shipped}")

    if fm_ready != table_ready:
        count_mismatches.append(f"Ready To Ship: frontmatter={fm_ready}, table={table_ready}")

    if fm_support_closed != table_support_closed:
        count_mismatches.append(f"Support Closed: frontmatter={fm_support_closed}, table={table_support_closed}")

    if fm_unsupported != table_unsupported:
        count_mismatches.append(f"Unsupported Partnership: frontmatter={fm_unsupported}, table={table_unsupported}")

    if fm_total != table_total:
        count_mismatches.append(f"Total: frontmatter={fm_total}, table={table_total}")

    if count_mismatches:
        print("  ❌ Count mismatches between frontmatter and table:")
        for mismatch in count_mismatches:
            print(f"     - {mismatch}")
    else:
        print("  ✓ Frontmatter and table counts match")

    # Step 5: Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    print(f"\n✓ Cards checked: {total_checked}")
    print(f"✓ State labels found: {len([k for k, v in state_label_map.items() if v])}/{len(STATE_LABEL_NAMES)}")

    if mismatches:
        print(f"\n❌ State mismatches found: {len(mismatches)}")
        for m in mismatches:
            print(f"\n  Card: {m['card_name']}")
            print(f"  URL: {m['card_url']}")
            print(f"  Expected: {m['expected_state']}")
            print(f"  Actual: {m['actual_state']}")
            print(f"  Labels: {m['actual_labels']}")
        return 1

    if count_mismatches:
        print(f"\n❌ Count mismatches found: {len(count_mismatches)}")
        return 1

    print(f"\n✅ ALL VALIDATIONS PASSED")
    print(f"   No state mismatches, no count discrepancies")
    return 0

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 validate_snapshot.py <tag>")
        print("Example: python3 validate_snapshot.py MCSL-377")
        print("Example: python3 validate_snapshot.py \"MCSL 377\"")
        sys.exit(2)

    tag = ' '.join(sys.argv[1:])

    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("ERROR: TRELLO_API_KEY and TRELLO_TOKEN must be set")
        sys.exit(2)

    exit_code = validate_snapshot(tag)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
