---
title: StorePep KB Index
category: index
status: complete
last_updated: 2026-04-13
git_reference: current
---

# StorePep KB Index

Last updated: 2026-04-13

## Architecture

- [Overview](architecture/overview.md) - High-level system architecture and component interaction
- [Frontend Architecture](architecture/frontend-architecture.md) - React, Redux, Material-UI setup and patterns
- [Backend Architecture](architecture/backend-architecture.md) - Express, MongoDB, service layer architecture
- [Technology Stack](architecture/technology-stack.md) - Complete dependency listing and version information
- [Data Flow](architecture/data-flow.md) - How data moves through the system (stub)
- [Authentication Flow](architecture/authentication-flow.md) - Login, sessions, and ACL (stub)
- [Deployment Pipeline](architecture/deployment-pipeline.md) - CI/CD and build process (stub)

## Modules

### Orders
- [Order Lifecycle](modules/orders/order-lifecycle.md) - Core order flow from import through shipping and tracking
- [Order Bulk Actions](modules/orders/order-bulk-actions.md) - 40+ bulk operations for managing orders at scale
- [Order Returns](modules/orders/order-returns.md) - Return label generation and return tracking
- [Order Address Management](modules/orders/order-address-management.md) - Address validation, correction, and multi-address handling

### Shipping
- [Carrier System Overview](modules/shipping/carrier-system-overview.md) - Multi-carrier architecture with adaptor pattern for 43 carriers
- [Carrier Configuration](modules/shipping/carrier-configuration.md) - Carrier credentials, settings, and account management
- [Rate Shopping](modules/shipping/rate-shopping.md) - Parallel rate fetching, service selection, and currency conversion
- [Label Generation](modules/shipping/label-generation.md) - Label creation, document generation, and customs handling
- [Carrier Integrations](modules/shipping/carrier-integrations.md) - Complete list of 46 carrier configurations across all regions
- [Shipment Tracking](modules/shipping/shipment-tracking.md) - Tracking system with 45+ carrier integrations, cron updates, Socket.io real-time notifications, and email alerts
- [Carrier Integration](modules/shipping/carrier-integration.md) - Carrier adapter pattern and API communication (stub)
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

## Product Management

- [April 2026 Roadmap](product/roadmap-april-2026.html) - Interactive roadmap: 12 sprint features + 17 L3 items + 68 tickets, Gantt timelines, drag-and-drop swimlanes, global search (opens in browser)
- [Product Backlog](product/backlog.md) - Scored, prioritized work items with impact/effort/confidence framework
- [Product Insights](product/insights.md) - Aggregated signals from Zendesk themes, test gaps, code hotspots
- [Customer Metrics](product/metrics.md) - Per-feature health scorecard with pain index (52 Shopify MCSL tickets)
- [FedEx REST Migration](product/features/carrier-migration-fedex-rest.md) - Feature story: FedEx SOAP->REST migration (Pain Index: 1700, 5 tickets)
- [Decision: PM Layer](product/decisions/2026-04-08-product-management-layer.md) - Why and how the product management layer was established
- [Weekly Dashboard: Apr 7](product/dashboards/week-2026-04-07.md) - Week of Apr 7: 54 tickets, 3 carrier deadlines, 17 customer-ranked features

## Features & Testing

- [Features](features.md) - Complete list of 95 user-facing features with test coverage status organized by regression test matrix
- [System Features Analysis](system-features-analysis.md) - High-level feature analysis with automation coverage, code complexity, estimated scenarios, and confidence scores
- [Adding New Carrier - Customer Journey](adding-new-carrier-customer-journey.md) - Complete guide for adding carriers: customer experience, 15+ feature impacts, gaps, testing requirements (~180 scenarios/carrier), and rollout strategy

## Patterns

- [API Conventions](patterns/api-conventions.md) - REST URL structure, request/response formats (stub)
- [Redux Patterns](patterns/redux-patterns.md) - Action/reducer conventions, 87 actions, 26 reducers (stub)
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

---

**Total pages**: 57
**Last ingestion**: 2026-04-13 (April 2026 interactive product roadmap)
**Status**: Architecture + Orders + Shipping (with Tracking) + Automation + Stores + Products + Warehouses + Product Management + Support Triage documented
**Test Coverage**: 58 automated Playwright tests covering 95 features
