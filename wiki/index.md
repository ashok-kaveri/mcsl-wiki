# StorePep KB Index

Last updated: 2026-04-08

## Architecture

- [Overview](architecture/overview.md) - High-level system architecture and component interaction
- [Frontend Architecture](architecture/frontend-architecture.md) - React, Redux, Material-UI setup and patterns
- [Backend Architecture](architecture/backend-architecture.md) - Express, MongoDB, service layer architecture
- [Technology Stack](architecture/technology-stack.md) - Complete dependency listing and version information

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

### Automation
- [Automation Overview](modules/automation/automation-overview.md) - Rule-based business logic engine for automatic order configuration
- [Automation Actions](modules/automation/automation-actions.md) - 24 action types for carrier, dimensions, addresses, and special services

### Stores
- [Store Integration Overview](modules/stores/store-integration-overview.md) - E-commerce platform connectors and webhook management
- [Platform Connectors](modules/stores/platform-connectors.md) - Shopify, WooCommerce, Magento, BigCommerce, PrestaShop, Amazon India

### Products
- [Product Management](modules/products/product-management.md) - Product catalog with variants, SKUs, inventory, and carrier-specific metadata
- [Product Import/Export](modules/products/product-import-export.md) - CSV import/export and automated store synchronization

### Warehouses
- [Warehouse Selection](modules/warehouses/warehouse-selection.md) - WMS with strategy-based warehouse selection and Odoo integration

## Features & Testing

- [Features](features.md) - Complete list of 95 user-facing features with test coverage status organized by regression test matrix
- [System Features Analysis](system-features-analysis.md) - High-level feature analysis with automation coverage, code complexity, estimated scenarios, and confidence scores
- [Adding New Carrier - Customer Journey](adding-new-carrier-customer-journey.md) - Complete guide for adding carriers: customer experience, 15+ feature impacts, gaps, testing requirements (~180 scenarios/carrier), and rollout strategy

## Patterns

*No patterns documented yet. Cross-cutting concerns will be added as modules are ingested.*

## Operations

*No operations guides documented yet. Deployment, setup, and maintenance docs to be added.*

---

**Total pages**: 25
**Last ingestion**: 2026-04-08 (Shipment Tracking + Test Coverage)
**Status**: Architecture + Orders + Shipping (with Tracking) + Automation + Stores + Products + Warehouses documented
**Test Coverage**: 58 automated Playwright tests covering 95 features
