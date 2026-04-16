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
  BLUE='\033[0;34m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED='' YELLOW='' GREEN='' BLUE='' BOLD='' NC=''
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
ok()   { echo -e "  ${GREEN}OK${NC}    $1"; }
info() { echo -e "  ${BLUE}INFO${NC}  $1"; }

# ─── Page classification helpers ────────────────────────────────────────────

is_zendesk_summary() { [[ "$1" == wiki/zendesk/summaries/* ]]; }
is_story_card()      { [[ "$1" == wiki/product/stories/ZI-* ]]; }
is_zendesk_index()   { [[ "$1" =~ ^wiki/zendesk/[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; }
is_pipeline_output() { is_zendesk_summary "$1" || is_story_card "$1" || is_zendesk_index "$1"; }

# Valid values
valid_categories="architecture|module|pattern|operation|product|product-feature|product-decision|product-release|index|test-coverage|guide|support|analysis"
valid_statuses_standard="complete|partial|needs-update|draft|in-progress"
valid_statuses_product="proposed|accepted|superseded|shipped|in-progress"
valid_statuses_zendesk="open|new|pending|closed|solved"
valid_statuses_all="${valid_statuses_standard}|${valid_statuses_product}|${valid_statuses_zendesk}"

# Collect all wiki pages
wiki_files=()
while IFS= read -r f; do
  wiki_files+=("$f")
done < <(find wiki -name "*.md" -type f | sort)
pages=${#wiki_files[@]}

# ─── 1. Frontmatter validation ───────────────────────────────────────────────

echo -e "\n${BOLD}==> 1. Checking frontmatter...${NC}"

standard_required=(title category status last_updated)
summary_required=(title ticket_id status last_updated)
story_no_fm_count=0

for file in "${wiki_files[@]}"; do
  # Skip log.md — append-only, no frontmatter
  if [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi

  # Check for frontmatter delimiters
  first_line=$(head -1 "$file")
  if [[ "$first_line" != "---" ]]; then
    # Story cards without frontmatter: count but don't error individually
    if is_story_card "$file"; then
      ((story_no_fm_count++))
      continue
    fi
    error "$file — no YAML frontmatter found"
    continue
  fi

  # Extract frontmatter (between first and second ---)
  frontmatter=$(sed -n '1,/^---$/{ /^---$/d; p; }' "$file" | tail -n +1)

  # ── Zendesk summaries: different required fields ──
  if is_zendesk_summary "$file"; then
    for field in "${summary_required[@]}"; do
      if ! echo "$frontmatter" | grep -q "^${field}:"; then
        error "$file — missing required field: $field"
      fi
    done
    # Validate status against zendesk-specific values
    status_val=$(echo "$frontmatter" | grep "^status:" | sed 's/^status:[[:space:]]*//' | tr -d '"' | tr -d "'")
    if [ -n "$status_val" ]; then
      if ! echo "$status_val" | grep -qE "^(${valid_statuses_zendesk}|${valid_statuses_standard})$"; then
        error "$file — invalid status: '$status_val'"
      fi
    fi
    continue
  fi

  # ── Story cards with frontmatter: lighter validation ──
  if is_story_card "$file"; then
    for field in title status last_updated; do
      if ! echo "$frontmatter" | grep -q "^${field}:"; then
        warn "$file — missing field: $field"
      fi
    done
    continue
  fi

  # ── Standard wiki pages ──
  # Detect category first so we can scope required-field checks
  cat_val=$(echo "$frontmatter" | grep "^category:" | sed 's/^category:[[:space:]]*//' | tr -d '"' | tr -d "'")

  for field in "${standard_required[@]}"; do
    # Decision records use `date:` instead of `last_updated:` (per CLAUDE.md §Decision Record Template)
    if [[ "$field" == "last_updated" && "$cat_val" == "product-decision" ]]; then
      if ! echo "$frontmatter" | grep -qE "^(date|last_updated):"; then
        error "$file — missing required field: date (or last_updated)"
      fi
      continue
    fi
    if ! echo "$frontmatter" | grep -q "^${field}:"; then
      error "$file — missing required field: $field"
    fi
  done

  # Validate category value
  if [ -n "$cat_val" ]; then
    if ! echo "$cat_val" | grep -qE "^(${valid_categories})$"; then
      error "$file — invalid category: '$cat_val' (expected: ${valid_categories})"
    fi
  fi

  # Validate status value (allow all statuses — scoped validation by category)
  status_val=$(echo "$frontmatter" | grep "^status:" | sed 's/^status:[[:space:]]*//' | tr -d '"' | tr -d "'")
  if [ -n "$status_val" ]; then
    if ! echo "$status_val" | grep -qE "^(${valid_statuses_all})$"; then
      error "$file — invalid status: '$status_val'"
    fi
  fi

  # Validate date format
  date_val=$(echo "$frontmatter" | grep "^last_updated:" | sed 's/^last_updated:[[:space:]]*//' | tr -d '"' | tr -d "'")
  if [ -n "$date_val" ]; then
    if ! echo "$date_val" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
      error "$file — invalid date format: '$date_val' (expected: YYYY-MM-DD)"
    fi
  fi

  # Conditional: domain required when category=module
  if [[ "$cat_val" == "module" ]]; then
    if ! echo "$frontmatter" | grep -q "^domain:"; then
      error "$file — category 'module' requires a 'domain' field"
    fi
  fi

  # Warn if git_reference is missing (recommended for standard pages)
  if ! echo "$frontmatter" | grep -q "^git_reference:"; then
    warn "$file — missing field: git_reference"
  fi
done

if [ "$story_no_fm_count" -gt 0 ]; then
  warn "${story_no_fm_count} story cards lack YAML frontmatter (need migration)"
fi

# ─── 2. Broken internal links ────────────────────────────────────────────────

echo -e "\n${BOLD}==> 2. Checking internal links...${NC}"

broken_count=0
for file in "${wiki_files[@]}"; do
  dir=$(dirname "$file")

  # Strip code fences from file before scanning, then grep with line numbers
  awk 'BEGIN{fence=0} /^```/{fence=!fence; print NR": "; next} !fence{print NR": "$0}' "$file" | \
  grep -E '[0-9]+: .*\[.*\]\(.*' 2>/dev/null | while IFS= read -r match; do
    lineno="${match%%: *}"
    line="${match#*: }"

    echo "$line" | grep -oE '\[[^]]*\]\([^)]+\)' | sed 's/.*](//' | sed 's/)$//' | while IFS= read -r link; do
      # Strip anchor fragments
      link_path="${link%%#*}"

      # Skip external links, empty paths, directory links, and raw/ (volatile external content)
      case "$link_path" in
        http://*|https://*|"") continue ;;
        */) continue ;;
        *../raw/*|raw/*) continue ;;
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

echo -e "\n${BOLD}==> 3. Checking orphan pages...${NC}"

orphan_count=0
for file in "${wiki_files[@]}"; do
  # Skip entry points and pipeline outputs
  if [[ "$file" == "wiki/index.md" ]] || [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi
  if is_pipeline_output "$file"; then
    continue
  fi

  basename_file=$(basename "$file")
  linked=false
  for other in "${wiki_files[@]}"; do
    if [[ "$other" == "$file" ]]; then
      continue
    fi
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

echo -e "\n${BOLD}==> 4. Checking index coverage...${NC}"

missing_count=0
index_content=$(cat wiki/index.md)

for file in "${wiki_files[@]}"; do
  # Skip index, log, and pipeline outputs (not individually listed in index)
  if [[ "$file" == "wiki/index.md" ]] || [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi
  if is_pipeline_output "$file"; then
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

# ─── 5. Staleness detection ──────────────────────────────────────────────────

echo -e "\n${BOLD}==> 5. Checking staleness...${NC}"

stale_count=0
today=$(date +%s)
stale_days=30
head_commit=$(git rev-parse HEAD 2>/dev/null || echo "")

for file in "${wiki_files[@]}"; do
  if [[ "$file" == "wiki/log.md" ]]; then
    continue
  fi
  if is_pipeline_output "$file"; then
    continue
  fi

  first_line=$(head -1 "$file")
  if [[ "$first_line" != "---" ]]; then
    continue
  fi

  frontmatter=$(sed -n '1,/^---$/{ /^---$/d; p; }' "$file" | tail -n +1)

  # Check last_updated age (or `date:` for decision records)
  date_val=$(echo "$frontmatter" | grep -E "^(last_updated|date):" | head -1 | sed 's/^[^:]*:[[:space:]]*//' | tr -d '"' | tr -d "'")
  if [ -n "$date_val" ] && echo "$date_val" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
    file_epoch=$(date -j -f "%Y-%m-%d" "$date_val" +%s 2>/dev/null || echo "")
    if [ -n "$file_epoch" ]; then
      age_days=$(( (today - file_epoch) / 86400 ))
      if [ "$age_days" -gt "$stale_days" ]; then
        warn "$file — last updated ${age_days} days ago ($date_val)"
        ((stale_count++))
      fi
    fi
  fi

  # Check git_reference staleness (if it's a commit hash, not "current")
  git_ref=$(echo "$frontmatter" | grep "^git_reference:" | sed 's/^git_reference:[[:space:]]*//' | tr -d '"' | tr -d "'")
  if [ -n "$git_ref" ] && [ "$git_ref" != "current" ] && [ -n "$head_commit" ]; then
    if git cat-file -e "$git_ref" 2>/dev/null; then
      commits_behind=$(git rev-list --count "${git_ref}..HEAD" 2>/dev/null || echo "0")
      if [ "$commits_behind" -gt 50 ]; then
        warn "$file — git_reference is ${commits_behind} commits behind HEAD"
      fi
    fi
  fi
done

if [ "$stale_count" -eq 0 ]; then
  ok "No stale pages detected"
fi

# ─── 6. Completeness report ──────────────────────────────────────────────────

echo -e "\n${BOLD}==> 6. Completeness report...${NC}"

partial_count=0
needs_update_count=0

for file in "${wiki_files[@]}"; do
  if is_pipeline_output "$file"; then
    continue
  fi

  first_line=$(head -1 "$file")
  if [[ "$first_line" != "---" ]]; then
    continue
  fi

  frontmatter=$(sed -n '1,/^---$/{ /^---$/d; p; }' "$file" | tail -n +1)
  status_val=$(echo "$frontmatter" | grep "^status:" | sed 's/^status:[[:space:]]*//' | tr -d '"' | tr -d "'")

  if [[ "$status_val" == "partial" ]]; then
    info "$file — status: partial"
    ((partial_count++))
  elif [[ "$status_val" == "needs-update" ]]; then
    info "$file — status: needs-update"
    ((needs_update_count++))
  fi
done

if [ "$partial_count" -eq 0 ] && [ "$needs_update_count" -eq 0 ]; then
  ok "All pages are complete"
else
  info "${partial_count} partial, ${needs_update_count} needs-update"
fi

# ─── 7. Pipeline health ──────────────────────────────────────────────────────

echo -e "\n${BOLD}==> 7. Pipeline health...${NC}"

# Zendesk: raw tickets vs summaries
raw_shopify=$(find raw/zendesk/shopify -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
raw_other=$(find raw/zendesk/other_platforms -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
raw_total=$((raw_shopify + raw_other))
summary_count=$(find wiki/zendesk/summaries -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "$raw_total" -gt "$summary_count" ]; then
  delta=$((raw_total - summary_count))
  warn "Zendesk: ${delta} raw tickets unsummarized (${summary_count} summaries / ${raw_total} raw tickets)"
else
  ok "Zendesk: all ${raw_total} raw tickets have summaries"
fi

# Story cards: frontmatter migration status
story_total=$(find wiki/product/stories -name "ZI-*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
story_with_fm=0
if [ "$story_total" -gt 0 ]; then
  while IFS= read -r f; do
    if [[ "$(head -1 "$f")" == "---" ]]; then
      ((story_with_fm++))
    fi
  done < <(find wiki/product/stories -name "ZI-*.md" -type f)
fi
story_missing_fm=$((story_total - story_with_fm))

if [ "$story_missing_fm" -gt 0 ]; then
  warn "Story cards: ${story_missing_fm}/${story_total} need frontmatter migration"
else
  ok "Story cards: all ${story_total} have frontmatter"
fi

# ─── 8. Naming conventions ───────────────────────────────────────────────────

echo -e "\n${BOLD}==> 8. Checking naming conventions...${NC}"

naming_issues=0
for file in "${wiki_files[@]}"; do
  basename_file=$(basename "$file" .md)

  # Allow: lowercase-with-hyphens, YYYY-MM-DD dated files, ZI-NNN story cards, digits-only (ticket IDs)
  if echo "$basename_file" | grep -qE '^[a-z0-9-]+$'; then
    continue
  fi
  if echo "$basename_file" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
    continue
  fi
  if echo "$basename_file" | grep -qE '^ZI-[0-9]+$'; then
    continue
  fi
  if echo "$basename_file" | grep -qE '^[0-9]+$'; then
    continue
  fi

  warn "$file — filename should be lowercase-with-hyphens"
  ((naming_issues++))
done

if [ "$naming_issues" -eq 0 ]; then
  ok "All filenames follow naming conventions"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

errors=$(cat "$err_file")
warnings=$(cat "$warn_file")

echo -e "\n${BOLD}==> Summary: $pages pages checked, $errors error(s), $warnings warning(s)${NC}"

if [ "$errors" -gt 0 ]; then
  exit 1
fi
exit 0
