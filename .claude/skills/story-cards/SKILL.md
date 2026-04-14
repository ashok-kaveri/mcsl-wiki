---
name: story-cards
description: Generate product story cards from Zendesk ZI issues. Creates well-crafted user stories with acceptance criteria from ticket summaries, and pushes them as Trello cards. Use when the user wants to create story cards, generate stories, or turn ZI issues into actionable dev cards.
argument-hint: <ZI-NNN|all|range|release> [board-url] [--no-trello]
allowed-tools: Bash, Read, Write, Glob, Grep, Agent, WebFetch, TodoWrite, AskUserQuestion
disable-model-invocation: false
---

# Story Card Generator

Generate product-quality story cards from Zendesk ZI issues. You are a **product owner with 15+ years of experience**. Every story card you write must be something a CEO can scan in 10 seconds, a developer can build from, and QA can verify.

**Argument**:
- `ZI-NNN` — generate a single story card
- `ZI-001:ZI-020` — generate a range
- `all` — generate all ZI issues
- `all shopify` / `all woocommerce` / `all magento` — filter by product
- `apr-13-16` / `apr-16-18` / `apr-18-21` / `apr-21-25` / `apr-25-30` — generate by release window
- Append a Trello board URL to push cards to that board (e.g., `all https://trello.com/b/xyz`)
- Append `--no-trello` to skip Trello and only generate markdown

**Default Trello board**: `StoryLab` (board ID: `69dd9134576a26fcb79b670d`, URL: `https://trello.com/b/d1xk25XH/storylab`). If no board URL is provided, cards are pushed to StoryLab.

---

## Data Sources (read order)

1. `wiki/zendesk/2026-04-13.md` — canonical ZI ID → ticket mapping, area tags
2. `wiki/zendesk/summaries/<ticketId>.md` — **full structured ticket summary** (embedded verbatim into the story card)
3. `wiki/product/backlog.md` — which backlog cluster this issue belongs to
4. Raw ticket JSON (via python) — for exact `created_at` timestamp to compute SLA

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
1. Look up ZI-NNN in daily index → get ticket ID, title, area
2. Read `wiki/zendesk/summaries/<ticketId>.md` — full summary (strip YAML frontmatter)
3. Read raw JSON for `created_at` timestamp (check both `raw/zendesk/shopify/` and `raw/zendesk/other_platforms/`)
4. Compute SLA target and status
5. Write the user story, acceptance criteria, and GWT scenarios following the writing rules
6. Write story card to `wiki/product/stories/ZI-NNN.md`
7. Push to Trello (unless `--no-trello`):
   - Determine lane from pain/area mapping
   - Card name format: `ZI-NNN — <title> [#<ticketId>]` — ticket number in brackets for searchability
   - Assign ALL applicable labels (comma-separated `idLabels`):
     - Product label (Shopify MCSL / WooCommerce / Magento)
     - Pain label (Pain 10 or Pain 8-9)
     - Theme label (Label & Document Quality / Carrier Platform / Order & Product Data / International & Customs / Onboarding & Retention / Rates & Intelligence / Feature Requests)
     - Carrier label(s) (🚚 FedEx / 🚚 UPS / 🚚 USPS / 🚚 DHL / etc.) — detect from ticket summary + title keywords
     - SLA Breached label (if SLA is breached)
   - `POST /cards` with full markdown as `desc`
   - `pos`: `"top"` for SLA breached cards, `"bottom"` otherwise
   - Record Trello shortUrl in the markdown file's Cross-Links

### Batch by release (`apr-13-16`, etc.)
1. Parse all ZI issues from daily index
2. Filter issues matching the release window's lane + pain criteria
3. Sort by priority: SLA breached first, then pain desc, then ticket age
4. Process each issue: read summary, compute SLA, write story + push to Trello
5. For large batches (20+ cards): spawn agents in groups of ~10, but **if agents fail on permissions, write cards yourself in the main thread**
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
