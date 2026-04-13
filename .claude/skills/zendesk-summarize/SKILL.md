---
name: zendesk-summarize
description: Process Zendesk ticket JSON files into structured wiki summaries and a daily issue index. Use when the user wants to summarize tickets, extract issues, update summaries, or run the Zendesk pipeline.
argument-hint: [all|delta|<ticketId>]
allowed-tools: Bash, Write, Read, Edit, Glob, Grep, Agent
---

# Zendesk Issue Extraction Pipeline

Process Zendesk tickets from `raw/zendesk/shopify/*.json` into structured summaries under `wiki/zendesk/summaries/`.

**Argument**: `$ARGUMENTS`
- `all` — reprocess every ticket (full rebuild)
- `delta` — only tickets changed since last extraction (default)
- `<ticketId>` — process a single specific ticket

---

## Pipeline

`raw/zendesk/*.json` → `wiki/zendesk/summaries/*.md` → `wiki/zendesk/YYYY-MM-DD.md`

**Critical rule**: Downstream artifacts (backlog, roadmap) read from summaries, NEVER from raw JSON. The summaries are the quality-gated source of truth.

---

## Step 1: Determine scope

**If `all`**: List all `raw/zendesk/shopify/*.json` files.

**If `delta`**: Find changed files since last extraction:
```bash
# Read git_reference from the latest wiki/zendesk/YYYY-MM-DD.md
# Then: git diff <git_reference>..HEAD --name-only -- raw/zendesk/shopify/
```

**If `<ticketId>`**: Process only `raw/zendesk/shopify/<ticketId>.json`.

## Step 2: Sync check

For each ticket in scope:
```bash
python3 -c "
import json, os
path = 'raw/zendesk/shopify'
for f in sorted(os.listdir(path)):
    if not f.endswith('.json'): continue
    try:
        d = json.load(open(os.path.join(path, f)))
        comments = len(d.get('comments', []))
        flags = []
        if comments == 100: flags.append('TRUNCATED?')
        if flags: print(f'{f}: {\" \".join(flags)}')
    except:
        print(f'{f}: CORRUPT')
"
```

Report any truncated or corrupt files.

## Step 3: Summarize each ticket

For each ticket, read the full JSON in one pass using python (NEVER use chunked Read with offset/limit on JSON):

```bash
python3 -c "
import json
d = json.load(open('raw/zendesk/shopify/<ID>.json'))
t = d['ticket']
cs = d.get('comments', [])
# Print: subject, status, dates, tags, store, all comments
"
```

**Read comments in reverse** to find current state first, then forward for timeline.

Write `wiki/zendesk/summaries/<ticketId>.md` with this template:

```markdown
---
title: "Ticket #<id> — <subject>"
ticket_id: <id>
status: <open|new|closed>
customer: <name> (<store>)
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_updated: <today>
---

# Ticket #<id> — <subject>

- **Customer**: <name> (<store>)
- **Duration**: <dates> (<ongoing|resolved>)

## Timeline & Key Phases

### Phase 1: <title> (<dates>)
- <key events>

## Open Issues

1. **<Title>** — <description>. Blocked: <who>. Severity: <signal>. Area: <tag>. (Comment #N)

(If none: "No open issues — lifecycle-only.")

## Resolved Issues

1. **<Title>** — <how/when>. (Comment #N)

## Customer Context

- <details>
```

**Summarization rules:**
- Open issues = LATEST state only (L3 escalations, pending requests). NOT every comment.
- Each open issue MUST cite comment number + include: title, blocked, severity, area tag.
- Area tags: onboarding, carrier-config, carrier-migration, label-generation, rate-shopping, tracking, returns, international, order-management, product-management, feature-request
- Lifecycle-only tickets: "No open issues — lifecycle-only ticket."

**Parallelization**: For `all` mode, spawn agents in batches of ~10 tickets.

## Step 4: Build daily index

Extract all open issues from `wiki/zendesk/summaries/*.md` and write `wiki/zendesk/YYYY-MM-DD.md`:

```markdown
---
title: Zendesk Issue Extraction — YYYY-MM-DD
category: support
sources: [zendesk]
status: complete
last_updated: YYYY-MM-DD
git_reference: <HEAD>
---

# Zendesk Issue Extraction — YYYY-MM-DD

**Tickets processed**: N
**Tickets with open issues**: N
**Total open issues**: N

## Summary by Feature Area
| Feature Area | Issues | Tickets |
|---|---|---|

## Issue Index
| ID | Issue | Ticket | Area |
|---|---|---|---|
| ZI-001 | ... | [#NNNNNN](summaries/NNNNNN.md) | ... |

## Issues by Feature Area
### <area> (N issues)
| ID | Issue | Ticket |
|---|---|---|
```

## Step 5: Report

Print summary:
- Tickets processed / skipped / flagged
- Open issues extracted (total + by area)
- Link to daily index file

Remind the user to run `/roadmap regenerate` to update the roadmap from the new summaries.
