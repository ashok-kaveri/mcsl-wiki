---
title: FedEx REST API Migration Support
category: product-feature
domain: shipping
sources: [zendesk, regression-scenarios, storepep-react, mcsl-test-automation]
status: proposed
last_updated: 2026-04-08
git_reference: b367ffe7e91f3fe5ccc496676bbfee860ed8c003
---

# FedEx REST API Migration Support

## Problem Statement

FedEx is deprecating their SOAP/XML API in favor of REST/JSON. Customers who have migrated (or are being forced to migrate) their FedEx credentials to REST are experiencing broken rate fetching, label generation failures, and missing features (e.g., document upload).

- **Evidence**: [#382425](../../../raw/zendesk/shopify/382425.json) (rates broken post-migration), [#379042](../../../raw/zendesk/shopify/379042.json) (migration deadline approaching), [#382188](../../../raw/zendesk/shopify/382188.json) (document upload missing in REST), [#379098](../../../raw/zendesk/shopify/379098.json) (migration help needed)
- **Affected users**: 4 customers reporting directly; likely affects all FedEx users as migration deadline approaches
- **Impact**: Revenue-critical — FedEx is one of the most used carriers. Broken FedEx = customers cannot ship.
- **Urgency**: External deadline from FedEx. Customers receiving migration notices.

## User Stories

### Story 1: As a merchant, I want to migrate my FedEx account from SOAP to REST API so that my shipping continues to work after FedEx deprecates SOAP

**Acceptance Criteria**:
- [ ] Given a merchant with existing FedEx SOAP credentials, when they enter new REST API credentials (Client ID + Secret), then the system validates and saves them
- [ ] Given REST credentials are configured, when a rate request is made, then rates are fetched via the REST API successfully
- [ ] Given REST credentials are configured, when a label is generated, then the label is created via the REST API successfully
- [ ] Given a merchant has both old SOAP and new REST credentials, when they save, then the system uses REST and disables SOAP

**Regression Scenarios** (from regression matrix):
- Single Label Generation sheet: All FedEx label scenarios
- Rate Domestic/International sheets: All FedEx rate scenarios
- Carrier Specific sheet: FedEx-specific features

### Story 2: As a merchant, I want to upload additional documents (commercial invoices, dangerous goods forms) via FedEx REST API so that my international shipments comply with customs requirements

**Acceptance Criteria**:
- [ ] Given FedEx REST credentials, when uploading a commercial invoice PDF, then the document is attached to the shipment via REST API
- [ ] Given FedEx REST credentials, when generating a label for dangerous goods, then DG paperwork is properly included
- [ ] Given a document upload attempt that fails, when the API returns an error, then a clear error message is shown to the merchant

**Regression Scenarios**:
- Label Generation sheet: Document upload scenarios
- Special Services sheet: Dangerous goods with FedEx

### Story 3: As a merchant, I want a guided migration path from FedEx SOAP to REST so that I can switch without downtime

**Acceptance Criteria**:
- [ ] Given the FedEx settings page, when a merchant has SOAP credentials, then a migration banner/guide is shown
- [ ] Given the migration flow, when a merchant enters REST credentials, then a test shipment validates the new setup before going live
- [ ] Given a failed test shipment, when the REST API returns errors, then the system explains what's wrong and suggests fixes

## Cross-Links

| Type | Link | Relationship |
|------|------|-------------|
| Wiki Module | [Carrier Configuration](../../modules/shipping/carrier-configuration.md) | FedEx credential storage and settings |
| Wiki Module | [Label Generation](../../modules/shipping/label-generation.md) | FedEx label creation (1800+ LOC request builder) |
| Wiki Module | [Rate Shopping](../../modules/shipping/rate-shopping.md) | FedEx rate fetching |
| Wiki Module | [Carrier System Overview](../../modules/shipping/carrier-system-overview.md) | ShipmentAdaptor pattern |
| Test Coverage | [Features](../../features.md) | FedEx automation status |
| Zendesk | [#382425](../../../raw/zendesk/shopify/382425.json), [#379042](../../../raw/zendesk/shopify/379042.json), [#382188](../../../raw/zendesk/shopify/382188.json), [#379098](../../../raw/zendesk/shopify/379098.json) | Customer reports |
| Carrier Guide | [Adding New Carrier](../../adding-new-carrier-customer-journey.md) | Integration pattern reference |
| Backlog | [Item #1](../backlog.md) | Prioritization |

## Customer Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| Related tickets (30d) | 4 | up |
| Avg resolution time | unresolved | - |
| Automation confidence | 🔴 0% (migration-specific) | - |
| Regression coverage | partial (FedEx SOAP tested, REST untested) | - |
| Pain Index | 1700 (highest) | - |

## Acceptance Sign-off

| Criteria | Status | Verified By |
|----------|--------|------------|
| All stories implemented | ⬜ | |
| FedEx REST rate fetch works | ⬜ | |
| FedEx REST label generation works | ⬜ | |
| FedEx REST document upload works | ⬜ | |
| Migration guide visible to SOAP users | ⬜ | |
| Regression scenarios pass (FedEx) | ⬜ | |
| No open P1/P2 FedEx tickets | ⬜ | |
| Automation confidence >= 70% | ⬜ | |

## Related Pages

- [Product Insights](../insights.md) - Carrier migration theme analysis
- [Customer Metrics](../metrics.md) - Pain index calculation
