---
name: mcsl-open-tickets
description: Fetch all open Zendesk tickets for the Shopify Multi Carrier Shipping Label app within a date range. Use when looking up MCSL open tickets, checking the support queue for the shipping label app, or reviewing recent customer issues.
argument-hint: <start-date> <end-date>
allowed-tools: Bash
disable-model-invocation: true
---

# MCSL Open Tickets

Fetch all open Zendesk tickets for the **Shopify Multi Carrier Shipping Label** app between **$ARGUMENTS**.

The arguments are two dates in YYYY-MM-DD format: `<start-date> <end-date>`.

## Setup

Same credentials as the zendesk-search skill. Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "ZENDESK_SUBDOMAIN": "your-subdomain",
    "ZENDESK_EMAIL": "your-email@company.com",
    "ZENDESK_API_TOKEN": "your-api-token"
  }
}
```

---

## Steps

Parse the two dates from `$ARGUMENTS` (space-separated: `start end`).

Run the search API call, fetching all pages. Zendesk returns max 100 results per page, so loop until there's no `next_page`.

**First page:**
```bash
curl -s -G "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/search.json" \
  --data-urlencode "query=type:ticket status:open tags:shopify_multi_carrier_shipping_label_app created>={START_DATE} created<={END_DATE}" \
  --data-urlencode "sort_by=created_at" \
  --data-urlencode "sort_order=desc" \
  -u "$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
```

**Subsequent pages** (if `next_page` is present in the response):
```bash
curl -s "{next_page_url}" -u "$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
```

Keep fetching until `next_page` is null. Collect all results across pages.

## Output format

Present all results as a markdown table:

| # | Ticket | Subject | Priority | Requester ID | Created | Updated |
|---|--------|---------|----------|--------------|---------|---------|
| 1 | #12345 | Subject line (truncated to 60 chars) | high | 12345678 | 2026-04-07 | 2026-04-08 |

After the table, show:
- **Total**: N open MCSL tickets between {start} and {end}
- **Date range**: {start} to {end}

If no tickets are found, say so and confirm the date range.

If a required env var is missing or the API returns an error, state what went wrong and point to the setup section.
