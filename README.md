# StorePep React Knowledge Base

An LLM-maintained wiki for the StorePep React codebase - a living, evolving companion to the code.

## What is this?

This is **not** traditional documentation that you write yourself. Instead, this is a knowledge base that **Claude maintains automatically** as you explore and work with the StorePep codebase.

Think of it as having a meticulous librarian who:
- Reads the code you point it to
- Extracts and summarizes the key information
- Creates interlinked wiki pages
- Keeps everything organized and cross-referenced
- Updates pages when code changes
- Never forgets connections between components

You curate what to explore. Claude does all the documentation grunt work.

## How it works

1. **Ingest**: You tell Claude to ingest a part of the codebase (e.g., "ingest the order management system")
   - Claude reads the relevant files
   - Discusses key findings with you
   - Creates/updates wiki pages with summaries, dependencies, and cross-references
   - Logs the activity

2. **Query**: You ask questions (e.g., "how does subscription validation work?")
   - Claude searches the wiki
   - Reads relevant pages
   - Checks source code if needed
   - Answers with citations

3. **Lint**: You ask Claude to health-check the wiki
   - Identifies stale pages
   - Finds missing documentation
   - Suggests areas to explore next

## Structure

```
wiki/
├── architecture/     # System-level docs (overview, frontend, backend, data flow)
├── modules/          # Feature/domain pages (orders, shipping, products, etc.)
├── patterns/         # Cross-cutting concepts (Redux patterns, API conventions)
├── operations/       # Dev/ops guides (setup, deployment, migrations)
├── index.md          # Catalog of all pages
└── log.md            # Chronological activity log
```

## Why this approach?

Traditional documentation gets stale because maintaining it is tedious:
- Updating cross-references across dozens of files
- Keeping summaries current when code changes
- Noting when new code contradicts old documentation
- Remembering to update related pages

LLMs don't get bored. They can touch 15 files in one pass. The wiki stays maintained because the cost of maintenance is near zero.

**Your job**: Curate sources, direct analysis, ask good questions, think about what it means.

**Claude's job**: Everything else - reading, summarizing, cross-referencing, filing, bookkeeping.

## Typical workflow

```bash
# Open this directory with Claude Code
cd /Users/sheeka/projects/external/storepep/mcsl-wiki

# Open Obsidian (or your favorite markdown viewer) in another window
# to browse the wiki as Claude builds it

# Tell Claude what to ingest
"Ingest the order management system"
"Ingest the Shopify integration"
"Ingest the subscription and payment flow"

# Ask questions
"How does multi-carrier shipping work?"
"What's the Redux state structure for orders?"
"Where does authentication happen?"

# Maintain the wiki
"Lint the wiki - what needs updating?"
"The carrier integration changed - update the relevant pages"
```

## Viewing the wiki

**Recommended**: [Obsidian](https://obsidian.md) - free markdown editor with graph view
- Open this folder as an Obsidian vault
- See the graph view to visualize page connections
- Follow links between pages naturally
- View both the wiki and your code side-by-side

**Alternatives**:
- Any markdown viewer
- VSCode with markdown preview
- Just read the raw markdown files

## About StorePep

StorePep is a multi-tenant SaaS logistics platform for e-commerce shipping and fulfillment:
- Multi-carrier shipping (FedEx, UPS, DHL, 15+ carriers)
- E-commerce integrations (Shopify, WooCommerce, Magento, etc.)
- Order management and automation
- Label generation and manifest creation
- Subscription-based access with payment processing

**Codebase**: `../storepep-react/storepepSAAS`
- Frontend: React 16.10.2, Redux, Material-UI
- Backend: Express.js, MongoDB, Socket.io
- Scale: 698 frontend files, 92 MongoDB models, 82 API routes, 106+ DB migrations

## Configuration

See `CLAUDE.md` for the complete schema that defines how Claude maintains this wiki:
- Page templates
- Ingestion workflows
- Cross-referencing conventions
- Log formats
- Special considerations for StorePep

## Getting started

If you're new to this KB:

1. Read this README
2. Browse `wiki/index.md` to see what's documented
3. Browse `wiki/log.md` to see what's been done recently
4. Open `wiki/architecture/overview.md` for the big picture (after initial bootstrap)
5. Ask Claude to ingest the areas you're working on

---

**Pattern Credit**: Inspired by the "LLM Wiki" pattern - a approach to building personal knowledge bases using LLMs as maintainers rather than retrievers.
