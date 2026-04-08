#!/usr/bin/env bash
set -uo pipefail

cd "$(git rev-parse --show-toplevel)"

errors=0
warnings=0
pages=0

# Colors (if terminal supports it)
if [ -t 1 ]; then
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  GREEN='\033[0;32m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED='' YELLOW='' GREEN='' BOLD='' NC=''
fi

# Temp files for counting across subshells
err_file=$(mktemp)
warn_file=$(mktemp)
echo 0 > "$err_file"
echo 0 > "$warn_file"
trap 'rm -f "$err_file" "$warn_file" /tmp/wiki_lint_broken' EXIT

error() {
  echo -e "  ${RED}ERROR${NC} $1"
  echo $(( $(cat "$err_file") + 1 )) > "$err_file"
}
warn() {
  echo -e "  ${YELLOW}WARN${NC}  $1"
  echo $(( $(cat "$warn_file") + 1 )) > "$warn_file"
}
ok()    { echo -e "  ${GREEN}OK${NC}    $1"; }

# Collect all wiki pages
wiki_files=()
while IFS= read -r f; do
  wiki_files+=("$f")
done < <(find wiki -name "*.md" -type f | sort)
pages=${#wiki_files[@]}

# ─── 1. Frontmatter validation ───────────────────────────────────────────────

echo -e "\n${BOLD}==> Checking frontmatter...${NC}"

required_fields=(title category status last_updated)
valid_statuses="complete|partial|needs-update|draft|in-progress"

for file in "${wiki_files[@]}"; do
  # Skip log.md — it's append-only and has no frontmatter
  if [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi

  # Check for frontmatter delimiters
  first_line=$(head -1 "$file")
  if [[ "$first_line" != "---" ]]; then
    error "$file — no YAML frontmatter found"
    continue
  fi

  # Extract frontmatter (between first and second ---)
  frontmatter=$(sed -n '1,/^---$/{ /^---$/d; p; }' "$file" | tail -n +1)

  for field in "${required_fields[@]}"; do
    if ! echo "$frontmatter" | grep -q "^${field}:"; then
      error "$file — missing required field: $field"
    fi
  done

  # Validate status value
  status_val=$(echo "$frontmatter" | grep "^status:" | sed 's/^status:[[:space:]]*//' | tr -d '"' | tr -d "'")
  if [ -n "$status_val" ]; then
    if ! echo "$status_val" | grep -qE "^(${valid_statuses})$"; then
      error "$file — invalid status: '$status_val' (expected: ${valid_statuses})"
    fi
  fi

  # Validate date format
  date_val=$(echo "$frontmatter" | grep "^last_updated:" | sed 's/^last_updated:[[:space:]]*//' | tr -d '"' | tr -d "'")
  if [ -n "$date_val" ]; then
    if ! echo "$date_val" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
      error "$file — invalid date format: '$date_val' (expected: YYYY-MM-DD)"
    fi
  fi

  # Warn if git_reference is missing (not required, but recommended)
  if ! echo "$frontmatter" | grep -q "^git_reference:"; then
    warn "$file — missing field: git_reference"
  fi
done

# ─── 2. Broken internal links ────────────────────────────────────────────────

echo -e "\n${BOLD}==> Checking internal links...${NC}"

broken_count=0
for file in "${wiki_files[@]}"; do
  dir=$(dirname "$file")

  # Strip code fences from file before scanning, then grep with line numbers
  # We process the file tracking fence state to exclude code blocks
  awk 'BEGIN{fence=0} /^```/{fence=!fence; print NR": "; next} !fence{print NR": "$0}' "$file" | \
  grep -E '[0-9]+: .*\[.*\]\(.*' 2>/dev/null | while IFS= read -r match; do
    lineno="${match%%: *}"
    line="${match#*: }"

    # Extract link targets using sed — get all (path) from [text](path)
    echo "$line" | grep -oE '\[[^]]*\]\([^)]+\)' | sed 's/.*](//' | sed 's/)$//' | while IFS= read -r link; do
      # Strip anchor fragments
      link_path="${link%%#*}"

      # Skip external links and empty paths
      case "$link_path" in
        http://*|https://*|"") continue ;;
      esac

      # Resolve relative path
      target="$dir/$link_path"
      resolved=$(cd "$(dirname "$target")" 2>/dev/null && echo "$(pwd)/$(basename "$target")") || resolved=""

      if [ -n "$resolved" ]; then
        resolved="${resolved#"$(pwd)/"}"
      fi

      if [ -z "$resolved" ] || [ ! -f "$resolved" ]; then
        echo -e "  ${RED}ERROR${NC} $file:$lineno → $link_path (not found)"
        echo "1" >> /tmp/wiki_lint_broken
      fi
    done
  done
done

if [ -f /tmp/wiki_lint_broken ]; then
  broken_count=$(wc -l < /tmp/wiki_lint_broken | tr -d ' ')
  echo $(( $(cat "$err_file") + broken_count )) > "$err_file"
  rm -f /tmp/wiki_lint_broken
fi

if [ "$broken_count" -eq 0 ]; then
  ok "All internal links valid"
fi

# ─── 3. Orphan pages ─────────────────────────────────────────────────────────

echo -e "\n${BOLD}==> Checking orphan pages...${NC}"

orphan_count=0
for file in "${wiki_files[@]}"; do
  # Skip index.md and log.md — they're entry points, not orphans
  if [[ "$file" == "wiki/index.md" ]] || [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi

  basename_file=$(basename "$file")
  # Check if any other wiki file links to this page
  linked=false
  for other in "${wiki_files[@]}"; do
    if [[ "$other" == "$file" ]]; then
      continue
    fi
    # Search for the filename in link targets
    if grep -q "$basename_file" "$other" 2>/dev/null; then
      linked=true
      break
    fi
  done

  if ! $linked; then
    warn "$file — not linked from any other page"
    ((orphan_count++))
  fi
done

if [ "$orphan_count" -eq 0 ]; then
  ok "No orphan pages"
fi

# ─── 4. Index coverage ───────────────────────────────────────────────────────

echo -e "\n${BOLD}==> Checking index coverage...${NC}"

missing_count=0
index_content=$(cat wiki/index.md)

for file in "${wiki_files[@]}"; do
  # Skip index.md and log.md
  if [[ "$file" == "wiki/index.md" ]] || [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi

  basename_file=$(basename "$file")
  if ! echo "$index_content" | grep -q "$basename_file"; then
    warn "$file — not listed in index.md"
    ((missing_count++))
  fi
done

if [ "$missing_count" -eq 0 ]; then
  ok "All pages listed in index.md"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

errors=$(cat "$err_file")
warnings=$(cat "$warn_file")

echo -e "\n${BOLD}==> Summary: $pages pages checked, $errors error(s), $warnings warning(s)${NC}"

if [ "$errors" -gt 0 ]; then
  exit 1
fi
exit 0
