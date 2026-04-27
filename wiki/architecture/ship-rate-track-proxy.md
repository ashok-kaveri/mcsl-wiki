---
title: Ship Rate Track Proxy Service
category: architecture
sources: [ship-rate-track-proxy]
status: partial
last_updated: 2026-04-27
git_reference: 0187f5ff1de74aa8b8769b98beef22fc29327b69
---

# Ship Rate Track Proxy Service

## Overview

Ship rate track proxy service providing carrier API implementations for shipping, rating, and tracking operations. Acts as an abstraction layer between StorePep and carrier APIs.

**Source**: `raw/ship-rate-track-proxy/` (GitLab: pghive/services/ship-rate-track-proxy-api)

## Architecture

_To be documented: proxy architecture, carrier API adapters, request/response transformation_

## Key Components

_To be documented: carrier-specific adapters, rate shopping logic, tracking integrations_

## Data Flow

_To be documented: rate request flow, label generation flow, tracking update flow_

## Supported Carriers

_To be documented: list of carriers with proxy implementations_

## API Endpoints

_To be documented: proxy API endpoints, authentication, request/response formats_

## Integration Points

_To be documented: how this service integrates with the main storepep-react application, carrier registration service_

## Dependencies

_To be documented: external dependencies, carrier API libraries, database requirements_

## Related Pages

- [Carrier System Overview](../modules/shipping/carrier-system-overview.md)
- [Rate Shopping](../modules/shipping/rate-shopping.md)
- [Label Generation](../modules/shipping/label-generation.md)
- [Shipment Tracking](../modules/shipping/shipment-tracking.md)
- [Carriers and Adapters](carriers-and-adapters.md)
- [Carrier Integration](../modules/shipping/carrier-integration.md)
