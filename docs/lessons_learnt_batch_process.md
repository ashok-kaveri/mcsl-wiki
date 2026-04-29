# Lessons Learned - Batch Processing

## Issue: Progress File Not Updated After Background Task Completion

**Date**: 2026-04-29
**Context**: Story cards generation (`/story-cards delta`)

### What Happened

During batch processing of 12 ZI issues (ZI-472 through ZI-483):
- First 6 cards (ZI-472 to ZI-477) completed successfully with progress file updates
- Final 6 cards (ZI-478 to ZI-483) were launched as background task `be9b429`
- Background task timed out after 120 seconds
- Task was killed, but 3 cards (ZI-478, 479, 480) had already been created
- Manually completed remaining 3 cards (ZI-481, 482, 483)
- **Progress file `/tmp/story_cards_progress.txt` was never updated for the final 6 cards**

### Result

Progress file showed:
```
✅ ZI-472 - DONE (https://trello.com/c/KdBiTSx1)
...
✅ ZI-477 - DONE (https://trello.com/c/XUNuKjsW)
⏳ ZI-478 - PENDING
⏳ ZI-479 - PENDING
⏳ ZI-480 - PENDING
⏳ ZI-481 - PENDING
⏳ ZI-482 - PENDING
⏳ ZI-483 - PENDING
```

But in reality, all 12 cards were complete:
- All markdown files existed in `wiki/product/stories/`
- All cards were pushed to Trello with valid URLs
- All Trello links were present in the markdown files

### Root Cause

When a background task times out or is killed:
1. The progress file updates inside the background task don't get written
2. Manual completion of remaining items bypassed the progress file update mechanism
3. No final verification step to sync progress file with actual completion status

### Lesson Learned

**Always verify completion status from source of truth, not just progress file**

For batch processes:
1. Progress file is a tracking tool, not the source of truth
2. After any background task timeout or interruption, verify actual outputs:
   - Check if files exist on disk
   - Check if external resources (Trello cards) were created
   - Grep for completion markers (URLs, IDs) in output files
3. Update progress file after manual recovery
4. Add a final verification step that reconciles progress file with actual outputs

### Fix Applied

Verified all 6 "pending" cards by:
- Checking markdown files exist: `ls -la wiki/product/stories/ZI-{478..483}.md`
- Extracting Trello URLs: `grep "| Trello |" wiki/product/stories/ZI-{478..483}.md`
- Updated progress file to reflect actual completion status

### Prevention

For future batch processes:
1. **Before starting loop**: Create progress file
2. **During loop**: Update progress file after each item
3. **On interruption**: Don't trust progress file alone - verify outputs
4. **After completion**: Run verification script that checks:
   - All expected files exist
   - All expected external resources created
   - Progress file matches reality
5. **Consider**: Adding a `verify` mode to batch skills that reconciles progress file with actual state
