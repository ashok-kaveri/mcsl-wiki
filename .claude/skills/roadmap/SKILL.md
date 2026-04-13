---
name: roadmap
description: Regenerate or validate the April 2026 product roadmap from wiki summaries and backlog. Use when the user says roadmap, regenerate roadmap, update roadmap, or validate roadmap.
argument-hint: [regenerate|validate]
allowed-tools: Bash, Write, Read, Edit, Glob, Grep, Agent
---

# Roadmap Generator

Regenerate or validate `wiki/product/roadmap-april-2026.html` from the wiki summaries and backlog.

**Argument**: `$ARGUMENTS`
- `regenerate` — rebuild ZEN_FEATURES, THEMES, and KPIs from summaries (default)
- `validate` — check JS syntax only, report errors

**Critical rule**: Read from `wiki/zendesk/summaries/*.md` and `wiki/product/backlog.md`. NEVER read from `raw/zendesk/*.json`.

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
- `SP_FEATURES` — 12 sprint plan items (DO NOT MODIFY)
- `L3_ITEMS` — 17 L3 items (DO NOT MODIFY)
- `RELEASES` — preserve as-is
- `EPICS` — preserve as-is
- `STRATEGY` — preserve as-is
- `TECH_ITEMS` — preserve as-is
- `OPPS` — preserve as-is
- All rendering JavaScript (everything after `const app = ...`)

### Step 3: Generate ZEN_FEATURES

One `zf<N>` entry per ZI issue (where N = ZI number). Structure:

```javascript
zf<N>:{id:'zf<N>',title:'<issue title>',desc:'#<ticket> — <area>',lane:'<lane>',tags:[],pain:<pain>,effort:3,customers:1,start:<start>,end:<end>,theme:'<theme>',children:[{id:'#<ticket>',t:'ZI-<N>'}]},
```

**Lane assignment** (based on area):
- `now` (Apr 13-18): label-generation, order-management, international
- `next` (Apr 18-25): carrier-config, carrier-migration, product-management, returns
- `later` (Apr 25-30): onboarding, rate-shopping, tracking, feature-request

**Theme mapping** (7 themes):
| Area | Theme ID |
|---|---|
| label-generation | labels |
| carrier-config | carrier |
| carrier-migration | carrier |
| onboarding | onboarding |
| order-management | data |
| product-management | data |
| international | intl |
| returns | intl |
| rate-shopping | rates |
| tracking | rates |
| feature-request | requests |

### Step 4: Generate THEMES

7 data-driven themes. For each theme, collect all zf IDs + relevant sp/l3 IDs:

```javascript
const THEMES = [
  {id:'labels', label:'Label & Document Quality', color:'#c0392b',
   desc:'...', target:'Zero label-related tickets',
   kpis:{tickets:<count>, pain:8, revenue:'Retention'},
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
- onboarding: (none)
- requests: (none)

### Step 5: Update header KPIs

Update the KPI line:
```html
<div class="kpi"><b>12+17+<ZEN_COUNT></b><span>Sprint+L3+ZenDesk</span></div>
```

Update ZI Issues KPI if present.

### Step 6: Update description text

Ensure the theme description says `<N> investment themes` matching THEMES.length.

### Step 7: Validate

Run the validate check (Step from validate mode above). If errors, fix them before finishing.

### Step 8: Report

Print:
- ZEN_FEATURES: N entries
- THEMES: N themes
- Total features: N (SP + L3 + ZEN)
- JS validation: OK/ERROR
- Remind user to preview in browser

---

## Important notes

- The `children` array for each zf entry MUST have proper JS syntax: `[{id:'#<ticket>',t:'ZI-<N>'}]` — note the closing `}` before `]`
- THEMES features arrays use string IDs: `['zf1','zf2','l3_1']` — no object syntax
- After editing, always validate JS syntax with the node check
- SP_FEATURES and L3_ITEMS are maintained by the sprint planning process, not this skill
