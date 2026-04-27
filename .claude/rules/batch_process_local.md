# Batch Processing Rules

## Progress File Requirement

**CRITICAL**: When executing any skill or workflow iteratively in a loop (processing multiple items), you MUST create a progress tracking file BEFORE starting the loop.

### When This Applies

- Generating multiple story cards
- Processing batches of Zendesk tickets
- Analyzing multiple files or modules
- Any loop with >5 iterations
- Any process that takes >2 minutes

### Required Pattern

1. **Before loop starts**: Create progress file (e.g., `story_cards_progress.txt`)
2. **During loop**: Write status after each item
3. **On restart**: Check file to skip completed items

If you start a batch process without creating a progress file first, STOP and create it before proceeding.
