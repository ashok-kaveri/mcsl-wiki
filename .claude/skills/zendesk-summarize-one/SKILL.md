---
name: zendesk-summarize-one
description: Summarize a single Zendesk ticket from raw JSON into a structured wiki summary. Use when the user wants to quickly summarize one specific ticket without running the full pipeline.
argument-hint: <ticketId>
allowed-tools: Bash, Write, Read, Glob
---

# Zendesk Single Ticket Summarizer

Process one specific Zendesk ticket from `raw/zendesk/**/<ticketId>.json` into a structured summary at `wiki/zendesk/summaries/<ticketId>.md`.

**Argument**: `$ARGUMENTS` — the ticket ID to summarize

**Key difference from `/zendesk-summarize`**: This skill processes only one ticket and does NOT update the daily index. Use this for quick ticket reviews or when you want to re-summarize one ticket without touching the pipeline.

---

## Step 1: Locate the ticket JSON

Search for `$ARGUMENTS.json` across all product directories:

```bash
find raw/zendesk -name "$ARGUMENTS.json" -type f
```

If not found, report: "Ticket $ARGUMENTS not found in raw/zendesk/. Check if the ticket exists or sync raw data."

If found, note the full path to determine the product.

## Step 2: Read and parse the ticket

Read the full JSON in one pass using Python:

```bash
python3 -c "
import json, sys
from datetime import datetime

ticket_path = sys.argv[1]
data = json.load(open(ticket_path))
ticket = data['ticket']
comments = data.get('comments', [])

# Print ticket metadata
print(f'Subject: {ticket.get(\"subject\", \"(no subject)\")}')
print(f'Status: {ticket.get(\"status\", \"unknown\")}')
print(f'Created: {ticket.get(\"created_at\", \"unknown\")}')
print(f'Updated: {ticket.get(\"updated_at\", \"unknown\")}')
print(f'Requester: {ticket.get(\"requester\", {}).get(\"name\", \"unknown\")}')
print(f'Tags: {ticket.get(\"tags\", [])}')
print(f'Comments: {len(comments)}')
print()
print('---COMMENTS---')
for i, c in enumerate(comments, 1):
    author = c.get('author', {}).get('name', 'unknown')
    created = c.get('created_at', '')
    body = c.get('body', '')
    is_public = c.get('public', True)
    visibility = 'PUBLIC' if is_public else 'INTERNAL'
    print(f'[{i}] {visibility} | {author} | {created}')
    print(body[:200] + ('...' if len(body) > 200 else ''))
    print()
" "<path-to-ticket.json>"
```

## Step 3: Determine product

From the ticket path:
- `raw/zendesk/shopify/` → product: `shopify`
- `raw/zendesk/other_platforms/` → derive from tags:
  - `woocommerce_shipping_services` → `woocommerce`
  - `magento_multi_carrier_shipping_label_app` → `magento`
  - `bigcommerce_shipping_label_app` → `bigcommerce`
  - `storepep_saas` → `storepep`
  - `fedex_amea` → `fedex-amea`
  - Default to `other_platforms` if unclear

## Step 4: Analyze and summarize

**CRITICAL**: Consult `@docs/lessons_learned_zendesk_summarize.md` for best practices, especially:
- Priority reading order for large tickets (L3 comments first)
- How to handle numbered lists in L3 escalations (each item = distinct issue)
- Search patterns for `dev_needed` tickets

Read through the comments (in reverse to find current state, then forward for timeline) and identify:

1. **Timeline & Key Phases**: Major phases of the ticket lifecycle (initial request, investigation, escalation, resolution)
2. **Open Issues**: Current blockers, unresolved problems, pending requests
   - Each issue must include:
     - Clear title
     - Description
     - Who is blocked (customer/support/engineering)
     - Severity signal (P1/P2/critical/minor)
     - Feature area tag (see list below)
     - Comment citation
3. **Resolved Issues**: Problems that were fixed, with how/when
4. **Customer Context**: Store name, business type, shipping volume, any special circumstances

**Feature area tags**:
- `onboarding` — installation, setup, welcome tickets, uninstalls
- `carrier-config` — carrier-specific setup, credentials, account issues
- `carrier-migration` — API migrations (e.g., FedEx SOAP→REST)
- `label-generation` — label creation, manifests, label errors
- `rate-shopping` — rate fetch, rate display, rate rules
- `tracking` — shipment tracking, status updates
- `returns` — return label generation, return tracking
- `international` — customs, dangerous goods, country of manufacture, commercial invoices
- `order-management` — order data, line items, order errors
- `product-management` — product import, product data
- `feature-request` — customer feature suggestions
- `other` — uncategorized / multi-issue

**Lifecycle-only tickets**: If the ticket is just installation welcome or uninstall win-back with no substantive customer reply, write: "No open issues — lifecycle-only ticket."

## Step 4.5: Quality Gate (MANDATORY)

**EVERY summary MUST pass these checks before writing. If ANY check fails, REWRITE the summary.**

### Title Quality Checklist

- [ ] **NOT a question or email subject** — Transform into actionable statement
  - ❌ Bad: "Give the WooCommerce Shipping Services Plugin another try? We can extend the free trial."
  - ✅ Good: "Customer requesting free trial extension to re-evaluate WooCommerce plugin"
  - ❌ Bad: "FW: FW: [##31020##] Your ticket has been Closed"
  - ✅ Good: "Customer following up on closed ticket #31020"
- [ ] **Describes the core issue/request** — Not the email metadata
  - ❌ Bad: "Welcome to PluginHive! We're here to help you save both time and money."
  - ✅ Good: "New WooCommerce installation onboarding"
  - ❌ Bad: "another new site"
  - ✅ Good: "Support request for new WooCommerce store setup"
- [ ] **Concise and specific** — Under 80 characters, actionable
  - ❌ Bad: "RE: [PluginHive] Re: Can you help me set up live rate calculations on ..."
  - ✅ Good: "Live rate calculation setup assistance needed"

### Timeline Quality Checklist

- [ ] **NO "Full analysis pending"** — Must have actual phases with events
  - ❌ Bad: "*Auto-generated summary from N comments. Full analysis pending.*"
  - ✅ Good: "### Phase 1: Initial Request (2026-04-13)\n- Customer reports label failures..."
- [ ] **Chronological phases** — Group comments into meaningful phases
  - ✅ Good: "Phase 1: Initial Request → Phase 2: Investigation → Phase 3: Escalation"
- [ ] **Key events extracted** — Not every comment, just significant changes
  - ✅ Good: "Customer escalated to phone request after 3 days no response"

### Open Issues Quality Checklist

- [ ] **NOT copy/paste of title** — Each issue is distinct analysis
  - ❌ Bad: Open issue title identical to ticket title
  - ✅ Good: "Label generation timeout for orders >50 items (customer ships 200/day)"
- [ ] **Has all required fields** — Title, description, blocked, severity, area, comment citation
  - ✅ Each issue includes: who's blocked, severity signal, area tag, comment #
- [ ] **Proper area tagging** — Not generic "other" unless truly uncategorized
  - ❌ Bad: "Give plugin another try" → `carrier-config`
  - ✅ Good: "Give plugin another try" → `onboarding`
- [ ] **Lifecycle tickets identified** — If no substantive reply, mark as lifecycle-only
  - ✅ Good: "No open issues — lifecycle-only ticket (installation welcome)"

### Customer Context Quality Checklist

- [ ] **NOT "unknown"** — Extract from ticket or mark as not available
  - ❌ Bad: "Store: unknown"
  - ✅ Good: "Store: not provided in ticket" OR actual store name from comments
- [ ] **Actual context extracted** — Volume, plan, setup, pain points
  - ❌ Bad: Just product name
  - ✅ Good: "50 orders/day, uses FedEx+USPS, international to Canada primarily"

### ENFORCEMENT

**If summary fails ANY check:**
1. **STOP** — do not write summary file
2. **REWRITE** — title, timeline, open issues, or customer context
3. **RE-VALIDATE** — run through checklist again
4. **ONLY THEN WRITE**

**This is non-negotiable.** Poor summaries waste PM time and create bad story cards downstream.

---

## Step 5: Write the summary file

Create or overwrite `wiki/zendesk/summaries/$ARGUMENTS.md`:

```markdown
---
title: "Ticket #<id> — <subject>"
ticket_id: <id>
product: <shopify|woocommerce|magento|bigcommerce|storepep|fedex-amea|other_platforms>
status: <open|new|pending|on-hold|closed|solved>
customer: <name> (<store>)
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_updated: <today YYYY-MM-DD>
---

# Ticket #<id> — <subject>

- **Customer**: <name> (<store>)
- **Product**: <full product name>
- **Duration**: <created-date> to <updated-date or "ongoing"> (<N days>)

## Timeline & Key Phases

### Phase 1: <title> (<date range>)
- <key events in chronological order>
- <focus on significant changes, not every comment>

### Phase 2: <title> (<date range>)
- ...

## Open Issues

1. **<Issue Title>** — <description of the problem>. Blocked: <customer|support|engineering>. Severity: <signal from comments>. Area: <feature-area-tag>. (Comment #N)

(Or: "No open issues — lifecycle-only ticket." / "No open issues — all resolved.")

## Resolved Issues

1. **<Issue Title>** — <how it was resolved> on <date>. (Comment #N)

(Or: "No resolved issues documented." if the ticket had no technical issues)

## Customer Context

- **Store**: <store name/URL if available>
- **Business type**: <if mentioned — e.g., "apparel retailer", "electronics", "B2B">
- **Shipping volume**: <if mentioned — e.g., "50 orders/day", "seasonal spikes">
- **Technical setup**: <relevant details — e.g., "uses FedEx + USPS", "international only">
- **Other context**: <any special circumstances, SLAs, VIP status, etc.>
```

## Step 6: Report

Print:
- "✅ Summarized ticket #$ARGUMENTS"
- "📄 Summary: wiki/zendesk/summaries/$ARGUMENTS.md"
- "🔍 Product: <product-name>"
- "📊 Open issues: N | Resolved issues: N"
- "🏷️ Areas: <list of feature area tags>"

**Note**: This skill does NOT update the daily index (`wiki/zendesk/YYYY-MM-DD.md`). To incorporate this ticket into the index, run `/zendesk-summarize delta`.

---

## Example Usage

```
/zendesk-summarize-one 383750
```

This will:
1. Find `raw/zendesk/shopify/383750.json` (or other_platforms)
2. Parse the ticket and all comments
3. Create/update `wiki/zendesk/summaries/383750.md` with structured analysis
4. Report summary stats

Use this for:
- Quick ticket review without running full pipeline
- Re-summarizing one ticket after raw JSON updates
- Spot-checking ticket data before full extraction
