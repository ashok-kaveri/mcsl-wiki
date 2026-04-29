#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# Usage: ./scripts/sync-zendesk-by-ids.sh <ticket_id1> <ticket_id2> ...
# Example: ./scripts/sync-zendesk-by-ids.sh 384139 302656 364411

if [ $# -eq 0 ]; then
  echo "Usage: $0 <ticket_id1> <ticket_id2> ..."
  echo "Example: $0 384139 302656 364411"
  exit 1
fi

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

# Product tag mappings (from sources.yaml)
SHOPIFY_TAG="shopify_multi_carrier_shipping_label_app"
OTHER_PLATFORM_TAGS=(
  "woocommerce_shipping_services"
  "fedex_amea_woocommerce_shipping_services"
  "magento_multi_carrier_shipping_label_app"
  "bigcommerce_multi_carrier_shipping_label_app"
  "storepep_shipping_solution"
  "bigcommerce_ship_rate_and_track_for_fedex"
)

# --- Helper: Determine product directory based on ticket tags ---
determine_product_dir() {
  local tags="$1"

  # Check for shopify tag
  if echo "$tags" | jq -e --arg tag "$SHOPIFY_TAG" 'any(. == $tag)' > /dev/null 2>&1; then
    echo "shopify"
    return
  fi

  # Check for other platform tags
  for tag in "${OTHER_PLATFORM_TAGS[@]}"; do
    if echo "$tags" | jq -e --arg tag "$tag" 'any(. == $tag)' > /dev/null 2>&1; then
      echo "other_platforms"
      return
    fi
  done

  # Default to other_platforms if no match
  echo "other_platforms"
}

# --- Fetch each ticket by ID ---
total=$#
count=0
success_count=0
skipped_count=0
error_count=0

echo "Fetching $total ticket(s) from Zendesk..."
echo ""

for tid in "$@"; do
  count=$((count + 1))

  echo "[$count/$total] Fetching ticket #$tid..."

  # Fetch ticket details
  ticket_response=$(curl -s "$BASE_URL/tickets/$tid.json" -u "$AUTH")

  # Check if ticket exists
  error=$(echo "$ticket_response" | jq -r '.error // ""')
  if [ -n "$error" ]; then
    echo "  ❌ ERROR: $error"
    error_count=$((error_count + 1))
    continue
  fi

  # Extract ticket data
  ticket=$(echo "$ticket_response" | jq '.ticket')
  tags=$(echo "$ticket" | jq -r '.tags')
  support_type=$(echo "$ticket" | jq -r '.support_type // "unknown"')
  status=$(echo "$ticket" | jq -r '.status')

  # Skip if not support_type=agent
  if [ "$support_type" != "agent" ]; then
    echo "  ⏭️  Skipped (support_type=$support_type, want agent)"
    skipped_count=$((skipped_count + 1))
    continue
  fi

  # Determine product directory
  product_dir=$(determine_product_dir "$tags")
  ZENDESK_DIR="$ZENDESK_BASE/$product_dir"
  mkdir -p "$ZENDESK_DIR"

  # Fetch comments
  comments_response=$(curl -s "$BASE_URL/tickets/$tid/comments.json" -u "$AUTH")
  comments=$(echo "$comments_response" | jq '.comments')

  # Save to JSON file
  jq -n --argjson t "$ticket" --argjson c "$comments" \
    '{ticket: $t, comments: $c}' \
    > "$ZENDESK_DIR/$tid.json"

  echo "  ✅ Saved to $ZENDESK_DIR/$tid.json (status: $status, product: $product_dir)"
  success_count=$((success_count + 1))
done

echo ""
echo "================================================================================"
echo "SYNC SUMMARY"
echo "================================================================================"
echo "Total requested: $total"
echo "Successfully synced: $success_count"
echo "Skipped (support_type≠agent): $skipped_count"
echo "Errors: $error_count"
echo ""

if [ $success_count -gt 0 ]; then
  echo "✅ Synced $success_count ticket(s) to raw/zendesk/"
  echo ""
  echo "Next steps:"
  echo "  1. Run: /zendesk-summarize delta"
  echo "  2. Run: /story-cards delta"
fi
