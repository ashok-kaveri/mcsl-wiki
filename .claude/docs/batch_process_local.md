# Batch Processing Documentation

## Progress File Format

```
# Batch: <description>
# Started: <timestamp>
# Total items: <count>

<item-id>: pending
<item-id>: in-progress <timestamp>
<item-id>: complete <timestamp>
<item-id>: error <timestamp> <error-message>
```

## Example

```bash
# Create progress file
cat > story_cards_progress.txt <<EOF
# Batch: Story cards ZI-303 to ZI-337
# Started: $(date)
# Total items: 35
EOF

# Process loop
for zi_id in ZI-303 ZI-304 ... ZI-337; do
  echo "$zi_id: in-progress $(date)" >> story_cards_progress.txt

  # Process item
  if generate_story_card "$zi_id"; then
    echo "$zi_id: complete $(date)" >> story_cards_progress.txt
  else
    echo "$zi_id: error $(date) $error" >> story_cards_progress.txt
  fi
done
```

## Benefits

- **Resumability**: Skip completed items on restart
- **Visibility**: User can check progress anytime
- **Debugging**: Know exactly where failures occurred
- **Audit**: Record of what was processed when
- **Safety**: No duplicate processing

## Non-Compliance

If you start a batch process without creating a progress file first, STOP and create it before proceeding.
