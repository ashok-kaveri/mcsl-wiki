# Lessons Learned: Zendesk Summarization

This document captures lessons learned from summarizing Zendesk tickets to improve future summarization quality.

---

## Lesson 1: Always Read Internal L3 Escalation Comments First

**Date**: 2026-04-30
**Ticket**: #379098 (FedEx REST API migration)
**Issue**: Missed that CSV signature update feature was also broken, not just automation rules

### What Happened

When summarizing ticket #379098, I initially identified only ONE open issue (automation rule ASR not working), but missed that the CSV signature update feature was ALSO broken. This was a critical omission because:

1. It meant TWO self-serve workflows were broken (not one)
2. It explained WHY the customer needed daily manual intervention
3. It showed the problem was much more severe than initially documented

### Root Cause Analysis

**Why I missed it:**

1. **Focused on last 5 comments for "current state"** - Only looked at recent customer-facing updates (#82-86) showing the workaround in action, not the diagnostic phase

2. **Skipped internal diagnostic comments** - The critical information was in Comment #46 (INTERNAL) from L3:
   ```
   1. We will fix signature option not working in automation rule in next release.
   2. We will fix signature update option via CSV in next release.
   ```
   This clearly lists TWO broken features, but I collapsed them into one issue.

3. **Didn't trace the investigation timeline** - Jumped from "initial problem report" → "current workaround" without reading the middle investigation phase (Comments #44-46) where support identified both failures

4. **Used shortcuts for large tickets** - With 86 comments, I used "last 5 comments" heuristic instead of systematically reading ALL INTERNAL comments

### What Should Have Been Done

**Priority reading order for complex tickets:**

1. **First: Read ALL INTERNAL L3 escalation comments**
   - Search for: `"Need assistance from L3"`, `"L3:"`, `"[Veena]"`, `"dev_needed"`
   - These contain structured root cause analysis
   - Each item in numbered lists is likely a DISTINCT issue

2. **Second: Read internal diagnostic comments**
   - Comments marked INTERNAL often contain:
     - Root cause findings
     - Multiple broken features discovered during investigation
     - Technical details not shared with customer

3. **Third: Read customer-facing resolution comments**
   - These show what was communicated to customer
   - Often summarize multiple issues into simplified workarounds

4. **Fourth: Read latest status updates**
   - Shows current state
   - May not reveal all underlying issues

**Example search pattern:**

```bash
# Extract all L3 escalation comments
python3 << 'EOF'
import json
data = json.load(open('raw/zendesk/shopify/379098.json'))
for i, c in enumerate(data['comments'], 1):
    body = c.get('body', '')
    if 'L3' in body or 'Need assistance from L3' in body or 'Veena' in body:
        print(f"Comment #{i}: {body[:500]}")
EOF
```

### The Fix

For ticket #379098, the corrected summary now includes:

**Open Issues:**
1. Adult Signature automation rule not working (carrier-migration)
2. **CSV signature update feature broken** (product-management) ← MISSED INITIALLY
3. Daily manual product ASR updates required (product-management)
4. Packaging type validation errors (label-generation)

### Best Practice Going Forward

**For tickets with `dev_needed` tag or L3 escalations:**

1. **Extract all INTERNAL comments first** - These contain technical diagnosis
2. **Look for numbered lists in L3 comments** - Each item is likely a distinct broken feature
3. **Map each L3 finding to an open issue** - Don't collapse multiple findings into one issue
4. **Cross-check with customer complaints** - Ensure all customer pain points map to identified root causes

**Quality gate question:**
*"Did I read every INTERNAL comment with 'L3', 'dev_needed', or root cause analysis?"*

If NO → go back and read them before finalizing the summary.

---

## Template: How to Handle Large Tickets (50+ comments)

For tickets with many comments:

1. **Don't read chronologically** - Start with diagnostic comments, not timeline
2. **Use targeted search patterns:**
   ```bash
   # Find L3 escalations
   grep -i "l3\|dev_needed\|veena" ticket.json

   # Find root cause statements
   grep -i "root cause\|identified\|issue is" ticket.json

   # Find fix commitments
   grep -i "will fix\|next release\|planned for" ticket.json
   ```
3. **Build issue list from L3 findings** - Start with what engineering identified
4. **Then add customer-reported symptoms** - Ensure all complaints map to issues
5. **Finally construct timeline** - Group chronologically after understanding all issues

---

## Future Enhancements

Consider adding to the zendesk-summarize workflow:

- **Pre-summarization diagnostic step**: Automatically extract and highlight all INTERNAL L3 comments
- **Quality gate**: Require listing all items from L3 numbered lists as separate open issues
- **Search hints**: When ticket has `dev_needed` tag, auto-search for L3 escalation comments first

---

*Last updated: 2026-04-30*
