---
name: zendesk-summarize
description: Process Zendesk ticket JSON files into structured wiki summaries and a daily issue index. Use when the user wants to summarize tickets, extract issues, update summaries, or run the Zendesk pipeline.
argument-hint: [all|delta|<ticketId>] [shopify|other_platforms|all-products]
allowed-tools: Bash, Write, Read, Edit, Glob, Grep, Agent
---

# Zendesk Issue Extraction Pipeline

Process Zendesk tickets from all product directories under `raw/zendesk/` into structured summaries under `wiki/zendesk/summaries/`.

**Source directories** (from `raw/sources.yaml`):
- `raw/zendesk/shopify/` — Shopify Multi Carrier Shipping Label App tickets
- `raw/zendesk/other_platforms/` — WooCommerce, Magento, BigCommerce, StorePep, FedEx AMEA tickets

**Argument**: `$ARGUMENTS`
- First word — scope:
  - `all` — reprocess every ticket (full rebuild)
  - `delta` — only tickets changed since last extraction (default)
  - `<ticketId>` — process a single specific ticket
- Second word (optional) — product filter:
  - `shopify` — only `raw/zendesk/shopify/`
  - `other_platforms` — only `raw/zendesk/other_platforms/`
  - `all-products` — both directories (default)

---

## Pipeline

`raw/zendesk/**/*.json` → `wiki/zendesk/summaries/*.md` → `wiki/zendesk/YYYY-MM-DD.md`

**Critical rule**: Downstream artifacts (backlog, roadmap) read from summaries, NEVER from raw JSON. The summaries are the quality-gated source of truth.

---

## Step 0: Resolve product directories

Based on the product filter argument, build the list of directories to process:

```python
PRODUCT_DIRS = {
    "shopify": "raw/zendesk/shopify",
    "other_platforms": "raw/zendesk/other_platforms",
}
```

- If product filter is `shopify` → process only `raw/zendesk/shopify/`
- If product filter is `other_platforms` → process only `raw/zendesk/other_platforms/`
- If product filter is `all-products` or omitted → process both directories
- Skip any directory that doesn't exist on disk

## Step 1: Determine scope

**If `all`**: List all `*.json` files across the selected product directories.

**If `delta`**: Find changed files since last extraction:
```bash
# Read git_reference from the latest wiki/zendesk/YYYY-MM-DD.md
# Then for each product dir:
# git diff <git_reference>..HEAD --name-only -- raw/zendesk/shopify/ raw/zendesk/other_platforms/
```

**If `<ticketId>`**: Search all product directories for `<ticketId>.json` — use whichever directory contains it.

## Step 2: Sync check

For each product directory in scope:
```bash
python3 -c "
import json, os, sys

dirs = sys.argv[1:]
for d in dirs:
    if not os.path.isdir(d):
        print(f'SKIP {d} (not found)')
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json'): continue
        try:
            data = json.load(open(os.path.join(d, f)))
            comments = len(data.get('comments', []))
            flags = []
            if comments == 100: flags.append('TRUNCATED?')
            if flags: print(f'{d}/{f}: {\" \".join(flags)}')
        except:
            print(f'{d}/{f}: CORRUPT')
" raw/zendesk/shopify raw/zendesk/other_platforms
```

Report any truncated or corrupt files.

## Step 3: Summarize each ticket

For each ticket, read the full JSON in one pass using python (NEVER use chunked Read with offset/limit on JSON):

```bash
python3 -c "
import json
d = json.load(open('<PRODUCT_DIR>/<ID>.json'))
t = d['ticket']
cs = d.get('comments', [])
# Print: subject, status, dates, tags, store, all comments
"
```

**Determine the product** from the ticket's file location:
- `raw/zendesk/shopify/` → product: `shopify`
- `raw/zendesk/other_platforms/` → product: derive from tags (`woocommerce_shipping_services` → `woocommerce`, `magento_multi_carrier_shipping_label_app` → `magento`, etc.)

**Read comments in reverse** to find current state first, then forward for timeline.

Write `wiki/zendesk/summaries/<ticketId>.md` with this template:

```markdown
---
title: "Ticket #<id> — <subject>"
ticket_id: <id>
product: <shopify|woocommerce|magento|bigcommerce|storepep|fedex-amea>
status: <open|new|closed>
customer: <name> (<store>)
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_updated: <today>
---

# Ticket #<id> — <subject>

- **Customer**: <name> (<store>)
- **Product**: <product name>
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
- **Product field** is mandatory in frontmatter — derived from directory or ticket tags.

**Parallelization**: For `all` mode, spawn agents in batches of ~10 tickets.

## Step 4: Build daily index

Extract all open issues from `wiki/zendesk/summaries/*.md` and write `wiki/zendesk/YYYY-MM-DD.md`.

**Hard invariants**:
1. **Same ticket numbers stay open across rebuilds.** Every ZI-NNN that appeared in the prior index MUST appear in the new index, even if the current summary no longer has a matching issue (carry-forward with prior data).
2. **Duplicates get new ZIs with `Duplicate Of` back-links.** When a ticket's re-summarized open issue doesn't exactly match a prior ZI's title but clearly refers to the same work (same ticket, token overlap), assign a new ZI and set `Duplicate Of: <old-ZI>`. The old ZI still appears as a standalone row.

**ID assignment pipeline** (in order):

1. **Exact match** — normalize `(ticket_id, title)`; if the pair exists in prior index, preserve the old ZI. No duplicate marker.
2. **First-pass fuzzy match** — same ticket, first-5-tokens prefix overlap OR token subset. Emit a new ZI with `duplicate_of: <prior-ZI>`.
3. **Fresh assignment** — no prior match. Assign `ZI-<next-int>` starting from `max(prior-ZIs) + 1`. No duplicate marker.
4. **Second-pass cross-reference** — for each prior ZI not yet matched, if any NEW ZI on the SAME ticket (without a duplicate_of) has Jaccard token-overlap ≥ 0.15 or ≥ 2 shared content-words with the prior title, re-link that new ZI as `duplicate_of: <prior-ZI>`.
5. **Carry-forward** — any prior ZI still unreferenced is added to the new index as a standalone row with its prior title and area.

**Area inheritance** (fix for old-format summaries lacking `Area: <tag>` metadata):

1. Parse `Area: <tag>` from the issue body. If present and in `VALID_AREA_TAGS`, use it.
2. Otherwise, look up the same `(ticket, normalized-title)` in the prior index; if that row has a non-`other` area, inherit it.
3. Otherwise, scan prior index for any row on the same ticket with token-prefix overlap; inherit its area if non-`other`.
4. Fall back to `other`.

**Trello API pagination gotcha** (if future label-writing work is added here): `/boards/{id}/labels` defaults to 50. Always pass `limit=1000`. `/boards/{id}/cards` has no effective cap by default, so DO NOT pass `limit` (it would accidentally cap).

### Index file format

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
**Total issues (active + duplicates)**: N
**Active issues (non-duplicate)**: N
**Marked as duplicate of previous**: N
**Preserved from prior index (exact match)**: N
**Preserved from prior index (carried forward, no current match)**: N
**New IDs assigned (fresh)**: N (starting from ZI-NNN)
**Areas inherited from prior index**: N

> **Schema**: Issue Index has 6 columns including `Duplicate Of`. New issues whose ticket + title fuzzy-match an older ZI get a new ID but point back to the older one. Old ZIs are preserved regardless.

## Summary by Product
| Product | Tickets | Active Issues |
|---|---|---|

## Summary by Feature Area
| Feature Area | Issues | Tickets |
|---|---|---|

## Issue Index
| ID | Issue | Ticket | Product | Area | Duplicate Of |
|---|---|---|---|---|---|
| ZI-001 | ... | [#NNNNNN](summaries/NNNNNN.md) | shopify | ... | — |
| ZI-119 | ... | [#NNNNNN](summaries/NNNNNN.md) | shopify | ... | [ZI-102](#zi-102) |

## Issues by Feature Area
### <area> (N active issues)
| ID | Issue | Ticket | Product |
|---|---|---|---|
```

The `Issues by Feature Area` section should EXCLUDE duplicates (active issues only); `Issue Index` is the full list including duplicates. Duplicates are omitted from `Summary by Product` / `Summary by Feature Area` counts so those remain true active-issue counts.

## Step 5: Report

Print summary:
- Tickets processed / skipped / flagged (broken down by product directory)
- Open issues extracted (total + by area + by product)
- Link to daily index file

Remind the user to run `/roadmap regenerate` to update the roadmap from the new summaries.
