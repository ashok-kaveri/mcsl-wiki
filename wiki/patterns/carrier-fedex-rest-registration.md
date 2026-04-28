---
title: FedEx REST Registration Flow
category: pattern
sources: [carrier-registration]
status: complete
last_updated: 2026-04-28
git_reference: aa78e90db3b0d01ce297d68a370fc67524440a9f
---

# FedEx REST Registration Flow

## Overview

This document describes the **FedEx REST API registration workflow** used by carrier-registration service to onboard merchants with FedEx accounts. Unlike OAuth-based carriers, FedEx uses a **multi-step validation process** with three alternative paths depending on merchant account type and preferences.

**Source**: Documented in `raw/carrier-registration/docs/fedex/*.puml`

**Key characteristics**:
- **Three validation methods**: PIN-based (SMS/Email), Invoice-based, Support-based
- **Multi-step process**: Address validation → Validation method → Child credential generation
- **Child credentials**: FedEx issues child API keys (`child_Key`, `child_secret`) per merchant
- **No OAuth**: Uses FedEx's proprietary registration API (not OAuth 2.0)
- **Platform-specific parent credentials**: StorePep maintains parent OAuth credentials per platform and region
- **Automatic selection**: System detects best validation method based on account status

## Registration Methods Comparison

| Method | User Experience | Use Case | Flow Steps | Credentials Returned |
|--------|----------------|----------|------------|---------------------|
| **PIN-based** (SMS/Email) | User enters PIN from FedEx | Standard merchant accounts | Address validation → PIN generation → PIN validation | `child_Key` + `child_secret` |
| **Invoice-based** | User enters invoice details | Accounts without MFA enabled | Address validation → Invoice validation | `child_Key` + `child_secret` |
| **Support-based** | Auto-approved (no user action) | Pre-approved enterprise accounts | Address validation only | `child_Key` + `child_secret` (immediate) |

## High-Level Flow Diagram

```
Actors:
├─ PluginHive Customer (merchant)
├─ FedEx Registration Client (FedEx App UI)
├─ PHive FedEx App (StorePep platform)
├─ Carrier Registration API (carrier-registration microservice)
├─ Auth Provider (internal token service)
└─ FedEx API (FedEx REST endpoints)

Flow:
┌───────────────────────────────────────────────────────────────┐
│ 1. INITIATION                                                 │
└───────────────────────────────────────────────────────────────┘
Customer: Register FedEx
    ↓
FedEx App: Lookup registration details
    ↓
PHive FedEx App: Check if license available?
    ├─ Yes → Lookup license from DB
    └─ No → Generate license (app installation + shop combination)
    ↓
PHive FedEx App: Check if already registered?
    ├─ Yes → Send representation with success details → STOP
    └─ No → Continue
    ↓
PHive FedEx App: Create token for carrier registration API
    ↓
Auth Provider: Generate token to access Registration API
    ↓
PHive FedEx App: Redirect to bookmark with license + token
    ↓

┌───────────────────────────────────────────────────────────────┐
│ 2. BOOKMARK POLLING (Resource Representation)                │
└───────────────────────────────────────────────────────────────┘
Carrier Registration API: Provide resource representation for license
    ↓
Decision: Registration status?
    ├─ Not registered and not verified
    │   → Send resource with register link (no OTP link)
    │
    ├─ Registered but not verified
    │   → Send resource with OTP link only
    │
    └─ Registered and verified
        → Redirect to app with accessToken → COMPLETE

┌───────────────────────────────────────────────────────────────┐
│ 3A. REGISTRATION FLOW - PIN-BASED (SMS/Email)                │
└───────────────────────────────────────────────────────────────┘
FedEx Registration Client: Display registration form
    - Fields: Address, Account Number, Validation Type (Email/SMS)
    ↓
Customer: Fill form and submit
    ↓
Carrier Registration API: Receive details
    ↓
FedEx API: Address Validation API
    - Validates address and account number
    - Returns: accountAuthToken (for MFA)
    ↓
Carrier Registration API: Generate PIN
    ↓
FedEx API: PIN Generation API
    - Sends PIN via SMS or Email
    - Returns: status (PIN sent successfully)
    ↓
Carrier Registration API: Return resource with OTP link
    ↓
FedEx Registration Client: Display OTP form
    ↓
Customer: Enter PIN received from FedEx
    ↓
FedEx Registration Client: Submit PIN
    ↓
Carrier Registration API: Receive PIN
    ↓
FedEx API: PIN Validation API
    - Validates PIN
    - Returns: child_Key + child_secret
    ↓
Carrier Registration API: Save credentials in database
    ↓
Carrier Registration API: Generate token to access Auth Provider
    ↓
Auth Provider: Provide client and secret to access Proxy API
    ↓
Carrier Registration API: Send redirect link with token
    ↓
PHive FedEx App: Save credentials in database
    ↓
Carrier Registration API: Publish "carrier registered for shop" event
    ↓
COMPLETE

┌───────────────────────────────────────────────────────────────┐
│ 3B. REGISTRATION FLOW - INVOICE-BASED                        │
└───────────────────────────────────────────────────────────────┘
FedEx Registration Client: Display registration form
    - Fields: Address, Account Number, Invoice Details
    ↓
Customer: Fill form with invoice (date, number, amount, currency)
    ↓
Carrier Registration API: Receive details
    ↓
FedEx API: Address Validation API
    - Validates address and account number
    - Returns: accountAuthToken
    ↓
Carrier Registration API: Skip PIN generation (invoice path)
    ↓
FedEx Registration Client: Display invoice validation form
    ↓
Customer: Submit invoice details
    ↓
Carrier Registration API: Receive invoice
    ↓
FedEx API: Invoice Validation API
    - Validates invoice against account
    - Returns: child_Key + child_secret
    ↓
[Same completion flow as PIN-based from here]

┌───────────────────────────────────────────────────────────────┐
│ 3C. REGISTRATION FLOW - SUPPORT-BASED (Auto-Approved)        │
└───────────────────────────────────────────────────────────────┘
FedEx Registration Client: Display registration form
    - Fields: Address, Account Number
    ↓
Customer: Fill form and submit
    ↓
Carrier Registration API: Receive details
    ↓
FedEx API: Address Validation API
    - Validates address and account number
    - Returns: child_Key + child_secret (immediate)
    - NO accountAuthToken (account pre-approved)
    ↓
Carrier Registration API: No PIN or invoice needed
    ↓
[Completion flow same as PIN-based]
```

## Implementation Details

### Code Location
- **Provider**: `src/modules/infrastructure/fedex-rest/Carrier.js`
- **API Orchestrator**: `src/modules/infrastructure/fedex-rest/FedexApi.js`
- **Address Validation**: `src/modules/infrastructure/fedex-rest/AddressValidationApi.js`
- **PIN Generation**: `src/modules/infrastructure/fedex-rest/PinGenerationApi.js`
- **PIN Validation**: `src/modules/infrastructure/fedex-rest/PinValidationApi.js`
- **Invoice Validation**: `src/modules/infrastructure/fedex-rest/InvoiceValidationApi.js`
- **Workflow Steps**: `src/modules/infrastructure/fedex-rest/WorkflowStepsProviderImpl.js`

### Registration Orchestration

**Location**: `Carrier.js:46`

```javascript
async register(request) {
  const { platform, countryCode, connectionMode: environment = 'live' } = request.accountDetails;
  const carrier = { platform, countryCode };
  const fedexApi = new FedexApi(carrier, environment);

  const { addressValidationResponse, pinGenerationResponse } = await fedexApi.register(request);

  const responses = [addressValidationResponse, pinGenerationResponse];
  return buildRegistrationResponseToSend(request, responses);
}
```

**Location**: `FedexApi.js:38`

```javascript
async register(data) {
  const { accountDetails: { validationType } } = data;

  // Step 1: Address Validation (always required)
  const addressValidationResponse = await this.addressValidationApi.validate(data);

  // Check for Support Validation (auto-approved)
  if (isSupportValidation(addressValidationResponse)) {
    return { addressValidationResponse };  // Done! Credentials already received
  }

  // Check for Support Validation failure
  if (isSupportValidationFailure(addressValidationResponse, validationType)) {
    throw createSupportValidationError(data);
  }

  // For Invoice or Support, stop here (no PIN needed)
  if (['INVOICE', 'SUPPORT'].includes(validationType)) {
    return { addressValidationResponse };
  }

  // Step 2: PIN Generation (for SMS/Email validation)
  const { accountAuthToken } = addressValidationResponse;
  const pinGenerationResponse = await this.pinGenerationApi.generate(data, accountAuthToken);

  return { addressValidationResponse, pinGenerationResponse };
}
```

### Step 1: Address Validation

**Location**: `AddressValidationApi.js:82`

**Request**:
```javascript
{
  address: {
    streetLines: ["123 Main St", "Suite 100"],
    city: "Memphis",
    stateOrProvinceCode: "TN",
    countryCode: "US",
    postalCode: "38103"
  },
  accountNumber: {
    value: "123456789"
  },
  customerName: "John Doe"
}
```

**API Call**:
```javascript
POST https://apis.fedex.com/oauth2/address-validation
Authorization: Bearer {platformOAuthToken}
Content-Type: application/json
x-locale: en_US
```

**Response (PIN-based path)**:
```javascript
{
  output: {
    mfaOptions: [{
      accountAuthToken: "eyJhbGc...",  // Token for next step
      // ... other MFA options
    }]
  }
}
```

**Response (Support-based path - auto-approved)**:
```javascript
{
  output: {
    credentials: {
      child_Key: "l7xxxx...",
      child_secret: "xxxx..."
    }
  }
}
```

**Parsing Logic** (AddressValidationApi.js:5):
```javascript
const validate = (response) => {
  const {
    credentials: { child_Key: key, child_secret: secret } = {},
    mfaOptions = []
  } = response?.output || {};
  const { accountAuthToken } = mfaOptions?.[0] || {};

  // Support Validation: Credentials returned immediately
  if (key && secret) {
    return { key, secret, type: 'Support Validation' };
  }

  // PIN/Invoice Validation: accountAuthToken for next step
  if (mfaOptions.length && accountAuthToken) {
    return { accountAuthToken, type: 'Address Validation' };
  }

  return null;  // Validation failed
};
```

### Step 2A: PIN Generation (SMS/Email)

**Location**: `PinGenerationApi.js:35`

**Request**:
```javascript
{
  locale: "en_US",
  option: "SMS"  // or "EMAIL"
}
```

**API Call**:
```javascript
POST https://apis.fedex.com/oauth2/pin-generation
Authorization: Bearer {platformOAuthToken}
x-account-auth-token: {accountAuthToken}  // From address validation
Content-Type: application/json
```

**Response**:
```javascript
{
  output: {
    status: "PIN sent successfully"
  }
}
```

### Step 2B: Invoice Validation (Alternative)

**Location**: `InvoiceValidationApi.js:41`

**Request**:
```javascript
{
  invoiceDetail: {
    date: "2024-01-15",
    number: "INV-12345",
    amount: "150.00",
    currency: "USD"
  }
}
```

**API Call**:
```javascript
POST https://apis.fedex.com/oauth2/invoice-validation
Authorization: Bearer {platformOAuthToken}
x-account-auth-token: {accountAuthToken}  // From address validation
Content-Type: application/json
```

**Response**:
```javascript
{
  output: {
    child_Key: "l7xxxx...",
    child_secret: "xxxx..."
  }
}
```

### Step 3: PIN Validation

**Location**: `PinValidationApi.js:37`

**Request**:
```javascript
{
  secureCodePin: "123456",  // PIN received by user
  customerName: "John Doe"
}
```

**API Call**:
```javascript
POST https://apis.fedex.com/oauth2/pin-validation
Authorization: Bearer {platformOAuthToken}
x-account-auth-token: {accountAuthToken}  // From address validation
Content-Type: application/json
```

**Response**:
```javascript
{
  output: {
    child_Key: "l7xxxx...",
    child_secret: "xxxx..."
  }
}
```

## Platform Credentials Architecture

### Parent vs Child Credentials

**Parent Credentials** (StorePep-owned):
- Managed by StorePep per platform and region
- Used for address validation, PIN generation, PIN validation APIs
- OAuth 2.0 tokens obtained via FedEx Developer Portal
- Stored in `config.json` under `fedexRest.tracking.credentials`

**Child Credentials** (Merchant-specific):
- Issued by FedEx for each merchant account
- Used by ship-rate-track-proxy for shipping operations
- No expiry (unlike OAuth tokens)
- Stored encrypted in `merchant_credentials` table

### Regional OAuth Credentials

**Location**: `config.json`

```json
{
  "fedexRest": {
    "tracking": {
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

**Regions**:
- **US**: United States
- **APAC**: Asia-Pacific
- **MEISA**: Middle East, Indian Subcontinent, Africa
- **LAC**: Latin America and Caribbean
- **CA**: Canada
- **AMEA**: Africa, Middle East, Asia (alternate grouping)

**Platforms**:
- `PH-MCSL-QA` — StorePep Shopify QA environment
- `PH-BIGCOMMERCE-SHIPPING-SERVICE` — BigCommerce
- `PH-MAGENTO-SHIPPING-SERVICE` — Magento
- `Fedex-App` — Direct FedEx app
- `FEDEX_PLUGIN` — Plugin-based integration

### Platform Credential Lookup

**Location**: `PlatformCredentials.js`

```javascript
platformCredentials.get({ platform, countryCode, environment }, 'platform');
// Returns: { client_id, client_secret } for the platform/region
```

The system determines the correct parent credentials based on:
1. **Platform** (`PH-MCSL-QA`, `Fedex-App`, etc.)
2. **Country Code** (`US`, `CA`, `GB`, etc.) → mapped to region
3. **Environment** (`sandbox` or `live`)

## Workflow States

The workflow uses a state machine with three distinct workflow providers:

### InvoiceBasedRegistrationSteps

**Location**: `InvoiceBasedRegistrationSteps.js`

```javascript
check() {
  return {
    isRegistered: /* address validated with authToken */,
    isVerified: /* invoice validated with credentials */,
    authToken: /* from address validation */,
  };
}
```

### PinBasedRegistrationSteps

**Location**: `PinBasedRegistrationSteps.js`

```javascript
check() {
  return {
    isRegistered: /* address + PIN generated */,
    isVerified: /* PIN validated with credentials */,
    authToken: /* from address validation */,
  };
}
```

### SupportBasedRegistrationSteps

**Location**: `SupportBasedRegistrationSteps.js`

```javascript
check() {
  return {
    isRegistered: false,
    isVerified: /* address validation returned credentials immediately */,
    authToken: '',
  };
}
```

### Workflow Decision Logic

**Location**: `WorkflowStepsProviderImpl.js:15`

```javascript
const checkRegistrationStatusFor = (data) => {
  const registrationOptions = [
    new InvoiceBasedRegistrationSteps(data),
    new PinBasedRegistrationSteps(data),
    new SupportBasedRegistrationSteps(data)
  ];

  // Check each workflow to see which applies
  const results = registrationOptions.map((option) => ({
    ...option.check(),
    validation: option.isApplicable() ? option.name : null
  }));

  // Reduce to single status
  return results.reduce((acc, result) => ({
    isRegistered: acc.isRegistered || result.isRegistered,
    isVerified: acc.isVerified || result.isVerified,
    authToken: result.authToken || acc.authToken,
    validation: acc.validation || result.validation,
  }), {
    isRegistered: false,
    isVerified: false,
    authToken: '',
    validation: null,
  });
};
```

## Bookmark Resource Representation

### State 1: Not Registered

```json
{
  "_links": {
    "self": { "href": "/api/carriers/{carrierId}/registration?licenseKey={key}" },
    "register": {
      "href": "/api/carriers/{carrierId}/registration",
      "method": "POST",
      "fields": {
        "accountDetails": {
          "accountNumber": "",
          "firstName": "",
          "lastName": "",
          "addressLines": [],
          "city": "",
          "stateCode": "",
          "countryCode": "",
          "postalCode": "",
          "validationType": "SMS"  // or "EMAIL", "INVOICE", "SUPPORT"
        }
      }
    }
  },
  "status": "not_registered"
}
```

### State 2: Registered, Not Verified (PIN or Invoice needed)

```json
{
  "_links": {
    "self": { "href": "/api/carriers/{carrierId}/registration?licenseKey={key}" },
    "verify": {
      "href": "/api/carriers/{carrierId}/registration/{registrationId}/verification",
      "method": "POST",
      "fields": {
        "code": ""  // PIN from SMS/Email
      }
    }
  },
  "status": "registered_not_verified",
  "validation": "Pin Validation"  // or "Invoice Validation"
}
```

**For Invoice validation**:
```json
{
  "_links": {
    "verify": {
      "href": "/api/carriers/{carrierId}/registration/{registrationId}/verification",
      "fields": {
        "invoice": {
          "date": "",
          "number": "",
          "amount": "",
          "currency": "USD"
        }
      }
    }
  }
}
```

### State 3: Verified (Complete)

```json
{
  "_links": {
    "self": { "href": "/api/carriers/{carrierId}/registration?licenseKey={key}" },
    "credentials": {
      "href": "/api/carriers/{carrierId}/registration/credentials"
    }
  },
  "status": "verified",
  "redirect": "{appUrl}?token={accessToken}"
}
```

## Error Handling

### Common FedEx Errors

**Location**: `fedex-rest/errorHandler.js`

| Error | HTTP Status | Cause | Resolution |
|-------|-------------|-------|------------|
| `ADDRESS_VALIDATION_FAILED` | 400 | Invalid address or account number | Re-enter valid address |
| `PIN_GENERATION_FAILED` | 502 | FedEx API unavailable | Retry or use invoice method |
| `PIN_VALIDATION_FAILED` | 400 | Incorrect PIN | Re-send PIN or retry |
| `INVOICE_VALIDATION_FAILED` | 400 | Invoice doesn't match account | Verify invoice details |
| `SUPPORT_VALIDATION_FAILURE` | 400 | Account not pre-approved | Use PIN or invoice method |
| `ACCOUNT_NOT_FOUND` | 404 | Account number doesn't exist | Verify account number |

### Error Response Format

```javascript
{
  error: 'FedExAddressValidationFailedError',
  message: 'FedEx [REST] Address Validation Failed',
  details: {
    request: { ... },
    response: {
      errors: [{
        code: 'ADDRESS_VALIDATION_FAILED',
        message: 'Invalid address'
      }]
    }
  }
}
```

## Database Schema

### `merchant_registration`

```sql
{
  id: uuid,
  license_key_hash: sha256(licenseKey),
  carrier_id: uuid,  -- FedEx REST carrier ID
  account_number: "123456789",
  request_data: jsonb,  -- Original registration request
  response_data: jsonb,  -- Interaction data (address validation, PIN generation, etc.)
  status: 'verified',   -- 'pending' → 'registered' → 'verified'
  created_at: timestamp,
  updated_at: timestamp
}
```

**interaction_data** structure:
```json
[
  {
    "request": { ... },
    "response": { ... },
    "type": "Address Validation",
    "source": { "accountDetails": { ... } },
    "platform": "PH-MCSL-QA"
  },
  {
    "request": { ... },
    "response": { "output": { "status": "PIN sent successfully" } },
    "type": "Pin Generation"
  },
  {
    "request": { "secureCodePin": "123456", "customerName": "John Doe" },
    "response": { "output": { "child_Key": "...", "child_secret": "..." } },
    "type": "Pin Validation"
  }
]
```

### `merchant_credentials`

```sql
{
  id: uuid,
  license_key_hash: sha256(licenseKey),
  carrier_id: uuid,
  credential_version: 1,
  credentials: encrypted({
    "username": "l7xxxx...",  -- child_Key
    "password": "xxxx...",    -- child_secret
    "client_id": "...",       -- parent OAuth client_id (for reference)
    "client_secret": "..."    -- parent OAuth client_secret (for reference)
  }),
  created_at: timestamp,
  updated_at: timestamp
}
```

## Event Flow

### Events Emitted

**`CarrierRegisteredForPluginLicense`** (emitted after verification):
```javascript
{
  registrationId: "uuid",
  licenseKey: "...",
  carrierId: "fedex-rest-uuid",
  response: {
    connectionMode: "live",  // or "sandbox"
    requestResponseData: [
      { type: "Address Validation", ... },
      { type: "Pin Generation", ... },
      { type: "Pin Validation", ... }
    ],
    username: "l7xxxx...",  // child_Key
    password: "xxxx...",    // child_secret
    client_id: "...",       // parent credentials (for ship-rate-track-proxy)
    client_secret: "..."
  }
}
```

**Consumed by**:
- **StorePep Platform**: Cache credentials for ship-rate-track-proxy
- **Analytics Service**: Track FedEx adoption and validation method usage
- **Notification Service**: Send confirmation email with account details

## Differences from Other Carriers

### FedEx REST vs UPS OAuth

| Aspect | FedEx REST | UPS OAuth |
|--------|-----------|-----------|
| **Auth Method** | Proprietary registration API | OAuth 2.0 authorization code |
| **User Action** | Enter PIN or invoice | Login to UPS account |
| **Credentials** | Child key + secret (static) | Access token + refresh token (expiring) |
| **Parent Credentials** | StorePep OAuth tokens | StorePep client_id + secret |
| **Validation** | 3 methods (PIN/Invoice/Support) | Single OAuth flow |
| **Token Refresh** | Not needed (static) | Automatic via refresh_token |
| **Multi-factor** | PIN via SMS/Email | OAuth login (may have MFA) |

### FedEx REST vs FedEx SOAP (Legacy)

| Aspect | FedEx REST | FedEx SOAP |
|--------|-----------|------------|
| **API Protocol** | REST + JSON | SOAP + XML |
| **Registration** | REST registration API | Manual credential creation |
| **Credentials** | Child key + secret | Meter number + account + key + password |
| **Platform Support** | Regional parent credentials | Single global credential |
| **Account Validation** | Address + PIN/Invoice | Manual verification |

## Related Patterns

- [Carrier OAuth Registration Flow](carrier-oauth-flow.md) — OAuth-based carrier registration (UPS, USPS, Amazon)
- [Carrier Registration Service](../architecture/carrier-registration.md) — Overall registration architecture
- [Ship-Rate-Track-Proxy Service](../architecture/ship-rate-track-proxy.md) — Consumes child credentials for shipping operations

## References

- **PlantUML Diagrams**: `raw/carrier-registration/docs/fedex/*.puml`
- **FedEx Developer Portal**: https://developer.fedex.com
- **FedEx REST API Docs**: https://developer.fedex.com/api/en-us/catalog.html

## Notes

**Validation Methods**: PIN-based (SMS/Email), Invoice-based, Support-based (auto-approved)
**Flow Type**: Proprietary multi-step registration (not OAuth)
**Credentials**: Child API keys (`child_Key`, `child_secret`) issued per merchant
**Parent Credentials**: StorePep maintains OAuth tokens per platform and region
**Regional Support**: US, APAC, MEISA, LAC, CA, AMEA
**Platform Support**: Shopify, WooCommerce, Magento, BigCommerce, direct FedEx app
**Database**: merchant_registration (status tracking), merchant_credentials (encrypted child keys)
**Events**: CarrierRegisteredForPluginLicense emitted after verification complete
