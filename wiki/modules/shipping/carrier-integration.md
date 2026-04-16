---
title: Carrier Integration
category: module
domain: shipping
status: complete
last_updated: 2026-04-16
git_reference: current
sources: [storepep-react]
---

# Carrier Integration

## Overview

This page is the **engineer's reference** for the carrier integration layer — the code-level patterns, file conventions, and shared infrastructure that sit between the unified adaptor and each carrier's API. Use this page when implementing a new carrier, debugging a carrier-specific bug, or reviewing recent integration work.

**Not in scope here** (covered elsewhere):
- The factory pattern narrative and the list of 43 carriers → [Carrier System Overview](carrier-system-overview.md)
- Credential schema and per-carrier config fields → [Carrier Configuration](carrier-configuration.md)
- End-to-end label creation and document generation → [Label Generation](label-generation.md)
- Customer-facing rollout and cross-feature impact → [Adding a New Carrier — Customer Journey](../../adding-new-carrier-customer-journey.md)

## Directory Layout

All carrier integrations live under:

```
server/src/shared/API/carriers/
├── amazonShipping/
├── apcPostalLogistics/
├── aramex/
├── auPostMyPostBusiness/
├── auPostMyPostBusinessOauth/
├── australiaPost/
├── blueDart/
├── canadaPost/
├── canpar/
├── ...
├── easyPost/          # aggregator (C22)
├── eshipz/            # aggregator (C47)
├── fedex/             # SOAP (C2)
├── fedExRest/         # REST (C39)
├── ups/               # XML (C3)
├── upsRestApi/        # OAuth REST (C38)
├── usps/              # direct USPS (C5)
├── uspsRest/          # REST (C45/C46/C48)
└── ...
```

**Scale**: 47 subdirectories covering direct integrations, dual API variants, and aggregators.

## The Three-File Pattern per Carrier

Every carrier directory follows the same three-file convention:

| File | Responsibility |
|------|---------------|
| `<carrier>ShipmentHelper.js` | The adapter class implementing the unified interface (`getRates`, `createShipment`, `cancelShipment`, …). Orchestrates the API call lifecycle. |
| `<carrier>RequestBuilder.js` | Builds the carrier-specific request object (XML/SOAP envelope or JSON body) from normalized order + package data. |
| `<carrier>Helper.js` | Shared utilities: code lookups, unit converters, date formatters, validators. |

**Why the split**: separating transport (the helper) from payload construction (the builder) from shared logic keeps the helper file narrowly focused on the adapter interface and API call lifecycle. Request builders get large and stable; helpers change more often.

**Example — FedEx** (the heaviest integration):

| File | Size |
|------|------|
| `fedex/fedexShipmentHelper.js` | ~100 KB |
| `fedex/fedexRequestBuilder.js` | ~109 KB |
| `fedex/fedexHelper.js` | ~28 KB |

**Example — Sendle** (one of the simplest):

| File | Size |
|------|------|
| `sendle/sendleShipmentHelper.js` | ~15 KB |
| `sendle/sendleRequestBuilder.js` | (small) |
| `sendle/sendleHelper.js` | 181 lines |

## Dispatch — What to Modify

The dispatch mechanism is the factory in `shared/storepepAdaptors/shipmentAdaptor.js`. For the pattern narrative see [Carrier System Overview](carrier-system-overview.md#adaptor-pattern). To **register a new carrier in dispatch** you touch three files:

| File | Change |
|------|--------|
| `server/src/storePepConstants.js:41-90` | Add a new `<CARRIER>_CARRIER_CODE: 'C<n>'` constant. Codes are sequential; the highest current code is `C54`. |
| `shared/storepepAdaptors/shipmentAdaptor.js` | Add a new `case` in `getShipmentCreatorBasedOnCarrier()` returning `new <Carrier>ShipmentHelper()`. |
| `shared/serviceCodes.js` | Add the carrier's service-code → friendly-name map (e.g. `FEDEX_GROUND → "Fedex Ground"`). |

## HTTP Client & Retry

The only codified HTTP client factory today is FedEx's:

- **Location**: `server/src/shared/API/carriers/fedex/httpClientFactory.js:1-110`
- **Transport**: axios with configurable retries and exponential backoff
- **Retry triggers**: transient HTTP errors plus carrier-specific codes (e.g. FedEx SOAP error `1421`)
- **Configuration**: `config.fedexHttpRetryClientConfig.retries` and `retryIntervalInMilliseconds`

```js
const retries = config.fedexHttpRetryClientConfig.retries || 0;
const retryInterval = config.fedexHttpRetryClientConfig.retryIntervalInMilliseconds || 0;
const retryableCodes = [1421]; // FedEx-specific
```

**Important caveat**: this factory is **not shared** across carriers. Other carriers build their own axios or node-soap clients. See [Known Issues / Tech Debt](#known-issues--tech-debt).

## Authentication Patterns

Four patterns are in use. The credential fields themselves are documented in [Carrier Configuration](carrier-configuration.md) — this page maps patterns to example carriers.

| Pattern | Example Carriers | Notes |
|---------|------------------|-------|
| API Key / Secret | Sendle, Amazon Shipping, Delhivery | Modern REST |
| Username / Password + Account Number | FedEx (C2 SOAP), UPS (C3 XML) | Legacy enterprise APIs |
| OAuth 2.0 | FedEx REST (C39), UPS OAuth (C38), USPS REST (C45/C46/C48), Australia Post MPB OAuth | Token refresh is currently manual — see tech debt |
| Merchant ID + API Key | Stamps.com, EasyPost | Aggregator-style |

## Carrier-Specific Error Code Dictionaries

Each helper declares its own `errorCodes` dictionary mapping numeric carrier codes to centralised StorePep error event types.

**Example — FedEx** (`fedexShipmentHelper.js:57-67`):

```js
const errorCodes = {
  556:  { storepepErrorType: storepepErrorEvents.SERVICE_MISMATCH },
  522:  { storepepErrorType: storepepErrorEvents.INVALID_DESTINATION_ADDRESS },
  6541: { storepepErrorType: storepepErrorEvents.INVALID_SHIPPER_PHONE_NUMBER },
  1000: { storepepErrorType: storepepErrorEvents.AUTHENTICATION_FAILURE },
};
```

**Event catalogue**: `shared/storepepTransactions/storepepErrorEvents.js` — 49 centralised error types (e.g. `SERVICE_MISMATCH`, `INVALID_DESTINATION_ADDRESS`, `NO_RATES_AVAILABLE_FROM_CARRIER`, `AUTHENTICATION_FAILURE`, `COD_NOT_AVAILABLE_FOR_SERVICE`).

**User-facing messages**: `shared/storepepTransactions/storepepErrorEventsMessage.js` maps event types to customer-readable messages.

**Rule when adding a carrier**: reuse an existing event type if the failure mode already exists. Only extend `storepepErrorEvents.js` when the carrier surfaces a genuinely novel failure. Divergent event types fragment the error UX.

## Dual API Variants

Three carriers currently have two (or more) integrations during migration from legacy to modern APIs:

| Carrier | Legacy | Modern |
|---------|--------|--------|
| FedEx | `C2` — SOAP/XML | `C39` — REST (OAuth) |
| UPS | `C3` — XML | `C38` — REST OAuth |
| USPS | `C4` (Stamps.com), `C5` (direct) | `C45`, `C46`, `C48` — REST / OAuth variants |

**Why two codes coexist**:
- Migration period — existing merchants stay on legacy until cut over
- Feature parity gaps — some capabilities only exist on one API
- Merchant preference — e.g. Stamps.com vs direct USPS

**Practical implication**: when editing a FedEx/UPS/USPS feature, verify whether the change affects the legacy helper, the modern helper, or both. The recent FedEx REST negotiated rates work (PR #2902) is an example of modern-only enhancement.

## Aggregators

Two aggregator-style integrations sit alongside direct carriers:

- **EasyPost** (`C22`) — `easyPost/easyPostShipmentHelper.js`. Unified API to 100+ carriers; used when merchants want quick onboarding or coverage for carriers without direct integration. For the integration pattern see [Carrier System Overview](carrier-system-overview.md#2-easypost-aggregation).
- **Eshipz** (`C47`) — multi-carrier gateway, similar role.

**Choice heuristic**: direct integrations give full feature access (freight, hold-at-location, carrier-specific special services) and potentially better rates; aggregators give faster setup and broader coverage. For active examples of the tension see the Royal Mail 3PI decision in [2026-04-15-royal-mail-integration-constraints.md](../../product/decisions/2026-04-15-royal-mail-integration-constraints.md).

## Credential Handling

Credential **schema** is documented in [Carrier Configuration](carrier-configuration.md). Integration-side notes:

- **Encryption**: `shared/storepepFiles/encryptionDecryption.js` — AES-256, applied before persistence
- **Decrypt-on-read**: credentials are decrypted inside `shared/DBCallFunctions/carriersDbCall.js` when `findCarriersWithLean` returns carrier docs
- **Live vs sandbox**: `productionKey: boolean` on the carrier doc discriminates; helpers branch on this to pick the correct API URL / account

## Recent Integration Activity

The pulse of the integration layer over the last 3–6 months (as of April 2026). Shows where active patterns and active failure modes are concentrated:

| Change | Reference |
|--------|-----------|
| Delhivery Proxy (`C54`) — new carrier using Delhivery as upstream rate/track provider | PR #2903 |
| USPS Scan Form & Manifest — end-of-day manifest generation | commit f4fe948df |
| UPS Dangerous Goods Transportation Mode fix | PR #2909 |
| FedEx REST negotiated rates — per-toggle selection between budget-constrained and negotiated rates | PR #2902 |
| FedEx Saturday Delivery eligibility in REST builder | commit 8e4874cc6 |
| PostNord — country of origin at product level | PR #2899 |
| Australia Post MyPost Business OAuth | PRs #2803, #2826 |
| Australia Post chunked manifest (with toggle to disable) | PRs #2824, #2805 |
| EasyPost data sanitization (null-description handling) | PR #2721 |

**Themes**:
- **OAuth migrations** (Australia Post, USPS variants, UPS/FedEx dual APIs)
- **Manifest handling** (USPS scan form, Australia Post chunking)
- **Rate/service toggles** (FedEx negotiated rates, Saturday delivery)
- **Data sanitization at aggregator boundaries** (EasyPost)

## Adding a New Carrier — Engineering Checklist

Server-side only. For the customer-facing / cross-feature work see [Adding a New Carrier — Customer Journey](../../adding-new-carrier-customer-journey.md).

1. **Register the carrier code** in `server/src/storePepConstants.js` (`<CARRIER>_CARRIER_CODE`)
2. **Create the directory** `server/src/shared/API/carriers/<carrierName>/`
3. **Implement `<carrierName>ShipmentHelper.js`** with the required interface methods (at minimum `getRates`, `createShipment`, `validateCarrierCredentials`; add `cancelShipment`, `getTracking`, `createPickup`, `createManifest`, `validateAddress` as the carrier supports them)
4. **Implement `<carrierName>RequestBuilder.js`** to construct the API payload
5. **Implement `<carrierName>Helper.js`** for shared utilities
6. **Wire dispatch** — add a `case` in `shared/storepepAdaptors/shipmentAdaptor.js`
7. **Map service codes** in `shared/serviceCodes.js`
8. **Extend the carrier model** in `server/src/models/carriers.js` if carrier-specific credential/preference fields are needed
9. **Declare an `errorCodes` dictionary** inside the helper; add new event types to `storepepErrorEvents.js` only for novel failures
10. **Choose an auth pattern** (API key, OAuth, account number — see [Authentication Patterns](#authentication-patterns)) and implement token acquisition/refresh accordingly
11. **Decide on direct vs aggregator** — if the carrier is available through EasyPost, evaluate whether a proxy integration (like Delhivery Proxy C54) is enough

## Known Issues / Tech Debt

- **No unified HTTP client** — `httpClientFactory.js` is FedEx-only; other carriers reinvent retry/timeout logic
- **Inconsistent error response shapes** — older helpers return slightly different error objects
- **Partial feature coverage** — not all carriers implement `cancelShipment()`, `getTracking()`, `createManifest()`
- **Manual OAuth token refresh** — carriers using OAuth do not share a token-refresh abstraction
- **No shared retry-policy abstraction** — each helper codes its own retry behaviour (see FedEx 1421 example)
- **Large helper files** — FedEx's `fedexShipmentHelper.js` (~100 KB) and `fedexRequestBuilder.js` (~109 KB) indicate missing decomposition; changes in these files have wide blast radius

## Dependencies

- [Carrier System Overview](carrier-system-overview.md) — adaptor pattern, full carrier list, rate/label flows
- [Carrier Configuration](carrier-configuration.md) — credential schema, per-carrier fields
- [Label Generation](label-generation.md) — end-to-end label creation
- [Adding a New Carrier — Customer Journey](../../adding-new-carrier-customer-journey.md) — customer-facing rollout

## Referenced By

- Carrier-specific product stories and decisions under `wiki/product/stories/` and `wiki/product/decisions/`
- Zendesk ticket summaries in `wiki/zendesk/summaries/` that cite integration-layer issues

## Related Pages

- [Carrier System Overview](carrier-system-overview.md)
- [Carrier Configuration](carrier-configuration.md)
- [Label Generation](label-generation.md)
- [Adding a New Carrier — Customer Journey](../../adding-new-carrier-customer-journey.md)
