#!/usr/bin/env python3
"""
Mode 3b: Snapshot release state from Trello to wiki
"""
import sys
import os
import json
import urllib.request
import urllib.parse
import argparse
from datetime import datetime

# Board name to ID mapping
BOARD_NAMES = {
    'storylab': '69dd9134576a26fcb79b670d',
    'ph-wip': '63e1e0414b6026c45be1087c',
}

DEFAULT_STORYLAB_BOARD = '69dd9134576a26fcb79b670d'
PH_WIP_BOARD = '63e1e0414b6026c45be1087c'

def resolve_board_id(board_input):
    """Resolve board name or ID to board ID"""
    if not board_input:
        return PH_WIP_BOARD  # Default to ph-wip for iteration workflow

    # Check if it's a known board name (case-insensitive)
    board_lower = board_input.lower()
    if board_lower in BOARD_NAMES:
        return BOARD_NAMES[board_lower]

    # Otherwise assume it's a board ID
    return board_input

# Parse arguments
parser = argparse.ArgumentParser(
    description='Snapshot release state from Trello to wiki',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
Examples:
  snapshot_release.py "MCSL 377"
  snapshot_release.py "MCSL 377" --board storylab
  snapshot_release.py "MCSL 377" --lane "SL MCSL 377: Iteration backlog"

Board names: ph-wip (default), storylab
Or use full board ID
    '''
)
parser.add_argument('tag', help='Release tag name (e.g., "MCSL 377")')
parser.add_argument('--board', default=None, help='Board name (storylab, ph-wip) or board ID (default: ph-wip)')
parser.add_argument('--lane', default=None, help='Lane filter (optional)')

args = parser.parse_args()

TAG = args.tag
BOARD_INPUT = args.board
BOARD_ID = resolve_board_id(BOARD_INPUT)
LANE_FILTER = args.lane

TAG_SLUG = TAG.lower().replace(' ', '-')

# API setup
KEY = os.environ['TRELLO_API_KEY']
TOKEN = os.environ['TRELLO_TOKEN']

def api_get(path):
    """Fetch from Trello API"""
    url = f"https://api.trello.com/1{path}"
    sep = '&' if '?' in url else '?'
    url = f"{url}{sep}key={KEY}&token={TOKEN}"
    return json.load(urllib.request.urlopen(url))

board_display = BOARD_INPUT if BOARD_INPUT else "ph-wip (default)"
print(f"Snapshot: {TAG}")
print(f"  Board: {board_display} ({BOARD_ID})")
print(f"  Lane filter: {LANE_FILTER or 'None'}")
print()

# Check if release file exists
release_path = f"wiki/product/releases/{TAG_SLUG}.md"
is_first_snapshot = not os.path.exists(release_path)

preserved = {
    'git_reference': None,
    'status': 'draft',
    'shipped_at': 'null',
    'tickets_delta_on_last_sync': 0
}

if not is_first_snapshot:
    print("Reading existing release file...")
    # Read existing frontmatter to preserve git_reference
    with open(release_path, 'r') as f:
        content = f.read()
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                frontmatter = content[3:end]
                for line in frontmatter.split('\n'):
                    if line.startswith('git_reference:'):
                        preserved['git_reference'] = line.split(':', 1)[1].strip()
                    elif line.startswith('status:'):
                        preserved['status'] = line.split(':', 1)[1].strip()
                    elif line.startswith('shipped_at:'):
                        preserved['shipped_at'] = line.split(':', 1)[1].strip()
                    elif line.startswith('tickets_delta_on_last_sync:'):
                        preserved['tickets_delta_on_last_sync'] = int(line.split(':', 1)[1].strip())

git_ref = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() if is_first_snapshot else preserved['git_reference']

# Save for next steps
snapshot_data = {
    'tag': TAG,
    'tag_slug': TAG_SLUG,
    'board_id': BOARD_ID,
    'lane_filter': LANE_FILTER,
    'ph_wip_board': PH_WIP_BOARD,
    'is_first_snapshot': is_first_snapshot,
    'preserved': preserved,
    'git_ref': git_ref
}

with open('/tmp/snapshot_data.json', 'w') as f:
    json.dump(snapshot_data, f, indent=2)

print(f"✓ Step 1 complete - first snapshot: {is_first_snapshot}")
print(f"  Preserved git_reference: {preserved['git_reference']}")
print(f"  Preserved status: {preserved['status']}")
print()

# Step 2: Fetch all labels from source board
print("Step 2: Fetching labels...")
all_labels = api_get(f"/boards/{BOARD_ID}/labels?fields=name,color,id&limit=1000")
print(f"  Fetched {len(all_labels)} labels from board")

# Multi-tag resolution: look for both "MCSL 377" and "SL: MCSL 377"
tag_label_ids = []
for label in all_labels:
    label_name = label['name'].strip()
    if label_name.lower() == TAG.lower() or label_name.lower() == f"sl: {TAG.lower()}":
        tag_label_ids.append(label['id'])
        print(f"  Found tag label: '{label['name']}' (ID: {label['id']})")

if not tag_label_ids:
    print(f"\n❌ No label found matching '{TAG}' or 'SL: {TAG}'")
    print("\nAvailable labels:")
    for lbl in sorted(all_labels, key=lambda x: x['name']):
        print(f"  - {lbl['name']}")
    sys.exit(1)

# Resolve Support Closed labels
support_closed_variants = ['closed by support', 'sl: closed by support']
support_closed_label_ids = []
for label in all_labels:
    if label['name'].strip().lower() in support_closed_variants:
        support_closed_label_ids.append(label['id'])
        print(f"  Found Support Closed label: '{label['name']}' (ID: {label['id']})")

if not support_closed_label_ids:
    print("  ⚠️  No 'Closed by Support' label found on board")

# Resolve Unsupported Partnership labels
unsupported_partnership_label_ids = []
for label in all_labels:
    if label['name'].strip().lower() == 'unsupported partnership for carrier':
        unsupported_partnership_label_ids.append(label['id'])
        print(f"  Found Unsupported Partnership label: '{label['name']}' (ID: {label['id']})")

if not unsupported_partnership_label_ids:
    print("  ⚠️  No 'Unsupported Partnership For Carrier' label found on board")

# Fetch all cards from source board
print()
print("Fetching cards from source board...")
all_cards = api_get(f"/boards/{BOARD_ID}/cards?attachments=true&fields=name,desc,idList,idLabels,shortUrl")
print(f"  Total cards on board: {len(all_cards)}")

# Filter by tag
tagged_cards = [c for c in all_cards if any(tid in c.get('idLabels', []) for tid in tag_label_ids)]
print(f"  Cards with tag '{TAG}': {len(tagged_cards)}")

# If lane filter specified, filter by lane
if LANE_FILTER:
    # Fetch lanes
    lanes = api_get(f"/boards/{BOARD_ID}/lists?fields=name,id")
    matching_lane = next((l for l in lanes if l['name'] == LANE_FILTER), None)

    if not matching_lane:
        print(f"\n❌ Lane '{LANE_FILTER}' not found on board")
        print("\nAvailable lanes:")
        for lane in lanes:
            print(f"  - {lane['name']}")
        sys.exit(1)

    tagged_cards = [c for c in tagged_cards if c['idList'] == matching_lane['id']]
    print(f"  Cards in lane '{LANE_FILTER}': {len(tagged_cards)}")

print()

# Save snapshot data for processing
snapshot_data['tagged_cards'] = tagged_cards
snapshot_data['all_labels'] = all_labels
snapshot_data['tag_label_ids'] = tag_label_ids
snapshot_data['support_closed_label_ids'] = support_closed_label_ids
snapshot_data['unsupported_partnership_label_ids'] = unsupported_partnership_label_ids

with open('/tmp/snapshot_data.json', 'w') as f:
    json.dump(snapshot_data, f, indent=2)

print(f"✓ Step 2 complete - saved snapshot data to /tmp/snapshot_data.json")
