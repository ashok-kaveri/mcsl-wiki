#!/usr/bin/env python3
"""
Process cards and determine states for release snapshot
"""
import json
import re
from datetime import datetime

# Load data from previous script
with open('/tmp/snapshot_data.json', 'r') as f:
    data = json.load(f)

tagged_cards = data['tagged_cards']
all_labels = data['all_labels']
tag_label_ids = data['tag_label_ids']
support_closed_label_ids = set(data['support_closed_label_ids'])
unsupported_partnership_label_ids = set(data['unsupported_partnership_label_ids'])

print("Step 3: Determining card states...")
print(f"  Processing {len(tagged_cards)} cards")
print()

# Build state label map
STATE_LABEL_NAMES = ['SHIPPED', 'PROD', 'QA_VERIFIED', 'QA Reported', 'Ready for QA', 'Dev Done', 'DEV', 'BUG REPORTED', 'SL: Carrier Platform Issues', 'Spill Over']
state_label_map = {}

for state_name in STATE_LABEL_NAMES:
    matching_labels = [lbl for lbl in all_labels if lbl['name'].strip().lower() == state_name.lower()]
    state_label_map[state_name] = {lbl['id'] for lbl in matching_labels}

# Build label name lookup for carrier extraction
label_id_to_name = {lbl['id']: lbl['name'] for lbl in all_labels}

# Validate critical labels
CRITICAL_LABELS = ['Dev Done', 'QA_VERIFIED', 'PROD', 'SHIPPED', 'DEV']
missing = [name for name in CRITICAL_LABELS if not state_label_map.get(name)]
if missing:
    print(f"  ❌ CRITICAL: Missing state labels: {missing}")
    exit(1)

print(f"  ✓ Found all critical state labels")

# Function to determine card state
def coarsen_state(card):
    """Determine the 8-state legend state for a card"""
    card_label_ids = set(card.get('idLabels', []))

    # Check StoryLab closure labels first (highest priority)
    if support_closed_label_ids and card_label_ids & support_closed_label_ids:
        return "Support Closed"

    if unsupported_partnership_label_ids and card_label_ids & unsupported_partnership_label_ids:
        return "Unsupported Partnership"

    # Check ph-WIP state labels in precedence order
    state_precedence = [
        ('SHIPPED', 'Shipped'),
        ('PROD', 'Shipped'),
        ('QA_VERIFIED', 'Ready To Ship'),
        ('SL: Carrier Platform Issues', 'Carrier Platform Issues'),
        ('BUG REPORTED', 'BUG REPORTED'),
        ('QA Reported', 'QA READY'),
        ('Ready for QA', 'QA READY'),
        ('Dev Done', 'QA READY'),
        ('DEV', 'DEV'),
        ('Spill Over', 'Spill Over'),
    ]

    for label_name, coarsened_state in state_precedence:
        label_ids = state_label_map.get(label_name, set())
        if label_ids and card_label_ids & label_ids:
            return coarsened_state

    # No state label found
    return "Open (not started)"

# Build state buckets
cards_by_state = {
    'Shipped': [],
    'Ready To Ship': [],
    'Support Closed': [],
    'Unsupported Partnership': [],
    'Carrier Platform Issues': [],
    'BUG REPORTED': [],
    'QA READY': [],
    'DEV': [],
    'Open (not started)': [],
    'Spill Over': []
}

# High Risk cards (both QA_VERIFIED and SL: Carrier Platform Issues)
high_risk_cards = []

# Parse ZI ID and ticket ID for each card
for card in tagged_cards:
    # Extract ZI ID from name (ZI-NNN pattern)
    zi_match = re.search(r'(ZI-\d+)', card['name'], re.IGNORECASE)
    card['zi_id'] = zi_match.group(1).upper() if zi_match else None

    # Extract ticket ID from name ([#NNNNNN] pattern)
    ticket_match = re.search(r'\[#(\d+)\]', card['name'])
    card['ticket_id'] = ticket_match.group(1) if ticket_match else None

    # Extract carriers from labels (look for labels with carrier emoji prefix 🚚)
    carriers = []
    for label_id in card.get('idLabels', []):
        label_name = label_id_to_name.get(label_id, '')
        # Look for carrier labels - those starting with 🚚 emoji
        if label_name and '🚚' in label_name:
            # Extract carrier name (remove emoji and "SL: " prefix if present)
            carrier = label_name.replace('🚚', '').replace('SL:', '').strip()
            if carrier:
                carriers.append(carrier)
    card['carriers'] = carriers

    # Determine state
    state = coarsen_state(card)
    cards_by_state[state].append(card)
    card['state'] = state

    # Check for high-risk cards (QA_VERIFIED + Carrier Platform Issues OR QA_VERIFIED + Unsupported Partnership)
    card_label_ids = set(card.get('idLabels', []))
    qa_verified_ids = state_label_map.get('QA_VERIFIED', set())
    carrier_platform_ids = state_label_map.get('SL: Carrier Platform Issues', set())

    has_qa_verified = qa_verified_ids and card_label_ids & qa_verified_ids
    has_carrier_platform = carrier_platform_ids and card_label_ids & carrier_platform_ids
    has_unsupported_partnership = unsupported_partnership_label_ids and card_label_ids & unsupported_partnership_label_ids

    if has_qa_verified and (has_carrier_platform or has_unsupported_partnership):
        high_risk_cards.append(card)

# Print state distribution
print("State distribution:")
for state, cards in cards_by_state.items():
    if cards:
        print(f"  {state}: {len(cards)}")

total_cards = sum(len(cards) for cards in cards_by_state.values())
print(f"  Total: {total_cards}")

if high_risk_cards:
    print(f"\n⚠️  High Risk cards: {len(high_risk_cards)}")
    print("    QA_VERIFIED + (Carrier Platform Issues OR Unsupported Partnership)")
    print("    (Possible use of customer credentials for verification)")
print()

# Save processed data
with open('/tmp/processed_cards.json', 'w') as f:
    json.dump({
        'cards_by_state': {k: v for k, v in cards_by_state.items()},
        'total_cards': total_cards,
        'state_counts': {state: len(cards) for state, cards in cards_by_state.items()},
        'high_risk_cards': high_risk_cards
    }, f, indent=2)

print("✓ Step 3 complete - processed data saved to /tmp/processed_cards.json")
