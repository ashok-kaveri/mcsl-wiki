---
name: roadmap
description: Regenerate, validate, or refresh per-card data in the April 2026 product roadmap from wiki summaries and backlog. Use when the user says roadmap, regenerate roadmap, update roadmap, validate roadmap, or refresh roadmap cards.
argument-hint: [regenerate|validate|refresh-cards]
allowed-tools: Bash, Write, Read, Edit, Glob, Grep, Agent
---

# Roadmap Generator

Regenerate, validate, or refresh per-card data in `wiki/product/roadmap-april-2026.html` from the wiki summaries and backlog.

**Argument**: `$ARGUMENTS`
- `regenerate` — rebuild ZEN_FEATURES, THEMES, and KPIs from summaries (default)
- `validate` — check JS syntax only, report errors
- `refresh-cards` — refresh `title` + `desc` on existing ZEN_FEATURES entries. Preserves structure: no entry added, removed, or reordered. No planning fields (lane/pain/effort/customers/start/end/theme/children) touched. SP_FEATURES / L3_ITEMS / THEMES / KPIs / RELEASES untouched.

**Critical rule**: Read from `wiki/zendesk/summaries/*.md` and `wiki/product/backlog.md`. NEVER read from `raw/zendesk/*.json`.

---

## Mode: `refresh-cards`

Lightweight refresh that enforces **Hard invariant #2** — the set of `ZEN_FEATURES` entries is frozen. New ZIs do NOT enter the roadmap via this command; only existing entries' display fields are refreshed.

**Contract**:
- Parse `ZEN_FEATURES` block from `wiki/product/roadmap-april-2026.html` (typically bracketed by `const ZEN_FEATURES = {` and a trailing `};` a few dozen lines later).
- For each entry `zf<N>` extract its `children[0].t` (the ZI-NNN).
- For each ZI, look up the latest state in `wiki/zendesk/2026-04-16.md` Issue Index:
  - **ZI present as active (no `Duplicate Of`)** → read current `title` and `area` → update fields `title` and `desc` in the JS object. `desc` format stays `'#<ticket> — <area>'`.
  - **ZI is a `Duplicate Of` another** → leave entry byte-identical. The preserved old ZI data is still canonical.
  - **ZI not in current index** → leave entry byte-identical; emit a `// stale: ZI-XXX not in 2026-04-16 index` comment line above the entry.
- Write back the block. VERIFY with `diff` that ONLY the ZEN_FEATURES block's lines changed (nothing in SP_FEATURES, L3_ITEMS, THEMES, KPIs, RELEASES, or the HTML shell).

**Refused operations** (the command refuses to execute any of these, even if requested):
- Add a new `zf<N+1>` entry (would break Hard invariant #2).
- Delete an existing `zf<N>` entry.
- Reorder entries.
- Modify `id`, `lane`, `tags`, `pain`, `effort`, `customers`, `start`, `end`, `theme`, or `children`.
- Touch `SP_FEATURES`, `L3_ITEMS`, `THEMES`, `KPIs`, `RELEASES`, `ALL_FEATURES`, or any HTML/CSS/JS outside the ZEN_FEATURES assignment.

**Verification after running** (do NOT skip):
1. `grep -c "^  zf" roadmap-april-2026.html` — count before and after must match (expected: 105).
2. `git diff roadmap-april-2026.html | grep '^[-+]' | grep -v '^---\|^+++' | head -20` — every changed line must be inside the ZEN_FEATURES block.
3. `grep -oE "ZI-1[0-3][0-9]" roadmap-april-2026.html | sort -u` — must return EMPTY (no ZI-106..ZI-139 entered the roadmap).

---

## Product Management Intent

You are a product manager with 15+ years of experience. The roadmap serves a team of 15 engineers and QA, and must be easily understood by the CEO, Support, and Partnerships teams.

### What the roadmap contains

1. **Release schedule** fitting the L3 72-hour SLA
2. **Product roadmap** for April with these views:
   a. Epic roadmap
   b. Features roadmap
   c. Release roadmap
   d. Strategy roadmap
   e. Technology roadmap
   f. Opportunity roadmap
   g. Theme roadmap — drill down into each theme to see its features
   h. Release calendar with Gantt timeline

### Format

- HTML page with Gantt-like timeline
- Items in **NOW / NEXT / LATER** swimlanes — moving an item between lanes should reflect on the timeline
- Each grouping (releases, strategy, tech, opportunity) hierarchically shows items with **pain, effort, customer score**
- Themes listed for April, with drill-down into features per theme
- Each release shows planned cards/tickets with themes highlighted

### Guiding principles

1. **72-hour SLA**: First response < 15 min. Triage < 4h. Dev fix < 48h. Ship to prod < 72h.
2. **Zero ticket goal**: We want to get to zero open tickets.
3. **L3 drives revenue**: L3 work is also a revenue opportunity, not just support.
4. **Feature overlap**: Feature requests should ideally overlap with L3 work.
5. **Revenue focus**: Prioritize features that drive revenue.
6. **3-customer rule**: A feature with 3+ customers asking → move into this week's backlog.
7. **Pain + effort visible**: Every feature shows support pain and effort scores.
8. **Ticket correlation**: Correlate with existing cards/tickets in play.
9. **Sprint plan inclusion**: Include features from `raw/a_proposed_april_plan/MCSL_April_2026_Sprint_Plan.html` (these are the SP_FEATURES).

### Data sources (read order)

1. `wiki/zendesk/summaries/*.md` — per-ticket structured summaries (open issues, customer context)
2. `wiki/zendesk/YYYY-MM-DD.md` — daily index with ZI IDs and area counts
3. `wiki/product/backlog.md` — scored, clustered backlog items
4. `wiki/product/roadmap-april-2026.html` — existing roadmap (preserve SP_FEATURES, L3_ITEMS, rendering code)
5. `raw/a_proposed_april_plan/MCSL_April_2026_Sprint_Plan.html` — sprint plan features (read-only reference)

---

## Validate mode

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('wiki/product/roadmap-april-2026.html', 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
for (const name of ['THEMES','SP_FEATURES','L3_ITEMS','ZEN_FEATURES']) {
  const re = name === 'THEMES'
    ? /const THEMES = (\[[\s\S]*?\]);/
    : new RegExp('const ' + name + ' = (\\\\{[\\\\s\\\\S]*?\\\\});');
  const block = m[1].match(re);
  if (!block) { console.log(name + ': NOT FOUND'); continue; }
  try {
    eval('var x = ' + block[1]);
    const len = Array.isArray(x) ? x.length : Object.keys(x).length;
    console.log(name + ': OK (' + len + ' entries)');
  } catch(e) { console.log(name + ': ERROR - ' + e.message); }
}
"
```

If errors found, report them and stop. If OK, report counts and stop.

---

## Regenerate mode

### Step 1: Extract issues from summaries

Read all `wiki/zendesk/summaries/*.md` files. For each, parse the **Open Issues** section to extract:
- Issue title
- Feature area tag (from `Area: <tag>`)
- Source ticket ID (from filename)

Build a list of all open issues with ZI-NNN IDs (matching the daily index).

Also read the latest `wiki/zendesk/YYYY-MM-DD.md` daily index for the canonical ZI ID assignments.

### Step 2: Read existing roadmap

Read `wiki/product/roadmap-april-2026.html`. Extract and preserve:
- All CSS and HTML (everything before `<script>` and after `</script>`)
- `SP_FEATURES` — sprint plan items (DO NOT MODIFY)
- `L3_ITEMS` — L3 items (DO NOT MODIFY)
- `RELEASES` — preserve as-is (sprint-sourced items stay, update Zendesk-sourced items)
- `EPICS` — preserve as-is
- `STRATEGY` — preserve as-is
- `TECH_ITEMS` — preserve as-is
- `OPPS` — preserve as-is
- All rendering JavaScript (everything after `const app = ...`)

### Step 3: Generate ZEN_FEATURES

One `zf<N>` entry per ZI issue (where N = ZI number). Each issue is its own card — not clustered.

```javascript
zf<N>:{id:'zf<N>',title:'<issue title>',desc:'#<ticket> — <area>',lane:'<lane>',tags:[],pain:<pain>,effort:3,customers:1,start:<start>,end:<end>,theme:'<theme>',children:[{id:'#<ticket>',t:'ZI-<N>'}]},
```

**Lane assignment** (based on area + 3-customer rule + pain):
- `now` (Apr 13-18): label-generation, order-management, international, anything with 3+ customers or pain >= 8
- `next` (Apr 18-25): carrier-config, carrier-migration, product-management, returns
- `later` (Apr 25-30): onboarding, rate-shopping, tracking, feature-request

**Theme mapping** (7 data-driven themes):

| Area | Theme ID | Theme Label |
|---|---|---|
| label-generation | labels | Label & Document Quality |
| carrier-config | carrier | Carrier Platform |
| carrier-migration | carrier | Carrier Platform |
| onboarding | onboarding | Onboarding & Retention |
| order-management | data | Order & Product Data |
| product-management | data | Order & Product Data |
| international | intl | International & Customs |
| returns | intl | International & Customs |
| rate-shopping | rates | Rates & Intelligence |
| tracking | rates | Rates & Intelligence |
| feature-request | requests | Feature Requests |

### Step 4: Generate THEMES

7 data-driven themes. For each theme, collect all zf IDs + relevant sp/l3 IDs:

```javascript
const THEMES = [
  {id:'labels', label:'Label & Document Quality', color:'#c0392b',
   desc:'<N> ZI issues. Packing slips, label gen, declared values, manifests.',
   target:'Zero label-related tickets',
   kpis:{tickets:<count>, pain:<avg>, revenue:'Retention'},
   features:[<sp/l3 IDs>, <zf IDs>]},
  // ... carrier, data, intl, onboarding, rates, requests
];
```

**Sprint/L3 items per theme:**
- labels: l3_6, l3_7, l3_8, l3_10, l3_11
- carrier: sp7, sp43, sp8, sp1, sp10, sp39, sp2, sp3, sp4, sp38, l3_1, l3_2, l3_4, l3_5, l3_9, l3_12, l3_13
- data: sp42, l3_14, l3_15, l3_16
- intl: l3_3
- rates: sp33, l3_17
- onboarding: (none from sprint)
- requests: (none from sprint)

### Step 5: Update header KPIs

Update:
- `SPRINT+L3+ZENDESK` counter: `12+17+<ZEN_COUNT>`
- `ZI ISSUES` counter: total open issues
- `OPEN TICKETS` counter: total tickets
- `P0-CRITICAL` counter: items with p0 tag
- Theme description: `<N> investment themes`

### Step 6: Validate

Run the validate check. If JS syntax errors, fix them before finishing.

**Common pitfalls:**
- `children` array: `[{id:'#<ticket>',t:'ZI-<N>'}]` — note closing `}` before `]`
- THEMES features arrays: `['zf1','zf2','l3_1']` — string IDs, no object syntax
- Don't use `replace_all` on patterns that exist in both THEMES and ZEN_FEATURES (e.g., `']},`)

### Step 7: Report

Print:
- ZEN_FEATURES: N entries (one per ZI issue)
- THEMES: N themes
- Total features: N (SP + L3 + ZEN)
- JS validation: OK/ERROR
- Remind user to preview in browser and hard-refresh

---

## Search behavior

The roadmap has a global search that:
- Searches across ALL data (features, releases, themes, epics, strategy, tech, opportunities)
- Matches on: id, title, desc, tags, theme, and children (ticket numbers, ZI IDs)
- **Only dims sections that have matches** — sections with zero matches stay at full opacity
- Matched cards get orange outline + glow, moved to top of container
- Gantt rows match via feature data lookup (not just label text)

---

## Important notes

- SP_FEATURES and L3_ITEMS are maintained by the sprint planning process, not this skill
- The roadmap is a self-contained HTML file (~80KB) with embedded CSS + JS
- After any edit, always validate JS syntax with the node check
- The search index is built at page load from ALL_FEATURES — any new zf entries are automatically searchable
