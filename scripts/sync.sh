#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# --- Git submodules ---
echo "==> Syncing git submodules..."
git submodule update --remote

# --- Google Sheets (download as xlsx) ---
echo "==> Syncing Google Sheets..."
mkdir -p raw/sheets

# Parse google-sheet sources from sources.yaml
# Extracts url and path for each google-sheet type source
in_google_sheet=false
sheet_url=""
sheet_path=""

while IFS= read -r line; do
  if [[ "$line" =~ ^[[:space:]]+type:[[:space:]]+google-sheet ]]; then
    in_google_sheet=true
    continue
  fi

  if $in_google_sheet; then
    if [[ "$line" =~ ^[[:space:]]+path:[[:space:]]+(.+) ]]; then
      sheet_path="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]+url:[[:space:]]+\"?([^\"]+)\"? ]]; then
      sheet_url="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]*[a-z_-]+: ]] && [[ ! "$line" =~ ^[[:space:]]+(path|url|pattern|sync|description): ]]; then
      # Hit a new source entry — process what we have
      if [ -n "$sheet_url" ] && [ -n "$sheet_path" ]; then
        export_url="${sheet_url}/export?format=xlsx"
        echo "  Downloading: $sheet_path"
        curl -sL "$export_url" -o "$sheet_path"
      fi
      in_google_sheet=false
      sheet_url=""
      sheet_path=""
    fi
  fi
done < raw/sources.yaml

# Handle last entry if it was a google-sheet
if $in_google_sheet && [ -n "$sheet_url" ] && [ -n "$sheet_path" ]; then
  export_url="${sheet_url}/export?format=xlsx"
  echo "  Downloading: $sheet_path"
  curl -sL "$export_url" -o "$sheet_path"
fi

# --- Zendesk tickets ---
echo "==> Syncing Zendesk tickets..."
bash scripts/sync-zendesk.sh

# --- Commit if anything changed ---
changed=$(git diff --name-only)
untracked=$(git ls-files --others --exclude-standard raw/)

all_changes="$changed"
if [ -n "$untracked" ]; then
  all_changes=$(printf "%s\n%s" "$changed" "$untracked" | sed '/^$/d')
fi

if [ -z "$all_changes" ]; then
  echo "==> Already up to date."
  exit 0
fi

echo "==> Changed:"
echo "$all_changes"

echo "$all_changes" | xargs git add
git commit -m "Sync sources: $(echo "$all_changes" | sed 's|raw/||g' | tr '\n' ', ' | sed 's/,$//')"

echo "==> Done."
