---
name: single-ticket
description: Fetch a Zendesk ticket and its full history. Use when the user asks to look up, show, or get a Zendesk ticket, or mentions a ticket ID.
argument-hint: <ticket-id>
allowed-tools: Bash
disable-model-invocation: true
---

# Zendesk Ticket Info

Fetch ticket **$ARGUMENTS** from Zendesk and present a clear summary.

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

## Output format

Present results as:

**Ticket #$ARGUMENTS — `<subject>`**
- Status / Priority / Type
- Requester | Assignee | Group
- Created / Updated

**Conversation** — comments in chronological order with author, timestamp, and body (public vs internal noted)

**History** — audit events summarising field changes and status transitions (skip no-op events)

If a required env var is missing or the API returns 401/404, clearly state what went wrong and point to the setup instructions above.
