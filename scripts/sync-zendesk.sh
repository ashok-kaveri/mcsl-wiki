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

# --- Read product sync definitions from sources.yaml ---
SOURCES_YAML="raw/sources.yaml"
if [ ! -f "$SOURCES_YAML" ]; then
  echo "ERROR: $SOURCES_YAML not found." >&2
  exit 1
fi

# Extract product keys from zendesk.products
PRODUCT_KEYS=$(yq '.sources.zendesk.products | keys | .[]' "$SOURCES_YAML")
if [ -z "$PRODUCT_KEYS" ]; then
  echo "ERROR: No products found in $SOURCES_YAML under sources.zendesk.products" >&2
  exit 1
fi

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

ZENDESK_BASE="raw/zendesk"

# --- Sync each product ---
for subdir in $PRODUCT_KEYS; do
  product_path=".sources.zendesk.products.$subdir"

  # Read filters string and extract query filter (strip support_type if present — that's a post-filter)
  raw_filters=$(yq "$product_path.filters" "$SOURCES_YAML")
  query_filter=$(echo "$raw_filters" | sed 's/,\{0,1\} *support_type=[^ ,]*//' | sed 's/^ *//' | sed 's/ *$//')
  # Check if support_type=agent post-filter is required
  post_filter_agent=false
  if echo "$raw_filters" | grep -q 'support_type=agent'; then
    post_filter_agent=true
  fi

  # Read tags — supports both single "tag" field and "tags" array
  single_tag=$(yq "$product_path.tag // \"\"" "$SOURCES_YAML")
  tags_array=$(yq "$product_path.tags // [] | .[]" "$SOURCES_YAML" 2>/dev/null || true)

  # Build tag query for Zendesk search
  # Single tag: tags:foo
  # Multiple tags: tags:foo tags:bar (OR logic in Zendesk search)
  tag_query=""
  if [ -n "$single_tag" ]; then
    tag_query="tags:$single_tag"
  elif [ -n "$tags_array" ]; then
    # Multiple tags — Zendesk search OR: wrap in parentheses
    tag_parts=""
    while IFS= read -r t; do
      [ -n "$t" ] && tag_parts="${tag_parts:+$tag_parts OR }tags:$t"
    done <<< "$tags_array"
    tag_query="($tag_parts)"
  else
    echo "WARNING: [$subdir] No tag or tags defined, skipping." >&2
    continue
  fi

  ZENDESK_DIR="$ZENDESK_BASE/$subdir"
  LAST_SYNC_FILE="$ZENDESK_DIR/.last_sync"

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

  echo "==> [$subdir] Fetching tickets: $start_date to $end_date"
  echo "    Filter: $query_filter $tag_query"

  # --- Search for tickets (with pagination) ---
  ticket_ids=()
  page_url="$BASE_URL/search.json"
  page_num=1

  while [ -n "$page_url" ] && [ "$page_url" != "null" ]; do
    echo "  Fetching search results (page $page_num)..."

    if [ "$page_num" -eq 1 ]; then
      response=$(curl -s -G "$page_url" \
        --data-urlencode "query=type:ticket $query_filter $tag_query created>=$start_date created<=$end_date" \
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
    echo "==> [$subdir] Updated last sync date to $end_date"
    continue
  fi

  # --- Fetch each ticket's details + comments ---
  count=0
  new_count=0
  for tid in "${ticket_ids[@]}"; do
    count=$((count + 1))

    # Skip if ticket already exists (delta sync)
    if [ -f "$ZENDESK_DIR/$tid.json" ]; then
      echo "  [$count/$total] Skipping #$tid (already synced)"
      continue
    fi

    echo "  [$count/$total] Fetching ticket #$tid..."

    ticket=$(curl -s "$BASE_URL/tickets/$tid.json" -u "$AUTH")
    comments=$(curl -s "$BASE_URL/tickets/$tid/comments.json" -u "$AUTH")

    # Post-filter: only save tickets with support_type=agent (when configured)
    if [ "$post_filter_agent" = true ]; then
      support_type=$(echo "$ticket" | jq -r '.ticket.support_type // "unknown"')
      if [ "$support_type" != "agent" ]; then
        echo "  [$count/$total] Skipping #$tid (support_type=$support_type, want agent)"
        continue
      fi
    fi

    jq -n --argjson t "$ticket" --argjson c "$comments" \
      '{ticket: $t.ticket, comments: $c.comments}' \
      > "$ZENDESK_DIR/$tid.json"

    new_count=$((new_count + 1))
  done

  # --- Update last sync date ---
  echo "$end_date" > "$LAST_SYNC_FILE"

  echo "==> [$subdir] Synced $new_count new tickets to $ZENDESK_DIR/ ($total total matched)"
  echo "==> [$subdir] Updated last sync date to $end_date"
done
