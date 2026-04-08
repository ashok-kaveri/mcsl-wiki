---
name: zendesk-search
description: Search and filter Zendesk tickets by any criteria. Use this whenever the user wants to find tickets, look up recent issues, search by status/assignee/tag/date, list open tickets, or query their Zendesk support queue — even if they don't say "search" explicitly.
argument-hint: <search-query>
allowed-tools: Bash
---

# Zendesk Ticket Search

Search Zendesk tickets using the query **$ARGUMENTS**.

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

Run the search API call using the `$ZENDESK_SUBDOMAIN`, `$ZENDESK_EMAIL`, and `$ZENDESK_API_TOKEN` environment variables:

```bash
curl -s -G "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/search.json" \
  --data-urlencode "query=type:ticket $ARGUMENTS" \
  --data-urlencode "sort_by=updated_at" \
  --data-urlencode "sort_order=desc" \
  -u "$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
```

The `type:ticket` prefix is added automatically so users don't need to include it. The query uses Zendesk's search syntax — common patterns:

- `status:open` — all open tickets
- `assignee:me` — tickets assigned to the authenticated user
- `tags:urgent` — tickets tagged "urgent"
- `created>2026-01-01` — tickets created after a date
- `subject:refund` — tickets with "refund" in the subject
- `priority:high status:open` — combine multiple filters

If the response includes `next_page`, there are more results. Mention how many total results (`count` field) and that only the first page is shown.

## Output format

Present results as a table:

| # | Ticket | Status | Priority | Requester | Assignee | Updated |
|---|--------|--------|----------|-----------|----------|---------|
| 1 | #12345 — Subject line | open | high | requester name | assignee name | 2026-04-07 |

After the table, show:
- **Total results**: N tickets found
- **Showing**: first N of M (if paginated)

If no results are found, say so clearly and suggest broadening the query.

If a required env var is missing or the API returns 401/404, clearly state what went wrong and point to the setup instructions above.
