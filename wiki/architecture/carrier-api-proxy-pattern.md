---
title: Carrier API Proxy Pattern
category: architecture
sources: [ship-rate-track-proxy]
status: complete
last_updated: 2026-04-27
git_reference: 0187f5ff1de74aa8b8769b98beef22fc29327b69
---

# Carrier API Proxy Pattern

## Overview

The ship-rate-track-proxy service implements a unified API Gateway pattern for heterogeneous carrier integrations. It provides a single, consistent REST API that abstracts away the complexity of 18+ carrier APIs with different protocols (SOAP, REST, XML), authentication mechanisms (OAuth, API keys, certificates), and data formats.

## Problem Statement

**Challenge**: Integrating with multiple shipping carriers requires:
- **Protocol diversity**: SOAP (FedEx legacy, UPS), REST (FedEx modern, USPS OAuth, TForce), proprietary XML
- **Authentication complexity**: OAuth 2.0, API keys, username/password, certificate-based auth, token refresh
- **Data format variations**: Different request/response structures per carrier
- **Error handling inconsistency**: Each carrier has unique error codes and formats
- **Environment management**: Separate sandbox vs production URLs and credentials per carrier
- **Versioning**: API version changes (e.g., FedEx SOAP → FedEx REST migration)

**Without a proxy**:
- Main application must implement 18 carrier-specific adapters
- Code duplication for common patterns (retry, logging, error mapping)
- Difficult to add new carriers (changes in multiple places)
- Hard to migrate carriers between API versions (widespread changes)

## Architectural Pattern

### Adapter Pattern + API Gateway

```
┌──────────────────┐
│  StorePep Main   │
│     System       │
└────────┬─────────┘
         │ Unified REST API
         │ (single interface)
         ▼
┌────────────────────────────────────────────┐
│      Ship-Rate-Track-Proxy (Gateway)       │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Unified REST API Layer              │ │
│  │  - /rates, /shipment, /tracking      │ │
│  │  - Standard request/response format  │ │
│  └──────────────┬───────────────────────┘ │
│                 │                          │
│  ┌──────────────▼───────────────────────┐ │
│  │  Middleware Pipeline                 │ │
│  │  - errorHandler                      │ │
│  │  - parseCarrier (selects adapter)    │ │
│  │  - publishAnalytics (SQS events)     │ │
│  └──────────────┬───────────────────────┘ │
│                 │                          │
│  ┌──────────────▼───────────────────────┐ │
│  │  Carrier Adapters (pluggable)        │ │
│  │  ┌─────┬─────┬─────┬─────┬─────┐    │ │
│  │  │FedEx│ UPS │USPS │TFrc │ ... │    │ │
│  │  └─────┴─────┴─────┴─────┴─────┘    │ │
│  └──────────────┬───────────────────────┘ │
│                 │                          │
└─────────────────┼──────────────────────────┘
                  │ Protocol-specific requests
         ┌────────┼────────┬────────┬────────┐
         ▼        ▼        ▼        ▼        ▼
    ┌────────┐ ┌────┐  ┌──────┐ ┌──────┐ ┌───────┐
    │ FedEx  │ │UPS │  │USPS  │ │TForce│ │ ...   │
    │  APIs  │ │APIs│  │ APIs │ │ APIs │ │ APIs  │
    └────────┘ └────┘  └──────┘ └──────┘ └───────┘
```

## Unified API Design

### Standard Request Flow

```
1. Client → POST /carriers/{carrier}/rates
   - Standard request format (JSON)
   - Carrier specified in URL path

2. parseCarrier middleware
   - Extracts carrier from path
   - Loads carrier config from config.json
   - Selects appropriate adapter module

3. Carrier Adapter
   - Transforms unified request → carrier-specific format
   - Handles authentication (OAuth, API key, etc.)
   - Calls carrier API
   - Transforms carrier response → unified format
   - Maps errors to standard codes

4. Response → Client
   - Standard response format (JSON)
   - HTTP status codes normalized
```

### Endpoint Categories

All endpoints follow `/carriers/{carrier}/{category}` pattern:

| Category | Endpoint | Purpose |
|----------|----------|---------|
| **Index** | `GET /carriers/{carrier}` | List available services for carrier |
| **Rates** | `POST /carriers/{carrier}/rates` | Get shipping rates |
| **Shipment** | `POST /carriers/{carrier}/shipment` | Create/confirm shipment (label) |
| **Shipment** | `DELETE /carriers/{carrier}/shipment` | Cancel/void shipment |
| **Returns** | `POST /carriers/{carrier}/shipment/returns` | Create return label |
| **Pickup** | `POST /carriers/{carrier}/shipment/pickup` | Request pickup |
| **Pickup** | `DELETE /carriers/{carrier}/shipment/pickup` | Cancel pickup |
| **Tracking** | `POST /carriers/{carrier}/shipment/tracking` | Get tracking details |
| **Access Points** | `POST /carriers/{carrier}/access-points` | Find drop-off locations |
| **Address** | `POST /carriers/{carrier}/validated-address` | Validate address |
| **Landed Cost** | `POST /carriers/{carrier}/landed-cost` | Calculate duties/taxes |
| **Documents** | `POST /carriers/{carrier}/shipment/documents` | Upload customs docs |
| **Manifest** | `POST /carriers/{carrier}/manifest` | Generate end-of-day manifest |

### Middleware Pipeline

**Request processing order**:

1. **errorHandler** — Wraps all controllers, catches exceptions, maps to HTTP errors
2. **parseCarrier** — Extracts carrier from URL, loads config, selects adapter
3. **publishAnalytics** (optional) — Publishes rate/shipment events to SQS for analytics
4. **Controller** — Invokes carrier adapter with unified request
5. **Carrier Adapter** — Transforms and calls carrier API

**Example middleware composition**:
```typescript
export const upsRate = errorHandler(parseCarrier(publishAnalytics(rate)));
```

This creates the pipeline: `errorHandler → parseCarrier → publishAnalytics → rate controller`.

## Carrier Module Pattern

### Module Structure

Each carrier implements a consistent structure:

```
modules/{carrier}/
├── services/
│   ├── auth/
│   │   └── AuthProviderImpl.ts       # OAuth/token management
│   ├── rates/
│   │   └── RateProviderImpl.ts       # Rate shopping
│   ├── shipment/
│   │   └── ShipmentProviderImpl.ts   # Label generation
│   ├── tracking/
│   │   └── TrackingProviderImpl.ts   # Shipment tracking
│   ├── pickup/
│   │   └── PickupProviderImpl.ts     # Pickup scheduling
│   ├── AccessPointProviderImpl.ts    # Drop-off locations
│   ├── AddressValidationProviderImpl.ts
│   ├── LandedCostProviderImpl.ts     # Duties/taxes
│   ├── ETDProviderImpl.ts            # Estimated delivery
│   └── ModuleLoader.ts               # DI container setup
```

### Provider Interface Pattern

All providers implement a standard interface for their category:

**RateProvider**:
```typescript
interface RateProvider {
  rate(request: UnifiedRateRequest): Promise<UnifiedRateResponse>;
}
```

**ShipmentProvider**:
```typescript
interface ShipmentProvider {
  confirm(request: UnifiedShipmentRequest): Promise<UnifiedShipmentResponse>;
  accept(request: AcceptRequest): Promise<AcceptResponse>;
  cancel(request: CancelRequest): Promise<CancelResponse>;
}
```

**TrackingProvider**:
```typescript
interface TrackingProvider {
  track(request: UnifiedTrackingRequest): Promise<UnifiedTrackingResponse>;
}
```

### ModuleLoader Pattern

Each carrier has a `ModuleLoader.ts` that configures the DI container:

```typescript
// Example pattern (pseudo-code)
export class ModuleLoader {
  static load(container, config) {
    container.register('RateProvider', RateProviderImpl);
    container.register('ShipmentProvider', ShipmentProviderImpl);
    container.register('TrackingProvider', TrackingProviderImpl);
    container.register('AuthProvider', AuthProviderImpl);
    // ... register all providers
  }
}
```

The `parseCarrier` middleware uses this to dynamically load the right module.

## Configuration System

### config.json Structure

Massive 122KB JSON file with per-carrier configuration:

```json
{
  "carriers": {
    "{CARRIER_NAME}": {
      "registration": {
        "default": "{uuid}"  // Links to ph-registration service
      },
      "analytics": {
        "carrierCode": "C2"  // Maps to main system carrier codes
      },
      "name": "{CARRIER_NAME}",
      "defaultPluginHiveCredentials": {
        // Test credentials for sandbox
      },
      "index": {
        "serviceId": "{uuid}"  // Root service ID
      },
      "sandbox": [
        {
          "url": "https://sandbox.carrier.com/api",
          "serviceId": "{uuid}",
          "category": "rates",
          "relName": "rates",
          "name": "RateProviderImpl",
          "subCategory": { /* optional */ }
        },
        // ... more services
      ],
      "live": [
        // Same structure as sandbox, different URLs
      ]
    }
  }
}
```

**Service ID system**: Each carrier capability gets a UUID that:
- Uniquely identifies the service
- Maps to provider implementation class name
- Links to ph-registration service credentials
- Used for analytics tracking

### Dynamic Provider Loading

**parseCarrier middleware flow**:

1. Extract carrier name from URL path (`/carriers/UPS/rates` → `"UPS"`)
2. Load carrier config from `config.json.carriers.UPS`
3. Determine environment (sandbox vs live) from request headers
4. Find service config matching category (e.g., `"rates"`)
5. Load provider class by name (`config.name` → `"RateProviderImpl"`)
6. Instantiate provider with config (URL, credentials, service ID)
7. Invoke provider method with unified request

## Authentication Strategy

### OAuth 2.0 (USPS, FedEx REST)

**Token caching**:
- Auth providers cache access tokens
- Refresh tokens before expiry
- Shared across requests (in-memory)

**Flow**:
```
1. First request → AuthProvider.getToken()
2. If no cached token → Call OAuth endpoint
3. Cache token with TTL (expires_in - buffer)
4. Return token for request
5. Subsequent requests → Use cached token
6. Token expired → Refresh automatically
```

### API Key / Username+Password (UPS, FedEx SOAP)

**Stored in**:
- AWS SSM Parameter Store (via RemoteConfig)
- OR config.json defaultPluginHiveCredentials (test/sandbox)
- OR ph-registration service (production)

**Credential resolution order**:
1. Check request headers for user-provided credentials
2. Else, load from ph-registration service by serviceId
3. Else, use defaultPluginHiveCredentials from config.json
4. Else, error (no credentials available)

### Certificate-based (rare)

Some carriers require client certificates for HTTPS. Managed via:
- AWS Secrets Manager (cert + private key)
- Loaded on bootstrap
- Attached to Axios HTTPS agent

## Error Handling Strategy

### Error Mapping Pipeline

```
Carrier API Error
    ↓
Carrier Adapter catches exception
    ↓
Maps to standard error code + message
    ↓
Throws standardized error object
    ↓
errorHandler middleware catches
    ↓
Maps to HTTP status code
    ↓
Returns JSON error response
```

### Standard Error Format

```json
{
  "error": {
    "code": "RATE_UNAVAILABLE",
    "message": "No rates available for this shipment",
    "carrierCode": "ERR-123",
    "carrierMessage": "Original carrier error message",
    "details": { /* carrier-specific details */ }
  }
}
```

### Error Categories

- **Authentication errors** → 401 Unauthorized
- **Validation errors** → 400 Bad Request
- **Not found** (tracking, shipment) → 404 Not Found
- **Carrier unavailable** → 503 Service Unavailable
- **Rate limit exceeded** → 429 Too Many Requests
- **Unknown errors** → 500 Internal Server Error

### Retry Strategy

**Implemented in `carrier-api-client`**:
- Retry on 5xx errors (server-side)
- Exponential backoff (100ms, 200ms, 400ms, ...)
- Max 3 retries
- No retry on 4xx errors (client-side)

**status5xxWrapper**:
Wraps HTTP calls, retries on 500/502/503/504.

## Analytics Publishing

**publishAnalytics middleware**:
- Intercepts rate and shipment requests
- Publishes event to SQS queue
- Non-blocking (fire-and-forget)
- Used for:
  - Rate shopping analytics
  - Carrier usage tracking
  - Performance monitoring

**Event payload**:
```json
{
  "carrier": "UPS",
  "category": "rates",
  "timestamp": "2026-04-27T10:00:00Z",
  "serviceId": "{uuid}",
  "request": { /* sanitized request */ },
  "response": { /* sanitized response */ },
  "duration_ms": 450
}
```

## Benefits of This Pattern

1. **Separation of concerns**: Main system doesn't need carrier-specific logic
2. **Independent scaling**: Proxy can scale separately from main app
3. **Resilience**: Failures isolated to proxy; main app unaffected
4. **Versioning**: Can run multiple API versions side-by-side (e.g., FedEx SOAP + REST)
5. **Testability**: Mock carrier responses without hitting real APIs
6. **Observability**: Centralized logging, metrics, analytics for all carriers
7. **Easier onboarding**: Add new carrier by implementing standard interfaces

## Trade-offs

### Advantages ✅
- **Single API contract** for all carriers
- **Centralized** authentication, error handling, retry logic
- **Easy to migrate** carriers between API versions
- **Analytics** built-in (rate shopping, usage tracking)

### Disadvantages ❌
- **Additional network hop** (latency ~50-100ms)
- **Single point of failure** (proxy down = all carriers down)
  - Mitigated: Lambda auto-scaling, multi-AZ deployment
- **Config complexity**: 122KB config file hard to maintain
- **Limited carrier-specific features**: Unified API constrains to common denominator

## Deployment

**Serverless Lambda deployment**:
- Express app wrapped with `@vendia/serverless-express`
- API Gateway → Lambda handler
- Cold start: ~500ms (config load from SSM)
- Warm requests: ~50ms overhead

**Multi-environment**:
- QA: `phive-workload-qa01`
- Prod: `phive-workload-prod02`
- Deployed via Ansible + Terraform

## Related Patterns

- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter) — Each carrier module is an adapter
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html) — Single entry point for multiple backends
- [Facade Pattern](https://refactoring.guru/design-patterns/facade) — Simplifies complex carrier APIs
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy) — Swap carrier implementations at runtime

## Related Pages

- [Ship-Rate-Track-Proxy Service](../modules/shipping/ship-rate-track-proxy.md) — Implementation details
- [Carrier System Overview](../modules/shipping/carrier-system-overview.md) — Main system carrier architecture
