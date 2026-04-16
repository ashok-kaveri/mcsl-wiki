# StorePep KB Activity Log

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
