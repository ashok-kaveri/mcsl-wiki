---
name: story-cards
description: Generate product story cards from Zendesk ZI issues. Creates well-crafted user stories with acceptance criteria from ticket summaries, and pushes them as Trello cards. Use when the user wants to create story cards, generate stories, or turn ZI issues into actionable dev cards.
argument-hint: <ZI-NNN|all|delta|range|release> [lane] [board-url] [--no-trello]
allowed-tools: Bash, Read, Write, Glob, Grep, Agent, WebFetch, TodoWrite, AskUserQuestion
disable-model-invocation: false
---

# Story Card Generator

Generate product-quality story cards from Zendesk ZI issues. You are a **product owner with 15+ years of experience**. Every story card you write must be something a CEO can scan in 10 seconds, a developer can build from, and QA can verify.

**Argument**:
- `ZI-NNN` — generate a single story card
- `ZI-001:ZI-020` — generate a range
- `delta [lane]` — generate story cards from changed/new ZI issues only (default lane: apr-25-30)
  - `delta` — use APR 25-30 lane
  - `delta apr-13-16` — use APR 13-16 lane
  - `delta apr-16-18` — use APR 16-18 lane
  - etc.
- `all` — generate all ZI issues
- `all shopify` / `all woocommerce` / `all magento` — filter by product
- `apr-13-16` / `apr-16-18` / `apr-18-21` / `apr-21-25` / `apr-25-30` — generate by release window
- Append a Trello board URL to push cards to that board (e.g., `all https://trello.com/b/xyz`)
- Append `--no-trello` to skip Trello and only generate markdown

**Default Trello board**: `StoryLab` (board ID: `69dd9134576a26fcb79b670d`, URL: `https://trello.com/b/d1xk25XH/storylab`). If no board URL is provided, cards are pushed to StoryLab.

**Delta mode**: Automatically detects ZI issues created from changed/new Zendesk tickets (since last zendesk-summarize run). Useful after running `/zendesk-summarize delta` to quickly generate story cards for only the new support tickets without processing the entire backlog.

---

## Data Sources (read order)

1. `wiki/zendesk/2026-04-13.md` — canonical ZI ID → ticket mapping, area tags
2. `wiki/zendesk/summaries/<ticketId>.md` — **full structured ticket summary** (embedded verbatim into the story card)
3. `wiki/product/backlog.md` — which backlog cluster this issue belongs to
4. Raw ticket JSON (via python) — for exact `created_at` timestamp to compute SLA

---

## Delta Detection

**When to use `delta` mode:**
- After running `/zendesk-summarize delta` to extract new/changed Zendesk tickets
- To quickly generate story cards for only the new issues, without reprocessing the entire ZI catalog

**How it works:**
1. Read the latest daily index: `wiki/zendesk/YYYY-MM-DD.md`
2. Run `git diff <prior-commit>..HEAD -- raw/zendesk/` to find changed ticket files
3. For each changed ticket ID, find matching ZI issues in the daily index
4. Generate story cards for only those ZI issues
5. Push to the specified lane (default: APR 25-30)

**Delta anchor (git reference):**
- The daily index frontmatter contains `git_reference: <commit>` from the last zendesk-summarize run
- Delta mode diffs from that reference forward to find new/changed tickets
- If the reference is not in history (rebase/squash), falls back to `HEAD~1..HEAD`

**Example workflow:**
```bash
/zendesk-summarize delta      # Extract new/changed Zendesk tickets
/story-cards delta            # Generate story cards for those new issues (APR 25-30 lane)
/story-cards delta apr-13-16  # Or put them in a different lane
```

---

## StoryLab Board Structure

### Swimlanes (by release window)

Lanes are named after sprint release windows, not themes. Issues are assigned to lanes based on their **lane** (now/next/later) and **pain score**.

| Lane Name | Lane ID | Filter |
|-----------|---------|--------|
| `APR 13-16 · Week 1: Critical Fixes (Pain 10)` | `69dd9e0c273d0f0eb004e962` | lane=now AND pain=10 |
| `APR 16-18 · Week 1b: High Pain NOW (Pain 8-9)` | `69dd9e0c38d278e8c2c459d3` | lane=now AND pain 8-9 |
| `APR 18-21 · Week 2: NEXT Priority (Pain 8-9)` | `69dd9e0d579ac835a8b72efe` | lane=next AND pain 8-9 |
| `APR 21-25 · Week 2b: NEXT Remaining (Pain 5-7)` | `69dd9e0ee0844531e1074b13` | lane=next AND pain < 8 |
| `APR 25-30 · Week 3: LATER Items` | `69dd9e0e8a7bb8b998765ee7` | lane=later (all) |

### Lane Assignment Logic

```
now_areas = {label-generation, order-management, international}
next_areas = {carrier-config, carrier-migration, product-management, returns}
later_areas = {onboarding, rate-shopping, tracking, feature-request}

pain_map = {
  label-generation: 10, carrier-config: 8, carrier-migration: 7, onboarding: 4,
  order-management: 8, product-management: 9, international: 8, returns: 5,
  rate-shopping: 7, tracking: 4, feature-request: 5
}

if area in now_areas AND pain >= 10 → APR 13-16
if area in now_areas AND pain 8-9   → APR 16-18
if area in next_areas AND pain >= 8 → APR 18-21
if area in next_areas AND pain < 8  → APR 21-25
else (later)                        → APR 25-30
```

### Labels

| Label Name | Label ID | Color | Usage |
|------------|----------|-------|-------|
| `Shopify MCSL` | `69dd9134576a26fcb79b6723` | green | Product tag |
| `WooCommerce` | `69dd9134576a26fcb79b6725` | orange | Product tag |
| `Magento` | `69dd9134576a26fcb79b6727` | purple | Product tag |
| `Pain 10` | `69dd9134576a26fcb79b6726` | red | Severity tag |
| `Pain 8-9` | `69dd9134576a26fcb79b6724` | yellow | Severity tag |
| `SLA Breached` | `69dd9134576a26fcb79b6728` | blue | SLA status tag |
| `AI: Closed By Support` | `69dda72f123abc456def789g` | gray | Closed issue tag (auto-applied to resolved/closed tickets) |
| `Label & Document Quality` | `69dda3f5e846f4f43ea87d29` | red | Theme tag |
| `Carrier Platform` | `69dda3f5470641447a1bdc6e` | blue | Theme tag |
| `Order & Product Data` | `69dda3f67c209e8d65dc7978` | green | Theme tag |
| `International & Customs` | `69dda3f6e3f0ffaad39dfb82` | purple | Theme tag |
| `Onboarding & Retention` | `69dda3f73366b97280f973e1` | orange | Theme tag |
| `Rates & Intelligence` | `69dda3f75e4823b427cdec17` | yellow | Theme tag |
| `Feature Requests` | `69dda3f8fd2b781f799e7b1a` | sky | Theme tag |
| `🚚 FedEx` | `69dda71b16771e8f5339a16c` | purple | Carrier tag |
| `🚚 UPS` | `69dda71caf9e844c742b30b4` | sky | Carrier tag |
| `🚚 USPS` | `69dda71c82cf6793070ef4a8` | lime | Carrier tag |
| `🚚 DHL` | `69dda71dc5bbcef492f194f5` | yellow | Carrier tag |
| `🚚 PostNord` | `69dda71d00f918abc4017c3d` | pink | Carrier tag |
| `🚚 PostNL` | `69dda71db449b9124adb220f` | pink | Carrier tag |
| `🚚 Australia Post` | `69dda71e8ad8711e10023e59` | orange | Carrier tag |
| `🚚 BlueDart` | `69dda71e15af58313d824824` | blue | Carrier tag |
| `🚚 Royal Mail` | `69dda71fa9485fb90a389da9` | red | Carrier tag |
| `🚚 Canpar` | `69dda71fc1cb3047913d690f` | green | Carrier tag |
| `🚚 DPD` | `69dda71f95b500c95b729813` | lime | Carrier tag |
| `🚚 Delivro` | `69dda72014f1d93c606bc376` | black | Carrier tag |
| `🛠️ DEV` | `69ddcada5e444b9157da951d` | orange | Dev status (in active development) |
| `✅ DEV DONE` | `69ddcadb130379d4cb79b4ef` | lime | Dev status (code complete, not yet QA) |
| `🧪 QA` | `69ddcadb1d2769d25b6a6f92` | sky | Dev status (in QA / ready for QA) |
| `🚀 PROD` | `69ddcadcd5d8f116d99db5f4` | green | Dev status (shipped to production) |
| `📋 BACKLOG` | `69ddcadcd2bfb5a850ffb2cc` | black | Dev status (in backlog / cards to groom) |

### Card Priority (position within lane)

Cards are ordered by priority within each lane:
1. SLA breached cards first (longest overdue at top)
2. Then by pain score descending
3. Then by ticket age (oldest first — longest waiting)

Use `"pos": "top"` for highest priority, `"pos": "bottom"` for lowest within the lane.

### Trello API Details

Credentials in `.claude/settings.local.json` under `env`:
- `TRELLO_API_KEY`
- `TRELLO_TOKEN`

**Create card**:
```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$KEY&token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idList": "<lane_id>",
    "name": "ZI-NNN — <title>",
    "desc": "<full markdown card content>",
    "idLabels": "<label_id1>,<label_id2>",
    "pos": "top"
  }'
```

**Read credentials via python**:
```python
import json
sl = json.load(open('.claude/settings.local.json'))
key = sl['env']['TRELLO_API_KEY']
token = sl['env']['TRELLO_TOKEN']
```

---

## Story Card Format

Output: `wiki/product/stories/ZI-NNN.md` AND a Trello card on StoryLab.

The markdown file and the Trello card `desc` field use the same content:

```markdown
# ZI-NNN — <short title>

| Field | Value |
|-------|-------|
| **Ticket** | #NNNNNN |
| **Theme** | `<theme label>` |
| **App** | `<Shopify MCSL / WooCommerce / Magento>` |
| **Area** | <feature-area> |
| **Customers Affected** | N |
| **Pain** | N/10 |
| **Reported** | YYYY-MM-DD HH:MM UTC |
| **SLA Target** | YYYY-MM-DD HH:MM UTC (72h) |
| **SLA Status** | 🟢 On Track / 🟡 At Risk / 🔴 Breached (N days overdue) |

---

## Ticket Summary

<!-- Source: wiki/zendesk/summaries/<ticketId>.md -->

<FULL TICKET SUMMARY VERBATIM — everything after the YAML frontmatter>
<Customer info, Product, Duration, Timeline & Key Phases, Open Issues, Resolved Issues, Customer Context>
<Do NOT condense, paraphrase, or summarize>

---

## User Story

As a **<role grounded in the customer's real situation>**,
I want **<the underlying need — not the bug title restated>**,
so that **<the business/human outcome they actually care about>**.

---

## Acceptance Criteria (Simple)

- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] <Criterion 3>
- [ ] <Criterion 4>
- [ ] <Criterion 5>

---

## Acceptance Criteria (Given/When/Then)

### Scenario: <Happy path>
- **Given** <precondition>
- **When** <action>
- **Then** <expected outcome>
- **And** <additional assertion>

### Scenario: <Broader fix / edge case>
- **Given** <precondition>
- **When** <action>
- **Then** <expected outcome>

### Scenario: <Prevention / scale>
- **Given** <precondition>
- **When** <action>
- **Then** <expected outcome>
```

For the markdown file only, add YAML frontmatter at the top and a Cross-Links section at the bottom:

```markdown
---
title: "ZI-NNN — <short title>"
zi_id: ZI-NNN
ticket_id: <ticketId>
product: <shopify|woocommerce|magento>
theme: <labels|carrier|data|intl|onboarding|rates|requests>
area: <feature-area-tag>
pain: <1-10>
status: proposed
created: YYYY-MM-DD
sla_target: YYYY-MM-DDTHH:MM:SSZ
last_updated: YYYY-MM-DD
---

<card content above>

---

## Cross-Links

| Type | Link |
|------|------|
| Ticket Summary | [#NNNNNN](../../zendesk/summaries/NNNNNN.md) |
| Daily Index | [ZI-NNN](../../zendesk/2026-04-13.md) |
| Backlog | [<cluster name>](../backlog.md) |
| Roadmap | [roadmap-zi](../roadmap-zi-2026-04-14.html) |
| Trello | <card shortUrl after creation> |
```

---

## Writing Rules

### User Story — The Most Important Section

**You are translating customer pain into product intent.** The user story is NOT a restatement of the bug. It captures what the customer actually needs and why it matters to their business.

**Anti-patterns (NEVER do these):**
- ❌ "I want PostNL service code 6942 to be available" — restates the ticket title
- ❌ "I want label generation to succeed consistently" — vague, could mean anything
- ❌ "I want order sync to work through Cloudflare" — names the technical cause, not the need
- ❌ "I want the bug fixed" — useless

**Good patterns (DO these):**
- ✅ Start from the customer's SITUATION, not the bug report
- ✅ The "I want" should be the UNDERLYING NEED that would survive even if the technical solution changes
- ✅ The "so that" should name a REAL CONSEQUENCE the customer feels (money lost, time wasted, trust broken, team frustrated)
- ✅ Think: "If I were this merchant, what would I actually say to my board/partner/employee?"

**Framework for writing the story:**

1. **Read the Customer Context** — who are they? What plan? How long a customer? What volume?
2. **Read the Open Issues** — what's broken? How long broken? Who's blocking whom?
3. **Identify the REAL pain** — not "feature X is missing" but "I'm paying for automation and doing it manually" or "I'm overpaying because the cheap option isn't available"
4. **Write the role** — ground it in their situation: "store owner paying $30/month", "merchant who didn't choose their hosting stack", "high-volume seller shipping 10k labels/month"
5. **Write the want** — the underlying capability, not the bug fix: "all my contracted services available without waiting for dev work", "my orders to import regardless of what firewall sits in front"
6. **Write the so-that** — the business consequence: "my team stops wasting hours on manual shipments", "I don't have to become a Cloudflare expert to ship products"

**Proven examples:**

| ZI | ❌ Bad | ✅ Good |
|---|--------|---------|
| ZI-105 (label failures) | "I want label generation to succeed consistently" | "As a store owner paying $30/month for shipping automation, I want to understand why my labels keep failing and have the root cause fixed permanently, so that my team stops wasting hours on manual shipments that cost more than the app subscription itself, and I don't have to re-open the same ticket a second time" |
| ZI-096 (Cloudflare sync) | "I want order sync to work through Cloudflare" | "As a merchant who didn't choose their hosting security stack, I want my orders to import reliably regardless of what firewall or CDN sits in front of my store, so that my fulfillment pipeline isn't blocked for a month by infrastructure I don't control, and I don't need to become a Cloudflare expert just to ship my products" |
| ZI-098 (PostNL 6942) | "I want PostNL service code 6942 to be available" | "As a merchant who has a contract with PostNL for specific services, I want every service in my PostNL contract to be available in the app without waiting for a dev enhancement, so that I can use the cheapest tracked option for letterbox packages instead of overpaying for full parcel services or abandoning the app to generate labels manually on PostNL's portal" |
| ZI-081 (Amount field error) | "I want the Amount field error fixed" | "As a merchant trying to ship an order right now, I want label generation to never fail with a cryptic validation error that I can't fix myself, so that I don't have to open a support ticket and wait days just to ship one order while my customer wonders where their package is" |
| ZI-058 (eParcel delay) | "I want eParcel to be faster" | "As a high-volume merchant generating 50+ labels per day, I want bulk label generation to complete in seconds not minutes, so that my warehouse team isn't standing idle waiting for labels to print while orders pile up and same-day shipping cutoffs pass" |

### Ticket Summary — Verbatim from Zendesk Summarize

**ALWAYS** embed the full content from `wiki/zendesk/summaries/<ticketId>.md` (everything after the YAML frontmatter). Include:
- Customer info, Product, Duration lines
- All Timeline & Key Phases
- All Open Issues (with blocked/severity/area/comment citations)
- All Resolved Issues
- Customer Context

**Do NOT condense, paraphrase, or summarize.** The ticket summary IS the summary — it was already distilled by the zendesk-summarize pipeline. Embed it verbatim.

### Acceptance Criteria — Simple

5 checkboxes. Written so that:
- A QA engineer can verify each one independently
- A PM can read them in 30 seconds and know if the story is done
- At least one criterion addresses the SPECIFIC customer (their store, their orders)
- At least one criterion addresses PREVENTION (this shouldn't happen again / shouldn't require a ticket next time)
- No criterion is just "it works" — be specific about what "works" means

### Acceptance Criteria — Given/When/Then

3 scenarios minimum:
1. **Happy path** — the specific fix for this customer's issue
2. **Broader fix** — does the fix hold for similar cases? (other merchants, other carriers, other WAFs, etc.)
3. **Prevention/Scale** — how do we prevent this class of issue from recurring? (better error messages, self-serve config, dynamic service catalogs, etc.)

Each scenario must have:
- **Given**: a concrete precondition (not "given the system works")
- **When**: a specific user action
- **Then**: an observable, verifiable outcome
- **And** (optional): additional assertions that strengthen the test

### SLA Calculation

- Read the ticket's `created_at` from the raw JSON: `raw/zendesk/<product_dir>/<ticketId>.json`
- Use python: `json.load(open(path))['ticket']['created_at']`
- SLA target = `created_at + 72 hours`
- Status (compare against current date):
  - 🟢 **On Track**: today < SLA target
  - 🟡 **At Risk**: today is within 12 hours of SLA target
  - 🔴 **Breached**: today > SLA target — show "(N days overdue)"

### Theme Mapping

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

### Product Names

| Tag | Display Name |
|-----|-------------|
| shopify | Shopify MCSL |
| woocommerce | WooCommerce |
| magento | Magento |

---

## Execution

### Single card (`ZI-NNN`)
1. Look up ZI-NNN in daily index → get ticket ID, title, area, `Duplicate Of` (if any)
2. Read `wiki/zendesk/summaries/<ticketId>.md` — full summary (strip YAML frontmatter)
3. **Check ticket status**: Extract `status:` from summary frontmatter
   - If `status: closed` or `status: solved` → flag as "closed by support"
   - Will apply `AI: Closed By Support` label in step 8
4. Read raw JSON for `created_at` timestamp (check both `raw/zendesk/shopify/` and `raw/zendesk/other_platforms/`)
5. Compute SLA target and status
6. Write the user story, acceptance criteria, and GWT scenarios following the writing rules
7. Write story card to `wiki/product/stories/ZI-NNN.md` (include closure note if closed)
7.5. **QUALITY GATE (MANDATORY)** — Run the card through the Quality Assurance checklist above:
   - If ANY check fails → STOP, REWRITE, RE-VALIDATE, repeat until ALL checks pass
   - If ALL checks pass → proceed to step 8
   - **This is a hard stop. Do not skip.**
8. **Idempotency guard — enforces "old StoryLab cards are immutable"**:
   - If the ZI has `Duplicate Of: ZI-XXX` in the daily index → **skip the Trello push entirely.** The old card tracks the same work. Write a minimal markdown that cross-links to `wiki/product/stories/ZI-XXX.md` in its frontmatter (`duplicate_of: ZI-XXX`) and exit this step. Report `skipped_trello: duplicate_of=ZI-XXX`.
   - Else, **fetch the board fresh right now** (do NOT reuse a cached snapshot from earlier in the same run): `GET /boards/<STORYLAB>/cards?fields=name,desc,idLabels,shortUrl` (no `limit` param). Check if ANY existing card matches THIS ZI by:
     - Card name contains `[#<ticketId>]`
     - Card name starts with `ZI-<nnn>` (same ZI number)
     - Card `desc` mentions `ZI-<nnn>`
   - If ANY match → **skip the Trello push entirely.** NO `POST /cards`, NO `PUT /cards`, NO label additions, NO comment posts, NO desc rewrites. Report `existing_card: <shortUrl>`. The existing card retains 100% of its current state. The local markdown file still gets (re)generated — that's safe and expected.
   - Only if NO match → proceed to step 8 (actual Trello push).
   - **CRITICAL: This fetch must happen immediately before each POST — never cache it across cards. This is the only guard against duplicates.**
8. Push to Trello (unless `--no-trello`, and only if step 7 did not skip):
   - Determine lane from pain/area mapping
   - Card name format: `ZI-NNN — <title> [#<ticketId>]` — ticket number in brackets for searchability
   - Assign ALL applicable labels (comma-separated `idLabels`):
     - Product label (Shopify MCSL / WooCommerce / Magento)
     - Pain label (Pain 10 or Pain 8-9)
     - Theme label (Label & Document Quality / Carrier Platform / Order & Product Data / International & Customs / Onboarding & Retention / Rates & Intelligence / Feature Requests)
     - Carrier label(s) (🚚 FedEx / 🚚 UPS / 🚚 USPS / 🚚 DHL / etc.) — detect from ticket summary + title keywords
     - Dev status label — correlate with ph-WIP board (see ph-WIP Correlation below)
     - SLA Breached label (if SLA is breached)
     - **`AI: Closed By Support` label (if ticket status is "closed" or "solved")** — marks issues resolved by support without code changes
   - `POST /cards` with full markdown as `desc`
   - `pos`: `"top"` for SLA breached cards, `"bottom"` otherwise
   - Record Trello shortUrl in the markdown file's Cross-Links
9. **Correlate with ph-WIP board** (see ph-WIP Correlation section below):
   - Only runs for newly-created cards (step 8 executed).
   - Search ph-WIP for the ticket number in card name, desc, attachments, comments
   - If found: add dev status label + append ph-WIP Card section to card desc

### Delta mode (`delta [lane]`)

**Purpose**: Generate story cards for only the ZI issues created from changed/new Zendesk tickets (since last zendesk-summarize delta run).

**Steps**:
1. Parse the latest daily index: `wiki/zendesk/YYYY-MM-DD.md`
2. Read `git_reference` from daily index frontmatter (establishes delta anchor)
3. Run `git diff <git_reference>..HEAD --name-only -- raw/zendesk/` to find changed ticket JSON files
4. Extract ticket IDs from changed files: `raw/zendesk/product/<ticketId>.json` → list of ticket IDs
5. Search daily index for all ZI issues matching those ticket IDs
6. Determine target lane:
   - If `[lane]` argument provided (e.g., `delta apr-13-16`), use that lane
   - Otherwise, default to `apr-25-30`
7. For each ZI issue found, process using the Single Card workflow (steps 1-9 above)
8. Report: cards created, cards pushed to Trello, target lane, ZI ID range

**Example**:
```bash
/zendesk-summarize delta      # Extract new tickets, commit
/story-cards delta            # Generate cards for those new ZIs → APR 25-30 lane
/story-cards delta apr-16-18  # Or use a different lane
```

### Batch by release (`apr-13-16`, etc.)
1. Parse all ZI issues from daily index
2. Filter issues matching the release window's lane + pain criteria
3. Sort by priority: SLA breached first, then pain desc, then ticket age
4. Process each issue sequentially in the main thread: read summary, compute SLA, write story + push to Trello
5. **NEVER spawn parallel agents for Trello pushes** — parallel agents cause duplicate cards because each agent fetches a stale board snapshot before the other's card lands. Always process cards one at a time.
6. After all cards written: verify count, report per-lane stats

### Full batch (`all`)
1. Process all release windows in order: apr-13-16, apr-16-18, apr-18-21, apr-21-25, apr-25-30
2. Same logic as batch by release, applied to each window

### Report (after any execution)
Print:
- Cards created: N (markdown) + N (Trello)
- Per-lane breakdown: lane name → card count
- SLA summary: N on track, N at risk, N breached
- Board link: https://trello.com/b/d1xk25XH/storylab

---

## ph-WIP Correlation

Every StoryLab card is correlated with the **ph-WIP** Trello board (`63e1e0414b6026c45be1087c`, https://trello.com/b/PWKHwiCI) to determine dev status.

### How to Correlate

1. **Fetch all ph-WIP cards**: `GET /boards/63e1e0414b6026c45be1087c/cards?attachments=true&fields=name,desc,idList,shortUrl`
2. **Fetch ph-WIP lists**: `GET /boards/63e1e0414b6026c45be1087c/lists?fields=name,id`
3. **For each ZI issue**, search ph-WIP cards for the Zendesk ticket number in:
   - Card name
   - Card description
   - Attachment names/URLs
   - If still not found: fetch board comments via `GET /boards/{id}/actions?filter=commentCard&limit=1000` and search comment text
4. **Match pattern**: `#<ticketId>`, `<ticketId>`, or `zendesk.com/<ticketId>` in the searchable text
5. **When sanitizing card names for JS**: strip newlines, escape single quotes, truncate to 60 chars

### Dev Status Classification

Classify each ph-WIP lane into a dev status:

| Status | ph-WIP Lanes |
|--------|-------------|
| `BACKLOG` | Known issues, DevNeeded Cards, Cards to groom, Backlog, L3 Dev ready cards, Planning Lane, Handed Off from Product, Need more detail, Iteration Backlog, WMS Backlog |
| `DEV` | In Dev, Dev Box Testing |
| `DEV DONE` | Dev Done, L3 Debug/Tasks Tickets done(not need dev) |
| `QA` | Any lane containing "Ready for QA", "QA", "QA Automation", "Automation Done", "QA Verified", "Toggle On TestingPending" |
| `PROD` | Any lane starting with "PROD", "Releases Upcoming" |

### Dev Status Labels on StoryLab

| Label | ID | Color |
|-------|-----|-------|
| `🛠️ DEV` | `69ddcada5e444b9157da951d` | orange |
| `✅ DEV DONE` | `69ddcadb130379d4cb79b4ef` | lime |
| `🧪 QA` | `69ddcadb1d2769d25b6a6f92` | sky |
| `🚀 PROD` | `69ddcadcd5d8f116d99db5f4` | green |
| `📋 BACKLOG` | `69ddcadcd2bfb5a850ffb2cc` | black |

### ph-WIP Card Section in Description

When a match is found, append this section to the StoryLab card's description:

```markdown
---

## ph-WIP Card

**Card**: [<card name>](<shortUrl>)
**Lane**: <lane name>
**Link**: <shortUrl>
```

If multiple ph-WIP cards match the same ticket:
```markdown
**Additional card 2**: [<card name>](<shortUrl>) — <lane name>
```

### Carrier Detection

Auto-detect carriers from ticket summary + title using these keywords:

| Carrier | Keywords |
|---------|----------|
| FedEx | fedex, fed ex |
| UPS | ups |
| USPS | usps, stamps.com |
| DHL | dhl |
| PostNord | postnord |
| PostNL | postnl |
| Australia Post | australia post, auspost, eparcel, startrack |
| BlueDart | bluedart, blue dart |
| Royal Mail | royal mail, royalmail |
| Canpar | canpar |
| DPD | dpd |
| Delivro | delivro |

---

## Quality Assurance Gate (MANDATORY BEFORE PUBLISHING)

**EVERY story card MUST pass these checks before Trello push. If ANY check fails, REJECT and rewrite.**

### User Story Quality Checklist

- [ ] **NOT generic** — Does NOT say "store owner" or "merchant using this feature"
  - ❌ Bad: "As a store owner or merchant using this feature"
  - ✅ Good: "As a high-volume Shopify merchant paying $X/mo for automation"
- [ ] **Grounded in customer situation** — Includes specific context from the ticket (plan, volume, who's affected, how long problem persists)
  - ❌ Bad: "As a user"
  - ✅ Good: "As a store owner who didn't choose their hosting security stack"
- [ ] **Real pain identified** — The "so that" describes a CONSEQUENCE the customer feels, not "the bug is fixed"
  - ❌ Bad: "so that my shipping operations continue uninterrupted"
  - ✅ Good: "so that my team stops wasting hours on manual shipments that cost more than the app subscription itself"
- [ ] **Not restating the bug title** — The user story is the UNDERLYING NEED, not a restatement
  - ❌ Bad: "I want PostNL service code 6942 to be available"
  - ✅ Good: "I want every service in my PostNL contract available without waiting for dev work, so I can use the cheapest tracked option"

### Acceptance Criteria Quality Checklist

- [ ] **Has Given/When/Then scenarios** — NOT just "issue is resolved" checkboxes
  - ❌ Bad: `- [ ] Issue is resolved per customer request`
  - ✅ Good: `### Scenario: Customer imports products after Cloudflare WAF is active`
- [ ] **Scenarios are specific** — Each includes concrete precondition, action, observable outcome
  - ❌ Bad: Given "precondition"
  - ✅ Good: Given "store has Cloudflare WAF enabled on /wp-json endpoint"
- [ ] **At least 3 scenarios** — Happy path, broader fix, prevention
- [ ] **At least one scenario references the specific customer** — Their store, their volume, their constraint
- [ ] **Prevention scenario included** — How do we prevent this recurring? (better error messages, self-serve config, etc.)

### Ticket Summary Quality Checklist

- [ ] **Embedded verbatim** — Full summary from `wiki/zendesk/summaries/` included, NOT condensed
- [ ] **Customer context visible** — Ticket summary shows WHO reported it, WHEN, WHAT their setup is

### ENFORCEMENT

**If a card fails ANY check:**
1. **STOP** — do not push to Trello
2. **REWRITE** — user story and/or acceptance criteria
3. **RE-VALIDATE** — run through checklist again
4. **ONLY THEN PUSH**

**This is non-negotiable.** Generic boilerplate cards waste developer time and confuse the backlog. Every card must be worth reading.

---

## Sample Cards (validated quality)

These cards have been reviewed and approved as the quality standard:

**On StoryLab board (APR 13-16 lane):**
- `ZI-105` — https://trello.com/c/xcdDhB9O — Label failures forcing manual shipments (🟢 On Track)
- `ZI-081` — https://trello.com/c/h2ydg8oE — "Amount is a required field" error (🔴 Breached)
- `ZI-058` — https://trello.com/c/twgeW1TL — eParcel bulk generation delay 8+ sec (🔴 Breached)

**As markdown files:**
- `wiki/product/stories/ZI-105.md` — Shopify, label-generation, pain 10
- `wiki/product/stories/ZI-096.md` — WooCommerce, order-management, pain 8
- `wiki/product/stories/ZI-098.md` — Magento, carrier-config, pain 7
