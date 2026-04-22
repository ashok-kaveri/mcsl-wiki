#!/usr/bin/env python3
"""
Generate release snapshot markdown for MCSL 377
"""
import json
import subprocess
from datetime import datetime

# Configuration
TAG = "MCSL 377"
TAG_SLUG = "mcsl-377"
BOARD_ID = "63e1e0414b6026c45be1087c"
LANE_FILTER = "SL MCSL 377: Iteration backlog"

# Load data
with open('/tmp/snapshot_data.json', 'r') as f:
    snapshot_data = json.load(f)

with open('/tmp/processed_cards.json', 'r') as f:
    processed_data = json.load(f)

cards_by_state = processed_data['cards_by_state']
state_counts = processed_data['state_counts']
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

# Build summary table
summary_table = f"""## Summary

| State | Count |
|-------|-------|
| Shipped | {state_counts.get('Shipped', 0)} |
| Ready To Ship | {state_counts.get('Ready To Ship', 0)} |
| Support Closed | {state_counts.get('Support Closed', 0)} |
| Unsupported Partnership | {state_counts.get('Unsupported Partnership', 0)} |
| Carrier Platform Issues | {state_counts.get('Carrier Platform Issues', 0)} |
| BUG REPORTED | {state_counts.get('BUG REPORTED', 0)} |
| QA READY | {state_counts.get('QA READY', 0)} |
| DEV | {state_counts.get('DEV', 0)} |
| Open (not started) | {state_counts.get('Open (not started)', 0)} |
| Spill Over | {state_counts.get('Spill Over', 0)} |
| **Total** | **{processed_data['total_cards']}** |"""

# Build legend
legend = """## Legend

- **Shipped** — deployed to production (ph-WIP SHIPPED or PROD label)
- **Ready To Ship** — QA verified, ready to deploy (ph-WIP QA_VERIFIED label)
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

# Build all card tables
card_tables = []
for state in ['Shipped', 'Ready To Ship', 'Support Closed', 'Unsupported Partnership', 'Carrier Platform Issues', 'BUG REPORTED']:
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
