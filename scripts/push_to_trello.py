#!/usr/bin/env python3
"""Push story cards to Trello StoryLab board."""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
STORIES_DIR = WIKI_ROOT / "wiki" / "product" / "stories"
SETTINGS_PATH = WIKI_ROOT / ".claude" / "settings.local.json"

# Load credentials
with open(SETTINGS_PATH) as f:
    settings = json.load(f)
    TRELLO_KEY = settings['env']['TRELLO_API_KEY']
    TRELLO_TOKEN = settings['env']['TRELLO_TOKEN']

BOARD_ID = "69dd9134576a26fcb79b670d"
TARGET_LANE_ID = "69dd9e0e8a7bb8b998765ee7"  # APR 25-30

# Label IDs
LABEL_IDS = {
    'shopify': '69dd9134576a26fcb79b6723',
    'woocommerce': '69dd9134576a26fcb79b6725',
    'magento': '69dd9134576a26fcb79b6727',
    'pain_10': '69dd9134576a26fcb79b6726',
    'pain_8-9': '69dd9134576a26fcb79b6724',
    'labels': '69dda3f5e846f4f43ea87d29',
    'carrier': '69dda3f5470641447a1bdc6e',
    'data': '69dda3f67c209e8d65dc7978',
    'intl': '69dda3f6e3f0ffaad39dfb82',
    'onboarding': '69dda3f73366b97280f973e1',
    'rates': '69dda3f75e4823b427cdec17',
    'requests': '69dda3f8fd2b781f799e7b1a',
}


def parse_story_card(zi_id):
    """Parse story card markdown to extract metadata and content."""
    story_path = STORIES_DIR / f"{zi_id}.md"
    if not story_path.exists():
        return None

    with open(story_path) as f:
        content = f.read()

    # Parse frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"')

    # Extract card content (everything between frontmatter and Cross-Links)
    body = parts[2].strip()
    if '## Cross-Links' in body:
        card_content = body.split('## Cross-Links')[0].strip()
    else:
        card_content = body

    # Extract title from frontmatter (already has ZI- prefix removed if present)
    title_raw = frontmatter.get('title', '')
    if title_raw.startswith(f'{zi_id} — '):
        title_clean = title_raw.replace(f'{zi_id} — ', '', 1)
    elif title_raw.startswith(f'"{zi_id} — '):
        title_clean = title_raw.replace(f'"{zi_id} — ', '', 1).rstrip('"')
    else:
        title_clean = title_raw.strip('"')

    return {
        'zi_id': zi_id,
        'ticket_id': frontmatter.get('ticket_id'),
        'product': frontmatter.get('product'),
        'theme': frontmatter.get('theme'),
        'pain': int(frontmatter.get('pain', 5)),
        'title': title_clean,
        'content': card_content
    }


def get_label_ids(card_data):
    """Determine which label IDs to apply."""
    labels = []

    # Product label
    product = card_data['product']
    if product in LABEL_IDS:
        labels.append(LABEL_IDS[product])

    # Pain label
    pain = card_data['pain']
    if pain >= 10:
        labels.append(LABEL_IDS['pain_10'])
    elif pain >= 8:
        labels.append(LABEL_IDS['pain_8-9'])

    # Theme label
    theme = card_data['theme']
    if theme in LABEL_IDS:
        labels.append(LABEL_IDS[theme])

    return labels


def push_to_trello(card_data):
    """Push a single card to Trello."""
    zi_id = card_data['zi_id']
    ticket_id = card_data['ticket_id']
    title = card_data['title']
    content = card_data['content']

    # Build card name
    card_name = f"{zi_id} — {title[:60]} [#{ticket_id}]"

    # Get labels
    label_ids = get_label_ids(card_data)

    # Build request
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = {
        "idList": TARGET_LANE_ID,
        "name": card_name,
        "desc": content,
        "idLabels": ','.join(label_ids),
        "pos": "bottom"
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result.get('shortUrl', '')
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP Error: {e.code} {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: push_to_trello.py ZI-NNN")
        sys.exit(1)

    zi_id = sys.argv[1]
    card_data = parse_story_card(zi_id)

    if not card_data:
        print(json.dumps({"status": "error", "message": "Failed to parse card"}))
        sys.exit(1)

    url = push_to_trello(card_data)

    if url:
        print(json.dumps({"status": "success", "zi_id": zi_id, "url": url}))
    else:
        print(json.dumps({"status": "error", "zi_id": zi_id}))
        sys.exit(1)
