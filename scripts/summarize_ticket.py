#!/usr/bin/env python3
"""
Step 1: Summarize a single Zendesk ticket from JSON to markdown.

Usage: python summarize_ticket.py <path/to/ticket.json>
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def normalize_title(title):
    """Normalize issue title for duplicate detection."""
    # Lowercase
    title = title.lower()
    # Remove punctuation
    title = re.sub(r'[^\w\s]', '', title)
    # Collapse whitespace
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def derive_product(json_path, ticket_data):
    """Derive product from directory structure or tags."""
    path_str = str(json_path)

    # Check directory
    if '/shopify/' in path_str:
        return 'shopify'

    # Check tags for other_platforms
    tags = ticket_data.get('ticket', {}).get('tags', [])

    for tag in tags:
        if tag.startswith('woocommerce'):
            return 'woocommerce'
        if tag.startswith('magento'):
            return 'magento'

    # Check custom_fields for product_name
    custom_fields = ticket_data.get('ticket', {}).get('custom_fields', [])
    for field in custom_fields:
        if field.get('id') == 360008205591:  # product_name field
            value = field.get('value', '')
            if 'shopify' in value:
                return 'shopify'
            if 'woocommerce' in value:
                return 'woocommerce'
            if 'magento' in value:
                return 'magento'

    return 'unknown'


def extract_area_tag(comment_text):
    """Extract feature area tag from comment text (basic heuristic)."""
    text_lower = comment_text.lower()

    # Pattern matching for area detection
    area_map = {
        'label-generation': ['label', 'packing slip', 'manifest', 'print'],
        'carrier-config': ['carrier', 'service', 'ups', 'fedex', 'usps', 'dhl'],
        'product-management': ['product', 'variant', 'sku', 'import'],
        'order-management': ['order', 'sync', 'queue'],
        'rate-shopping': ['rate', 'shipping rate', 'checkout'],
        'tracking': ['tracking', 'track'],
        'international': ['customs', 'duty', 'hs code', 'commercial invoice'],
        'onboarding': ['onboarding', 'account', 'billing', 'subscription', 'plan'],
        'feature-request': ['feature request', 'enhancement', 'would like'],
    }

    for area, keywords in area_map.items():
        for keyword in keywords:
            if keyword in text_lower:
                return area

    return 'other'


def extract_severity(comment_text):
    """Extract severity signal from comment text."""
    text_lower = comment_text.lower()

    if any(word in text_lower for word in ['critical', 'urgent', 'blocking', 'cannot ship']):
        return 'H'
    if any(word in text_lower for word in ['important', 'needed', 'workaround']):
        return 'M'

    return 'L'


def parse_ticket(json_path):
    """Parse ticket JSON and extract key information."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    ticket = data.get('ticket', {})
    comments = data.get('comments', [])

    ticket_id = ticket.get('id')
    subject = ticket.get('subject', '')[:100]  # Truncate long subjects
    status = ticket.get('status', 'unknown')
    created_at = ticket.get('created_at', '')
    updated_at = ticket.get('updated_at', '')

    # Parse dates
    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d') if created_at else 'unknown'
    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00')).strftime('%Y-%m-%d') if updated_at else 'unknown'

    # Derive product
    product = derive_product(json_path, data)

    # Get customer info (requester)
    requester_id = ticket.get('requester_id')
    customer_name = f"User {requester_id}" if requester_id else "Unknown"

    # Extract custom fields for store name
    store_name = "unknown"
    custom_fields = ticket.get('custom_fields', [])
    for field in custom_fields:
        if field.get('id') == 360030770052:  # Store URL field
            store_name = field.get('value', 'unknown') or 'unknown'
            break

    # Process comments in reverse to find open issues
    open_issues = []

    # Read comments in reverse (latest first)
    for idx, comment in enumerate(reversed(comments)):
        comment_id = comment.get('id')
        author_id = comment.get('author_id')
        body = comment.get('body', '')

        # Skip if empty
        if not body or len(body.strip()) < 10:
            continue

        # Extract potential issues from recent comments (last 10)
        if idx < 10 and status in ['open', 'pending', 'new']:
            # Look for issue patterns
            if any(keyword in body.lower() for keyword in ['issue', 'problem', 'error', 'not working', 'failed', 'missing']):
                # Extract issue title (first sentence or first 100 chars)
                issue_title = body.split('.')[0][:100].strip()

                if issue_title and len(issue_title) > 10:
                    normalized = normalize_title(issue_title)

                    # Avoid duplicates
                    if not any(normalize_title(iss['title']) == normalized for iss in open_issues):
                        area = extract_area_tag(body)
                        severity = extract_severity(body)

                        open_issues.append({
                            'title': issue_title,
                            'normalized_title': normalized,
                            'area': area,
                            'severity': severity,
                            'blocked_by': 'unknown',
                            'comment_id': comment_id
                        })

    # If no issues found but ticket is open, create a generic one
    if not open_issues and status in ['open', 'pending', 'new']:
        # Use subject as issue
        issue_title = subject[:100]
        open_issues.append({
            'title': issue_title,
            'normalized_title': normalize_title(issue_title),
            'area': extract_area_tag(subject),
            'severity': 'M',
            'blocked_by': 'customer' if status == 'pending' else 'support',
            'comment_id': comments[-1].get('id') if comments else 0
        })

    return {
        'ticket_id': ticket_id,
        'subject': subject,
        'status': status,
        'product': product,
        'created_date': created_date,
        'updated_date': updated_date,
        'customer_name': customer_name,
        'store_name': store_name,
        'open_issues': open_issues,
        'comment_count': len(comments)
    }


def generate_summary_markdown(ticket_info):
    """Generate markdown summary from ticket info."""
    today = datetime.now().strftime('%Y-%m-%d')

    lines = []
    lines.append('---')
    lines.append(f'title: "Ticket #{ticket_info["ticket_id"]} — {ticket_info["subject"]}"')
    lines.append(f'ticket_id: {ticket_info["ticket_id"]}')
    lines.append(f'product: {ticket_info["product"]}')
    lines.append(f'status: {ticket_info["status"]}')
    lines.append(f'customer: {ticket_info["customer_name"]} ({ticket_info["store_name"]})')
    lines.append(f'created: {ticket_info["created_date"]}')
    lines.append(f'updated: {ticket_info["updated_date"]}')
    lines.append(f'last_updated: {today}')
    lines.append('---')
    lines.append('')
    lines.append(f'# Ticket #{ticket_info["ticket_id"]} — {ticket_info["subject"]}')
    lines.append('')
    lines.append(f'- **Customer**: {ticket_info["customer_name"]} ({ticket_info["store_name"]})')
    lines.append(f'- **Product**: {ticket_info["product"]}')
    lines.append(f'- **Status**: {ticket_info["status"]}')
    lines.append(f'- **Duration**: {ticket_info["created_date"]} to {ticket_info["updated_date"]}')
    lines.append('')
    lines.append('## Timeline & Key Phases')
    lines.append('')
    lines.append(f'*Auto-generated summary from {ticket_info["comment_count"]} comments. Full analysis pending.*')
    lines.append('')

    if ticket_info['open_issues']:
        lines.append('## Open Issues')
        lines.append('')
        for idx, issue in enumerate(ticket_info['open_issues'], 1):
            lines.append(f'{idx}. **{issue["title"]}** — ')
            lines.append(f'   Blocked: {issue["blocked_by"]}. Severity: {issue["severity"]}. ')
            lines.append(f'   Area: `{issue["area"]}`. (Comment #{issue["comment_id"]})')
            lines.append('')
    else:
        lines.append('## Open Issues')
        lines.append('')
        lines.append('No open issues — lifecycle-only ticket or resolved.')
        lines.append('')

    lines.append('## Customer Context')
    lines.append('')
    lines.append(f'- Store: {ticket_info["store_name"]}')
    lines.append(f'- Product: {ticket_info["product"]}')
    lines.append('')

    return '\n'.join(lines)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/ticket.json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    # Parse ticket
    ticket_info = parse_ticket(json_path)

    # Generate markdown
    markdown = generate_summary_markdown(ticket_info)

    # Write to wiki/zendesk/summaries/
    output_dir = Path(__file__).parent.parent / 'wiki' / 'zendesk' / 'summaries'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f'{ticket_info["ticket_id"]}.md'

    with open(output_path, 'w') as f:
        f.write(markdown)

    print(f"✓ {ticket_info['ticket_id']}: {ticket_info['status']}, {len(ticket_info['open_issues'])} issues, {ticket_info['product']}")


if __name__ == '__main__':
    main()
