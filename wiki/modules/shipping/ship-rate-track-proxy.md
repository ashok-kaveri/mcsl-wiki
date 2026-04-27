---
title: Ship-Rate-Track-Proxy Service
category: module
domain: shipping
sources: [ship-rate-track-proxy]
status: complete
last_updated: 2026-04-27
git_reference: 0187f5ff1de74aa8b8769b98beef22fc29327b69
---

# Ship-Rate-Track-Proxy Service

## Overview

Unified API Gateway microservice providing a standardized REST interface for 18+ shipping carrier integrations. Implements the Adapter Pattern to abstract heterogeneous carrier APIs (SOAP, REST, XML) into a single, consistent API contract.

**Repository**: `raw/ship-rate-track-proxy` (git submodule)
**Type**: TypeScript + Node.js + Express (Serverless Lambda deployment)
**Size**: 252 TypeScript files, ~5,886 LOC

## Key Capabilities

1. **Unified REST API** — Single interface for all carrier operations (rates, shipment, tracking, etc.)
2. **Protocol Abstraction** — SOAP, REST, XML carrier APIs accessed via consistent JSON endpoints
3. **Dynamic Carrier Loading** — Runtime adapter selection based on URL path
4. **Auth Management** — OAuth 2.0, API keys, certificates handled per carrier
5. **Error Normalization** — Maps carrier-specific errors to standard HTTP codes
6. **Analytics Publishing** — Sends rate/shipment events to SQS for tracking

## Architecture

See [Carrier API Proxy Pattern](../../architecture/carrier-api-proxy-pattern.md) for full architectural pattern.

**Request flow**:
```
Client → POST /carriers/UPS/rates
→ errorHandler → parseCarrier → publishAnalytics
→ UPS Rate Adapter → UPS API → Response
```

## Supported Carriers

**18 carriers across 4 regions**:

### North America
- **FedEx** (legacy SOAP) — All services
- **FedEx REST** (modern API) — All services (migration in progress)
- **UPS** (XML/SOAP) — All services
- **UPS REST** (modern API) — All services
- **USPS** (REST OAuth) — Rates, shipment, tracking
- **TForce** (REST) — Rates, shipment, tracking, pickup

### International
- **PostNord** (Sweden/Nordics)
- **Amazon Shipping** (NA + EU regions)
- **MyPost Business** (Australia Post)

### India
- **E-Shipz**
- **Delhivery**
- **Daakit**

### Other
- **UPS Stepping Stone** (special integration)
- **UPS Ready** (alternate endpoint)
- **UPS DAP** (delivered at place)

**Total**: ~180 provider implementations (18 carriers × ~10 services each)

## API Endpoints

All endpoints follow `/carriers/{carrier}/{category}` pattern.

### Core Operations

| Category | HTTP Method | Endpoint | Purpose |
|----------|-------------|----------|---------|
| **Index** | GET | `/carriers/{carrier}` | List available services |
| **Rates** | POST | `/carriers/{carrier}/rates` | Get shipping rates |
| **Shipment Confirm** | POST | `/carriers/{carrier}/shipment` | Create shipment (generate label) |
| **Shipment Accept** | PUT | `/carriers/{carrier}/shipment/accept` | Finalize shipment |
| **Shipment Cancel** | DELETE | `/carriers/{carrier}/shipment` | Void/cancel shipment |
| **Returns** | POST | `/carriers/{carrier}/shipment/returns` | Generate return label |
| **Pickup Request** | POST | `/carriers/{carrier}/shipment/pickup` | Schedule pickup |
| **Pickup Cancel** | DELETE | `/carriers/{carrier}/shipment/pickup` | Cancel pickup |
| **Tracking** | POST | `/carriers/{carrier}/shipment/tracking` | Get tracking status |

### Additional Services

| Category | Endpoint | Purpose |
|----------|----------|---------|
| **Access Points** | `/carriers/{carrier}/access-points` | Find drop-off locations |
| **Address Validation** | `/carriers/{carrier}/validated-address` | Validate shipping address |
| **Landed Cost** | `/carriers/{carrier}/landed-cost/calculate` | Calculate duties/taxes |
| **Landed Cost Estimate** | `/carriers/{carrier}/landed-cost/estimate` | Estimate duties/taxes |
| **Documents Upload** | `/carriers/{carrier}/shipment/documents` | Upload customs docs |
| **Document Delete** | DELETE `/carriers/{carrier}/shipment/documents/{id}` | Delete document |
| **Packing Slip** | `/carriers/{carrier}/shipment/packing-slip` | Generate packing slip |
| **Manifest** | `/carriers/{carrier}/manifest` | Generate end-of-day manifest |
| **Consolidated Shipment** | `/carriers/{carrier}/consolidated-shipment` | Master/child shipment handling |
| **Digital Assets** | `/carriers/{carrier}/digital-assets` | Upload branding assets |

## Carrier Module Pattern

### Directory Structure

Each carrier follows a consistent module structure:

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
│   ├── LandedCostProviderImpl.ts     # Duties/taxes calculation
│   ├── ETDProviderImpl.ts            # Estimated delivery time
│   └── ModuleLoader.ts               # DI container setup
```

**Example carriers**:
- `modules/fedex/` — Legacy SOAP implementation
- `modules/fedex-rest/` — Modern REST implementation
- `modules/ups/` — UPS XML/SOAP implementation
- `modules/ups-rest/` — UPS REST implementation
- `modules/usps/` — USPS OAuth REST implementation
- `modules/tforce/` — TForce REST implementation

### Provider Interface

All providers implement standard interfaces for their category.

**Example: RateProviderImpl** (`modules/ups/services/rates/RateProviderImpl.ts`):
```typescript
class RateProviderImpl {
  constructor(config, authProvider) {
    this.config = config;  // { url, serviceId, credentials }
    this.authProvider = authProvider;
  }

  async rate(request: UnifiedRateRequest): Promise<UnifiedRateResponse> {
    // 1. Transform unified request → carrier format
    const carrierRequest = this.transformRequest(request);

    // 2. Get auth token/credentials
    const auth = await this.authProvider.getAuth();

    // 3. Call carrier API
    const response = await axios.post(this.config.url, carrierRequest, {
      headers: { Authorization: auth }
    });

    // 4. Transform carrier response → unified format
    return this.transformResponse(response.data);
  }
}
```

### ModuleLoader Pattern

Each carrier has a `ModuleLoader.ts` that registers all providers:

```typescript
// Example: modules/ups/services/ModuleLoader.ts
export class ModuleLoader {
  static load(container, config) {
    container.register('AuthProvider', UPSAuthProvider, config.auth);
    container.register('RateProvider', RateProviderImpl, config.rates);
    container.register('ShipmentProvider', ShipmentProviderImpl, config.shipment);
    container.register('TrackingProvider', TrackingProviderImpl, config.tracking);
    container.register('PickupProvider', PickupProviderImpl, config.pickup);
    container.register('AccessPointProvider', AccessPointProviderImpl, config.accessPoints);
    container.register('AddressValidationProvider', AddressValidationProviderImpl, config.addressValidation);
    container.register('LandedCostProvider', LandedCostProviderImpl, config.landedCost);
  }
}
```

## Common Infrastructure

### Carrier API Client (`modules/common/carrier-api-client`)

**HTTP client abstraction** with built-in retry and error handling:

**Features**:
- Axios-based HTTP client
- Exponential backoff retry (3 attempts)
- 5xx error retry (via `status5xxWrapper`)
- Request/response logging
- Timeout management

**URLTemplateImpl**:
- Templated URL construction
- Variable substitution: `{variable}` placeholders
- Used for dynamic endpoint generation

### Authentication (`modules/common/external-auth`)

**OAuth 2.0 token management**:
- Token caching (in-memory)
- Automatic refresh before expiry
- Shared across requests
- Per-carrier token storage

**Credential resolution order**:
1. Request headers (user-provided)
2. ph-registration service (by serviceId)
3. config.json defaultPluginHiveCredentials (sandbox/test)
4. Error (no credentials)

### Error Handling (`modules/common/error-actions`)

**status5xxWrapper**:
- Wraps HTTP calls
- Retries on 500/502/503/504
- Exponential backoff
- Max 3 retries

**errorHandler** (`modules/api/controllers/errorHandler.ts`):
- Catches all controller exceptions
- Maps to HTTP status codes
- Formats standard error response
- Logs errors with stack traces

### Validation (`modules/common/validatable`)

**Schema validation**:
- JSON schema validation
- Request/response validation
- Throws standard errors on validation failure

### Logging (`modules/common/logger`)

**Winston-based logging**:
- Structured JSON logs
- Log levels: error, warn, info, debug
- Per-request context (correlation ID)

## Configuration System

### config.json Structure

**Massive 122KB JSON** with per-carrier configuration.

**Top-level structure**:
```json
{
  "carriers": {
    "FEDEX": { /* FedEx config */ },
    "FEDEXREST": { /* FedEx REST config */ },
    "UPS": { /* UPS config */ },
    "UPSREST": { /* UPS REST config */ },
    "USPS": { /* USPS config */ },
    "TFORCE": { /* TForce config */ },
    ...
  }
}
```

**Per-carrier structure**:
```json
{
  "FEDEX": {
    "registration": {
      "default": "5758707e-2346-45b0-9553-4240dd35bda3"  // ph-registration service ID
    },
    "analytics": {
      "carrierCode": "C2"  // Maps to main system carrier codes
    },
    "name": "FEDEX",
    "defaultPluginHiveCredentials": {
      // Test credentials for sandbox
      "userId": "phiveUser",
      "password": "PHIVEV0UDstWPY4nu5w=PHIVE",
      "accountNumber": "PHIVEACCOUNT007PHIVE",
      ...
    },
    "index": {
      "serviceId": "e2862b83-7202-43ca-a4d2-48620c0544b5"
    },
    "sandbox": [
      {
        "url": "https://wsbeta.fedex.com/web-services/rate",
        "serviceId": "95ae4ebc-920e-4995-8e35-50463c4e04c2",
        "category": "rates",
        "relName": "rates",
        "name": "SimpleRateProvider"
      },
      // ... 10+ services
    ],
    "live": [
      // Same structure, different URLs
    ]
  }
}
```

**Service configuration fields**:
- `url` — API endpoint URL
- `serviceId` — UUID linking to ph-registration credentials
- `category` — Service category (rates, shipment, tracking, etc.)
- `relName` — RESTful relation name (for HATEOAS links)
- `name` — Provider class name (for dynamic loading)
- `subCategory` — Optional sub-operations (e.g., shipment → confirmed/cancelled)

### RemoteConfig

**AWS SSM Parameter Store integration** (`modules/common/config/RemoteConfig.ts`):
- Loads additional config from SSM on bootstrap
- Caches config in memory
- Environment-specific paths: `/ship-rate-track-proxy/{env}/{key}`

**Config keys** (inferred):
- `ANALYTICS_SQS_QUEUE_URL` — SQS queue for analytics events
- `PH_REGISTRATION_API_URL` — ph-registration service endpoint
- Carrier-specific secrets (OAuth client IDs, API keys)

## Middleware Pipeline

### Controller Composition

All controllers are wrapped with middleware:

```typescript
// Example from modules/api/controllers/index.ts
export const upsRate = errorHandler(parseCarrier(publishAnalytics(rate)));
```

**Pipeline execution order** (right to left):
1. `rate` — Core controller logic
2. `publishAnalytics` — Publish event to SQS
3. `parseCarrier` — Load carrier config, select adapter
4. `errorHandler` — Catch exceptions, format errors

### parseCarrier Middleware

**Dynamic carrier adapter loading**:

```typescript
async function parseCarrier(controller) {
  return async (req, res, next) => {
    // 1. Extract carrier from URL path
    const carrier = req.params.carrier;  // "/carriers/UPS/rates" → "UPS"

    // 2. Load carrier config from config.json
    const config = configJson.carriers[carrier];
    if (!config) throw new Error(`Carrier ${carrier} not supported`);

    // 3. Determine environment (sandbox vs live)
    const env = req.headers['x-environment'] || 'sandbox';
    const services = config[env];  // config.sandbox or config.live

    // 4. Find service matching category
    const category = extractCategory(req.path);  // "rates", "shipment", etc.
    const serviceConfig = services.find(s => s.category === category);

    // 5. Load carrier module
    const module = await import(`src/modules/${carrier.toLowerCase()}/services/ModuleLoader`);

    // 6. Register providers in DI container
    const container = new Container();
    module.ModuleLoader.load(container, config);

    // 7. Resolve provider for this category
    const provider = container.resolve(`${capitalize(category)}Provider`);

    // 8. Attach to request for controller to use
    req.carrier = { config, provider };

    // 9. Continue to next middleware
    next();
  };
}
```

### publishAnalytics Middleware

**SQS event publishing** for rate and shipment operations:

```typescript
function publishAnalytics(controller) {
  return async (req, res, next) => {
    const startTime = Date.now();

    try {
      // Execute controller
      const result = await controller(req, res, next);

      // Publish success event
      await publishToSQS({
        carrier: req.params.carrier,
        category: extractCategory(req.path),
        timestamp: new Date().toISOString(),
        serviceId: req.carrier.config.serviceId,
        request: sanitize(req.body),
        response: sanitize(result),
        duration_ms: Date.now() - startTime,
        status: 'success'
      });

      return result;
    } catch (error) {
      // Publish failure event
      await publishToSQS({
        carrier: req.params.carrier,
        category: extractCategory(req.path),
        timestamp: new Date().toISOString(),
        serviceId: req.carrier.config.serviceId,
        request: sanitize(req.body),
        error: sanitize(error.message),
        duration_ms: Date.now() - startTime,
        status: 'failure'
      });

      throw error;
    }
  };
}
```

**Non-blocking**: Publishes events asynchronously (fire-and-forget).

## Controllers

### Unified Controllers (`modules/api/controllers/`)

Each controller handles a specific operation across all carriers:

**carrierIndex.ts**:
- `index()` — Lists available services for a carrier (HATEOAS links)
- `rate()` — Delegates to carrier's RateProvider

**shipment.ts**:
- `confirm()` — Create shipment (generate label)
- `accept()` — Finalize shipment
- `cancel()` — Void/cancel shipment
- `freightConfirm()` — Freight-specific shipment creation

**shipmentReturns.ts**:
- `confirm()` — Create return label
- `accept()` — Finalize return
- `cancel()` — Cancel return

**shipmentPickup.ts**:
- `request()` — Schedule pickup
- `cancel()` — Cancel pickup

**shipmentTracking.ts**:
- `track()` — Get tracking status

**addressValidation.ts**:
- `validate()` — Validate address

**accessPointProvider.ts**:
- `locations()` — Find drop-off locations

**shipmentLandedCost.ts**:
- `calculate()` — Calculate exact duties/taxes
- `estimate()` — Estimate duties/taxes

**documentManagement.ts**:
- `upload()` — Upload single document
- `uploadMultiple()` — Upload multiple documents
- `pushImage()` — Push image to carrier
- `deleteDocument()` — Delete document

**orderManagement.ts**:
- `label()` — Create label via order management flow
- `pay()` — Process payment

**consolidatedShipment.ts**:
- `closeOutShipment()` — Close out consolidated shipment
- `deleteMasterShipment()` — Delete master shipment
- `deleteChildShipment()` — Delete child shipment

**shipmentPackingSlip.ts**:
- `packingSlip()` — Generate packing slip

**manifest.ts**:
- `generate()` — Generate end-of-day manifest

## Request/Response Flow Example

### Rate Request

**Client request**:
```http
POST /carriers/UPS/rates
Content-Type: application/json

{
  "from": {
    "postalCode": "94111",
    "countryCode": "US"
  },
  "to": {
    "postalCode": "10001",
    "countryCode": "US"
  },
  "packages": [
    {
      "weight": { "value": 5, "unit": "LB" },
      "dimensions": { "length": 10, "width": 8, "height": 6, "unit": "IN" }
    }
  ]
}
```

**Unified response**:
```json
{
  "rates": [
    {
      "service": "UPS Ground",
      "serviceCode": "03",
      "totalCharge": { "amount": 12.50, "currency": "USD" },
      "deliveryDate": "2026-05-01",
      "transitDays": 3
    },
    {
      "service": "UPS 2nd Day Air",
      "serviceCode": "02",
      "totalCharge": { "amount": 25.00, "currency": "USD" },
      "deliveryDate": "2026-04-29",
      "transitDays": 1
    }
  ]
}
```

**Behind the scenes**:
1. `parseCarrier` loads UPS config, instantiates UPS RateProvider
2. Controller calls `provider.rate(unifiedRequest)`
3. Provider transforms to UPS XML format
4. Provider calls UPS API
5. Provider transforms UPS XML response to unified format
6. `publishAnalytics` sends event to SQS
7. Response returned to client

## Test Coverage

**Minimal test coverage**:
- **8 test files** (~395 LOC test code)
- **~5,886 LOC source code**
- **Coverage ratio**: 395 / 5,886 = **6.7%**

**Tests found**:

| Component | Tests | File |
|-----------|-------|------|
| USPS BaseProvider | Unit | `test/modules/usps/services/USPSBaseProvider.test.js` |
| USPS ShipmentAcceptHeaderBuilder | Unit | `test/modules/usps/services/ShipmentAcceptHeaderBuilder.test.js` |
| USPS DefaultHeaderBuilder | Unit | `test/modules/usps/services/DefaultHeaderBuilder.test.js` |
| URLTemplate | Unit | `test/modules/common/carrier-api-client/URLTemplateImpl.generated.test.ts` |
| status5xxWrapper | Unit | `test/modules/common/error-actions/status5xxWrapper.test.js` |
| errorHandler | Unit | `test/modules/common/http/errorHandler.test.js` |
| Validatable | Unit | `test/modules/common/validatable/Validatable.test.js` |
| Media types | Unit | `test/modules/common/media-types/index.test.js` |

**Major gaps**:
- ❌ **No carrier integration tests** (FedEx, UPS, TForce, etc.)
- ❌ **No end-to-end tests** (rate/shipment/tracking flows)
- ❌ **No controller tests** (shipment, tracking, rates)
- ❌ **No parseCarrier middleware tests**
- ❌ **No publishAnalytics tests**

**Coverage primarily on**:
- ✅ Common infrastructure (URL templates, error handling, validation)
- ✅ USPS-specific helpers (header builders)

## Dependencies

**Upstream** (main system → proxy):
- `storepep-react` — Main StorePep app (consumer of this API)

**Downstream** (proxy → external):
- Carrier APIs — FedEx, UPS, USPS, TForce, etc. (18+ carriers)
- `ph-registration` — Carrier credential management service
- AWS SQS — Analytics event queue

**Internal libraries**:
- `@phivejs/eventing` — Event bus (custom library)
- `express` + `@vendia/serverless-express` — HTTP server
- `axios` — HTTP client
- `winston` — Logging
- `jsonschema` — Schema validation
- `jsonwebtoken` + `jwks-rsa` — JWT auth
- `moment` — Date/time utilities

## Deployment

**Infrastructure as Code**:
- `deploy/` — Ansible playbooks for config promotion

**Deployment steps**:
1. Build: `npm run build` → compiles TS to `dist/`
2. Package: Zip `dist/` + `node_modules/` → Lambda artifact
3. Deploy: `ansible-playbook deploy_config.yml`

**Environments**:
- QA: `phive-workload-qa01`
- Prod: `phive-workload-prod02`

**Lambda configuration**:
- Runtime: Node.js 16.20.2 (Volta-managed)
- Handler: `dist/bin/www.js`
- Timeout: (not specified, likely 60s)
- Memory: (not specified)

## Known Issues / Tech Debt

1. **Extremely low test coverage** (6.7%) — No integration tests for carrier modules
   - Risk: Carrier API changes undetected until production failures
   - Mitigation: External integration test suite (if exists)

2. **Massive config file** (122KB JSON) — Hard to maintain, prone to errors
   - Risk: Typos, missing services, incorrect URLs
   - Mitigation: Config validation on startup (if exists)

3. **No config schema validation** — config.json structure not enforced
   - Risk: Invalid config causes runtime failures
   - Mitigation: Add JSON schema validation

4. **No versioning** — Same endpoints for all carrier API versions
   - Risk: Breaking changes when migrating carriers (e.g., FedEx SOAP → REST)
   - Mitigation: Run multiple versions side-by-side during migration

5. **Single point of failure** — Proxy down = all carriers down
   - Risk: Complete shipping outage if proxy fails
   - Mitigation: Lambda auto-scaling, multi-AZ deployment, circuit breaker fallback to direct carrier calls

6. **No rate limiting** — Can overwhelm carrier APIs
   - Risk: Rate limit bans from carriers
   - Mitigation: Add per-carrier rate limiting (token bucket)

7. **No caching** — Every rate request hits carrier API
   - Risk: Slow response times, high API costs
   - Mitigation: Add Redis cache for rate responses (short TTL)

8. **No request idempotency** — Duplicate shipment requests create duplicate labels
   - Risk: Financial loss (double charges), customer confusion
   - Mitigation: Add idempotency keys, duplicate detection

## Related Pages

- [Carrier API Proxy Pattern](../../architecture/carrier-api-proxy-pattern.md) — Architectural pattern
- [Carrier System Overview](carrier-system-overview.md) — Main system carrier architecture
- [Carrier Integrations](carrier-integrations.md) — List of all carrier configurations
