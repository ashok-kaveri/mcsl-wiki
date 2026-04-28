---
title: Carrier OAuth Registration Flow
category: pattern
sources: [carrier-registration]
status: complete
last_updated: 2026-04-28
git_reference: aa78e90db3b0d01ce297d68a370fc67524440a9f
---

# Carrier OAuth Registration Flow

## Overview

This document describes the **OAuth 2.0 authorization code flow** used by carrier-registration service to onboard merchants with carriers that require OAuth authentication. This pattern is used for:

- **UPS Ready OAuth** (`ups-ready-oauth`)
- **UPS DAP OAuth** (`ups-dap-oauth`)
- **USPS REST** (`usps-rest`)
- **Amazon Shipping** (`amazon-shipping`)
- **PostNord** (`postnord`)

**Source**: Documented in `raw/carrier-registration/docs/ups_oauth.puml`

**Key characteristics**:
- **OAuth 2.0 Authorization Code Grant** — Industry-standard three-legged OAuth flow
- **State token verification** — CSRF protection via state parameter
- **Polling-based status** — Client polls for registration completion (5-second intervals)
- **Multi-step confirmation** — Registration → Login → Account Confirmation → Access Key
- **Token storage** — Access tokens and refresh tokens stored encrypted in PostgreSQL

## Flow Diagram (PlantUML Source)

The following flow applies to UPS Ready OAuth, UPS DAP OAuth, USPS, and other OAuth-based carriers:

```
Actors:
├─ PluginHive Customer (merchant)
├─ App Client (Shopify/WooCommerce/Magento frontend)
├─ App Server (StorePep platform backend)
├─ Carrier Registration API (carrier-registration microservice)
├─ Auth Provider (internal token service)
├─ Jakash (state token reference service)
├─ Carrier API (UPS/USPS OAuth endpoints)
└─ Carrier Login (UPS/USPS login portal)

Flow:
┌───────────────────────────────────────────────────────────────┐
│ 1. INITIATION                                                 │
└───────────────────────────────────────────────────────────────┘
Customer: Add UPS Account
    ↓
App Client: Initiate Registration
    ↓
App Server: Generate and link license key
    ↓
Carrier Registration API: Insert license record
    ↓
App Server: Make pre-registration call
    ↓
Carrier Registration API: Insert registration records for license
    ↓
App Server: Insert carrier details
    ↓

┌───────────────────────────────────────────────────────────────┐
│ 2. POLLING LOOP (every 5 seconds)                            │
└───────────────────────────────────────────────────────────────┘
App Client: Poll registration status
    ↓
App Server: Call bookmark endpoint
    ↓
Carrier Registration API: Provide resource representation
    ↓
Decision: Registration status?
    ├─ Not registered → Return login URL
    ├─ Registered but not confirmed → Return confirmation URL
    └─ Confirmed → Return access key URL

┌───────────────────────────────────────────────────────────────┐
│ 3. LOGIN FLOW (Not Registered)                               │
└───────────────────────────────────────────────────────────────┘
Carrier Registration API: Call auth provider for state token
    ↓
Auth Provider: Return state token (CSRF protection)
    ↓
Carrier Registration API: Get reference for state token
    ↓
Jakash: Return reference for state token (persisted state)
    ↓
Carrier Registration API: Return carrier login URL
    ↓
App Server: Provide login URL to client
    ↓
App Client: Redirect user to carrier login page
    ↓
Carrier Login: Customer logs in with carrier credentials
    ↓
Carrier Login: Callback to registration API with state & auth code
    ↓
Carrier Registration API: Verify state token
    ↓
Decision: Valid state?
    ├─ Invalid → Show failure message
    └─ Valid →
        Carrier Registration API: Exchange auth code for tokens
            ↓
        Carrier API: Return access token + refresh token
            ↓
        Carrier Registration API: Call get user info API
            ↓
        Carrier API: Return user account information
            ↓
        Carrier Registration API: Update registration with tokens
            ↓
        Show registration success message

┌───────────────────────────────────────────────────────────────┐
│ 4. ACCOUNT CONFIRMATION (Registered but Not Confirmed)       │
└───────────────────────────────────────────────────────────────┘
App Server: Provide user account information to client
    ↓
App Client: Show account information to user
    ↓
Customer: Select relevant account details
    ↓
App Client: Submit account details
    ↓
App Server: Send account details to registration API
    ↓
Carrier Registration API: Update registration with account details
    ↓

┌───────────────────────────────────────────────────────────────┐
│ 5. ACCESS KEY GENERATION (Confirmed)                         │
└───────────────────────────────────────────────────────────────┘
App Server: Fetch client credentials
    ↓
Auth Provider: Generate and return client credentials
    ↓
App Server: Update carrier with credentials
    ↓
App Client: Stop polling (registration complete)
```

## UPS Ready OAuth Implementation

### Code Location
- **Provider**: `src/modules/infrastructure/ups-ready-oauth/RegistrationProvider.js`
- **API Client**: `src/modules/infrastructure/ups-ready-oauth/RemoteAPI.js`
- **Workflow**: `src/modules/infrastructure/ups-ready-oauth/WorkflowStepsProviderImpl.js`

### OAuth Endpoints

**UPS Ready OAuth API** (configured in `config.json`):
```javascript
{
  "ups-ready-oauth": {
    "api": {
      "sandbox": {
        "baseUrl": "https://wwwcie.ups.com",
        "clientId": "...",
        "secret": "...",
        "redirectUrl": "..."
      },
      "live": {
        "baseUrl": "https://onlinetools.ups.com",
        "clientId": "...",
        "secret": "...",
        "redirectUrl": "..."
      },
      "endpoints": {
        "generateToken": "/security/v1/oauth/token",
        "refreshToken": "/security/v1/oauth/refresh"
      }
    }
  }
}
```

### Token Generation (Authorization Code Exchange)

**Location**: `RemoteAPI.js:15`

```javascript
async generateToken(data) {
  const url = `${this.baseUrl}/security/v1/oauth/token`;
  const request = qs.stringify({
    grant_type: 'authorization_code',
    code: data.accountDetails.authCode,  // From callback
    redirect_uri: config['ups-ready-oauth'].api[this.environment].redirectUrl,
  });
  const headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'x-merchant-id': data.accountDetails.accountNumber,
  };
  return axios.post(url, request, {
    auth: { username: clientId, password: secret },  // Basic Auth
    headers
  });
}
```

**Request**:
- **Method**: POST
- **URL**: `https://wwwcie.ups.com/security/v1/oauth/token` (sandbox)
- **Auth**: HTTP Basic (client_id:secret)
- **Headers**: `x-merchant-id` (UPS account number)
- **Body** (form-encoded):
  - `grant_type=authorization_code`
  - `code={authCode}` (from OAuth callback)
  - `redirect_uri={registeredRedirectUrl}`

**Response**:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "refresh_token_expires_in": 86400,  // seconds
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Token Refresh

**Location**: `RemoteAPI.js:33`

```javascript
async refreshToken(token) {
  const url = `${this.baseUrl}/security/v1/oauth/refresh`;
  const request = qs.stringify({
    grant_type: 'refresh_token',
    refresh_token: token,
  });
  return axios.post(url, request, {
    auth: this.auth,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
}
```

**Fallback**: If refresh token is unavailable, generate new token with `client_credentials` grant (RemoteAPI.js:46):
```javascript
async generateTokenWithBasicAuth(data) {
  const request = qs.stringify({ grant_type: 'client_credentials' });
  return axios.post(url, request, {
    auth: this.auth,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'x-merchant-id': data.accountNumber
    }
  });
}
```

### Token Processing

**Location**: `RegistrationProvider.js:7`

```javascript
const process = (request, response, type) => ({
  tokenDetails: {
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    refreshTokenExpiresAt: response.refresh_token_expires_in
      && new Date(Date.now() + (response.refresh_token_expires_in * 1000))
  },
  requestResponseData: {
    request,
    response,
    type,  // 'Registration' or 'Token Refresh'
  },
});
```

Tokens are stored in `merchant_credentials` table with:
- `credential_version` — Incremented on each refresh
- `credentials` — Encrypted JSON containing `tokenDetails`

## Registration States

The polling loop returns different URLs based on registration state:

### State 1: Not Registered
**Bookmark response**:
```json
{
  "_links": {
    "login": {
      "href": "https://carrier-login-url?state={stateToken}&client_id={clientId}&redirect_uri={callbackUrl}"
    }
  },
  "status": "not_registered"
}
```

**Client action**: Redirect user to carrier login URL

### State 2: Registered but Not Confirmed
**Bookmark response**:
```json
{
  "_links": {
    "confirm": {
      "href": "/api/carriers/{carrierId}/registration/{registrationId}/account-confirmation"
    }
  },
  "status": "registered",
  "accountDetails": {
    "accountNumber": "...",
    "accountName": "...",
    "email": "..."
  }
}
```

**Client action**: Display account details to user, submit confirmation

### State 3: Confirmed (Complete)
**Bookmark response**:
```json
{
  "_links": {
    "accessKey": {
      "href": "/api/carriers/{carrierId}/registration/credentials"
    }
  },
  "status": "confirmed"
}
```

**Client action**: Fetch credentials, stop polling, show success

## State Token (CSRF Protection)

### State Token Generation Flow

1. **Carrier Registration API** calls **Auth Provider**: "Generate state token for this license + carrier"
2. **Auth Provider** returns opaque state token (JWT or UUID)
3. **Carrier Registration API** calls **Jakash**: "Store reference for state token"
4. **Jakash** persists mapping: `state_token → { licenseKey, carrierId, timestamp }`
5. **Carrier Registration API** includes state token in OAuth authorization URL

### State Token Verification Flow (Callback)

1. Carrier redirects back with `?state={token}&code={authCode}`
2. **Carrier Registration API** extracts state token
3. **Carrier Registration API** calls **Jakash**: "Lookup state token"
4. **Jakash** returns `{ licenseKey, carrierId, timestamp }` or null
5. If null or expired (>15 min) → **Reject** (potential CSRF attack)
6. If valid → **Exchange auth code for tokens**

### Security Properties

- **CSRF prevention**: Attacker cannot forge valid state token
- **Timeout**: State tokens expire after 15 minutes
- **One-time use**: State token consumed after verification
- **Binding**: State token bound to specific license + carrier

## Polling Strategy

**Client behavior**:
```javascript
// Pseudocode
const poll = async () => {
  const interval = 5000;  // 5 seconds
  let status = 'not_registered';

  while (status !== 'confirmed') {
    const response = await fetch(`/bookmark?licenseKey=${key}&carrierId=${id}`);
    const { _links, status: newStatus } = await response.json();

    if (_links.login) {
      window.location.href = _links.login.href;  // Redirect to carrier login
      return;  // Stop polling (user leaves app)
    } else if (_links.confirm) {
      showAccountConfirmation(_links.confirm.href, response.accountDetails);
      return;  // Stop polling (wait for user action)
    } else if (_links.accessKey) {
      await fetchCredentials(_links.accessKey.href);
      return;  // Stop polling (complete)
    }

    await sleep(interval);
  }
};
```

**Server caching**: Bookmark endpoint should cache registration state for 5 seconds to avoid DB hammering.

## Error Handling

### Common OAuth Errors

**Location**: `ups-ready-oauth/errorHandler.js`

| Error | HTTP Status | Cause | Resolution |
|-------|-------------|-------|------------|
| `invalid_grant` | 400 | Auth code expired/invalid | Restart OAuth flow |
| `invalid_client` | 401 | Client credentials wrong | Check config.json |
| `invalid_scope` | 403 | Requested scope not granted | Adjust OAuth scope |
| `server_error` | 502 | Carrier API down | Retry with backoff |
| `invalid_state` | 400 | State token invalid/expired | Restart OAuth flow |

### Error Response Format

```json
{
  "error": "invalid_grant",
  "error_description": "Authorization code has expired",
  "errorCode": "OAUTH_AUTH_CODE_EXPIRED"
}
```

## Database Schema

### `merchant_registration`

Registration record created on initiation:

```sql
{
  id: uuid,
  license_key_hash: sha256(licenseKey),
  carrier_id: uuid,
  account_number: null,  -- Populated after confirmation
  request_data: jsonb,   -- Original registration request
  response_data: jsonb,  -- OAuth callback data
  status: 'pending',     -- 'pending' → 'registered' → 'confirmed'
  created_at: timestamp,
  updated_at: timestamp
}
```

### `merchant_credentials`

Tokens stored after OAuth exchange:

```sql
{
  id: uuid,
  license_key_hash: sha256(licenseKey),
  carrier_id: uuid,
  credential_version: 1,  -- Incremented on refresh
  credentials: encrypted({
    accessToken: "...",
    refreshToken: "...",
    refreshTokenExpiresAt: "2024-01-02T00:00:00Z"
  }),
  created_at: timestamp,
  updated_at: timestamp
}
```

## UPS DAP OAuth Differences

UPS offers two OAuth programs:

| Feature | UPS Ready OAuth | UPS DAP OAuth |
|---------|----------------|---------------|
| **Target Audience** | Small/medium merchants | Large enterprise merchants |
| **Authorization** | User login (3-legged OAuth) | Pre-approved (2-legged OAuth possible) |
| **Account Number** | Required in `x-merchant-id` header | May use service contract number |
| **Scopes** | Standard shipping scopes | Extended enterprise scopes |
| **Base URL** | `onlinetools.ups.com` | `onlinetools.ups.com` (same) |
| **Endpoints** | `/security/v1/oauth/token` | `/security/v1/oauth/token` (same) |

**Implementation**: Both use the same OAuth flow; differences are in configuration (`config.json`) and merchant enrollment process.

## Differences from Legacy Carriers

### Legacy Carriers (FedEx SOAP, UPS legacy)
- **Credentials**: API key + password (static)
- **Storage**: Stored directly in `merchant_credentials`
- **Flow**: Single-step registration (no OAuth)
- **Expiry**: No token expiry (static credentials)

### OAuth Carriers (UPS Ready, USPS, Amazon)
- **Credentials**: OAuth access token + refresh token
- **Storage**: Encrypted in `merchant_credentials` with versioning
- **Flow**: Multi-step (login → callback → confirmation)
- **Expiry**: Tokens expire (1 hour access, 24 hours refresh)
- **Refresh**: Automatic background refresh via `TokenRefreshProvider`

## Event Flow

### Events Emitted

**`CarrierRegisteredForPluginLicense`** (RegistrationProvider.js:30):
```javascript
{
  registrationId: "uuid",
  licenseKey: "...",
  carrierId: "uuid",
  response: {
    tokenDetails: {
      accessToken: "...",
      refreshToken: "...",
      refreshTokenExpiresAt: "..."
    },
    requestResponseData: { ... }
  }
}
```

**Consumed by**:
- **StorePep Platform**: Cache credentials for ship-rate-track-proxy
- **Analytics Service**: Track OAuth adoption
- **Notification Service**: Send confirmation email

## Related Patterns

- [Carrier Registration Service](../architecture/carrier-registration.md) — Overall registration architecture
- [Ship-Rate-Track-Proxy Service](../architecture/ship-rate-track-proxy.md) — Consumes credentials from this flow
- [Security](security.md) — JWT authentication, credential encryption

## References

- **PlantUML Diagram**: `raw/carrier-registration/docs/ups_oauth.puml`
- **UPS Ready OAuth Docs**: https://developer.ups.com/oauth-developer-guide
- **OAuth 2.0 RFC**: https://tools.ietf.org/html/rfc6749 (Authorization Code Grant: Section 4.1)

## Notes

**Applicable Carriers**: UPS Ready OAuth, UPS DAP OAuth, USPS REST, Amazon Shipping, PostNord
**Flow Type**: OAuth 2.0 Authorization Code Grant (3-legged)
**Security**: State token CSRF protection, encrypted credential storage, token refresh automation
**Polling**: 5-second interval bookmark polling until registration complete
**Database**: 35 migrations, 4 tables (merchant_registration, merchant_credentials, merchant_license_map, merchant_token_requests)
