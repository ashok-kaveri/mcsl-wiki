---
name: single-ticket
description: Fetch a Zendesk ticket and its full history, then update the wiki summary. Use when the user asks to look up, show, or get a Zendesk ticket, or mentions a ticket ID.
argument-hint: <ticket-id>
allowed-tools: Bash, Write, Read, Edit, Glob, Grep
---

# Zendesk Ticket Info

Fetch ticket **$ARGUMENTS** from Zendesk, present a summary, and update the wiki.

## Setup (one-time per team member)

Add credentials to `~/.claude/settings.json`:

```json
{
  "env": {
    "ZENDESK_SUBDOMAIN": "your-subdomain",
    "ZENDESK_EMAIL": "your-email@company.com",
    "ZENDESK_API_TOKEN": "your-api-token"
  }
}
```

Get your API token at: Zendesk Admin > Apps & Integrations > APIs > Zendesk API > Add API token

---

## Steps

### Step 1: Fetch ticket data

Run these three API calls using the `$ZENDESK_SUBDOMAIN`, `$ZENDESK_EMAIL`, and `$ZENDESK_API_TOKEN` environment variables:

**1. Ticket details:**
```bash
curl -s "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/tickets/$ARGUMENTS.json" \
  -u "$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
```

**2. Comments (conversation):**
```bash
curl -s "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/tickets/$ARGUMENTS/comments.json" \
  -u "$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
```

**3. Audits (field changes, status transitions):**
```bash
curl -s "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/tickets/$ARGUMENTS/audits.json" \
  -u "$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
```

### Step 2: Present summary

Present results as:

**Ticket #$ARGUMENTS — `<subject>`**
- Status / Priority / Type
- Requester | Assignee | Group
- Created / Updated

**Conversation** — comments in chronological order with author, timestamp, and body (public vs internal noted)

**History** — audit events summarising field changes and status transitions (skip no-op events)

### Step 3: Update wiki summary

After presenting the ticket, write or update `wiki/zendesk/summaries/$ARGUMENTS.md` with this structure:

```markdown
---
title: "Ticket #<id> — <subject>"
ticket_id: <id>
status: <open|new|closed>
customer: <name> (<store>)
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_updated: <today>
---

# Ticket #<id> — <subject>

- **Customer**: <name> (<store>)
- **Duration**: <dates> (<ongoing|resolved>)

## Timeline & Key Phases

### Phase 1: <title> (<dates>)
- <key events>

## Open Issues

1. **<Title>** — <description>. Blocked: <who>. Severity: <signal>. Area: <feature-area-tag>. (Comment #N)

(If none: "No open issues — lifecycle-only.")

## Resolved Issues

1. **<Title>** — <how/when>. (Comment #N)

## Customer Context

- <details>
```

**Summarization rules:**
- Open issues = LATEST state only (L3 escalations, pending requests, unresolved blockers). NOT a replay of every comment.
- Each open issue MUST cite the comment number and include: title, who's blocked, severity signal, feature area tag.
- Feature area tags: onboarding, carrier-config, carrier-migration, label-generation, rate-shopping, tracking, returns, international, order-management, product-management, feature-request
- Lifecycle-only tickets get: "No open issues — lifecycle-only ticket."

If a required env var is missing or the API returns 401/404, clearly state what went wrong and point to the setup instructions above.
