---
title: Carrier Registration Service
category: architecture
sources: [carrier-registration]
status: complete
last_updated: 2026-04-28
git_reference: aa78e90db3b0d01ce297d68a370fc67524440a9f
---

# Carrier Registration Service

## Overview

The **carrier-registration** service (`carrier-hive-api`) is a specialized microservice that manages the **onboarding and authentication lifecycle** for shipping carriers across StorePep's multi-platform ecosystem. While `ship-rate-track-proxy` handles shipping operations (rates, labels, tracking), this service handles the **registration, OAuth, and credential management** that must happen before any carrier can be used.

**Purpose**: Enable customers to connect their carrier accounts to StorePep by managing:
1. Carrier account registration workflows (multi-step, carrier-specific)
2. OAuth 2.0 token lifecycle (obtain, refresh, store)
3. Carrier credential storage and retrieval (encrypted per license)
4. License-to-carrier mappings
5. Platform-specific credential isolation (Shopify, WooCommerce, Magento, etc.)

**Source**: GitLab `pghive/services/carrier-registration-api`

## Comparison with ship-rate-track-proxy

| Aspect | carrier-registration | ship-rate-track-proxy |
|--------|---------------------|----------------------|
| **Purpose** | Carrier onboarding & credential management | Shipping operations (rates, labels, tracking) |
| **Lifecycle Phase** | Setup (one-time or periodic) | Runtime (per shipment) |
| **Primary Operations** | Register, verify, renew, refresh tokens | Get rates, create shipment, track, pickup |
| **Authentication** | Creates and manages credentials/tokens | Consumes credentials/tokens |
| **Frequency** | Infrequent (onboarding, renewals, token refresh) | High-frequency (every shipment) |
| **Database** | PostgreSQL (35+ migrations, 4 tables) | None (stateless proxy) |
| **State** | Stateful (stores registrations, credentials, licenses) | Stateless (API gateway) |
| **Deployment** | Lambda + API Gateway | Lambda + API Gateway |
| **Files** | 268 JS files (~11,958 LOC) | 252 TS files (~5,886 LOC) |
| **Carriers** | 15+ (focus on OAuth carriers) | 18+ (all operational carriers) |
| **API Pattern** | RESTful resource CRUD | Unified adapter pattern |
| **Events** | Emits: `CarrierRegisteredForPluginLicense` | Emits: Analytics events to SQS |
| **Dependencies** | PostgreSQL, @phivejs/eventing, JWT | None (external carrier APIs only) |
| **Test Coverage** | 17 tests (minimal) | 8 tests (6.7%) |

**Relationship**: carrier-registration is an **upstream dependency** of ship-rate-track-proxy. A merchant must complete registration here before ship-rate-track-proxy can make operational API calls on their behalf.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    StorePep Platform                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ User initiates carrier setup (Shopify, WooCommerce)    │  │
│  └─────────────────────┬──────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │
       ┌─────────────────▼──────────────────┐
       │  carrier-registration API          │
       │  ┌──────────────────────────────┐  │
       │  │ Express + Lambda              │  │
       │  │  - Routes (10+ endpoints)    │  │
       │  │  - Controllers (22 files)    │  │
       │  │  - Services (33 files)       │  │
       │  │  - Workflows (multi-step)    │  │
       │  └──────────────────────────────┘  │
       │  ┌──────────────────────────────┐  │
       │  │ Infrastructure (15 carriers) │  │
       │  │  - fedex-rest                │  │
       │  │  - ups-ready-oauth           │  │
       │  │  - ups-dap-oauth             │  │
       │  │  - amazon-shipping           │  │
       │  │  - postnord                  │  │
       │  │  - usps-rest                 │  │
       │  │  - ... (9 more)              │  │
       │  └──────────────────────────────┘  │
       │  ┌──────────────────────────────┐  │
       │  │ PostgreSQL Database          │  │
       │  │  - merchant_registration     │  │
       │  │  - merchant_credentials      │  │
       │  │  - merchant_license_map      │  │
       │  │  - merchant_token_requests   │  │
       │  └──────────────────────────────┘  │
       └─────────────┬──────────────────────┘
                     │
           ┌─────────┴─────────┐
           │                   │
    ┌──────▼────────┐   ┌──────▼──────────┐
    │ Carrier APIs  │   │ Event Bus       │
    │ (OAuth, SOAP) │   │ (@phivejs)      │
    └───────────────┘   └─────────────────┘
                               │
                        ┌──────▼──────────────┐
                        │ StorePep Listeners  │
                        │ (cache credentials) │
                        └─────────────────────┘
```

## Key Components

### Routes (`src/modules/shipping-carrier/routes/index.js`)

All routes scoped to `/:carrierId`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/registration` | GET | Get registration status and workflow steps |
| `/registration` | POST | Register merchant account with carrier |
| `/registration` | DELETE | Delete registration |
| `/pre-registration` | POST | Pre-registration check (availability, validation) |
| `/registration/license` | POST | Link license to carrier (license activation) |
| `/registration/license` | PUT | Renew license |
| `/registration/license` | DELETE | Deactivate license |
| `/registration/secondary/license` | POST | Link secondary license |
| `/registration/agreement/document` | GET | Fetch carrier agreement contract |
| `/registration/credentials` | GET | Fetch carrier credentials |
| `/registration/credentials` | PUT | Update elevated credentials |
| `/registration/approval` | POST | Link registration approval |
| `/registration/approval` | GET | Confirm registration |
| `/registration/account` | GET | Find account details |
| `/registration/:registrationId/verification` | POST | Verify registration (multi-step workflows) |
| `/registration/:registrationId/account-confirmation` | POST | Confirm account details |

### Controllers (`src/modules/shipping-carrier/controllers/`)

22 controller files handling request/response logic:

- **`registration.js`** — Core registration endpoint (registration.js:18)
  - `create()` — Initiate registration (registration.js:18)
  - `find()` — Get registration status (registration.js:67)
- **`registrationResource.js`** — HAL resource generation
- **`registrationWorkflowStepResource.js`** — Workflow step resources
- **`verification.js`** — Multi-step verification
- **`accountConfirmation.js`** — Account confirmation
- **`license.js`** — License management
- **`carrierCredentials.js`** — Credential retrieval
- **`credentialResource.js`** — Credential resource formatting
- **`agreementContract.js`** — Agreement document generation

### Services (`src/modules/shipping-carrier/services/`)

33 service files implementing business logic:

**Core Services**:
- **`RegistrationProvider.js`** — Registration orchestration (RegistrationProvider.js:15)
  - `register(request)` — Delegate to carrier, store result, emit event (RegistrationProvider.js:21)
  - `deactivate(registration)` — Deactivate registration (RegistrationProvider.js:40)
- **`LicenseRegistrationProvider.js`** — License-to-carrier mapping
  - `fetchHash(licenseKey)` — Hash license key for storage
  - `fetchRegistrationDataUsing(licenseKey, carrierId)` — Retrieve registration
- **`AuthProvider.js`** — OAuth token management
  - `fetchAccessToken(licenseKeyHash, carrierId)` — Get access token for API calls
- **`CredentialProvider.js`** — Credential storage/retrieval
  - `getCredentials(licenseId, licenseKeyHash, auth)` — Fetch encrypted credentials
- **`ElevatedCredentialProvider.js`** — Elevated credential updates
- **`TokenRefreshProvider.js`** — OAuth token refresh
- **`TemporaryCredentialProvider.js`** — Temporary credential management
- **`WorkflowStepsProvider.js`** — Multi-step workflow orchestration

**Request Normalizers**:
- **`AccountRegistrationRequestProvider.js`** — Normalize registration requests
- **`AccountRegistrationRequestNormalizer.js`** — Request validation and normalization

**Audit & History**:
- **`LicenseAuditTrailProvider.js`** — Audit trail for license changes
- **`LicenseAuditTrailRepository.js`** — Audit trail persistence

**Repositories**:
- **`RegistrationRepository.js`** — Registration CRUD
- **`LicenseRegistrationRepository.js`** — License mapping CRUD
- **`TemporaryCredentialRepository.js`** — Temporary credential storage
- **`ReferenceTokenRepository.js`** — Token reference storage
- **`TokenRequestsRepository.js`** — Token refresh request tracking

**Error Classes**:
- `InvalidRegistrationError`, `InvalidRequestError`, `LicenseExpiredError`, `LicenseNotFoundError`, `CredentialsNotFoundError`, `RegistrationFailedError`, `MaxAttemptsExceededError`, `TokenRefreshFailedError`, `UnsupportedPlatformError`

### Infrastructure Modules (`src/modules/infrastructure/`)

15 carrier-specific implementation modules:

**OAuth Carriers** (REST with OAuth 2.0):
- **`fedex-rest/`** — FedEx REST API with OAuth
  - 3 registration workflows: Invoice-based, PIN-based, Support-based
  - Regional OAuth credentials (US, APAC, MEISA, LAC, CA, AMEA)
  - Platform-specific credentials (PH-MCSL-QA, FEDEX_PLUGIN, etc.)
  - Files: `Carrier.js`, `WorkflowStepsProviderImpl.js`, `InvoiceValidationApi.js`, `PinGenerationApi.js`, `AddressValidationApi.js`
- **`ups-ready-oauth/`** — UPS Ready OAuth integration
- **`ups-dap-oauth/`** — UPS DAP OAuth integration
- **`amazon-shipping/`** — Amazon Shipping OAuth
- **`postnord/`** — PostNord OAuth

**Legacy Carriers**:
- **`fedex/`** — FedEx SOAP (legacy)
- **`ups/`** — UPS legacy API
- **`usps-rest/`** — USPS REST API

**Regional Carriers**:
- **`delhivery/`** — Delhivery (India)
- **`e-shipz/`** — e-Shipz
- **`mypost-business/`** — MyPost Business (Australia)
- **`tforce/`** — TForce
- **`daakit/`** — DAAkit

**Common Modules**:
- **`auth/`** — OAuth helper utilities
- **`license/`** — License validation
- **`registration-request/`** — Request builders

### Composite Services (`src/modules/shipping-carrier/composite-services/`)

- **`WorkflowProvider.js`** — Orchestrates multi-step registration workflows (WorkflowProvider.js:12)
  - `steps(licenseKey, carrierId, preferNew)` — Build workflow based on registration state (WorkflowProvider.js:13)
- **`Workflow.js`** — Workflow state machine
  - `newRegistrationStep()` — Create registration step
  - `newVerificationStep()` — Create verification step

### Database (`src/db/migrations/`)

35 migrations creating 4 primary tables:

**`merchant_registration`** (V0.0.1):
- Columns: `id`, `license_key_hash`, `carrier_id`, `account_number`, `request_data`, `response_data`, `status`, `created_at`, `updated_at`
- Purpose: Store registration requests and carrier responses

**`merchant_credentials`** (V0.0.13):
- Columns: `id`, `license_key_hash`, `carrier_id`, `credential_version`, `credentials` (encrypted), `created_at`, `updated_at`
- Purpose: Encrypted storage of carrier API credentials

**`merchant_license_carrier_registration_map`** (V0.0.2):
- Columns: `id`, `license_key_hash`, `carrier_id`, `registration_id`, `active`, `created_at`, `updated_at`
- Purpose: Map licenses to carrier registrations

**`merchant_token_requests`** (V0.0.18):
- Columns: `id`, `license_key_hash`, `carrier_id`, `token_request_data`, `token_response_data`, `status`, `created_at`, `updated_at`
- Purpose: Track OAuth token refresh requests

## Data Flow

### Registration Flow (FedEx REST Example)

```
1. User initiates registration
   ↓
2. POST /carriers/{carrierId}/registration
   - Headers: Authorization (Bearer JWT), x-phive-api-key
   - Body: { licenseKey, accountDetails, auth }
   ↓
3. Controller: registration.js:create()
   - Validate carrierId
   - Fetch license hash
   - Retrieve/create credentials
   ↓
4. Service: RegistrationProvider.register()
   - Validate request
   - Create registration record (pending)
   - Delegate to infrastructure module
   ↓
5. Infrastructure: fedex-rest/Carrier.js
   - Determine workflow type (Invoice/PIN/Support)
   - Call FedEx OAuth endpoint
   - Parse response
   ↓
6. Response handling
   - Update registration record (success/failure)
   - Store credentials in merchant_credentials
   - Update license mapping
   - Emit event: CarrierRegisteredForPluginLicense
   ↓
7. Return to client
   - V0 API: Redirect to auth URL with access token
   - V1 API: Return bookmark resource for next step
```

### Multi-Step Workflow (FedEx Invoice-Based)

```
Step 1: Address Validation
- User provides address
- API validates address with FedEx
- Returns registration ID

Step 2: Invoice Validation
- User provides invoice number
- API validates invoice with FedEx
- Stores validation result

Step 3: Account Confirmation
- FedEx confirms account creation
- API stores OAuth tokens
- Returns access token

Step 4: Verification
- User completes verification
- API marks registration as complete
- Emits CarrierRegisteredForPluginLicense event
```

### OAuth Token Refresh Flow

```
1. Token expires (background job or on-demand)
   ↓
2. TokenRefreshProvider.refresh()
   - Retrieve refresh token from merchant_credentials
   - Call carrier OAuth token endpoint
   ↓
3. Carrier returns new access token + refresh token
   ↓
4. Update merchant_credentials
   - Increment credential_version
   - Store new tokens (encrypted)
   ↓
5. Update merchant_token_requests (audit trail)
   ↓
6. Emit event (optional) for cache invalidation
```

## Configuration

### `config.json` (64KB)

Per-carrier configuration with platform and region segregation:

```json
{
  "fedexRest": {
    "id": "2ff7c77a-e741-4074-a496-29b91dc91b63",
    "analyticsCarrierCode": "C2",
    "tracking": {
      "id": "fb68cb48-5546-4e1c-9270-e1cdefd82859",
      "credentials": {
        "sandbox": {
          "platforms": {
            "PH-MCSL-QA": {
              "US": { "client_id": "...", "client_secret": "..." },
              "APAC": { "client_id": "...", "client_secret": "..." },
              "MEISA": { "client_id": "...", "client_secret": "..." },
              "LAC": { "client_id": "...", "client_secret": "..." },
              "CA": { "client_id": "...", "client_secret": "..." },
              "AMEA": { "client_id": "...", "client_secret": "..." }
            },
            "Fedex-App": { ... },
            "FEDEX_PLUGIN": { ... }
          }
        },
        "live": { ... }
      }
    }
  }
}
```

**Platform codes**:
- `PH-MCSL-QA` — StorePep Shopify QA
- `PH-BIGCOMMERCE-SHIPPING-SERVICE` — BigCommerce integration
- `PH-MAGENTO-SHIPPING-SERVICE` — Magento integration
- `Fedex-App` — Direct FedEx app integration
- `FEDEX_PLUGIN` — Plugin-based integration

**Regions**:
- US, APAC (Asia-Pacific), MEISA (Middle East/India/South Asia), LAC (Latin America/Caribbean), CA (Canada), AMEA (Africa/Middle East/Asia)

## API Design Patterns

### Content Negotiation

Supports multiple API versions via Accept header:
- `application/vnd.phive.external.carrier.v0+json` — V0 (legacy, redirect-based)
- `application/vnd.phive.external.carrier.v1+json` — V1 (RESTful, HAL resources)
- `application/json` — Default (V0 behavior)

### HAL Resources

V1 API returns HAL (Hypertext Application Language) resources with `_links`:

```json
{
  "_links": {
    "self": { "href": "/api/carriers/{carrierId}/registration" },
    "next": { "href": "/api/carriers/{carrierId}/registration/{registrationId}/verification" }
  },
  "registration": {
    "id": "...",
    "status": "pending_verification",
    "nextStep": "verification"
  }
}
```

### Error Handling

Custom error middleware (`src/modules/http/errorHandler.js`) maps exceptions to HTTP status codes:
- `InvalidRequestError` → 400 Bad Request
- `LicenseExpiredError` → 403 Forbidden
- `LicenseNotFoundError` → 404 Not Found
- `MaxAttemptsExceededError` → 429 Too Many Requests
- `RegistrationFailedError` → 502 Bad Gateway (carrier API error)

## Authentication & Security

### JWT Authentication (`src/modules/http/authMiddleware.js`)

All requests require:
- **Authorization header**: `Bearer <JWT>` with account UUID claim
- **x-phive-api-key header**: API key for rate limiting and identification

JWT validation:
- Issuer: StorePep platform
- Audience: carrier-registration service
- Claims: `{ custom: { accountUUID: "..." } }`

### Credential Encryption

Carrier credentials stored encrypted in PostgreSQL:
- Encryption algorithm: (not visible in code, likely AES-256)
- Storage: `merchant_credentials.credentials` column
- Versioning: `credential_version` for audit trail

### IP Address Tracking

Middleware `extractClientIpMiddleware.js` captures `req.clientIpAddress` for:
- Audit logging
- Fraud detection
- Regional routing (some carriers require IP-based region detection)

## Events

### Emitted Events

**`CarrierRegisteredForPluginLicense`** (RegistrationProvider.js:30):
```javascript
{
  registrationId: "uuid",
  licenseKey: "...",
  carrierId: "uuid",
  response: { /* carrier API response */ }
}
```

Consumed by:
- StorePep platform (cache credentials for ship-rate-track-proxy)
- Analytics service (track carrier adoption)
- Notification service (email confirmation)

## Deployment

### Infrastructure
- **Runtime**: AWS Lambda + API Gateway
- **Database**: PostgreSQL (RDS or Aurora)
- **Framework**: Express.js wrapped with `@vendia/serverless-express`
- **Entry points**:
  - `bin/www` — Local development server (port 3000)
  - `bin/wwwLambda` — Lambda handler

### Configuration Management
- **Ansible**: Deployment automation (`deploy/`)
- **Inventory**: `inventory/qa01`, `inventory/prod`
- **Playbooks**: `deploy_api.yml`, `deploy_config.yml`
- **Vault**: Encrypted secrets via `--ask-vault-pass`

### CI/CD
- **Jenkins**: `Jenkinsfile` defines pipeline
- **Docker**: Multi-stage builds
  - `Dockerfile` — API image
  - `LambdaDockerfile` — Lambda-optimized image
  - `MigrationDockerfile` — Database migrations

### Environment Variables
- `NODE_ENV` — development/production
- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — Token signing secret
- `AWS_REGION` — Lambda region

## Common Patterns

### Service Locator Pattern

`ServiceLocator.js` provides dependency injection:
```javascript
const registration = serviceLocator.find(carrierId, RegistrationProvider);
const license = serviceLocator.find(config.license.id, LicenseRegistrationProvider);
```

Each carrier infrastructure module registers its services:
```javascript
serviceLocator.register(carrierId, new FedExRestCarrier(), RegistrationProvider);
serviceLocator.register(carrierId, new WorkflowStepsProviderImpl(), WorkflowStepsProvider);
```

### Workflow Builder Pattern

Multi-step workflows use builder pattern:
```javascript
const workflow = new Workflow();
workflow.add(newRegistrationStep(...));
workflow.add(newVerificationStep(...));
workflow.finalize(redirectUrl);
return workflow.end(accessToken, licenseKeyHash);
```

### Repository Pattern

All database access abstracted through repositories:
```javascript
const registrationId = await this.repository.create(request);
await this.repository.update(registrationId, response, licenseKey, carrierId);
await this.repository.updateFailure(registrationId, err);
```

## Known Issues / Tech Debt

### Low Test Coverage
17 test files for 268 source files (~6% coverage). No integration tests visible for carrier workflows.

### Massive Config File
64KB `config.json` with repeated OAuth credentials. Needs:
- Split by carrier
- Environment-based overrides
- Secret management (not hardcoded credentials)

### No Idempotency
Registration endpoints lack idempotency keys. Duplicate calls may create duplicate registrations.

### Error Handling Gaps
Many carrier API errors not normalized. Different carriers return different error structures.

### No Rate Limiting
No visible rate limiting for registration attempts. Risk of brute-force attacks or carrier API quota exhaustion.

### Platform Detection
Platform extracted from request headers (`extractPlatformMiddleware.js:7`). Could be spoofed. Should use JWT claims.

### Legacy API (V0)
V0 API uses redirect-based flow, requiring client-side handling. V1 API (HAL resources) preferred but not adopted everywhere.

### Credential Versioning
`credential_version` increments but no cleanup of old versions. Database bloat risk.

## Related Pages

- [Ship-Rate-Track-Proxy Service](ship-rate-track-proxy.md) — Operational API (consumes credentials from this service)
- [Carrier System Overview](../modules/shipping/carrier-system-overview.md)
- [Carrier Configuration](../modules/shipping/carrier-configuration.md)
- [Carriers and Adapters](carriers-and-adapters.md)

## Notes

**Repository**: GitLab `pghive/services/carrier-registration-api`
**Current commit**: aa78e90db3b0d01ce297d68a370fc67524440a9f
**Tech stack**: Node.js (ES6/Babel), Express 4, PostgreSQL, @phivejs/eventing
**API**: RESTful with HAL, content negotiation (V0/V1)
**Database**: 35 migrations, 4 tables
**Files**: 268 JS files (~11,958 LOC)
**Tests**: 17 test files (minimal coverage)
