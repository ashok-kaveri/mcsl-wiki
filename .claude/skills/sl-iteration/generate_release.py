#!/usr/bin/env python3
"""
Generate release snapshot markdown
"""
import json
import subprocess
from datetime import datetime

# Load data
with open('/tmp/snapshot_data.json', 'r') as f:
    snapshot_data = json.load(f)

# Read configuration from snapshot data
TAG = snapshot_data['tag']
TAG_SLUG = snapshot_data['tag_slug']
BOARD_ID = snapshot_data['board_id']
LANE_FILTER = snapshot_data['lane_filter']

with open('/tmp/processed_cards.json', 'r') as f:
    processed_data = json.load(f)

cards_by_state = processed_data['cards_by_state']
state_counts = processed_data['state_counts']
high_risk_cards = processed_data.get('high_risk_cards', [])
preserved = snapshot_data['preserved']
git_ref = snapshot_data['git_ref']
is_first_snapshot = snapshot_data['is_first_snapshot']

print("Step 4: Generating release snapshot markdown...")
print()

# Prepare frontmatter fields
now_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

# Use preserved values or set new ones
frontmatter_git_ref = preserved.get('git_reference') if not is_first_snapshot else git_ref
frontmatter_status = preserved.get('status', 'draft')
frontmatter_shipped_at = preserved.get('shipped_at', 'null')

# Build frontmatter
frontmatter = f"""---
title: "Release {TAG}"
category: product-release
tag: "{TAG}"
tag_slug: {TAG_SLUG}
board_id: {BOARD_ID}
lane_filter: "{LANE_FILTER}"
status: {frontmatter_status}
last_synced: {now_utc}
shipped_at: {frontmatter_shipped_at}
git_reference: {frontmatter_git_ref}
tickets_delta_on_last_sync: {preserved.get('tickets_delta_on_last_sync', 0)}
cards_total: {state_counts.get('Shipped', 0) + state_counts.get('Ready To Ship', 0) + state_counts.get('Support Closed', 0) + state_counts.get('Unsupported Partnership', 0) + state_counts.get('Carrier Platform Issues', 0) + state_counts.get('BUG REPORTED', 0) + state_counts.get('QA READY', 0) + state_counts.get('DEV', 0) + state_counts.get('Open (not started)', 0) + state_counts.get('Spill Over', 0)}
cards_shipped: {state_counts.get('Shipped', 0)}
cards_ready_to_ship: {state_counts.get('Ready To Ship', 0)}
cards_high_risk: {len(high_risk_cards)}
cards_support_closed: {state_counts.get('Support Closed', 0)}
cards_unsupported_partnership: {state_counts.get('Unsupported Partnership', 0)}
cards_carrier_platform_issues: {state_counts.get('Carrier Platform Issues', 0)}
cards_bug_reported: {state_counts.get('BUG REPORTED', 0)}
cards_open: {state_counts.get('Open (not started)', 0)}
cards_spill_over: {state_counts.get('Spill Over', 0)}
---"""

# Build status banner
status_display = frontmatter_status
if frontmatter_status == "draft":
    status_display = "draft"
elif frontmatter_status == "shipped":
    status_display = f"SHIPPED {frontmatter_shipped_at}"

# Track cards across all sections to identify duplicates
section_membership = {}  # {zi_id: [list of sections]}

# Add cards from each state section
for state, cards in cards_by_state.items():
    for card in cards:
        zi = card.get('zi_id', 'N/A')
        if zi not in section_membership:
            section_membership[zi] = []
        section_membership[zi].append(state)

# Add High Risk cards as a separate section
for card in high_risk_cards:
    zi = card.get('zi_id', 'N/A')
    if zi not in section_membership:
        section_membership[zi] = []
    section_membership[zi].append('⚠️ High Risk')

# Find cards in multiple sections
multi_section_cards = {zi: sections for zi, sections in section_membership.items() if len(sections) > 1}

# Build note
multi_section_note = ""
if multi_section_cards:
    # Filter out None keys and sort
    valid_cards = {zi: sections for zi, sections in multi_section_cards.items() if zi is not None}
    card_details = [f"{zi} ({', '.join(sections)})" for zi, sections in sorted(valid_cards.items())]
    multi_section_note = f"\n\n**Note:** The following {len(multi_section_cards)} card(s) appear in multiple sections: {'; '.join(card_details)}. Total unique cards: {processed_data['total_cards']}."

summary_table = f"""## Summary

| State | Count |
|-------|-------|
| Shipped | {state_counts.get('Shipped', 0)} |
| Ready To Ship | {state_counts.get('Ready To Ship', 0)} |
| ⚠️ High Risk | {len(high_risk_cards)} |
| Support Closed | {state_counts.get('Support Closed', 0)} |
| Unsupported Partnership | {state_counts.get('Unsupported Partnership', 0)} |
| Carrier Platform Issues | {state_counts.get('Carrier Platform Issues', 0)} |
| BUG REPORTED | {state_counts.get('BUG REPORTED', 0)} |
| QA READY | {state_counts.get('QA READY', 0)} |
| DEV | {state_counts.get('DEV', 0)} |
| Open (not started) | {state_counts.get('Open (not started)', 0)} |
| Spill Over | {state_counts.get('Spill Over', 0)} |
| **Total** | **{processed_data['total_cards']}** |{multi_section_note}"""

# Build legend
legend = """## Legend

- **Shipped** — deployed to production (ph-WIP SHIPPED or PROD label)
- **Ready To Ship** — QA verified, ready to deploy (ph-WIP QA_VERIFIED label)
- **⚠️ High Risk** — cards with `QA_VERIFIED` AND (`SL: Carrier Platform Issues` OR `Unsupported Partnership`) labels (possible use of customer credentials for verification; requires special care before shipping)
- **Support Closed** — StoryLab card has `Closed by Support` (or `SL: Closed By Support` — both names map to the same state, case-insensitive) label; closed without code via support action
- **Unsupported Partnership** — StoryLab card has `Unsupported Partnership For Carrier` label (case-insensitive); unsupported carrier/partnership
- **Carrier Platform Issues** — external carrier/platform environment issues we cannot solve (ph-WIP `SL: Carrier Platform Issues` label)
- **BUG REPORTED** — code is in QA, bug has been reported (ph-WIP BUG REPORTED label)
- **QA READY** — code complete, in QA (ph-WIP Dev Done, Ready for QA, or QA Reported labels — NOT yet verified)
- **DEV** — active development (ph-WIP DEV label)
- **Open (not started)** — in product backlog but dev hasn't started (no ph-WIP state label)
- **Spill Over** — cards that could not be completed in the current iteration and were moved out (ph-WIP `Spill Over` label)"""

# Function to build card tables for each state
def build_card_table(state, cards):
    if not cards:
        return f"## {state} (0)\n\n*No cards in this state*"

    lines = [f"## {state} ({len(cards)})\n"]

    if state in ['Shipped', 'Ready To Ship']:
        lines.append("| ZI | Ticket | Card |")
        lines.append("|----|--------|------|")
        for card in sorted(cards, key=lambda c: c.get('zi_id') or ''):
            zi = card.get('zi_id', 'N/A')
            ticket = card.get('ticket_id')
            ticket_link = f"[#{ticket}](../../zendesk/summaries/{ticket}.md)" if ticket else "N/A"
            card_link = f"[Link]({card['shortUrl']})"
            lines.append(f"| {zi} | {ticket_link} | {card_link} |")

    elif state == 'Support Closed':
        lines.append("| ZI | Ticket | Reason | Card |")
        lines.append("|----|--------|--------|------|")
        for card in sorted(cards, key=lambda c: c.get('zi_id') or ''):
            zi = card.get('zi_id', 'N/A')
            ticket = card.get('ticket_id')
            ticket_link = f"[#{ticket}](../../zendesk/summaries/{ticket}.md)" if ticket else "N/A"
            card_link = f"[Link]({card['shortUrl']})"
            reason = "pending"  # Would need to parse comments for actual reason
            lines.append(f"| {zi} | {ticket_link} | {reason} | {card_link} |")

    elif state == 'Unsupported Partnership':
        lines.append("| ZI | Ticket | Card |")
        lines.append("|----|--------|------|")
        for card in sorted(cards, key=lambda c: c.get('zi_id') or ''):
            zi = card.get('zi_id', 'N/A')
            ticket = card.get('ticket_id')
            ticket_link = f"[#{ticket}](../../zendesk/summaries/{ticket}.md)" if ticket else "N/A"
            card_link = f"[Link]({card['shortUrl']})"
            lines.append(f"| {zi} | {ticket_link} | {card_link} |")

    elif state == 'Carrier Platform Issues':
        lines.append("| ZI | Ticket | Carriers | Card |")
        lines.append("|----|--------|----------|------|")
        for card in sorted(cards, key=lambda c: c.get('zi_id') or ''):
            zi = card.get('zi_id', 'N/A')
            ticket = card.get('ticket_id')
            ticket_link = f"[#{ticket}](../../zendesk/summaries/{ticket}.md)" if ticket else "N/A"
            carriers = ', '.join(card.get('carriers', [])) if card.get('carriers') else 'N/A'
            card_link = f"[Link]({card['shortUrl']})"
            lines.append(f"| {zi} | {ticket_link} | {carriers} | {card_link} |")

    elif state in ['BUG REPORTED', 'QA READY', 'DEV', 'Open (not started)', 'Spill Over']:
        lines.append("| ZI | Ticket | Card |")
        lines.append("|----|--------|------|")
        for card in sorted(cards, key=lambda c: c.get('zi_id') or ''):
            zi = card.get('zi_id', 'N/A')
            ticket = card.get('ticket_id')
            ticket_link = f"[#{ticket}](../../zendesk/summaries/{ticket}.md)" if ticket else "N/A"
            card_link = f"[Link]({card['shortUrl']})"
            lines.append(f"| {zi} | {ticket_link} | {card_link} |")

    return "\n".join(lines)

# Build High Risk section
def build_high_risk_table(cards):
    if not cards:
        return ""

    lines = [f"## ⚠️ High Risk ({len(cards)})\n"]
    lines.append("**Cards with QA_VERIFIED AND (Carrier Platform Issues OR Unsupported Partnership)**")
    lines.append("*(Possible use of customer credentials for verification - requires special care)*\n")
    lines.append("| ZI | Ticket | Carriers | Card |")
    lines.append("|----|--------|----------|------|")
    for card in sorted(cards, key=lambda c: c.get('zi_id') or ''):
        zi = card.get('zi_id', 'N/A')
        ticket = card.get('ticket_id')
        ticket_link = f"[#{ticket}](../../zendesk/summaries/{ticket}.md)" if ticket else "N/A"
        carriers = ', '.join(card.get('carriers', [])) if card.get('carriers') else 'N/A'
        card_link = f"[Link]({card['shortUrl']})"
        lines.append(f"| {zi} | {ticket_link} | {carriers} | {card_link} |")

    return "\n".join(lines)

high_risk_table = build_high_risk_table(high_risk_cards)

# Build Ad-hoc Cards section (cards without ZI-NNN in name — typically dev-initiated work)
def build_adhoc_section(cards_by_state):
    adhoc = []
    for state, cards in cards_by_state.items():
        for card in cards:
            if not card.get('zi_id'):
                adhoc.append((state, card))

    if not adhoc:
        return ""

    lines = [f"## Ad-hoc Cards ({len(adhoc)})\n"]
    lines.append("*Cards tagged for this release but not mirrored from a ZI issue — typically dev-initiated work (refactors, infra, platform changes).*\n")
    for state, card in adhoc:
        name = card.get('name', '').strip()
        desc = (card.get('desc') or '').strip()
        # Keep first paragraph, cap at ~300 chars
        first_para = desc.split('\n\n', 1)[0].strip() if desc else '_No description_'
        if len(first_para) > 300:
            first_para = first_para[:300].rstrip() + '…'
        url = card.get('shortUrl', '')
        lines.append(f"### {name}\n")
        lines.append(f"**State:** {state}  ·  **Card:** [{url}]({url})\n")
        lines.append(f"{first_para}\n")
    return "\n".join(lines)

adhoc_section = build_adhoc_section(cards_by_state)

# Build all card tables
card_tables = []
for state in ['Shipped', 'Ready To Ship']:
    card_tables.append(build_card_table(state, cards_by_state.get(state, [])))

# Insert High Risk section after Ready To Ship
if high_risk_table:
    card_tables.append(high_risk_table)

# Continue with remaining states
for state in ['Support Closed', 'Unsupported Partnership', 'Carrier Platform Issues', 'BUG REPORTED']:
    card_tables.append(build_card_table(state, cards_by_state.get(state, [])))

# Build Spill Over section
spill_over_section = build_card_table('Spill Over', cards_by_state.get('Spill Over', []))

# Build "Still Open" section
still_open = []
still_open.append("## Still Open ({})".format(
    state_counts.get('QA READY', 0) + state_counts.get('DEV', 0) + state_counts.get('Open (not started)', 0)
))
still_open.append("")
still_open.append(build_card_table('QA READY', cards_by_state.get('QA READY', [])).replace('## QA READY', '### QA READY'))
still_open.append("")
still_open.append(build_card_table('DEV', cards_by_state.get('DEV', [])).replace('## DEV', '### DEV'))
still_open.append("")
still_open.append(build_card_table('Open (not started)', cards_by_state.get('Open (not started)', [])).replace('## Open (not started)', '### Open / not started'))

# Build notes section
notes = """## Notes

- Cards missing `[close-reason: ...]` comment: TBD
- Cards with no ph-WIP correlation: 0 (all cards are on ph-WIP board)
- Cards dropped since last snapshot: 0
- Warnings: None

## Cross-Links

- [Backlog](../backlog.md)
- [Latest Zendesk daily index](../../zendesk/)"""

# Assemble full markdown
markdown = f"""{frontmatter}

# Release {TAG}

> **Status**: {status_display} · **Last synced**: {now_utc.split()[0] + ' ' + now_utc.split()[1][:5]} UTC · **Board**: [ph-WIP](https://trello.com/b/{BOARD_ID})

{summary_table}

{legend}

{adhoc_section}

{chr(10).join(card_tables)}

{spill_over_section}

{chr(10).join(still_open)}

{notes}
"""

# Write to file
output_path = f"wiki/product/releases/{TAG_SLUG}.md"
with open(output_path, 'w') as f:
    f.write(markdown)

print(f"✓ Release snapshot written to {output_path}")
print()
print(f"Summary:")
print(f"  Total cards: {processed_data['total_cards']}")
print(f"  Shipped: {state_counts.get('Shipped', 0)}")
print(f"  Ready To Ship: {state_counts.get('Ready To Ship', 0)}")
if high_risk_cards:
    print(f"  ⚠️  High Risk: {len(high_risk_cards)} (QA_VERIFIED + Platform/Partnership Issues)")
print(f"  Support Closed: {state_counts.get('Support Closed', 0)}")
print(f"  Unsupported Partnership: {state_counts.get('Unsupported Partnership', 0)}")
print(f"  Carrier Platform Issues: {state_counts.get('Carrier Platform Issues', 0)}")
print(f"  BUG REPORTED: {state_counts.get('BUG REPORTED', 0)}")
print(f"  QA READY: {state_counts.get('QA READY', 0)}")
print(f"  DEV: {state_counts.get('DEV', 0)}")
print(f"  Open: {state_counts.get('Open (not started)', 0)}")
print(f"  Spill Over: {state_counts.get('Spill Over', 0)}")
print()
if frontmatter_git_ref and frontmatter_git_ref != 'None':
    print(f"git_reference: {frontmatter_git_ref[:8]} (preserved from previous snapshot)")
else:
    print(f"git_reference: {git_ref[:8]} (new snapshot)")
print(f"Status: {frontmatter_status}")
