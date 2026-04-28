---
title: Shopify Multi-Carrier App Shell
category: architecture
sources: [shopify-multicarrier-app]
status: complete
last_updated: 2026-04-28
git_reference: 8ca5f05476a5f44b05cf7d8ab79cf09d58d91743
---

# Shopify Multi-Carrier App Shell

## Overview

The `shopify-multicarrier-app` is a **Shopify-specific OAuth wrapper and installation shell** that acts as a bridge between Shopify stores and the main StorePep multi-carrier platform (`storepep-react`). It handles Shopify app installation, authentication, billing, and account provisioning, then delegates all shipping/carrier functionality to the core StorePep platform via API.

**Key distinction**: This is NOT the main StorePep application. It's a lightweight shell specifically for Shopify App Store distribution that:
1. Manages Shopify OAuth flow and store authentication
2. Provisions accounts on the main StorePep platform
3. Handles Shopify subscription billing
4. Syncs store metadata and locations
5. Acts as a proxy between Shopify and StorePep APIs

## Differences from storepep-react

| Aspect | shopify-multicarrier-app | storepep-react |
|--------|-------------------------|----------------|
| **Purpose** | Shopify installation shell | Main multi-carrier shipping platform |
| **Scope** | OAuth, billing, account setup | Full shipping workflow (orders, labels, carriers, tracking) |
| **UI** | Minimal (login/signup/plans) | Complete React/Redux shipping application |
| **Database** | Local MongoDB (shops, settings only) | Full platform database (orders, shipments, carriers, etc.) |
| **File count** | 113 JS files (84 server, 29 client) | Thousands of files |
| **Deployment** | Shopify App Store | SaaS platform |
| **Authentication** | Shopify OAuth + JWT to StorePep | StorePep native auth |
| **Business logic** | None — proxies to StorePep | All shipping/carrier logic |

**Analogy**: Think of `shopify-multicarrier-app` as an "embassy" in Shopify territory that registers citizens and issues visas to enter the main StorePep platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Shopify Ecosystem                        │
│  ┌──────────────┐         OAuth/Webhooks/Billing           │
│  │ Shopify Store│◄──────────────────────────────────────┐  │
│  └──────────────┘                                        │  │
└────────────────────────────────────────────────────────┼───┘
                                                          │
                 ┌────────────────────────────────────────┼───┐
                 │   shopify-multicarrier-app (Shell)    │   │
                 │  ┌──────────────────────────────────┐ │   │
                 │  │ Express Server                   │ │   │
                 │  │  - OAuth handler                 │ │   │
                 │  │  - Billing manager               │ │   │
                 │  │  - Account provisioner           │ │   │
                 │  │  - Location sync                 │ │   │
                 │  └──────────────────────────────────┘ │   │
                 │  ┌──────────────────────────────────┐ │   │
                 │  │ MongoDB (local)                  │ │   │
                 │  │  - shops (Shopify access tokens) │ │   │
                 │  │  - settings                      │ │   │
                 │  └──────────────────────────────────┘ │   │
                 └────────────────────────┼────────────────┼─┘
                                          │                │
                                  JWT Auth│                │React App
                                          │                │(minimal UI)
                 ┌────────────────────────▼────────────────┼─┐
                 │   StorePep Platform (storepep-react)   │ │
                 │  ┌──────────────────────────────────┐  │ │
                 │  │ Full Shipping Application        │  │ │
                 │  │  - Orders                        │  │ │
                 │  │  - Labels                        │  │ │
                 │  │  - Carriers                      │  │ │
                 │  │  - Tracking                      │  │ │
                 │  │  - Automation rules              │  │ │
                 │  └──────────────────────────────────┘  │ │
                 └────────────────────────────────────────┴─┘
```

## Key Components

### Server Routes

#### `server/routes/shopify.js` (600+ lines)
- **Location**: `server/routes/shopify.js`
- **Purpose**: Core Shopify integration — OAuth flow, app installation/uninstallation, billing
- **Key functions**:
  - `isAuthenticated()` — Validates shop access token and scopes (shopify.js:59)
  - `updateAccountSubscription()` — Syncs billing to StorePep (shopify.js:65)
  - `updateStoreInStorePep()` — Pushes store updates to platform (shopify.js:79)
  - OAuth callback handler (creates access token, registers account)
  - Webhook handlers for app uninstall
  - Billing charge creation and activation

#### `server/routes/storepepConnect.js` (600+ lines)
- **Location**: `server/routes/storepepConnect.js`
- **Purpose**: Account provisioning and sync with StorePep platform
- **Key functions**:
  - `loginToStore()` — JWT-based login to StorePep (storepepConnect.js:40)
  - `fetchLocationsAndAddInStorePep()` — Syncs Shopify locations (storepepConnect.js:68)
  - Account registration flow
  - Email verification
  - Location management

#### `server/routes/rates.js`
- **Location**: `server/routes/rates.js`
- **Purpose**: Proxy for rate calculation requests from Shopify to StorePep

#### `server/routes/plans.js`
- **Location**: `server/routes/plans.js`
- **Purpose**: Fetch available subscription plans from StorePep

#### `server/routes/settings.js`
- **Location**: `server/routes/settings.js`
- **Purpose**: Store-level settings management

#### `server/routes/droplocations/`
- **Location**: `server/routes/droplocations/`
- **Purpose**: Drop-off location management for local pickup

### Authentication & Middleware

#### `server/utils/installationFunctions.js`
- **Location**: `server/utils/installationFunctions.js`
- **Purpose**: Installation flow utilities
- **Key exports**:
  - `generateAccessToken()` — Exchange OAuth code for Shopify access token (installationFunctions.js:60)
  - `fetchShopDetailsFromShopifyAndUpdateDb()` — Pull shop metadata from Shopify API (installationFunctions.js:28)
  - `checkAndCreateWebhooksForAppUninstall()` — Register uninstall webhook (installationFunctions.js:78)

#### `server/utils/authenticateRequestMiddleware.js`
- **Location**: `server/utils/authenticateRequestMiddleware.js`
- **Purpose**: JWT authentication for StorePep API calls

#### `server/middlewares/shopifyPermissionCheck.js`
- **Location**: `server/middlewares/shopifyPermissionCheck.js`
- **Purpose**: Validate Shopify scopes and permissions

### Database Models

#### `server/models/shops.js`
- **Location**: `server/models/shops.js`
- **Purpose**: Shopify store installation records
- **Schema fields**:
  - `shop` — Shopify domain (e.g., `store.myshopify.com`)
  - `accessToken` — Shopify API access token (encrypted)
  - `isActive` — Installation status
  - `storePepExternalAccountId` — UUID linking to StorePep account
  - `storePepStoreUUID` — UUID linking to StorePep store
  - `storePepPlanId` — Active subscription plan
  - `isCarrierServicesApiEnabled` — Carrier Services API enabled flag
  - `scopes` — Granted OAuth scopes
  - `chargeId` — Shopify billing charge ID
  - `trialDaysRemaining` — Free trial countdown
  - `isPaymentRefreshRequired` — Payment re-auth flag

#### `server/models/settings.js`
- **Location**: `server/models/settings.js`
- **Purpose**: Store-specific settings

### Client Components

#### `client/components/login.js`
- **Location**: `client/components/login.js`
- **Purpose**: StorePep account login form

#### `client/components/signup.js`
- **Location**: `client/components/signup.js`
- **Purpose**: New StorePep account registration

#### `client/components/storepepPlans.js`
- **Location**: `client/components/storepepPlans.js`
- **Purpose**: Plan selection UI (fetches plans from StorePep)

#### `client/components/settings/`
- **Location**: `client/components/settings/`
- **Purpose**: Settings management UI

## Data Flow

### Installation Flow
1. **User clicks "Install" on Shopify App Store**
2. Shopify redirects to `/shopify/install` with shop domain
3. App generates OAuth URL with required scopes
4. User authorizes app on Shopify
5. Shopify redirects to `/shopify/callback` with code
6. App exchanges code for access token (installationFunctions.js:60)
7. App fetches shop details from Shopify API (installationFunctions.js:28)
8. App creates local `shops` record with access token
9. App registers webhook for uninstall
10. **App calls StorePep API** to register external account
11. **App calls StorePep API** to add store
12. **App calls StorePep API** to sync locations
13. App redirects user to login/signup or main app

### Authentication Flow
1. User lands on app embedded in Shopify admin
2. App validates shop is in DB and scopes match (shopify.js:59)
3. If valid, app logs user into StorePep via JWT (storepepConnect.js:40)
4. StorePep returns session token
5. React app loads with StorePep token
6. All subsequent API calls use StorePep JWT

### Billing Flow
1. App checks if shop has active charge
2. If not, redirects to plan selection
3. User selects plan, app calls Shopify Billing API
4. Shopify redirects to confirm charge
5. User confirms, Shopify redirects back with charge_id
6. App activates charge on Shopify
7. **App notifies StorePep** of subscription via `/api/shopifysubscription`

## Dependencies

### External Platform
- **StorePep Platform** (`storepepBaseURL`) — All shipping functionality
  - Account registration: `/api/v1/multicarrier/account/register`
  - Account login: `/api/v1/multicarrier/account/login`
  - Store management: `/api/v1/multicarrier/store/add`, `/edit`, `/install`, `/uninstall`
  - Location sync: `/api/v1/multicarrier/locations/add`
  - Rate calculation: `/api/v1/storepep/rates`
  - Plans: `/api/v1/multicarrier/plans`
  - Subscription update: `/api/shopifysubscription`

### Shopify APIs
- **OAuth**: App installation and authorization
- **Admin API**: Shop details, locations, webhooks
- **Billing API**: Recurring charges
- **Carrier Services API** (optional): Live rate calculation at checkout

### Internal Dependencies
- `@phivejs/config` — Configuration management
- `@phivejs/eventing` — Event publishing (app install/uninstall events)
- `@phivejs/eventsourcing-support` — Event sourcing infrastructure
- `@phivejs/feature-switch` — Feature toggles
- `shopify-api-node` — Shopify API client
- `@shopify/polaris` — Shopify UI components

## Configuration

### Environment Variables (sampleEnv)

**Shopify OAuth**:
- `SHOPIFY_API_KEY` — Shopify app API key
- `SHOPIFY_API_SECRET` — Shopify app secret
- `SHOPIFY_APP_NAME` — Display name
- `scopes` — Comma-separated OAuth scopes (read_orders, write_orders, read_shipping, etc.)
- `serverAddress` — Public URL for OAuth callback and webhooks
- `PLATFORM` — Platform type (`SHOPIFY` or `UPSCTP`)

**StorePep Integration**:
- `storepepBaseURL` — Base URL for StorePep platform API
- `storepepClientURL` — StorePep frontend URL
- `appName` — App identifier (e.g., `MCSL`)
- `STORE_TYPE` — Store type code (e.g., `S5`)

**Database**:
- `database` — MongoDB database name
- `DB_HOST` — MongoDB host
- `DB_USERNAME` / `DB_PASSWORD` — MongoDB credentials

**Feature Toggles** (featureToggles.json):
- `app.redirects.enabled` — Redirect feature flag
- `install.uninstall.zendesk.ticket.email.alerts.disabled` — Disable Zendesk alerts for install/uninstall

## Common Patterns

### JWT Token Generation
All StorePep API calls require JWT authentication. The app generates tokens with:
- **Issuer**: `MULTI_CARRIER_ISSUER` (defined in constants)
- **Audience**: `STOREPEP_JWT_AUDIENCE`
- **Secret**: `jwtSecretForMultiCarrierApp`
- **Payload**: `{ storeType: 'S5', platformSessionId, platformUserId }`

Example:
```javascript
const appToken = await generateJWTToken(
  { storeType: 'S5' },
  config.jwtSecretForMultiCarrierApp,
  constants.MULTI_CARRIER_ISSUER,
  constants.STOREPEP_JWT_AUDIENCE
);
const headers = { Authorization: `Bearer ${appToken}` };
```

### StorePep API Call Pattern
```javascript
const shopFromDb = await findOneShopWithLean({ shop });
const appToken = await generateJWTToken(...);
const headers = {
  Authorization: `Bearer ${appToken}`,
  'x-phive-app': appName,
  'x-shop-domain-phive': shop,
};
const response = await axios.post(
  `${storepepBaseURL}${endpoint}`,
  { externalAccountUUID: shopFromDb.storePepExternalAccountId, ...data },
  { headers }
);
```

### Shopify API Call Pattern
```javascript
const shopFromDb = await findOneShopWithLean({ shop });
const headers = { 'X-Shopify-Access-Token': shopFromDb.accessToken };
const response = await axios.get(
  `https://${shop}/admin/api/${config.currentApiVersion}/endpoint`,
  { headers }
);
```

## Known Issues / Tech Debt

### Legacy Fields
The `shops` schema contains many commented-out fields (shops.js:12-28) suggesting incomplete cleanup from previous iterations.

### Hardcoded Configuration
- Trial days hardcoded in schema default: `trialDaysRemaining: { type: Number, default: config.trialDays }`
- Scopes validated as exact string match (not array comparison) in `isAuthenticated()` (shopify.js:62)

### Error Handling
- Many API calls lack comprehensive error handling
- Installation failures may leave orphaned records in either local DB or StorePep platform

### Security
- Access tokens stored in MongoDB (should verify encryption at rest)
- JWT secrets managed via environment variables (ensure secure key rotation)

### Scope Management
- OAuth scopes are hardcoded in environment variable
- Scope updates require full re-authentication flow
- `isPaymentRefreshRequired` flag suggests manual payment refresh pattern

## Related Pages

- Main platform architecture: `storepep-react` (to be documented)
- [Source Registry](../../raw/sources.yaml)

## Notes

**Repository**: git@bitbucket.org:xadapter-cyd/shopify-multicarrier-app.git
**Current commit**: 8ca5f05476a5f44b05cf7d8ab79cf09d58d91743
**Tech stack**: React 16, Redux, Express 4, Mongoose 5, Shopify Polaris 3, Node >= 8.1
**Build**: Webpack 4 with Babel (ES2015/React presets)
