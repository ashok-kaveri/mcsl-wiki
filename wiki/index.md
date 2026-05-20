---
title: StorePep KB Index
category: index
status: complete
last_updated: 2026-04-28
git_reference: current
---

# StorePep KB Index

Last updated: 2026-04-28

## Sources

Git submodules (code repositories):
- [storepep-react](../raw/storepep-react/) - Main StorePep SaaS codebase (React frontend + Node backend)
- [shopify-multicarrier-app](../raw/shopify-multicarrier-app/) - Shopify shell for multi carrier app
- [mcsl-test-automation](../raw/mcsl-test-automation/) - Playwright E2E test suite
- [carrier-registration](../raw/carrier-registration/) - Carrier registration service
- [ship-rate-track-proxy](../raw/ship-rate-track-proxy/) - Ship rate track APIs (carrier API implementations)
- [reporting](../raw/reporting/) - Reporting source base
- [order-search](../raw/order-search/) - Order search service for advanced search and filtering
- [storepep-internal-api](../raw/storepep-internal-api/) - Internal API service for inter-service communication
- [order-updates](../raw/order-updates/) - Order updates service handling status changes and notifications
- [fulfillment-service](../raw/fulfillment-service/) - Fulfillment service managing order fulfillment workflows

Other sources:
- Zendesk tickets - Customer support tickets (webhook-json)
- Regression scenarios - Master regression test plan (Google Sheets CSV export)
- Stage Zero Analysis - Cross-app support triage sheet (Google Sheets)
- Slack conversations - Internal product/engineering discussions (manual markdown)

## Architecture

- [Overview](architecture/overview.md) - High-level system architecture and component interaction
- [Shopify Multi-Carrier App Shell](architecture/shopify-multicarrier-app.md) - Shopify OAuth wrapper and installation shell bridging Shopify stores to StorePep platform
- [Frontend Architecture](architecture/frontend-architecture.md) - React, Redux, Material-UI setup and patterns
- [Backend Architecture](architecture/backend-architecture.md) - Express, MongoDB, service layer architecture
- [Technology Stack](architecture/technology-stack.md) - Complete dependency listing and version information
- [Carriers and Adapters](architecture/carriers-and-adapters.md) - Complete catalog of 45+ shipping carriers with codes (C1-C54), adapter classes, API endpoints, and protocol types
- [File Co-Change Coupling Map](architecture/coupling-map.md) - Files that frequently change together; blast-radius reference for planned changes (5233 pairs from last year)
- [Reverse Test Coverage Map](architecture/reverse-test-coverage.md) - Source file → test spec mapping; blast-radius reference for planned changes
- [Event-Driven Reporting](architecture/event-driven-reporting.md) - Event-driven architecture for async order aggregation and CSV export with SQS/S3/email delivery
- [Carrier API Proxy Pattern](architecture/carrier-api-proxy-pattern.md) - Unified API Gateway pattern for 18+ carrier integrations with adapter pattern, dynamic loading, and protocol abstraction (SOAP/REST/XML)
- [Carrier Registration Service](architecture/carrier-registration.md) - Carrier onboarding and OAuth management microservice with 15+ carriers, PostgreSQL credential storage, multi-step workflows, and HAL API (268 JS files, 35 migrations)
- [Order Search](architecture/order-search.md) - Order search service architecture (stub)
- [StorePep Internal API](architecture/storepep-internal-api.md) - Internal API service architecture (stub)
- [Order Updates](architecture/order-updates.md) - Order updates service architecture (stub)
- [Fulfillment Service](architecture/fulfillment-service.md) - Fulfillment service architecture (stub)
- [Data Flow](architecture/data-flow.md) - How data moves through the system (stub)
- [Authentication Flow](architecture/authentication-flow.md) - Login, sessions, and ACL (stub)
- [Deployment Pipeline](architecture/deployment-pipeline.md) - CI/CD and build process (stub)

## Modules

### Frontend
- [Orders UI](modules/frontend/orders-ui.md) - React/Redux order management interface with AG Grid, real-time updates, bulk actions, and advanced filtering
- [Shipping UI](modules/frontend/shipping-ui.md) - Label generation, manifests, carrier configuration (70+ carriers), rate shopping, tracking, OAuth registration flows
- [Packaging UI](modules/frontend/packaging-ui.md) - Box inventory, packing algorithms (5 methods), product-box mappings, carrier boxes, unit conversions
- [Settings UI](modules/frontend/settings-ui.md) - Comprehensive account configuration: stores (7 platforms), automation (21 components), users/permissions, tax, general settings

### Orders
- [Order Lifecycle](modules/orders/order-lifecycle.md) - Core order flow from import through shipping and tracking
- [Order Bulk Actions](modules/orders/order-bulk-actions.md) - 40+ bulk operations for managing orders at scale
- [Order Returns](modules/orders/order-returns.md) - Return label generation and return tracking
- [Order Address Management](modules/orders/order-address-management.md) - Address validation, correction, and multi-address handling

### Shipping
- [Carrier System Overview](modules/shipping/carrier-system-overview.md) - Multi-carrier architecture with adaptor pattern for 43 carriers
- [Ship-Rate-Track-Proxy Service](modules/shipping/ship-rate-track-proxy.md) - Unified API Gateway microservice for 18+ carriers with 252 files, 10 service categories, dynamic adapter loading, 6.7% test coverage (8 tests)
- [Carrier Configuration](modules/shipping/carrier-configuration.md) - Carrier credentials, settings, and account management
- [Rate Shopping](modules/shipping/rate-shopping.md) - Parallel rate fetching, service selection, and currency conversion
- [Label Generation](modules/shipping/label-generation.md) - Label creation, document generation, and customs handling
- [Carrier Integrations](modules/shipping/carrier-integrations.md) - Complete list of 46 carrier configurations across all regions
- [Shipment Tracking](modules/shipping/shipment-tracking.md) - Tracking system with 45+ carrier integrations, cron updates, Socket.io real-time notifications, and email alerts
- [Carrier Integration](modules/shipping/carrier-integration.md) - Engineering reference: 3-file pattern per carrier, HTTP retry, error code dicts, OAuth patterns, recent activity, checklist for adding a carrier
- [Batch Processing](modules/shipping/batch-processing.md) - Bulk label generation and queue management (stub)

### Automation
- [Automation Overview](modules/automation/automation-overview.md) - Rule-based business logic engine for automatic order configuration
- [Automation Actions](modules/automation/automation-actions.md) - 24 action types for carrier, dimensions, addresses, and special services
- [Automation Conditions](modules/automation/automation-conditions.md) - Condition types and evaluation logic

### Workflows
- [Automation Rules](modules/workflows/automation-rules.md) - Rule creation, conditions, and action execution (stub)

### Integrations
- [Store Platforms](modules/integrations/store-platforms.md) - Shopify, WooCommerce, Magento OAuth and sync (stub)

### Stores
- [Store Integration Overview](modules/stores/store-integration-overview.md) - E-commerce platform connectors and webhook management
- [Platform Connectors](modules/stores/platform-connectors.md) - Shopify, WooCommerce, Magento, BigCommerce, PrestaShop, Amazon India

### Products
- [Product Management](modules/products/product-management.md) - Product catalog with variants, SKUs, inventory, and carrier-specific metadata
- [Product Import/Export](modules/products/product-import-export.md) - CSV import/export and automated store synchronization

### Warehouses
- [Warehouse Selection](modules/warehouses/warehouse-selection.md) - WMS with strategy-based warehouse selection and Odoo integration

### Reporting
- [Reporting Service](modules/reporting/reporting.md) - Event-driven async order data aggregation and CSV export service with 46 tests (1.27:1 test ratio)

## Product Management

- [April 2026 Roadmap](product/roadmap-april-2026.html) - Interactive roadmap: 12 sprint features + 17 L3 items + 68 tickets, Gantt timelines, drag-and-drop swimlanes, global search (opens in browser)
- [April 2026 L3 Roadmap](product/roadmap-zi-2026-04-14.html) - ZI issue roadmap with Trello correlation, dev status, StoryLab cards, and ph-WIP lane tracking (opens in browser)
- [Product Backlog](product/backlog.md) - 11 backlog items scored from 93 ZI issues (66 tickets), impact/effort/confidence framework
- [Product Insights](product/insights.md) - Aggregated signals from Zendesk themes, test gaps, code hotspots
- [Customer Metrics](product/metrics.md) - Per-feature health scorecard with pain index (52 Shopify MCSL tickets)
- [FedEx REST Migration](product/features/carrier-migration-fedex-rest.md) - Feature story: FedEx SOAP->REST migration (Pain Index: 1700, 5 tickets)
- [Decision: PM Layer](product/decisions/2026-04-08-product-management-layer.md) - Why and how the product management layer was established
- [Decision: Royal Mail 3PI](product/decisions/2026-04-15-royal-mail-integration-constraints.md) - Royal Mail requires 3PI approval; EasyPost test credentials being pursued
- [Weekly Dashboard: Apr 7](product/dashboards/week-2026-04-07.md) - Week of Apr 7: 54 tickets, 3 carrier deadlines, 17 customer-ranked features

### Story Cards (ZI Issues)

- [Story Cards Directory](product/stories/) - 100+ story cards generated from Zendesk ZI issues with acceptance criteria and Trello links
- [ZI-012 — End of Day manifest / SCAN sheet](product/stories/ZI-012.md) - USPS Stamps SCAN form for consolidated pickup barcode (Pain: 10, Ticket #348049)

## Features & Testing

- [Features](features.md) - Complete list of 95 user-facing features with test coverage status organized by regression test matrix
- [System Features Analysis](system-features-analysis.md) - High-level feature analysis with automation coverage, code complexity, estimated scenarios, and confidence scores
- [Adding New Carrier - Customer Journey](adding-new-carrier-customer-journey.md) - Complete guide for adding carriers: customer experience, 15+ feature impacts, gaps, testing requirements (~180 scenarios/carrier), and rollout strategy

## Patterns

- [Carrier OAuth Registration Flow](patterns/carrier-oauth-flow.md) - OAuth 2.0 authorization code flow for UPS Ready, UPS DAP, USPS, Amazon Shipping, and PostNord with state token CSRF protection, polling-based status, multi-step confirmation, and token refresh automation
- [FedEx REST Registration Flow](patterns/carrier-fedex-rest-registration.md) - FedEx REST API multi-step registration with 3 validation methods (PIN-based SMS/Email, Invoice-based, Support-based auto-approval), child credential generation, platform-specific parent OAuth tokens, and regional support (US/APAC/MEISA/LAC/CA/AMEA)
- [Redux Patterns](patterns/redux-patterns.md) - Complete Redux architecture: ~100 action types, 30+ action modules, 26+ reducers, async patterns with Redux Thunk, Redux Form integration, immutable state updates, selector patterns, and best practices
- [API Conventions](patterns/api-conventions.md) - REST URL structure, request/response formats (stub)
- [Component Patterns](patterns/component-patterns.md) - React component conventions, Material-UI (stub)
- [Error Handling](patterns/error-handling.md) - Server and client-side error patterns (stub)
- [Service Layer](patterns/service-layer.md) - Backend service class structure (stub)
- [Event Sourcing](patterns/event-sourcing.md) - Event-driven patterns, Socket.io updates (stub)
- [Security](patterns/security.md) - ACL, input validation, credential storage (stub)
- [Access Control](patterns/access-control.md) - Role-based permissions and feature gating (stub)

## Operations

- [Local Setup](operations/local-setup.md) - Development environment setup (stub)
- [Database Migrations](operations/database-migrations.md) - Migration strategy, 106+ migrations (stub)
- [Monitoring](operations/monitoring.md) - Logging, alerting, observability (stub)

## Support

- [Ground Zero Triage](support/ground-zero/index.md) - Cross-app ticket analysis: 68 tickets across 5 apps, 10 issue categories, 6 sprint views
  - [Pain Ranking](support/ground-zero/pain-ranking.md) - All issues ranked from most to least painful across 4 tiers
  - [By App](support/ground-zero/by-app.md) - Per-app breakdown (Shopify, WooCommerce, BigCommerce, Magento) with cross-app patterns
  - [Insights](support/ground-zero/insights.md) - 7 key insights + aging backlog risk analysis
  - [Sprint Views](support/ground-zero/sprint-views.md) - 6 actionable priority queues from Sprint Zero to Carrier Expansion

### Zendesk Issue Extraction

- [Issue Extraction — 2026-05-20](zendesk/2026-05-20.md) - 11-ticket delta; 37 new issues (ZI-520 → ZI-556) across MCSL, FedEx app, AusPost & NZ Post roadmaps
- [Issue Extraction — 2026-05-11](zendesk/2026-05-11.md) - 17-ticket delta; ZI-496 → ZI-519
- [Issue Extraction — 2026-04-20](zendesk/2026-04-20.md) - Latest ZI issues extracted from Shopify MCSL tickets, grouped by feature area
- [Area Coupling Map](zendesk/area-coupling.md) - ZI area co-occurrence map; blast-radius reference cross-referenced against code coupling
- Per-ticket summaries: [zendesk/summaries/](zendesk/summaries/) - One structured summary per ticket with timeline, open/resolved issues, customer context

---

**Total pages**: 244+ (77 wiki + 66 ticket summaries + 100+ story cards + 1 index)
**Last update**: 2026-04-30 (Documented frontend shipping, packaging, and settings UI modules)
**Status**: Architecture + Orders + Shipping + Automation + Stores + Products + Warehouses + Reporting + Product Management + Support Triage + Zendesk Issue Pipeline + Frontend (Orders, Shipping, Packaging, Settings) documented
**Test Coverage**: 58 automated Playwright tests covering 95 features
**Client Scale**: 702 JS files, ~100 Redux action types, 30+ action modules, 26+ reducers, 100+ routes, 70+ carrier forms, 12 settings sections
**Sources**: 10 git submodules + 4 other source types (Zendesk, Google Sheets, Slack)
