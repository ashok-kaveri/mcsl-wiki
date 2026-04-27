# StorePep KB Activity Log

## [2026-04-27 14:56] zendesk-summarize | Delta extraction (30 tickets, schema migration)
- Processed: 30 delta tickets (24 shopify, 6 other_platforms)
- Created/updated: 30 summaries in `zendesk/summaries/*.md`
- Created: `zendesk/2026-04-27.md` — daily index with 6-column schema (added "Duplicate Of" column)
- Updated: `log.md`
- Git reference: c6f2681a3cd88e11f5247c84a2228a7a0e2e1a2e
- Summary: Delta extraction pipeline with schema migration from 5-column to 6-column Issue Index format. **Delta Detection**: Identified 30 changed tickets since last extraction (git ref 630297e). **Pipeline**: 6-step automated workflow (summarize_ticket.py → load_summaries.py → load_prior_index.py → assign_zi_ids.py → generate_daily_index.py → validate_daily_index.py). **5-Step ID Assignment**: (1) Exact match preserved 75 prior ZIs, (2) Fuzzy duplicate detection found 27 similar issues (Jaccard similarity ≥0.4) caused by title truncation in prior index, (3) Fresh assignment for 35 new issues (ZI-276 to ZI-310), (4) Cross-reference within new ZIs (none found), (5) Carry-forward of 65 prior ZIs not exact-matched. **Schema Migration**: Added "Duplicate Of" column to track issue relationships — 27 new ZIs reference prior ZIs as duplicates (e.g., ZI-276 → ZI-183 with 0.71 similarity). **Issue Stats**: 202 total active issues (up from 140), spanning ZI-136 to ZI-337. All 140 prior ZI IDs preserved. **Fuzzy Match Quality**: Spot-checked 5 fuzzy matches, all valid with 0.57-0.80 similarity scores. **Validation**: All checks passed — no duplicate ZIs, all "Duplicate Of" references valid, all ticket links resolve, issue count matches. **Implementation**: Created 7 Python scripts + driver shell script for automated future runs. Fixed title sanitization (newlines → spaces, pipe escaping) and duplicate ID assignment bug. **Product Breakdown**: shopify 36 issues, woocommerce 20 issues, unknown 130 issues, magento 1 issue (unchanged). **Area Breakdown**: other 59 issues, onboarding 14 issues, carrier-config 13 issues, label-generation 18 issues, order-management 11 issues, product-management 10 issues, etc.

## [2026-04-27 10:15] ingest | Ship-Rate-Track-Proxy Service
- Created: `architecture/carrier-api-proxy-pattern.md` — Unified API Gateway pattern with adapter pattern
- Created: `modules/shipping/ship-rate-track-proxy.md` — Ship-rate-track-proxy service module documentation
- Updated: `index.md` — Added carrier API proxy architecture page and ship-rate-track-proxy module to shipping section
- Updated: `log.md`
- Git reference: 0187f5ff1de74aa8b8769b98beef22fc29327b69 (ship-rate-track-proxy submodule)
- Summary: Ingested ship-rate-track-proxy microservice (252 TypeScript files, ~5,886 LOC). Documented unified API Gateway pattern providing consistent REST interface for 18+ carrier integrations (FedEx, UPS, USPS, TForce, PostNord, Amazon Shipping, etc.). Architectural patterns: Adapter pattern (per-carrier modules), API Gateway pattern (single entry point), dynamic provider loading (parseCarrier middleware), middleware pipeline (errorHandler → parseCarrier → publishAnalytics). Key features: 10 service categories (rates, shipment, tracking, pickup, returns, access-points, address-validation, landed-cost, documents, manifest), protocol abstraction (SOAP/REST/XML → unified JSON), OAuth 2.0 token management, error normalization, analytics publishing to SQS. Module structure: consistent pattern across all carriers (auth, rates, shipment, tracking, pickup services), ModuleLoader for DI, provider interfaces. Common infrastructure: carrier-api-client (retry/error handling), external-auth (OAuth), error-actions (5xx wrapper), validatable (schema validation), logger (Winston). Configuration: 122KB config.json with per-carrier sandbox/live URLs, service IDs, provider mappings. Test coverage: 8 tests (395 LOC, 6.7% ratio) — minimal coverage, no carrier integration tests identified as major tech debt. Deployment: Lambda + API Gateway, Node 16.20.2. Identified 8 tech debt items (low test coverage, massive config file, no schema validation, no versioning, SPOF risk, no rate limiting, no caching, no idempotency).

## [2026-04-27 09:45] ingest | Reporting Service
- Created: `architecture/event-driven-reporting.md` — Event-driven architecture pattern for async order aggregation
- Created: `modules/reporting/reporting.md` — Reporting service module documentation
- Updated: `index.md` — Added reporting architecture page and module to index
- Updated: `log.md`
- Git reference: 4728b3d692a83006cf44c6a40c57b06574e49639 (reporting submodule)
- Summary: Ingested reporting microservice (111 TypeScript files, ~3,800 LOC). Documented event-driven architecture with SQS message queues, denormalized order snapshots, async CSV export workflow, and S3/email delivery. Core components: OrderImportUnitaryService (order sync from main system), ReportScheduler (job creation), OrderExportUnitaryService (streaming CSV generation), filter system (composable criteria: Equals/Like/Range), event listeners (JobCreated → export, JobUpdated → email). Test coverage: 46 tests (~4,822 LOC, 1.27:1 test ratio), 6 integration tests covering DB operations and streaming exports. Database: 2 tables (Order with 36 fields, Job with status tracking), 12 migrations. Deployment: Lambda + API Gateway, Terraform/Ansible for QA/Prod environments. Dependencies: main storepep-react (emits order events), TypeORM, pg-query-stream, nodemailer, @phivejs/eventing (custom event bus). Identified 7 tech debt items (no pagination, no resume on failure, no incremental sync, S3 link expiry, no real-time reports, no queue backlog monitoring, no compression).

## [2026-04-27 02:29] sources | Added 7 New Source Repositories
- Added submodules:
  - `raw/carrier-registration` - Carrier registration service (GitLab)
  - `raw/ship-rate-track-proxy` - Ship rate track API implementations (GitLab)
  - `raw/reporting` - Reporting source base (Bitbucket)
  - `raw/order-search` - Order search service (GitLab)
  - `raw/storepep-internal-api` - Internal API service (GitLab)
  - `raw/order-updates` - Order updates service (GitLab)
  - `raw/fulfillment-service` - Fulfillment service (GitLab)
- Created: `architecture/carrier-registration.md` (placeholder stub)
- Created: `architecture/ship-rate-track-proxy.md` (placeholder stub)
- Created: `architecture/reporting.md` (placeholder stub)
- Created: `architecture/order-search.md` (placeholder stub)
- Created: `architecture/storepep-internal-api.md` (placeholder stub)
- Created: `architecture/order-updates.md` (placeholder stub)
- Created: `architecture/fulfillment-service.md` (placeholder stub)
- Updated: `raw/sources.yaml` (added 7 new git-submodule entries)
- Updated: `wiki/index.md` (added Sources section + 7 architecture pages)
- Updated: `wiki/log.md`
- Git reference: 5f4e58990f71acea410996b5e885f82c21e741e2
- Submodule commits:
  - carrier-registration: 8861b97
  - ship-rate-track-proxy: 0187f5f
  - reporting: 4728b3d
  - order-search: 87a25e4
  - storepep-internal-api: 71d57ae
  - order-updates: 95c3fe4
  - fulfillment-service: 4cef4a0
- Summary: Registered 7 additional code repositories as git submodules for future wiki ingestion. Services include: carrier-registration (carrier onboarding workflows), ship-rate-track-proxy (carrier API implementations), reporting (analytics and dashboards), order-search (advanced search/filtering), storepep-internal-api (inter-service communication), order-updates (status changes and notifications), and fulfillment-service (order fulfillment workflows). All submodules successfully cloned and ready for documentation. Created placeholder architecture pages with status=partial, ready for ingestion workflow when needed.

## [2026-04-23 15:00] ingest | Carriers and Adapters Complete Catalog
- Created: `architecture/carriers-and-adapters.md`
- Updated: `index.md` (added carriers-and-adapters.md to Architecture section)
- Updated: `log.md`
- Git reference: e5bf9867ce1e02cdbf9b2da90f081f15fa0be345 (storepep-react submodule)
- Sources analyzed:
  - `storePepConstants.js:41-90` - All carrier codes (C1-C54)
  - `storePepConstants.js:159-203` - Carrier name mappings
  - `shipmentAdaptor.js:1-191` - Adapter factory and class mappings
  - `storepepConfig.js` - API configuration patterns
  - Carrier-specific helper files (fedex, ups, australiaPost, dhl, canadaPost, blueDart, etc.)
- Summary: Comprehensive carrier integration reference cataloging all 45+ shipping carriers with carrier codes, descriptive names (e.g., "eParcel" for Australia Post C8), adapter class names, API protocols (SOAP, REST, XML), and endpoint URLs (sandbox/production where available in code). Organized by region (US/International, Australia/NZ, Canada, India, Europe, Middle East/Asia, Latin America) plus multi-carrier aggregators (EasyPost, Landmark Global). Documented legacy→modern API migrations (FedEx C2→C39, UPS C3→C38, USPS variants), special configurations (FedEx regional credentials, UPS integration modes, EasyPost 100+ carrier accounts, Australia Post eParcel variants), and known issues (SOAP deprecations, OAuth rate limits, regional endpoint complexity). Complete with "Adding a New Carrier" workflow and cross-references to shipping module pages.

## [2026-04-22 10:00] build | ZI Area Coupling Map
- Mode: build (full rebuild)
- Source: `wiki/zendesk/2026-04-20.md` (ZI issues) + `wiki/product/backlog.md` (clusters) + `wiki/architecture/coupling-map.md` (code coupling)
- ZI issues analyzed: 25 from 10 tickets
- Ticket co-occurrence pairs (≥2): 1
- Cluster co-occurrence pairs (≥1): 0
- Written: `wiki/zendesk/area-coupling.md`
- Cache: `.claude/cache/zendesk-overlap-data.json`
- Summary: Top overlap: carrier-config ↔ feature-request (2 tickets, no code co-changes). Most pairs are single-ticket overlaps below reporting threshold. No multi-area clusters detected in current backlog structure.

## [2026-04-16 16:30] ingest | Database Migrations Documentation
- Updated: `wiki/operations/database-migrations.md` (stub → complete)
- Git reference: 0f9b0bc965c82210bf38320d7c5a5ce60cfd44da (storepep-react submodule)
- Summary: Replaced stub with full documentation of the migrate-mongo workflow used by storepepSAAS. Covers tooling (migrate-mongo@^10.0.0, migrate-mongo-config.js targeting `storePep` db with `changelog` collection and `useFileHash: true`), migration anatomy (idempotency guards via mongoDictionary helpers, no-op down patterns, named indexes, background index builds), filename conventions, intent groupings across 108 migrations (31/32/38/7 across 2023-2026 — carrier service-code seeding ≈40% of corpus), runbook commands and required env vars, authoring checklist, and known issues including drift in backend-architecture.md (lists `server/src/db-migrations/migrations/` but actual path is `server/db-migrations/`).

## [2026-04-16 14:30] ingest | Carrier Integration — engineer's reference
- Updated: `wiki/modules/shipping/carrier-integration.md` (stub → complete, status flipped from needs-update → complete)
- Updated: `wiki/modules/shipping/carrier-system-overview.md` (added link in Dependencies)
- Updated: `wiki/modules/shipping/carrier-configuration.md` (added link in Related Pages)
- Updated: `wiki/modules/shipping/label-generation.md` (added link in Related Pages)
- Updated: `wiki/index.md` (replaced stub description with full one-line summary)
- Git reference: current
- Summary: Filled in the carrier-integration.md stub with an engineer-focused reference: three-file pattern per carrier (ShipmentHelper / RequestBuilder / Helper), dispatch checklist, HTTP retry pattern (FedEx httpClientFactory, not yet shared), four auth patterns, carrier-specific errorCodes dictionaries cross-referenced with the 49 centralised storepepErrorEvents, dual API migrations (FedEx C2/C39, UPS C3/C38, USPS variants), aggregator trade-offs (EasyPost, Eshipz), credential encryption notes, recent integration activity (Delhivery Proxy C54, FedEx REST negotiated rates, Australia Post OAuth + chunked manifest, PostNord country of origin, EasyPost sanitization), engineering checklist for adding a new carrier, and tech debt. Content complements but does not duplicate carrier-system-overview / carrier-configuration / label-generation — each claim is unique or explicitly delegated.

## [2026-04-16 10:00] ingest | Slack Source Type + Royal Mail Integration Constraints
- Created: `raw/slack/2026-04-15-royal-mail-easypost-integration.md` (raw Slack conversation)
- Created: `wiki/product/decisions/2026-04-15-royal-mail-integration-constraints.md` (decision record)
- Updated: `wiki/product/stories/ZI-057.md` (added Integration Constraints section)
- Updated: `raw/sources.yaml` (added slack source type)
- Updated: `wiki/index.md` (added decision record entry)
- Updated: `wiki/log.md`
- Git reference: current
- Summary: Added Slack as a new raw source type (manual, markdown with frontmatter). Captured internal Slack discussion (2026-04-15) revealing Royal Mail integration constraints: requires 3PI approval + OBA account + rates card approval from EasyPost/Royal Mail, no free production API for SaaS providers. QA blocked until EasyPost provides test credentials (Abhilash exploring). Decision record created, ZI-057 story card updated with constraints section. Pipeline: raw/slack/*.md → wiki/product/decisions/ + wiki/product/stories/ updates.

## [2026-04-13 20:00] ingest | Zendesk Issue Extraction & Backlog Regeneration
- Created: `zendesk/summaries/*.md` (66 per-ticket structured summaries)
- Created: `zendesk/2026-04-13.md` (daily index: 93 open issues from 66 tickets)
- Updated: `product/backlog.md` (regenerated: 11 clusters from 93 ZI issues)
- Updated: `product/roadmap-april-2026.html` (ZEN_FEATURES updated with ZI refs, 6 new zf entries)
- Updated: `index.md` (added Zendesk section)
- Updated: `log.md`
- Git reference: 5058f2c24d90fbaf9741d9279b8bdc8428a4af5e
- Source: `raw/zendesk/shopify/*.json` (66 valid, 1 corrupt, 2 truncated)
- Summary: Full pipeline run — each Zendesk ticket decomposed into structured summary with timeline, open/resolved issues, and customer context. 93 open issues extracted across 11 feature areas (label-generation 20, carrier-config 11, onboarding 11, order-management 10, international 10, product-management 9, carrier-migration 8, rate-shopping 6, feature-request 4, tracking 2, returns 2). Issues clustered into 11 backlog items with scoring. Roadmap ZEN_FEATURES updated with ZI cross-references. Pipeline: raw JSON → summaries → index → backlog → roadmap.

## [2026-04-10 12:00] ingest | Ground Zero Cross-App Support Triage
- Created: `support/ground-zero/index.md`
- Created: `support/ground-zero/pain-ranking.md`
- Created: `support/ground-zero/by-app.md`
- Created: `support/ground-zero/insights.md`
- Created: `support/ground-zero/sprint-views.md`
- Updated: `index.md` (added Support section, total pages 51→56)
- Updated: `log.md`
- Updated: `product/insights.md` (cross-link to ground-zero)
- Updated: `product/backlog.md` (cross-link to sprint-views)
- Updated: `raw/sources.yaml` (added stage-zero-analysis google-sheet source)
- Updated: `scripts/sync.sh` (added gid support for multi-tab Google Sheets)
- Source: `raw/sheets/stage-zero-analysis.xlsx` (synced 2026-04-10, gid=1368718443)
- Git reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
- Summary: Full cross-app triage of 68 open Zendesk tickets across Shopify (49), WooCommerce (15), BigCommerce (3), Magento (1). Tickets split into discrete issues, categorized into 10 issue types across 4 pain tiers. Top pain clusters: International/Customs (14 tickets, 10/10 pain), Product Import/Variants (11 tickets, 9/10), Carrier Integration/Migration (15 tickets, 8/10). 7 key insights distilled including aging backlog risk (tickets open 16-34 months). 6 sprint views created: Sprint Zero (deploy what's built), Fire Drill (AusPost/PostNord deadlines), Trust Restorers (data integrity), International Sprint (CI/customs batch), Scale Unlockers (variant limits), Carrier Expansion (new integrations).

## [2026-04-09 09:00] dashboard | Weekly Product Dashboard — Week of Apr 7
- Created: `product/dashboards/week-2026-04-07.md`
- Updated: `index.md`
- Git reference: 4f6714a0de70910399b45d628d3930f0404f6374
- Summary: Weekly dashboard synthesising 54 open Shopify MCSL tickets. Sections: Pulse metrics, 3 carrier deadlines (FedEx now, PostNord May 1, Australia Post Jul 7), feature health scorecard, 17 features ranked by customer demand across 3 tiers, carrier breakdown (9 carriers), recommended P0–P3 actions, stale ticket risk list.

## [2026-04-08 22:00] product-management | Product Management Layer Bootstrap

- Created: `product/backlog.md` - Scored backlog with 10 items from 52 Zendesk tickets
- Created: `product/insights.md` - Signal aggregation: 11 Zendesk themes, 7 test coverage gaps, 5 code hotspots, 3 emerging patterns
- Created: `product/metrics.md` - Customer health scorecard with pain index per feature area
- Created: `product/features/carrier-migration-fedex-rest.md` - Feature story with 3 user stories, acceptance criteria, cross-links
- Created: `product/decisions/2026-04-08-product-management-layer.md` - Decision record for PM layer approach
- Updated: `CLAUDE.md` - Added Product Management section with delta-aware resync workflows, templates, ticket categorization, cross-linking rules
- Updated: `index.md` - Added Product Management section
- Updated: `log.md`
- Git reference: b367ffe7e91f3fe5ccc496676bbfee860ed8c003
- Summary: Established source-driven product management layer (wiki/product/) synthesizing 52 open Shopify MCSL Zendesk tickets into actionable insights. **Zendesk Analysis**: Queried live API for tickets matching status<pending + support_type=agent + product=shopify_multi_carrier_shipping_label_app. Categorized into 11 feature areas: onboarding (9), carrier-config (8), label-generation (6), carrier-migration (4), order-management (3), australia-post (2), international (2), rate-shopping (2), tracking (1), feature-requests (1), other (14). **Key Signals**: 65% need dev work (dev_needed tag), FedEx migration is highest pain index (1700), 35% have high agent replies. **Delta-Aware Design**: All product pages use git_reference in frontmatter for delta detection on resync — git diff against raw/ finds new tickets, changed tests, updated sheets. Only delta is processed. **Ticket Categorization**: By product (shopify) and feature area, stored under wiki/product/. **Backlog Scoring**: Impact x Confidence / Effort framework with 10 initial items. **Pain Index**: Composite metric crossing ticket volume x severity with automation confidence — surfaces Carrier Migration, Rate Shopping, Australia Post as top priorities.

## [2026-04-08 20:45] guide | Added Associated Features Section to Carrier Journey Guide
- Updated: `adding-new-carrier-customer-journey.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Added comprehensive "Associated Features" section to carrier journey guide listing all 17 features affected by new carrier addition. **Features Organized**: Categorized by priority - Core (6 features: Carrier Config, Rate Shopping, Label Gen, Tracking, Service Selection, Cancellation), Important (4 features: Multi-Package, International, Return Labels, Special Services), Optional (3 features: Pickup, Manifest, Address Validation), Supporting (4 features: Rate Caching, Error Handling, Reports, Monitoring). **Feature Details**: Each feature includes what it does, customer interaction, code impact, automation percentage, test scenarios count, launch criticality, and related features. **Dependency Map**: ASCII diagram showing feature dependencies from Carrier Configuration as root to all dependent features (Rate Shopping → Service Selection → Automation, Label Generation → Multi-Package/International/Return/Special Services/Documents/Packaging, Tracking → Status Mapping/Email/Cron). **Priority Matrix**: Table showing 17 features across 4 priority levels with total 231 scenarios and 11.4% current automation. **Testing Priority**: Organized as Must Test (5 features before launch), Should Test (4 high-volume features), Can Test Later (4 optional features). **Implementation Complexity**: Effort estimates per feature ranging from 4-8h (special services) to 40-60h (label generation), with total complete implementation 136-212h and minimum viable 80-118h (Config + Rate + Label + Tracking + Errors). This section now serves as quick reference for understanding scope and dependencies when planning carrier integration.

## [2026-04-08 20:15] guide | Adding New Carrier - Customer Journey & Impact Analysis
- Created: `adding-new-carrier-customer-journey.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive guide for adding new carriers from customer perspective covering complete journey, system impacts, gaps, and rollout strategy. **Customer Journey**: Mapped 5 phases (Discovery, Registration, Onboarding, Daily Operations, Reporting) with 4 sub-phases in onboarding, identifying 20 pain points across customer experience from "Does MCSL support this carrier?" through daily label generation and tracking. **Feature Impact Analysis**: Documented 15 features affected by new carrier addition with priority classification (Core: Rate Shopping, Label Gen, Tracking; Optional: Pickup, Manifest, Address Validation) - each feature includes customer touchpoints, code changes needed, testing gaps, estimated scenarios, and criticality for launch. **Testing Requirements**: Per-carrier test matrix showing ~180 scenarios needed across 13 test categories (Registration 15, Rate Shopping 20, Label Generation 30, Tracking 25, Automation 12, International 15, Error Handling 20, etc.) with current coverage gaps (Registration 0%, Rate Shopping 0%, Tracking 7%, overall 11.4%). **Critical Gaps Identified**: 20 gaps categorized by severity - Critical (no carrier registration automation, no tracking status mapping, no post-save validation, no error message mapping, no label format validation), High Priority (no feature detection, no automation dry-run, no rate fetch audit, no tracking engine tests, no service code validation), Medium Priority (no carrier wizard, no comparison tool, no label preview, no health monitoring). **Documentation Needs**: Customer-facing (carrier setup guides per carrier 2-3 pages, comparison chart, troubleshooting guide 5 pages, feature matrix) and internal (integration checklist, API reference, status mapping guide). **Rollout Strategy**: 4-phase approach (Development & Testing 2-4 weeks, Soft Launch invite-only 2 weeks, General Availability 1 week, Post-Launch Maintenance ongoing) with go/no-go criteria, success metrics, and monitoring plan. **Launch Checklist**: Comprehensive 50+ item checklist covering pre-development, development (core features, optional features, advanced, error handling), testing, documentation, launch, and post-launch phases. **Complexity Examples**: Categorized carriers as Simple (Sendle 1-2 weeks, REST JSON, straightforward), Moderate (Canada Post 2-3 weeks, SOAP XML, bilingual, service points), Complex (FedEx 4-6 weeks, 1800+ LOC, 50+ fields, freight, customs). **Customer Pain Point Summary**: Table mapping each journey phase to customer goals, current pain points, and recommended fixes (e.g., Discovery phase: no carrier directory → create public carrier list; Onboarding: 50-field form no validation → multi-step wizard with test connection).

## [2026-04-08 19:30] analysis | System Features Comprehensive Analysis
- Created: `system-features-analysis.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Created comprehensive high-level feature analysis with automation coverage, code complexity assessment, scenario estimation, and confidence scoring. **Analysis Structure**: 20 high-level features analyzed covering Order Management, Label Generation, Carrier Configuration, Rate Shopping, Automation Rules, Tracking, Platform Connectors, Products, Warehouses, Bulk Actions, Packaging, Special Services, Auto Import, Grid Views, Reports, Account, Onboarding, COD, External Fulfillment, and Label Batching. **Complexity Assessment**: Categorized features by code complexity (6 Very High: 1000+ LOC, 9 High: 300-1000 LOC, 5 Medium/Low: <300 LOC) based on LOC counts from wiki documentation - Order Management (2139 LOC routes), Label Generation (1800+ LOC FedEx helper), Tracking (6800 LOC status mapper), Bulk Actions (2500+ LOC). **Scenario Estimation**: Estimated ~509 total test scenarios across all features with 75% confidence based on code analysis, API endpoints, business logic, carrier/platform multipliers, and error cases - ranging from 70 scenarios for Order Management to 5 scenarios for External Fulfillment. **Automation Coverage**: Detailed per-feature automation percentages showing 11.4% overall automation (58/509 scenarios) with breakdown: 100% coverage for 7 features (Label Gen, Packaging, Automation, Onboarding, COD, External Fulfillment, Batching), 0% for 6 critical features (Rate Shopping, Products, Warehouse, Auto Import, Reports). **Confidence Scoring**: 4-tier confidence assessment (High 92%+: 7 features, Medium 70-89%: 6 features, Low 40-69%: 2 features, None 0-39%: 5 features) with detailed justification per feature. **Critical Gaps Identified**: Priority 1 gaps (Auto Import, Rate Shopping, Product Management at 0% automation with high business impact), Priority 2 (Carrier Config 7%, Tracking 7%, Bulk Actions 30%), Priority 3 (Reports, Warehouse). **Recommendations**: Immediate actions (auto import, rate shopping, carrier expansion, product CRUD), short-term (tracking integration, bulk actions expansion, platform integration, warehouse tests), long-term (reports, multi-platform, all carriers, performance, E2E scenarios). **Methodology Documentation**: Included estimation methodology with confidence levels per feature and accuracy factors for transparency.

## [2026-04-08 19:00] test-coverage | Regression Test Matrix Integration
- Updated: `features.md` (complete restructure to align with regression test matrix)
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Restructured features.md to align with MCSL Regression Master Sheet from Google Sheets. **Matrix Structure**: Reorganized from test-type categories to feature area structure matching regression suite (Single Label Gen, Orders Grid, Packaging, SLGP, Quick Ship, General Settings, Views, Rules, Platform Setup, Adding Products, Tracking Page, Products Page, Account, Reports, Auto Import). **Ownership Mapping**: Added ownership assignments from spreadsheet (Ashok + Shahitha: Single Label Gen, Orders Grid, Reports; Basava: Packaging, SLGP, Quick Ship; Preethi + Anuja: General Settings; Preethi: Views). **Product Type Coverage**: Added product type matrix showing which product types (Simple, Digital, Custom, High Value, Dangerous Goods, Multi Product, Variable, Prepackaged) are tested across features. **Feature Area Details**: Each of 17 feature areas now includes purpose, owner, sub-components, automation status tables with product types, confidence scores, and test file mappings. **Automation Summary**: Top-level table showing automation percentage per feature area (100% for packaging, SLGP, quick ship, rules; 58% for orders grid; 0% for products, reports, auto import). **Critical Gaps Section**: Categorized gaps into High Priority (no automation - 8 areas), Medium Priority (partial - 6 areas), Low Confidence (3 areas) with specific recommendations. **Recommendations**: Immediate actions (auto import, product management, carrier coverage, tracking integration, grid filters), short-term (platform expansion, bulk actions, product types), long-term (reports, account, carrier registration, performance). **Test Organization**: Detailed test directory tree with 58 test files organized by functional domain. **Product Type Matrix**: Coverage analysis showing Simple and Multi Product well covered, Variable and Prepackaged not tested. **Maintenance Instructions**: Updated to include regression suite integration workflow for when spreadsheet data is updated.

## [2026-04-08 18:30] test-coverage | Complete Test Coverage Documentation
- Created: `features.md`
- Updated: `modules/orders/order-bulk-actions.md` (added test coverage section)
- Updated: `modules/shipping/label-generation.md` (added test coverage section)
- Updated: `modules/automation/automation-actions.md` (added test coverage section)
- Updated: `modules/shipping/carrier-configuration.md` (added test coverage section)
- Updated: `modules/shipping/shipment-tracking.md` (added test coverage section)
- Updated: `modules/stores/platform-connectors.md` (added test coverage section)
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive analysis of 58 Playwright test files in mcsl-test-automation, extracting 95 distinct user-facing features in plain English. **Features Document**: Created features.md organizing all tested features by category (Automation Rules, Carrier Configuration, COD, External Fulfillment, Label Batching, Onboarding, Order Management, Label Generation, Packaging, Document Management, Shopify Integration, Special Services) with test file references and module mappings. **Test Coverage Added**: Updated 6 module wiki pages with detailed test coverage sections including tested features tables, test file paths, coverage percentages, and lists of untested scenarios. **Statistics**: 58 test files analyzed covering 11 automation tests (100% coverage of tested actions), 3 carrier config tests (UPS only), 2 COD tests, 2 external fulfillment tests, 2 label batch tests, 2 onboarding tests, 22 order grid tests (12 action menu, 3 label generation, 7 advanced features), 5 order summary tests, 6 packaging tests, 1 Shopify test, 3 special services tests. **Coverage Highlights**: Order Bulk Actions 30%, Label Generation 100% (20/20 scenarios), Automation 46% (11/24 actions), Carrier Configuration <10% (UPS only), Tracking 7% (1 test), Platform Connectors (Shopify only). **Test Organization**: Tests organized by functional domain in mcsl-test-automation/tests/ directory with clear categorization for automation rules, carrier details, COD, fulfillment, batching, onboarding, order grid operations, packaging types, and special services.

## [2026-04-08 17:00] ingest | Shipment Tracking System
- Created: `modules/shipping/shipment-tracking.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive documentation of StorePep's shipment tracking system covering 45+ carrier integrations with automatic updates every 6 hours via cron job. **Architecture**: Three-layer data model (TrackingOrders for parent-level, TrackingPackages for individual packages, TrackingHistory for checkpoint timeline) with support for return shipment tracking. **Update Mechanism**: Scheduled cron job runs daily tracking task (storepepTrackingEngine.js:195-216) calling carrier APIs via ShipmentAdaptor pattern, with parallel tracking updates and rate limiting per carrier. **Status Mapping**: Universal status mapping system (storepepMappedTrackingStatus.js - 198KB, 6800+ lines) converts carrier-specific codes to StorePep standards (INITIAL, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED_UC, EXCEPTION_1/2/3) with 6-level attention type classification. **Real-time Updates**: Socket.io integration emits SOCKET_TRACKING_COMPLETED_CODE events to WebSocket server for live frontend notifications. **Email Notifications**: Automatic customer notifications via nodemailer with configurable triggers (trackingEventsEmailHelper.js) - emails sent on location change, status change, or attention type change with prevention of duplicate notifications. **Carrier Implementations**: Detailed documentation of FedEx (SOAP + REST), UPS (XML + OAuth), EasyPost tracking APIs with standardized response format. **Frontend**: React/Redux tracking container with status color coding (green/orange/red), timeline display, and manual re-track capability via POST /api/tracking/retrackall endpoint.

## [2026-04-07 23:00] ingest | Automation, Stores, Products, Warehouses
- Created: `modules/automation/automation-actions.md`
- Created: `modules/stores/store-integration-overview.md`
- Created: `modules/stores/platform-connectors.md`
- Created: `modules/products/product-management.md`
- Created: `modules/products/product-import-export.md`
- Created: `modules/warehouses/warehouse-selection.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive documentation of four critical StorePep domains completing the core feature set. **Automation**: Documented all 24 action types in AutomationActionsManager.js including carrier/service selection with fallback, package dimensions/weight (set/adjust), ship-from/display/sold-to addresses, order meta mapping, third-party billing, duties payer, insurance, delivery confirmation, carrier-specific special services (DHL, Aramex, Canada Post, PostNord, etc.), Saturday delivery, auto label generation, auto address correction, mark as not to ship, default service points (PostNord, DHL Sweden), and address-to-meta mapping. **Stores**: Documented store adapter pattern for 7 e-commerce platforms (Shopify, WooCommerce, Magento 2, Magento 1, BigCommerce, PrestaShop, Amazon India) with webhook management, OAuth/API authentication, order/product mapping, fulfillment sync, and platform-specific details (GraphQL bulk ops for Shopify, variant iteration for WooCommerce, SOAP for Magento 1, report-based for Amazon). **Products**: 191-line product model with physical attributes, customs data, carrier-specific metadata (dangerous goods, delivery signatures, dry ice, alcohol, restricted articles), SKU management, product types (simple, variable, variant, grouped, subscription), inventory tracking, and warehouse integration. **Warehouses**: WMS module with Strategy Pattern for warehouse selection (GeoDistanceStrategy using MongoDB geospatial queries, AddressBasedStrategy with routing rules), inventory-aware filtering, Odoo ERP integration, and automation override behavior where WMS-selected warehouse takes priority over automation-configured ship-from address.

## [2026-04-07 22:00] ingest | Shipping & Carriers System
- Created: `modules/shipping/carrier-system-overview.md`
- Created: `modules/shipping/carrier-configuration.md`
- Created: `modules/shipping/rate-shopping.md`
- Created: `modules/shipping/label-generation.md`
- Created: `modules/shipping/carrier-integrations.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Complete documentation of StorePep's multi-carrier shipping system - the foundation for label generation and fulfillment. Covered adaptor pattern for 43 carriers (46 configurations), parallel rate fetching with service selection, comprehensive label generation flow with multi-format support (PDF, ZPL, PNG), and customs handling for international shipments. Key findings: ShipmentAdaptor factory pattern (shipmentAdaptor.js:48-184), 487-line carrier model with carrier-specific fields, 300+ line addRateInfoToOrder.js for rate shopping, carrier-specific request builders (1800+ lines for FedEx), document stitching for packing slips and commercial invoices, and support for SOAP, REST, OAuth 2.0 authentication across global carriers.

## [2026-04-07 16:00] ingest | Order Management System
- Created: `modules/orders/order-lifecycle.md`
- Created: `modules/orders/order-bulk-actions.md`
- Created: `modules/orders/order-returns.md`
- Created: `modules/orders/order-address-management.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive documentation of order management - the core feature of StorePep. Covered complete order lifecycle (import → process → label → ship → track), 40+ bulk actions for high-volume operations, return label flow with separate tracking, and sophisticated address validation/correction system. Key findings: 2139-line orders route with 69 endpoints, 779-line order model with extensive multi-address support, OrderProcessingService for complex calculations, and event-sourced state transitions.

## [2026-04-07 14:00] bootstrap | Initial Architecture Documentation
- Created: `architecture/overview.md`
- Created: `architecture/frontend-architecture.md`
- Created: `architecture/backend-architecture.md`
- Created: `architecture/technology-stack.md`
- Created: `index.md`
- Created: `log.md` (this file)
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Initial architecture documentation covering system overview, frontend/backend structure, and complete technology stack. Bootstrap complete - ready for domain-specific ingestion.

## [2026-04-22 14:58] init | Co-Change Coupling Map
- Mode: init (since: 1 year ago)
- Source: `raw/storepep-react` @ `a5405aed`
- Commits analyzed: 599 (22 skipped — >30 files)
- Pairs above threshold (≥3): 5233
- Written: `wiki/architecture/coupling-map.md`
- Summary: Top coupling: featureToggles.json ↔ printSettingsHelperFunctions.js (133×)
