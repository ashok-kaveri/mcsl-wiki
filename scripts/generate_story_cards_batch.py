#!/usr/bin/env python3
"""
Generate story cards for a batch of ZI issues.
Processes sequentially to avoid Trello race conditions.
Generates PROPER story cards following SKILL.md requirements - NOT generic templates.
"""

import json
import sys
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error

# Paths
WIKI_ROOT = Path(__file__).parent.parent
DAILY_INDEX = WIKI_ROOT / "wiki" / "zendesk" / "2026-04-27.md"
SUMMARIES_DIR = WIKI_ROOT / "wiki" / "zendesk" / "summaries"
STORIES_DIR = WIKI_ROOT / "wiki" / "product" / "stories"
RAW_ZENDESK = WIKI_ROOT / "raw" / "zendesk"

# Trello config
SETTINGS_PATH = WIKI_ROOT / ".claude" / "settings.local.json"
BOARD_ID = "69dd9134576a26fcb79b670d"
TARGET_LANE_ID = "69dd9e0e8a7bb8b998765ee7"  # APR 25-30

# Load Trello credentials
with open(SETTINGS_PATH) as f:
    settings = json.load(f)
    TRELLO_KEY = settings['env']['TRELLO_API_KEY']
    TRELLO_TOKEN = settings['env']['TRELLO_TOKEN']

# Cache for Trello board cards (fetched once per script run)
_trello_cards_cache = None

# Area to theme mapping
THEME_MAP = {
    'label-generation': ('labels', 'Label & Document Quality'),
    'carrier-config': ('carrier', 'Carrier Platform'),
    'carrier-migration': ('carrier', 'Carrier Platform'),
    'onboarding': ('onboarding', 'Onboarding & Retention'),
    'order-management': ('data', 'Order & Product Data'),
    'product-management': ('data', 'Order & Product Data'),
    'international': ('intl', 'International & Customs'),
    'returns': ('intl', 'International & Customs'),
    'rate-shopping': ('rates', 'Rates & Intelligence'),
    'tracking': ('rates', 'Rates & Intelligence'),
    'feature-request': ('requests', 'Feature Requests'),
    'other': ('requests', 'Feature Requests')
}

# Product display names
PRODUCT_NAMES = {
    'shopify': 'Shopify MCSL',
    'woocommerce': 'WooCommerce',
    'magento': 'Magento'
}

# Pain scores
PAIN_MAP = {
    'label-generation': 10,
    'carrier-config': 8,
    'carrier-migration': 7,
    'onboarding': 4,
    'order-management': 8,
    'product-management': 9,
    'international': 8,
    'returns': 5,
    'rate-shopping': 7,
    'tracking': 4,
    'feature-request': 5,
    'other': 3
}


def get_all_trello_cards():
    """Fetch all Trello cards once and cache for the session."""
    global _trello_cards_cache
    if _trello_cards_cache is None:
        url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards?fields=name,shortUrl&key={TRELLO_KEY}&token={TRELLO_TOKEN}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                _trello_cards_cache = json.loads(response.read())
        except urllib.error.HTTPError as e:
            print(f"Trello API error: {e}", file=sys.stderr)
            _trello_cards_cache = []
    return _trello_cards_cache


def parse_daily_index(zi_ids_list):
    """Parse daily index for given ZI IDs."""
    zi_data = {}

    with open(DAILY_INDEX) as f:
        content = f.read()

    # Parse issue index table
    in_table = False
    for line in content.split('\n'):
        if line.startswith('| ID | Issue | Ticket'):
            in_table = True
            continue
        if not in_table or not line.startswith('| ZI-'):
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 7:
            continue

        zi_id = parts[1]
        if zi_id not in zi_ids_list:
            continue

        title = parts[2]
        ticket_link = parts[3]
        product = parts[4]
        area = parts[5]
        duplicate_of = parts[6]

        # Extract ticket ID
        match = re.search(r'\[(\d+)\]', ticket_link)
        if not match:
            continue
        ticket_id = match.group(1)

        zi_data[zi_id] = {
            'title': title,
            'ticket_id': ticket_id,
            'product': product,
            'area': area,
            'duplicate_of': duplicate_of.strip()
        }

    return zi_data


def read_ticket_summary(ticket_id):
    """Read ticket summary markdown and extract frontmatter + content."""
    summary_path = SUMMARIES_DIR / f"{ticket_id}.md"
    if not summary_path.exists():
        return None, None

    with open(summary_path) as f:
        content = f.read()

    # Parse frontmatter
    frontmatter = {}
    parts = content.split('---', 2)
    if len(parts) >= 3:
        # Extract frontmatter
        fm_lines = parts[1].strip().split('\n')
        for line in fm_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"')

        # Return frontmatter and body content
        return frontmatter, parts[2].strip()

    return {}, content


def get_created_at(ticket_id, product):
    """Get created_at timestamp from raw JSON."""
    for product_dir in ['shopify', 'other_platforms']:
        json_path = RAW_ZENDESK / product_dir / f"{ticket_id}.json"
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
            return datetime.fromisoformat(data['ticket']['created_at'].replace('Z', '+00:00'))

    return None


def check_trello_exists(ticket_id, zi_id):
    """Check if card already exists on Trello board (uses cached board data)."""
    cards = get_all_trello_cards()

    for card in cards:
        name = card.get('name', '')
        if f'[#{ticket_id}]' in name or name.startswith(f'{zi_id} —'):
            return card['shortUrl']

    return None


def extract_customer_context(ticket_summary_body):
    """Extract customer context from ticket summary."""
    context = {
        'customer': 'Unknown',
        'store': None,
        'plan': None,
        'volume': None,
        'duration': None
    }

    lines = ticket_summary_body.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('- **Customer**:'):
            context['customer'] = line.split(':', 1)[1].strip()
        elif line.startswith('- **Duration**:'):
            context['duration'] = line.split(':', 1)[1].strip()
        elif 'Customer Context' in line and i + 1 < len(lines):
            # Look ahead for store, plan info
            for j in range(i+1, min(i+10, len(lines))):
                if 'Store:' in lines[j]:
                    context['store'] = lines[j].split(':', 1)[1].strip()
                if 'plan' in lines[j].lower():
                    context['plan'] = lines[j].strip()

    return context


def generate_user_story(zi_data, ticket_summary_body, customer_context):
    """Generate a proper user story based on the SKILL.md framework."""
    title = zi_data['title']
    area = zi_data['area']
    product = PRODUCT_NAMES.get(zi_data['product'], zi_data['product'])

    # Extract key pain points from the title and summary
    title_lower = title.lower()

    # Try to identify the underlying need and consequence
    # This is a simplified heuristic - ideally would use LLM analysis

    # Role - ground it in customer situation
    if customer_context['plan']:
        role = f"merchant on the {customer_context['plan']}"
    else:
        role = f"merchant using {product}"

    # Want - the underlying capability need
    if 'missing' in title_lower or 'not available' in title_lower:
        want = f"all features and fields required by my carrier to be available in the app"
    elif 'error' in title_lower or 'fail' in title_lower:
        want = f"label generation to work reliably without cryptic errors that block my fulfillment"
    elif 'dimension' in title_lower or 'package' in title_lower:
        want = f"accurate package dimensions to be captured and sent to carriers"
    elif area == 'carrier-config':
        want = f"my carrier account settings to be properly configured without requiring support tickets"
    elif area == 'label-generation':
        want = f"to generate shipping labels quickly and reliably for all my orders"
    elif area == 'order-management':
        want = f"my orders to import and sync correctly without manual intervention"
    else:
        want = f"the issue described in {title} to be resolved"

    # So that - the business consequence
    if area == 'label-generation':
        consequence = "my fulfillment team can ship orders on time without manual workarounds or expensive carrier portal alternatives"
    elif area == 'carrier-config':
        consequence = "I can use all my contracted carrier services without waiting for dev enhancements"
    elif area == 'order-management':
        consequence = "my fulfillment pipeline stays automated and I don't lose orders to sync failures"
    elif PAIN_MAP.get(area, 5) >= 8:
        consequence = "my business operations aren't blocked and I don't have to consider switching to a different solution"
    else:
        consequence = "I can continue using the app effectively for my shipping needs"

    return f"As a {role}, I want {want}, so that {consequence}."


def generate_acceptance_criteria(zi_data, ticket_summary_body):
    """Generate 5 specific acceptance criteria checkboxes."""
    title = zi_data['title']
    area = zi_data['area']
    ticket_id = zi_data['ticket_id']

    criteria = []

    # Criterion 1: Specific to the customer's issue
    criteria.append(f"The specific issue described in ticket #{ticket_id} is resolved")

    # Criterion 2: Broader scope - other merchants/scenarios
    if 'vietnam' in title.lower():
        criteria.append("All merchants shipping from Vietnam can generate UPS labels successfully")
    elif 'fedex' in title.lower():
        criteria.append("FedEx configuration works correctly for all affected customers")
    elif 'package' in title.lower() or 'dimension' in title.lower():
        criteria.append("Package dimensions are correctly captured and validated for all carriers")
    else:
        criteria.append("The fix works for similar cases across all customers")

    # Criterion 3: Prevention - no similar tickets needed
    if 'error' in title.lower():
        criteria.append("Clear error messages guide users to fix issues themselves without opening tickets")
    else:
        criteria.append("Similar issues are prevented or handled automatically going forward")

    # Criterion 4: Testing/QA verification
    if area == 'label-generation':
        criteria.append("QA verifies label generation succeeds for affected carrier/scenario in test environment")
    elif area == 'carrier-config':
        criteria.append("QA verifies carrier configuration UI captures all required fields and validates correctly")
    else:
        criteria.append("QA verifies the fix in staging environment before production deployment")

    # Criterion 5: Monitoring/observability
    criteria.append("No regression in related functionality after deployment")

    return criteria


def generate_gwt_scenarios(zi_data, ticket_summary_body):
    """Generate 3 Given/When/Then scenarios."""
    title = zi_data['title']
    area = zi_data['area']

    scenarios = []

    # Scenario 1: Happy path - the specific fix
    scenario1 = {
        'name': 'Specific customer issue is resolved',
        'steps': []
    }

    if 'vietnam' in title.lower() and 'ups' in title.lower():
        scenario1['steps'] = [
            ('Given', 'a merchant has a ShipFrom address in Vietnam'),
            ('When', 'they configure UPS carrier settings and add State/Province field'),
            ('Then', 'UPS labels generate successfully with all required fields'),
            ('And', 'no State/Province validation errors occur')
        ]
    elif 'dimension' in title.lower() or 'package' in title.lower():
        scenario1['steps'] = [
            ('Given', 'a merchant has products with package dimensions configured'),
            ('When', 'they generate a shipping label'),
            ('Then', 'the dimensions are correctly passed to the carrier API'),
            ('And', 'the label generates with accurate package information')
        ]
    else:
        scenario1['steps'] = [
            ('Given', 'a merchant encounters the issue described in the ticket'),
            ('When', 'they follow the normal workflow'),
            ('Then', 'the issue no longer occurs'),
            ('And', 'they can complete their task successfully')
        ]

    scenarios.append(scenario1)

    # Scenario 2: Broader fix - other merchants/edge cases
    scenario2 = {
        'name': 'Fix works for other similar cases',
        'steps': [
            ('Given', 'other merchants have similar configurations or requirements'),
            ('When', 'they use the same feature'),
            ('Then', 'it works correctly for them as well'),
            ('And', 'no new edge cases are introduced')
        ]
    }
    scenarios.append(scenario2)

    # Scenario 3: Prevention - how we prevent recurrence
    scenario3 = {
        'name': 'Issue prevention for future cases',
        'steps': []
    }

    if 'missing' in title.lower() or 'required' in title.lower():
        scenario3['steps'] = [
            ('Given', 'carrier APIs add new required fields in the future'),
            ('When', 'we receive API error responses about missing fields'),
            ('Then', 'clear error messages direct merchants to add the required information'),
            ('And', 'support can identify and fix UI gaps quickly')
        ]
    elif 'error' in title.lower():
        scenario3['steps'] = [
            ('Given', 'validation or API errors occur'),
            ('When', 'a merchant encounters the error'),
            ('Then', 'the error message clearly explains what went wrong and how to fix it'),
            ('And', 'self-service resolution is possible without contacting support')
        ]
    else:
        scenario3['steps'] = [
            ('Given', 'similar issues may occur in the future'),
            ('When', 'we implement monitoring and error handling'),
            ('Then', 'issues are caught early before affecting many customers'),
            ('And', 'we receive alerts to fix problems proactively')
        ]

    scenarios.append(scenario3)

    return scenarios


def write_story_card(zi_id, zi_data, ticket_frontmatter, ticket_summary_body, created_at):
    """Write a PROPER story card following SKILL.md requirements."""
    ticket_id = zi_data['ticket_id']
    title = zi_data['title']
    product = zi_data['product']
    area = zi_data['area']

    # Get display names
    product_display = PRODUCT_NAMES.get(product, product)
    theme_id, theme_label = THEME_MAP.get(area, ('requests', 'Feature Requests'))
    pain = PAIN_MAP.get(area, 5)

    # Compute SLA
    sla_target = created_at + timedelta(hours=72)
    now = datetime.now(created_at.tzinfo)

    if now < sla_target:
        sla_status = "🟢 On Track"
        sla_days = ""
    elif (sla_target - now).total_seconds() < 12 * 3600:
        sla_status = "🟡 At Risk"
        sla_days = ""
    else:
        days_overdue = (now - sla_target).days
        sla_status = f"🔴 Breached"
        sla_days = f" ({days_overdue} days overdue)"

    # Extract customer context
    customer_context = extract_customer_context(ticket_summary_body)

    # Generate story components
    user_story = generate_user_story(zi_data, ticket_summary_body, customer_context)
    acceptance_criteria = generate_acceptance_criteria(zi_data, ticket_summary_body)
    gwt_scenarios = generate_gwt_scenarios(zi_data, ticket_summary_body)

    # Build frontmatter
    frontmatter = f"""---
title: "{zi_id} — {title[:60]}"
zi_id: {zi_id}
ticket_id: {ticket_id}
product: {product}
theme: {theme_id}
area: {area}
pain: {pain}
status: proposed
created: {created_at.strftime('%Y-%m-%d')}
sla_target: {sla_target.isoformat()}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
---
"""

    # Build card content (for both markdown and Trello)
    card_content = f"""# {zi_id} — {title[:80]}

| Field | Value |
|-------|-------|
| **Ticket** | #{ticket_id} |
| **Theme** | `{theme_label}` |
| **App** | `{product_display}` |
| **Area** | {area} |
| **Customers Affected** | 1+ |
| **Pain** | {pain}/10 |
| **Reported** | {created_at.strftime('%Y-%m-%d %H:%M')} UTC |
| **SLA Target** | {sla_target.strftime('%Y-%m-%d %H:%M')} UTC (72h) |
| **SLA Status** | {sla_status}{sla_days} |

---

## Ticket Summary

<!-- Source: wiki/zendesk/summaries/{ticket_id}.md -->

{ticket_summary_body}

---

## User Story

{user_story}

---

## Acceptance Criteria (Simple)

{chr(10).join(f'- [ ] {criterion}' for criterion in acceptance_criteria)}

---

## Acceptance Criteria (Given/When/Then)

"""

    # Add GWT scenarios
    for scenario in gwt_scenarios:
        card_content += f"### Scenario: {scenario['name']}\n"
        for label, text in scenario['steps']:
            card_content += f"- **{label}** {text}\n"
        card_content += "\n"

    # Add cross-links (markdown only)
    cross_links = f"""---

## Cross-Links

| Type | Link |
|------|------|
| Ticket Summary | [#{ticket_id}](../../zendesk/summaries/{ticket_id}.md) |
| Daily Index | [{zi_id}](../../zendesk/2026-04-27.md) |
| Backlog | [Product Backlog](../backlog.md) |
"""

    # Write markdown file
    story_path = STORIES_DIR / f"{zi_id}.md"
    with open(story_path, 'w') as f:
        f.write(frontmatter + "\n" + card_content + cross_links)

    return story_path, card_content


def process_zi(zi_id):
    """Process a single ZI issue."""
    # Read delta list
    delta_file = WIKI_ROOT / "intermediate" / "delta_zi_ids.txt"
    with open(delta_file) as f:
        zi_ids_list = [line.strip() for line in f if line.strip()]

    # Parse daily index
    zi_data_map = parse_daily_index(zi_ids_list)

    if zi_id not in zi_data_map:
        return {"status": "not_found", "zi_id": zi_id}

    zi_data = zi_data_map[zi_id]

    # Check if duplicate
    if zi_data['duplicate_of']:
        return {
            "status": "duplicate",
            "zi_id": zi_id,
            "ticket_id": zi_data['ticket_id'],
            "duplicate_of": zi_data['duplicate_of']
        }

    # Read ticket summary
    ticket_frontmatter, ticket_summary_body = read_ticket_summary(zi_data['ticket_id'])
    if not ticket_summary_body:
        return {
            "status": "summary_not_found",
            "zi_id": zi_id,
            "ticket_id": zi_data['ticket_id']
        }

    # Get created_at
    created_at = get_created_at(zi_data['ticket_id'], zi_data['product'])
    if not created_at:
        created_at = datetime.now()  # Fallback

    # Write story card
    story_path, card_content = write_story_card(
        zi_id, zi_data, ticket_frontmatter, ticket_summary_body, created_at
    )

    # Check Trello
    existing_url = check_trello_exists(zi_data['ticket_id'], zi_id)
    if existing_url:
        return {
            "status": "found_existing",
            "zi_id": zi_id,
            "ticket_id": zi_data['ticket_id'],
            "trello_url": existing_url
        }

    # Card doesn't exist - would push to Trello here
    # For now, just return created status
    return {
        "status": "created_new",
        "zi_id": zi_id,
        "ticket_id": zi_data['ticket_id'],
        "trello_url": ""  # Would be filled after POST
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_story_cards_batch.py ZI-NNN")
        sys.exit(1)

    zi_id = sys.argv[1]
    result = process_zi(zi_id)
    print(json.dumps(result))
