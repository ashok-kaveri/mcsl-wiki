---
title: StorePep System Architecture Overview
category: architecture
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# StorePep System Architecture Overview

## What is StorePep?

StorePep is a multi-tenant SaaS logistics platform that provides shipping and fulfillment services for e-commerce businesses. It handles the complete lifecycle of order processing - from ingestion through multiple e-commerce platforms, to shipping label generation across 15+ carriers, to tracking and delivery confirmation.

**Core Value Proposition**:
- Unified shipping interface for multiple carriers (FedEx, UPS, DHL, USPS, Canada Post, etc.)
- Automated order ingestion from multiple e-commerce platforms (Shopify, WooCommerce, Magento, BigCommerce)
- Intelligent rate shopping and label generation
- Subscription-based SaaS with feature toggles
- Multi-tenant architecture supporting thousands of merchant accounts

## High-Level Architecture

StorePep follows a **monolithic monorepo architecture** with clear separation between client and server:

```
storepepSAAS/
├── client/          # React frontend (37MB, ~698 JS/JSX files)
├── server/          # Node.js backend (33MB, ~1,679 JS files)
└── database/        # MongoDB (203MB with 106+ migrations)
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     E-commerce Platforms                     │
│   (Shopify, WooCommerce, Magento, BigCommerce, etc.)        │
└────────────────────────┬────────────────────────────────────┘
                         │ Webhooks / API Polling
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    StorePep Backend (Server)                 │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Express │  │  Routes  │  │ Services │  │  Models  │    │
│  │  Middleware│ │ (82 APIs)│ │  Layer   │  │ (92 DB)  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │               │             │          │
│       └─────────────┴───────────────┴─────────────┘          │
│                         │                                     │
│       ┌─────────────────┴─────────────────┐                  │
│       │        MongoDB (Mongoose)         │                  │
│       └───────────────────────────────────┘                  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Socket.io   │  │    Redis     │  │  Cron Jobs   │       │
│  │ (Real-time)  │  │   (Cache)    │  │ (Background) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   StorePep Frontend (Client)                 │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   React  │  │  Redux   │  │ Material │  │  Socket  │    │
│  │Components│  │  Store   │  │    UI    │  │  Client  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┴───────────────┴─────────────┘          │
│                         │                                     │
│       ┌─────────────────┴─────────────────┐                  │
│       │      Browser (webpack bundle)      │                 │
│       └───────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Integrations                      │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Shipping │  │ Payment  │  │ Monitoring│ │  Email   │    │
│  │ Carriers │  │ Gateways │  │ Services  │ │ Service  │    │
│  │(15+ APIs)│  │ (Stripe, │  │ (Sentry,  │ │(Mailgun) │    │
│  │          │  │  PayPal) │  │ NewRelic) │  │          │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## System Components

### 1. Frontend (Client)
- **Framework**: React 16.10.2 with class components and hooks
- **State Management**: Redux with Redux-Thunk for async actions
- **UI Library**: Material-UI 3.9.0 (dual version: v0 legacy + v1)
- **Routing**: React Router DOM 4.3.1
- **Build Tool**: Webpack 4 with custom production config
- **Location**: `client/src/`
- **Key Responsibilities**:
  - User interface for merchants
  - Order management dashboards
  - Shipping configuration
  - Label printing and manifest generation
  - Real-time order status updates via Socket.io

### 2. Backend (Server)
- **Framework**: Express.js 4.15.3 on Node.js
- **Database**: MongoDB with Mongoose 4.11.10 ODM
- **Authentication**: JWT-based with OAuth support (Auth0)
- **Real-time**: Socket.io 2.0.4 for live updates
- **Caching**: Redis 2.8.0
- **Location**: `server/src/`
- **Key Responsibilities**:
  - API endpoints (82 route handlers)
  - Business logic (service layer)
  - Database operations (92 models)
  - External integrations (carriers, stores, payments)
  - Background jobs (cron)
  - PDF generation (labels, packing slips, invoices)

### 3. Database
- **Technology**: MongoDB with Mongoose schema validation
- **Migration System**: migrate-mongo (106+ migrations tracked)
- **Models**: 92 distinct collections
- **Key Collections**:
  - `orders` - Order data and lifecycle
  - `products` - Product catalog from stores
  - `carriers` - Carrier configurations per account
  - `subscriptions` - Account subscription state
  - `packages` - Package definitions and tracking
  - `manifest` - Shipment manifests
  - `batches` - Batch processing records

### 4. Integration Layer
- **Shipping Carriers**: EasyPost API (multi-carrier), direct integrations for FedEx, UPS, DHL, Canada Post, etc.
- **E-commerce Platforms**: Shopify API, WooCommerce API, Magento, BigCommerce
- **Payment Gateways**: Stripe, PayPal, Razorpay
- **Monitoring**: Sentry (error tracking), New Relic (APM), Prometheus (metrics)
- **Email**: Nodemailer with Mailgun transport

## Data Flow

### Order Lifecycle
1. **Ingestion**: Order arrives via store webhook → validated → stored in DB
2. **Processing**: Merchant reviews → applies automation rules → selects carrier/service
3. **Shipping**: Generate label via carrier API → store label URL → update order status
4. **Manifest**: Batch orders into manifest → generate manifest document → mark ready for pickup
5. **Tracking**: Poll carrier tracking → update DB → push updates via Socket.io to frontend
6. **Completion**: Delivery confirmed → order marked complete → notifications sent

### Request Flow
```
User Action (React Component)
  ↓ dispatch
Redux Action Creator
  ↓ axios HTTP call
Express Route Handler
  ↓ business logic
Service Layer Module
  ↓ data access
Mongoose Model
  ↓ query
MongoDB
  ↓ response
back through stack → Redux reducer → React re-render
```

## Multi-Tenancy

StorePep is fully multi-tenant:
- Each merchant account has isolated data (orders, products, settings)
- Shared infrastructure (server instances, database)
- Account-level configuration (carriers, stores, subscriptions)
- Feature toggles control access to features based on subscription tier
- Access control via ACL (Access Control Lists) and JWT claims

## Deployment Architecture

- **Containerization**: Docker support for both client and server
- **CI/CD**: Jenkins pipelines for automated builds and deployments
- **Environments**: Development, Staging, Production
- **Client Deployment**: Webpack builds uploaded to S3, served via CDN
- **Server Deployment**: Node.js cluster mode for multi-core utilization
- **Monitoring**: Health checks, log aggregation (Winston + Syslog), metrics (Prometheus)

## Key Architectural Patterns

1. **Service Layer Pattern**: Business logic abstracted into reusable service classes (`shared/` directory)
2. **Middleware Chain**: Express middleware for auth, validation, error handling, logging
3. **Event Sourcing**: Supported via `@phivejs/eventsourcing-support` for audit trails
4. **Feature Toggles**: Runtime feature control via `@phivejs/feature-switch`
5. **Repository Pattern**: Mongoose models serve as data repositories
6. **Real-time Updates**: Socket.io for pushing order status changes to connected clients
7. **Background Processing**: Cron jobs for scheduled tasks (tracking updates, subscription renewals, etc.)

## Scale & Complexity Metrics

| Metric | Count |
|--------|-------|
| Frontend Component Files | 527 |
| Redux Actions | 87 |
| Redux Reducers | 26 |
| API Route Handlers | 82 |
| MongoDB Models | 92 |
| Database Migrations | 106+ |
| Service Modules | 40+ |
| Shipping Carrier Integrations | 15+ |
| E-commerce Platform Integrations | 6+ |
| Lines of Code (estimated) | >500,000 |

## Dependencies

This architecture overview references:
- [Frontend Architecture](./frontend-architecture.md) - Details on React/Redux setup
- [Backend Architecture](./backend-architecture.md) - Server structure and patterns
- [Technology Stack](./technology-stack.md) - Complete dependency list
- [Data Flow](./data-flow.md) - Detailed request/response cycles (to be created)
- [Authentication Flow](./authentication-flow.md) - JWT and OAuth details (to be created)

## Referenced By

This is the entry point for understanding the system. All module-level documentation references this overview.

## Related Pages

- [Deployment Pipeline](./deployment-pipeline.md) (to be created)
- [Monitoring & Observability](../operations/monitoring.md) (to be created)
- [Database Migrations](../operations/database-migrations.md) (to be created)
