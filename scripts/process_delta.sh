#!/bin/bash
# Driver script for Zendesk delta extraction with schema migration
# Orchestrates Steps 1-6 of the pipeline

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=================================================================="
echo "Zendesk Delta Extraction Pipeline"
echo "=================================================================="
echo "Repository: $REPO_ROOT"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Delta ticket list (31 files)
DELTA_SHOPIFY=(
    384891 385211 385304 385311 385331 385390 385525 385815
    386039 386073 386078 386099 386104 386107 386112 386116
    386133 386134 386168 386180 386192 386197 386203 386214
)

DELTA_OTHER=(
    385094 385906 386057 386065 386115 386169
)

echo "Step 1: Summarizing delta tickets"
echo "=================================================================="
echo "Processing $(( ${#DELTA_SHOPIFY[@]} + ${#DELTA_OTHER[@]} )) tickets..."
echo ""

# Process shopify tickets
for ticket_id in "${DELTA_SHOPIFY[@]}"; do
    json_path="$REPO_ROOT/raw/zendesk/shopify/${ticket_id}.json"
    if [ -f "$json_path" ]; then
        python3 "$SCRIPT_DIR/summarize_ticket.py" "$json_path"
    else
        echo "⚠️  WARNING: File not found: $json_path"
    fi
done

# Process other_platforms tickets
for ticket_id in "${DELTA_OTHER[@]}"; do
    json_path="$REPO_ROOT/raw/zendesk/other_platforms/${ticket_id}.json"
    if [ -f "$json_path" ]; then
        python3 "$SCRIPT_DIR/summarize_ticket.py" "$json_path"
    else
        echo "⚠️  WARNING: File not found: $json_path"
    fi
done

echo ""
echo "Step 2: Loading all current summaries"
echo "=================================================================="
python3 "$SCRIPT_DIR/load_summaries.py"

echo ""
echo "Step 3: Loading prior ZI assignments"
echo "=================================================================="
python3 "$SCRIPT_DIR/load_prior_index.py"

echo ""
echo "Step 4: Running 5-step ID assignment pipeline"
echo "=================================================================="
python3 "$SCRIPT_DIR/assign_zi_ids.py"

echo ""
echo "Step 5: Generating daily index (6-column schema)"
echo "=================================================================="
python3 "$SCRIPT_DIR/generate_daily_index.py"

echo ""
echo "Step 6: Validating daily index"
echo "=================================================================="
python3 "$SCRIPT_DIR/validate_daily_index.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================================="
    echo "✅ PIPELINE COMPLETED SUCCESSFULLY"
    echo "=================================================================="
    echo ""
    echo "Next steps:"
    echo "1. Review validation report above"
    echo "2. Spot-check fuzzy matches in intermediate/zi_assignments.json"
    echo "3. Update wiki/log.md with extraction entry"
    echo "4. Commit changes"
    echo ""
else
    echo ""
    echo "=================================================================="
    echo "❌ VALIDATION FAILED - DO NOT COMMIT"
    echo "=================================================================="
    echo ""
    exit 1
fi
