#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# --- Load env vars from .claude/settings.json (non-sensitive) ---
if [ -f ".claude/settings.json" ]; then
  while IFS= read -r line; do
    if [[ "$line" =~ \"(ZENDESK_SUBDOMAIN|ZENDESK_EMAIL)\":[[:space:]]*\"([^\"]+)\" ]]; then
      export "${BASH_REMATCH[1]}"="${BASH_REMATCH[2]}"
    fi
  done < ".claude/settings.json"
fi

# --- Load API token from .claude/settings.local.json (sensitive) ---
if [ -f ".claude/settings.local.json" ]; then
  while IFS= read -r line; do
    if [[ "$line" =~ \"(ZENDESK_API_TOKEN)\":[[:space:]]*\"([^\"]+)\" ]]; then
      export "${BASH_REMATCH[1]}"="${BASH_REMATCH[2]}"
    fi
  done < ".claude/settings.local.json"
fi

# --- Config ---
ZENDESK_DIR="raw/zendesk"
LAST_SYNC_FILE="$ZENDESK_DIR/.last_sync"
SEARCH_TAG="shopify_multi_carrier_shipping_label_app"

# --- Validate env vars ---
for var in ZENDESK_SUBDOMAIN ZENDESK_EMAIL ZENDESK_API_TOKEN; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: $var is not set." >&2
    echo "  ZENDESK_SUBDOMAIN, ZENDESK_EMAIL → .claude/settings.json" >&2
    echo "  ZENDESK_API_TOKEN               → .claude/settings.local.json" >&2
    exit 1
  fi
done

AUTH="$ZENDESK_EMAIL/token:$ZENDESK_API_TOKEN"
BASE_URL="https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2"

mkdir -p "$ZENDESK_DIR"

# --- Determine date range ---
if [ -n "${1:-}" ]; then
  start_date="$1"
elif [ -f "$LAST_SYNC_FILE" ]; then
  start_date=$(cat "$LAST_SYNC_FILE")
else
  start_date=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d '30 days ago' +%Y-%m-%d)
fi

end_date=$(date +%Y-%m-%d)

echo "==> Fetching open MCSL tickets: $start_date to $end_date"

# --- Search for tickets (with pagination) ---
ticket_ids=()
page_url="$BASE_URL/search.json"
page_num=1

while [ -n "$page_url" ] && [ "$page_url" != "null" ]; do
  echo "  Fetching search results (page $page_num)..."

  if [ "$page_num" -eq 1 ]; then
    response=$(curl -s -G "$page_url" \
      --data-urlencode "query=type:ticket status:open tags:$SEARCH_TAG created>=$start_date created<=$end_date" \
      --data-urlencode "sort_by=created_at" \
      --data-urlencode "sort_order=desc" \
      -u "$AUTH")
  else
    response=$(curl -s "$page_url" -u "$AUTH")
  fi

  ids=$(echo "$response" | jq -r '.results[].id')

  while IFS= read -r id; do
    [ -n "$id" ] && ticket_ids+=("$id")
  done <<< "$ids"

  page_url=$(echo "$response" | jq -r '.next_page // ""')

  page_num=$((page_num + 1))
done

total=${#ticket_ids[@]}
echo "  Found $total tickets"

if [ "$total" -eq 0 ]; then
  echo "  No tickets to sync."
  echo "$end_date" > "$LAST_SYNC_FILE"
  echo "==> Updated last sync date to $end_date"
  exit 0
fi

# --- Fetch each ticket's details + comments ---
count=0
for tid in "${ticket_ids[@]}"; do
  count=$((count + 1))
  echo "  [$count/$total] Fetching ticket #$tid..."

  ticket=$(curl -s "$BASE_URL/tickets/$tid.json" -u "$AUTH")
  comments=$(curl -s "$BASE_URL/tickets/$tid/comments.json" -u "$AUTH")

  jq -n --argjson t "$ticket" --argjson c "$comments" \
    '{ticket: $t.ticket, comments: $c.comments}' \
    > "$ZENDESK_DIR/$tid.json"
done

# --- Update last sync date ---
echo "$end_date" > "$LAST_SYNC_FILE"

echo "==> Synced $total tickets to $ZENDESK_DIR/"
echo "==> Updated last sync date to $end_date"
