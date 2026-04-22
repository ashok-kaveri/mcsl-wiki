#!/usr/bin/env python3
"""
Snapshot workflow for MCSL 377 release
Uses yq for YAML frontmatter parsing
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
import subprocess

# Configuration
KEY = os.environ['TRELLO_API_KEY']
TOKEN = os.environ['TRELLO_TOKEN']
PH_WIP_BOARD = '63e1e0414b6026c45be1087c'
DEFAULT_STORYLAB_BOARD = '69dd9134576a26fcb79b670d'

# Parsed arguments
TAG = "MCSL 377"
TAG_SLUG = TAG.replace(' ', '-').lower()
BOARD_ID = '63e1e0414b6026c45be1087c'
LANE_FILTER = 'SL MCSL 377: Iteration backlog'
NO_SYNC = True

print(f"=== Snapshot {TAG} ===")
print(f"Board: {BOARD_ID}")
print(f"Lane filter: {LANE_FILTER}")
print(f"--no-sync: {NO_SYNC}")
print()

# Step 1: Check if release file exists
release_file_path = f"wiki/product/releases/{TAG_SLUG}.md"
is_first_snapshot = not os.path.exists(release_file_path)

print(f"Step 1: Check release file")
print(f"  Path: {release_file_path}")
print(f"  First snapshot: {is_first_snapshot}")

# Preserved frontmatter fields
preserved = {}
if not is_first_snapshot:
    # Use yq to extract fields
    try:
        result = subprocess.run(
            ['yq', 'eval', '{git_reference, status, shipped_at}', release_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse yq output (JSON format)
        preserved = json.loads(result.stdout)
        print(f"  Preserved: git_reference={preserved.get('git_reference', 'N/A')[:8]}, status={preserved.get('status')}")
    except Exception as e:
        print(f"  ⚠️  Could not parse existing frontmatter: {e}")
        preserved = {}
print()

# Get current git reference
git_ref = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
print(f"Current git reference: {git_ref[:8]}")
print()

# Step 2: Fetch Trello state
print("Step 2: Fetching Trello data...")

def trello_get(path):
    url = f"https://api.trello.com/1{path}"
    sep = '&' if '?' in url else '?'
    url += f"{sep}key={KEY}&token={TOKEN}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"  ❌ GET {path} failed: {e}")
        return None

# Fetch all board labels with high limit
print(f"  Fetching labels from board {BOARD_ID}...")
all_labels = trello_get(f"/boards/{BOARD_ID}/labels?fields=name,color,id&limit=1000")
if not all_labels:
    print("  ❌ Failed to fetch labels")
    sys.exit(1)

print(f"  Found {len(all_labels)} labels")

# Resolve tag label (both variants)
tag_label_ids = []
for variant in [TAG, f"SL: {TAG}"]:
    for label in all_labels:
        if label['name'].strip().lower() == variant.lower():
            tag_label_ids.append(label['id'])
            print(f"  ✓ Found tag label: '{label['name']}' (ID: {label['id']})")

if not tag_label_ids:
    print(f"  ❌ No label found for '{TAG}' or 'SL: {TAG}'")
    print(f"  Available labels: {', '.join([l['name'] for l in all_labels[:20]])}")
    sys.exit(1)

# Resolve Support Closed label IDs
support_closed_variants = ['closed by support', 'sl: closed by support']
support_closed_label_ids = set()
for label in all_labels:
    label_name_lower = label['name'].strip().lower()
    if label_name_lower in support_closed_variants:
        support_closed_label_ids.add(label['id'])
        print(f"  ✓ Found Support Closed label: '{label['name']}' (ID: {label['id']})")

if not support_closed_label_ids:
    print(f"  ⚠️  WARNING: No 'Closed by Support' label found on board")

# Resolve Unsupported Partnership label IDs
unsupported_partnership_label_ids = set()
for label in all_labels:
    label_name_lower = label['name'].strip().lower()
    if label_name_lower == 'unsupported partnership for carrier':
        unsupported_partnership_label_ids.add(label['id'])
        print(f"  ✓ Found Unsupported Partnership label: '{label['name']}' (ID: {label['id']})")

if not unsupported_partnership_label_ids:
    print(f"  ⚠️  WARNING: No 'Unsupported Partnership For Carrier' label found on board")

print()

# Fetch all board lists
print(f"  Fetching lists from board {BOARD_ID}...")
all_lists = trello_get(f"/boards/{BOARD_ID}/lists?fields=name,id")
if not all_lists:
    print("  ❌ Failed to fetch lists")
    sys.exit(1)

print(f"  Found {len(all_lists)} lists")

# Find lane filter if specified
lane_filter_id = None
if LANE_FILTER:
    for lst in all_lists:
        if lst['name'] == LANE_FILTER:
            lane_filter_id = lst['id']
            print(f"  ✓ Found lane filter: '{LANE_FILTER}' (ID: {lane_filter_id})")
            break
    if not lane_filter_id:
        print(f"  ❌ Lane filter '{LANE_FILTER}' not found")
        print(f"  Available SL lanes: {', '.join([l['name'] for l in all_lists if l['name'].startswith('SL ')])}")
        sys.exit(1)

print()

# Fetch all cards from the board
print(f"  Fetching cards from board {BOARD_ID}...")
all_cards = trello_get(f"/boards/{BOARD_ID}/cards?fields=name,desc,idList,idLabels,shortUrl&attachments=true")
if all_cards is None:
    print("  ❌ Failed to fetch cards")
    sys.exit(1)

print(f"  Found {len(all_cards)} total cards on board")

# Filter to tagged cards
tagged_cards = []
for card in all_cards:
    # Check if card has any of the tag label IDs
    if any(tag_id in card.get('idLabels', []) for tag_id in tag_label_ids):
        # Check lane filter if specified
        if lane_filter_id is None or card['idList'] == lane_filter_id:
            tagged_cards.append(card)

print(f"  Found {len(tagged_cards)} cards with tag '{TAG}'" + (f" in lane '{LANE_FILTER}'" if LANE_FILTER else ""))

# Save intermediate data for next script
with open('/tmp/snapshot_data.json', 'w') as f:
    json.dump({
        'tagged_cards': tagged_cards,
        'all_labels': all_labels,
        'tag_label_ids': tag_label_ids,
        'support_closed_label_ids': list(support_closed_label_ids),
        'unsupported_partnership_label_ids': list(unsupported_partnership_label_ids),
        'preserved': preserved,
        'git_ref': git_ref,
        'is_first_snapshot': is_first_snapshot
    }, f, indent=2)

print(f"\n✓ Step 2 complete - data saved to /tmp/snapshot_data.json")
print(f"  Cards to process: {len(tagged_cards)}")
