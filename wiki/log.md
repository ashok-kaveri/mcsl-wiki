# StorePep KB Activity Log

## [2026-05-20 18:30] zendesk-summarize | 11-ticket delta — ZI-520 → ZI-556
- Trigger: User asked to fetch and summarise a batch of 11 new Zendesk tickets (9 fetched initially + 2 added mid-batch)
- Fetched via `scripts/sync-zendesk-by-ids.sh`:
  - shopify: #389826, #387563, #389467, #389897, #390108, #390510, #391078 (7)
  - other_platforms: #387845, #390097, #387886, #390467, #390467 (4)
- Created summaries: `wiki/zendesk/summaries/{389826,387563,387845,389467,389897,390097,390108,390510,387886,390467,391078}.md`
- Created daily index: `wiki/zendesk/2026-05-20.md` (37 issues; ZI-520 → ZI-556; 0 carry-forwards, 0 duplicates)
- Git reference: f627c31d4cd88d1490dd22bab4feb221abead04d (fetch commit)
- Headline themes:
  - **FedEx REST + no-postal-code countries** — ZI-548 (FedEx app, Morrison/Belgium) + ZI-555 (MCSL, Cybershaft/Japan) + ZI-556 (cross-app coordination). Same bug, two code paths; Morrison already escalated with multiple missed ETAs
  - **AusPost regulatory deadline 2026-08-04** — ZI-537/538/539 (mandatory recipient phone for eParcel + MPB; opt-out tracking)
  - **NZ Post Q4 roadmap** — ZI-540/541/542/543 (SOv2, label enhancements, MyNZPB SMB integration)
  - **Email sender / SMTP gap** — ZI-530, 552, 553, 554 (welcome emails, tracking notifications, end-customer complaint triage)
  - **Large-catalog merchants on small plans** — ZI-525, 533, 534, 535, 536 (78k-product ez90xj-ps + label-cap Anandhaas)
- Next: run `/roadmap regenerate` to refresh the roadmap from these new summaries

## [2026-05-11 17:00] zendesk-summarize-one + story-cards | Ticket #368959 re-pulled and 3 new ZIs added
- Trigger: User flagged that the existing summary for #368959 said "USPS manifest" and "customer: Not specified" — both wrong
- Re-pulled fresh from Zendesk API via `scripts/sync-zendesk-by-ids.sh 368959`
- Rewrote `wiki/zendesk/summaries/368959.md` — customer is Victoria Groetelaars / Greaves Jams (same as ZI-499); carriers are Canada Post + Canpar; 3 distinct open issues, not 1
- Added ZI-512/513/514 to `wiki/zendesk/2026-05-11.md` (manual update since the 368959 JSON change is uncommitted and wouldn't be picked up by formal git-diff delta)
- Created story cards:
  - ZI-512 — Canada Post manifest fulfill+transmit (label-generation, pain 10) — engineering done, blocked on credential testing → https://trello.com/c/H3DH4Z5X
  - ZI-513 — Canada Post discard-label UX for post-2025-07-02 regime (label-generation, pain 9) → https://trello.com/c/HaCxgIOH
  - ZI-514 — Opt-in for silent auto-carrier-fallback (rate-shopping, pain 8) → https://trello.com/c/eHGb6Rh1
- All 3 pushed with Duplicate label since they're same-ticket-different-ZI; APR 25-30 lane, pos:top (SLA breached)
- Same customer (Greaves Jams) now has 6 active ZIs across 2 tickets (#350796: ZI-499/500/501; #368959: ZI-512/513/514) — cumulative frustration signal worth flagging in the backlog

## [2026-05-11 16:30] story-cards | Delta — 17 cards pushed to StoryLab (APR 25-30 lane)
- Cards created: 5 (ZI-496, ZI-497, ZI-499, ZI-506, ZI-510, ZI-511) — single canonical card per ticket
- Cards created with Duplicate label: 11 (ZI-396, ZI-507, ZI-498, ZI-500, ZI-501, ZI-502, ZI-503, ZI-504, ZI-505, ZI-508, ZI-509) — same-ticket-different-ZI or daily-index dup_of references
- Cards superseded (desc replaced + comment): 1 (ZI-479 → points to ZI-508/509)
- All 17 validated via `validate_story_card.py` before push (5 cards required one rewrite cycle for vague-pattern words / short When clauses)
- Default lane APR 25-30 (`69dd9e0e8a7bb8b998765ee7`); all SLA-breached, `pos: top`
- Trello URLs recorded in script output; see board: https://trello.com/b/d1xk25XH/storylab

## [2026-05-11 15:30] zendesk-summarize | Delta — 11 tickets, 16 new ZIs (ZI-496 → ZI-511)
- Delta anchor: `107b291cb62386f4646e7a57ac37234db5d7bdde` (2026-05-08) → HEAD `88a256a3`
- Tickets processed: 11 (260001, 309068, 330209, 332163, 350796, 351838, 375662, 376856, 377088, 387029, 387108)
- Tickets with open issues: 9 (330209/332163 are closed-by-merge)
- Summaries created/refreshed:
  - New: 260001, 309068, 350796, 351838, 375662, 387029, 387108
  - Rewritten (prior summary failed quality gate): 376856, 377088
  - Refreshed last_updated only (JSON has 0 comments post-close): 330209, 332163
- Created: `wiki/zendesk/2026-05-11.md` — delta-only daily index
- ID assignments:
  - Fresh: ZI-496..ZI-501, ZI-503..ZI-506, ZI-508..ZI-511 (14 IDs)
  - Duplicate-of: ZI-502→ZI-499 (Composite Products), ZI-507→ZI-396 (UPS WorldEase)
  - Carry-forward from 2026-04-29: ZI-396 (376856), ZI-479 (377088 — prior mischaracterization superseded by ZI-508/509)
  - Carry-forward from 2026-05-08: ZI-494, ZI-495 (closed)
- Themes surfacing in this delta:
  - WooCommerce non-simple/variable product types: Bundled (ZI-496), Composite (ZI-499, ZI-502), Product Bundles/Add-Ons compatibility (ZI-500) — three customers blocked
  - FedEx SOAP→REST migration aftermath: Edit Package missing (ZI-508), insurance-surcharge bug from declared-value pass-through (ZI-509)
  - Carrier-API rejections: TNT Express `&`-in-product-name (ZI-510), APO addresses via Stamps USPS (ZI-504)
  - Order sync gaps: address/item edits not propagated (ZI-506)
- 7 of 14 active ZIs explicitly tagged `Planned for 378` in their tickets
- Next step: user should run `/roadmap regenerate` to update April 2026 roadmap from new summaries

## [2026-05-11 14:00] story-cards | Delta refresh — ZI-494, ZI-495 (DHL REST API migration)
- Delta anchor: `107b291cb62386f4646e7a57ac37234db5d7bdde` → HEAD `88a256a3`
- Changed Zendesk tickets: 11 files (2 mapped to existing ZIs, 9 unmapped — pre-ZI tickets)
- Matched ZI issues: ZI-494 (#330209), ZI-495 (#332163) — both closed/resolved
- Updated: `wiki/product/stories/ZI-494.md`, `wiki/product/stories/ZI-495.md` — refreshed SLA days-overdue (346→350, 333→337) and `last_updated`
- Validated: both pass `validate_story_card.py`
- StoryLab: 2 existing cards refreshed (same-ZI update path):
  - [ZI-494](https://trello.com/c/Katn81Sa) — desc refreshed, comment posted
  - [ZI-495](https://trello.com/c/Fo8tsnWb) — desc refreshed, comment posted
- Both cards already in APR 18-21 lane (`69dd9e0d579ac835a8b72efe`) with PROD label — no lane move, no label changes
- Note: 9 unmapped changed tickets (`376856`, `387029`, `260001`, `309068`, `350796`, `351838`, `375662`, `377088`, `387108`) are not in the 2026-05-08 daily index; they would need a `/zendesk-summarize delta` run before story-cards can pick them up

## [2026-04-30 15:30] ingest | Frontend Shipping, Packaging, and Settings UI
- Created: `modules/frontend/shipping-ui.md` — Shipping UI module: label generation, manifests (4 components), carrier configuration (70+ forms), rate shopping, tracking, OAuth flows (UPS, USPS, FedEx REST, Amazon, PostNord, Canada Post), multi-carrier support, test mode, default dimensions, special services, shipping zones
- Created: `modules/frontend/packaging-ui.md` — Packaging UI module: box inventory management (displayBoxes, addOrEditBox, addCarrierBox, addUspsBox), 5 packing algorithms (weight-based, box packing, stack packing, quantity-based, weight/volume-based), product-box mappings, carrier-specific boxes (USPS flat rate, FedEx One Rate), unit conversions (lbs/in, kgs/cm, gms/cm), advanced config, packing simulation
- Created: `modules/frontend/settings-ui.md` — Settings UI module: 12 settings sections (stores, carriers, shipper, automation, users, general, messages, tax, frontend rates, vendors, agreement policy, carrier rename), store connections (7 platforms: Shopify, WooCommerce, Magento 1/2, BigCommerce, PrestaShop, Amazon India), automation rule builder (21 components: conditions manager, actions manager, exceptions, zones, carrier priority, validation), user management (roles, permissions matrix, granular overrides), origin address, shipping zones, email templates, tax config, frontend rates API
- Updated: `index.md` — Added 3 frontend module pages, updated total pages to 244+, added client scale metrics (70+ carrier forms, 12 settings sections)
- Updated: `log.md`
- Git reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020 (storepep-react submodule)
- Summary: Documented comprehensive frontend UI for shipping, packaging, and settings. **Shipping UI**: Label generation workflows (single + bulk), rate shopping with comparison tables, manifest creation (USPS SCAN, FedEx/UPS end-of-day, Canada Post, DHL), tracking interface with real-time Socket.io updates, 70+ carrier-specific configuration forms (fedEx.js, ups.js, usps.js, dhlexpress.js, etc.), OAuth registration flows (UPS OAuth, USPS REST, Amazon Shipping, PostNord, Canada Post Connect, FedEx REST multi-step with PIN/Invoice/Support validation), carrier categories (Featured, Regional, Rates-Only, EasyPost), test mode toggle, default package dimensions per carrier, special services UI (signature, insurance, Saturday delivery, hold at location, dry ice, alcohol, COD), shipping zones. Redux state: label, tracking, trackingOrdersCount, carrierServices, carrierServiceNames, storedPackages, returnPackages. Actions: 433-line settingsActions.js with carrier management (add, update, archive, fetchInfo, EasyPost integration), label generation, manifest creation, package lifecycle. Performance: parallel rate fetching, rate caching (15 min), virtualized carrier list, lazy loading, PDF preview. **Packaging UI**: Packaging settings form (Redux Form), 5 packing methods with algorithm descriptions, 3 dimension/weight unit systems with precision converters (convertBoxWeightAndDimensions), box inventory management (custom boxes, carrier boxes, USPS flat rate), box data structure (dimensions, weight, maxWeight, outer dimensions, units, carrier affiliation), product-box mapping system (override automatic packing, priority system, forceBox flag), carrier-specific boxes (USPS Priority Mail/Flat Rate, FedEx One Rate), advanced configuration (box rotation, utilization %, padding, fragile handling), display components (displayBoxes table, addOrEditBox modal, addCarrierBox, addUspsBox), packing algorithm integration with label generation, unit conversion with 4-decimal precision. Redux state: packaging reducer with packingMethod, boxes array, productBoxMappings array, carrierBoxes object. **Settings UI**: 12 major settings sections, store connection manager (7 platforms: Shopify OAuth, WooCommerce API keys, Magento 1/2 REST/SOAP, BigCommerce OAuth, PrestaShop, Amazon India), store configuration per platform (sync frequency, order statuses, webhooks, fulfillment, product sync), branding (logo, colors, email templates, packing slip, tracking page), webhook management (event subscriptions, retry policy, monitoring), automation rule builder (21 components: setup.js, automationTable with drag-drop priority, addOrEditAutomationDetails multi-step wizard, automationConditionsManager with AND/OR logic, AutomationConditions component, automationActionsManager, carrierSelection, carrierPriority, servicesBasedOnCarrier, validateAutomationRules, addOrEditExceptions, exceptionConditionsManager, automationZones), automation conditions (order value, weight, destination, product attributes, shipping class, store source, customer type), automation actions (set carrier/service, package dimensions, address, discount, tag, signature, insurance, notification, skip automation), user management (usersSetup, usersSetupTable, addOrEditUser with roles: Owner/Admin/Manager/Staff, permissions component with granular matrix, UserListDialog), origin address configuration, shipping zones, tax settings (calculation method, provider integration, exemptions, nexus), frontend rates API (WooCommerce live rates: keys.js API key generation, shippingClass mapping, carriersList filtering, ratesAPIAutomationContainer rules), vendor settings (marketplace, commission, payouts), carrier rename (custom display names, white-labeling), messages (email templates with Draft-JS editor, SMS templates, variable insertion), agreement policy (terms, privacy, version tracking). Redux state: generalSettings, addressDetails (aliased originAddress), label, tracking, vendorDetails, plus form-specific reducers. Settings form pattern: Redux Form with enableReinitialize, validation, auto-save indicators, success/error alerts. Multi-step wizards (Stepper component) for complex flows (automation, carrier OAuth, onboarding). Tab-based organization for complex settings sections. Account setup status tracking (5 steps: store 20%, carrier 40%, address 60%, packaging 80%, first order 100%). Identified tech debt: 12 sections overwhelming IA, large form performance, validation inconsistency, permission matrix complexity, automation builder UX, no settings search, no export/import. Test coverage: Low-Medium (40-60%) - core settings tested, complex workflows manual.

## [2026-04-30 10:45] ingest | StorePep Client Frontend
- Updated: `architecture/frontend-architecture.md` — Expanded with complete Redux state structure (26+ reducers), dual routing system (100+ routes), ACL modules, QZ Tray printing integration, codebase metrics (702 JS files)
- Created: `modules/frontend/orders-ui.md` — React/Redux order management interface documentation with AG Grid, real-time Socket.io updates, bulk actions, filters, batch processing
- Updated: `patterns/redux-patterns.md` — Replaced stub with comprehensive Redux architecture: ~100 action types, 30+ action modules, async patterns, Redux Thunk, Redux Form, immutable updates, selectors, best practices, migration considerations
- Updated: `index.md` — Added Frontend section under Modules, updated Redux Patterns description, added client scale metrics, updated total pages to 241+
- Updated: `log.md`
- Git reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020 (storepep-react submodule)
- Summary: Ingested StorePep React client (702 JS files in client/src/). Documented comprehensive frontend architecture including: (1) React 16.10.2 + Redux 4.0.1 state management with 26+ reducers managing orders, products, shipping, automation, carriers, workflows, jobs, toggles, subscriptions, and UI state, (2) Dual routing system: StorepepUsersRoutes (239 lines, 100+ merchant routes) and StorepepTeamRoutes (admin routes) with HOC-based auth/subscription checks, (3) Redux patterns: ~100 action types, 30+ action modules organized by domain, async actions with Redux Thunk, Redux Form integration for form state, immutable update patterns, selector patterns, connect HOC usage, (4) Access control system with 6 ACL modules (userRoleBasedAccessMapper, urlToPermissionMapper, userBasedCarriers, userBasedAutomationConditions, storepepProcessBasedPermissions, config), (5) Real-time updates via Socket.io client (order status changes, label generation, tracking updates, batch completion), (6) UI framework: Material-UI dual version setup (v0 legacy + v3 modern), AG Grid 28.2.1 for high-performance data tables, React Dates, React DnD, Draft-JS for rich text, (7) Direct label printing via QZ Tray 2.2.4 for thermal printers, (8) Error tracking with Sentry 7.43.0 and Web Vitals 3.4.0, (9) Build system: Webpack 4 with code splitting, S3 deployment, Babel 7 transpilation. Created detailed Orders UI module page covering: order grid component (AllOrders with AG Grid), status tabs (All, Initial, Processing, Label Created, Shipped), filter system (date range, store, carrier, search), order summary panel, Redux state management (orders, ordersFilters, ordersTab, ordersCount, storedPackages, returnPackages), real-time Socket.io integration, bulk actions (process, generate labels, mark shipped, cancel, export), batch processing view, performance optimizations (virtualization, debounced search, memoization), and data flow. Documented complete Redux patterns including: action type constants, synchronous/async action creators, conditional action dispatch, action organization (30+ modules), reducer patterns (basic, composition, root reducer with global actions), immutable update patterns, Redux Form integration, selector patterns (basic, computed, cross-slice), connect HOC (mapStateToProps, mapDispatchToProps), async flow, best practices, performance considerations, and Redux Toolkit migration path. Identified tech debt: Material-UI version mixing, React 16.10.2 outdated, Redux-Form vs React Hook Form, Axios 0.19.0 security vulnerabilities, class components vs hooks, Webpack 4 vs 5, codebase size (702 files), AG Grid not latest, filter state complexity, real-time scaling challenges.

## [2026-04-28 19:00] document | FedEx REST Registration Flow Pattern
- Created: `patterns/carrier-fedex-rest-registration.md` — FedEx REST API multi-step registration documentation
- Updated: `index.md` — Added FedEx REST registration to Patterns section, updated total pages to 239+
- Updated: `log.md`
- Git reference: aa78e90db3b0d01ce297d68a370fc67524440a9f (carrier-registration submodule)
- Summary: Documented FedEx REST registration flow pattern from PlantUML diagrams (raw/carrier-registration/docs/fedex/*.puml) and implementation code. Three validation methods: (1) PIN-based (SMS/Email) - address validation → PIN generation → user enters PIN → PIN validation → child credentials, (2) Invoice-based - address validation → user enters invoice details → invoice validation → child credentials, (3) Support-based - address validation → auto-approved → child credentials immediately. Architecture: FedEx issues child API keys (child_Key + child_secret) per merchant, StorePep maintains parent OAuth credentials per platform (PH-MCSL-QA, Fedex-App, FEDEX_PLUGIN) and region (US, APAC, MEISA, LAC, CA, AMEA). Implementation files: Carrier.js (orchestration), FedexApi.js (API wrapper), AddressValidationApi.js, PinGenerationApi.js, PinValidationApi.js, InvoiceValidationApi.js. Workflow state machine: InvoiceBasedRegistrationSteps, PinBasedRegistrationSteps, SupportBasedRegistrationSteps with decision logic in WorkflowStepsProviderImpl.js. Bookmark resource representation: 3 states (not_registered → register link, registered_not_verified → verify link with PIN/invoice form, verified → redirect with accessToken). Error handling: ADDRESS_VALIDATION_FAILED, PIN_GENERATION_FAILED, PIN_VALIDATION_FAILED, INVOICE_VALIDATION_FAILED, SUPPORT_VALIDATION_FAILURE, ACCOUNT_NOT_FOUND. Database schema: merchant_registration (interaction_data with type markers), merchant_credentials (encrypted child_Key + child_secret). Events: CarrierRegisteredForPluginLicense emitted after verification with child credentials + parent credentials for ship-rate-track-proxy. Comparison tables: FedEx REST vs UPS OAuth (proprietary vs OAuth 2.0, child keys vs access tokens, 3 validation methods vs single OAuth flow), FedEx REST vs FedEx SOAP (REST/JSON vs SOAP/XML, registration API vs manual, regional parent creds vs global).

## [2026-04-28 18:15] document | Carrier OAuth Registration Flow Pattern
- Created: `patterns/carrier-oauth-flow.md` — OAuth 2.0 authorization code flow documentation
- Updated: `index.md` — Added carrier OAuth flow to Patterns section, updated total pages to 238+
- Updated: `log.md`
- Git reference: aa78e90db3b0d01ce297d68a370fc67524440a9f (carrier-registration submodule)
- Summary: Documented carrier OAuth registration flow pattern from PlantUML diagram (raw/carrier-registration/docs/ups_oauth.puml) and implementation code. Pattern applies to 5+ OAuth-based carriers (UPS Ready OAuth, UPS DAP OAuth, USPS REST, Amazon Shipping, PostNord). Flow stages: (1) Initiation - license generation and pre-registration, (2) Polling loop - 5-second interval bookmark polling for status, (3) Login flow - state token generation (CSRF protection via Auth Provider + Jakash), redirect to carrier login, OAuth callback with auth code, token exchange, user info fetch, (4) Account confirmation - user selects account details from carrier response, (5) Access key generation - client credentials returned, polling stops. Documented UPS Ready OAuth implementation (RemoteAPI.js, RegistrationProvider.js): generateToken() with authorization_code grant, refreshToken() with refresh_token grant, fallback generateTokenWithBasicAuth() with client_credentials grant. Database schema: merchant_registration (status tracking), merchant_credentials (encrypted token storage with versioning). State token security: CSRF prevention, 15-min timeout, one-time use, license+carrier binding. Error handling: invalid_grant, invalid_client, invalid_scope, server_error, invalid_state. Polling strategy: client-side loop with 5-second interval, server caching recommendation. Events: CarrierRegisteredForPluginLicense emitted to StorePep platform for credential caching. Comparison to legacy carriers: OAuth (access+refresh tokens, multi-step, expiry, auto-refresh) vs legacy (API key+password, single-step, static, no refresh). UPS Ready vs UPS DAP differences: target audience (SMB vs enterprise), authorization (3-legged vs 2-legged possible), scopes (standard vs extended).

## [2026-04-28 17:30] ingest | Carrier Registration Service
- Updated: `architecture/carrier-registration.md` — Replaced stub with comprehensive documentation
- Updated: `index.md` — Updated carrier-registration description in Architecture section
- Updated: `log.md`
- Git reference: aa78e90db3b0d01ce297d68a370fc67524440a9f (carrier-registration submodule)
- Summary: Ingested carrier-registration microservice (268 JS files, ~11,958 LOC, 35 migrations). Documented carrier onboarding and OAuth management service that manages registration workflows, credential storage, and token lifecycle for 15+ carriers (FedEx REST, UPS OAuth, Amazon Shipping, PostNord, USPS, Delhivery, etc.). Core functions: (1) Multi-step registration workflows (Invoice/PIN/Support-based for FedEx), (2) OAuth 2.0 token lifecycle (obtain, refresh, store), (3) Encrypted credential storage in PostgreSQL (4 tables: merchant_registration, merchant_credentials, merchant_license_map, merchant_token_requests), (4) License-to-carrier mappings, (5) Platform-specific credential isolation (Shopify, WooCommerce, Magento). Key routes: POST /registration (register), GET /registration (workflow steps), PUT /registration/license (renew), GET /registration/credentials (fetch), POST /registration/verification (verify). Services: 33 files (RegistrationProvider, LicenseRegistrationProvider, AuthProvider, CredentialProvider, TokenRefreshProvider, WorkflowStepsProvider). Infrastructure: 15 carrier modules with Service Locator pattern. API: RESTful with HAL resources, content negotiation (V0/V1), JWT auth + x-phive-api-key. Database: PostgreSQL with 35 migrations. Events: Emits CarrierRegisteredForPluginLicense consumed by StorePep platform for credential caching. Deployment: Lambda + API Gateway, Ansible, Jenkins CI/CD, Docker. Comparison table to ship-rate-track-proxy: registration is upstream stateful setup service (one-time/periodic), ship-rate-track-proxy is downstream stateless operational service (high-frequency per shipment). Identified 8 tech debt items (low test coverage 17 tests, 64KB config file, no idempotency, error handling gaps, no rate limiting, platform spoofing risk, V0 API legacy, credential versioning bloat).

## [2026-04-28 16:51] ingest | Shopify Multi-Carrier App Shell
- Added submodule: `raw/shopify-multicarrier-app` — Shopify shell for multi carrier app
- Created: `architecture/shopify-multicarrier-app.md` — Shopify OAuth wrapper and installation shell architecture
- Updated: `index.md` — Added shopify-multicarrier-app to sources and architecture section
- Updated: `log.md`
- Git reference: 8ca5f05476a5f44b05cf7d8ab79cf09d58d91743 (shopify-multicarrier-app submodule)
- Summary: Ingested shopify-multicarrier-app, a Shopify-specific OAuth/installation wrapper (113 JS files: 84 server, 29 client). This is NOT the main StorePep platform — it's a lightweight shell that handles Shopify App Store distribution. Core functions: (1) Shopify OAuth flow and store authentication, (2) Account provisioning on main StorePep platform via JWT, (3) Shopify subscription billing management, (4) Store metadata and location sync, (5) API proxy between Shopify and StorePep. Key routes: shopify.js (OAuth, billing, webhooks), storepepConnect.js (account registration, login, location sync), rates.js (rate proxy), plans.js (subscription plans). Database: Local MongoDB with shops schema (access tokens, StorePep UUIDs, billing info) and settings. Tech stack: React 16, Redux, Express 4, Mongoose 5, Shopify Polaris 3, @phivejs packages (config, eventing, feature-switch). Platform integration: All shipping logic delegated to StorePep via REST API with JWT auth. Documented differences from storepep-react: purpose (OAuth shell vs. full platform), scope (installation/billing vs. shipping workflow), UI (minimal vs. complete), database (shops only vs. full platform schema), deployment (Shopify App Store vs. SaaS). Identified tech debt: legacy schema fields, hardcoded scopes, error handling gaps, scope management pattern.

## [2026-04-27 20:51] ship | Release MCSL 377
- Release: `wiki/product/releases/mcsl-377.md` (status: shipped, shipped_at: 2026-04-27 20:51:14 UTC)
- Cards Ready To Ship: 18
- Cards Support Closed: 2
- Cards Unsupported Partnership: 2
- Cards Carrier Platform Issues: 2
- Total shipped/closed: 24
- Cards forced (non-terminal at ship): 12 (1 BUG REPORTED, 1 QA READY, 10 Open)
- Updated: `wiki/product/backlog.md` (added "Shipped in MCSL 377" section)
- Git reference: dfb7ba1ab99a9a1529c4f290b5984244a362c813
- Summary: Shipped MCSL 377 with 37 total cards using --force flag. 24 cards in terminal states (18 Ready To Ship, 2 Support Closed, 2 Unsupported Partnership, 2 Carrier Platform Issues). 12 non-terminal cards (1 BUG REPORTED, 1 QA READY, 10 Open) documented in Warnings section. No Trello writes (ship is pure wiki write).


## [2026-04-27 14:56] zendesk-summarize | Delta extraction (30 tickets, schema migration)
- Processed: 30 delta tickets (24 shopify, 6 other_platforms)
- Created/updated: 30 summaries in `zendesk/summaries/*.md`
- Created: `zendesk/2026-04-27.md` — daily index with 6-column schema (added "Duplicate Of" column)
- Updated: `log.md`
- Git reference: c6f2681a3cd88e11f5247c84a2228a7a0e2e1a2e
- Summary: Delta extraction pipeline with schema migration from 5-column to 6-column Issue Index format. **Delta Detection**: Identified 30 changed tickets since last extraction (git ref 630297e). **Pipeline**: 6-step automated workflow (summarize_ticket.py → load_summaries.py → load_prior_index.py → assign_zi_ids.py → generate_daily_index.py → validate_daily_index.py). **5-Step ID Assignment**: (1) Exact match preserved 75 prior ZIs, (2) Fuzzy duplicate detection found 27 similar issues (Jaccard similarity ≥0.4) caused by title truncation in prior index, (3) Fresh assignment for 35 new issues (ZI-276 to ZI-310), (4) Cross-reference within new ZIs (none found), (5) Carry-forward of 65 prior ZIs not exact-matched. **Schema Migration**: Added "Duplicate Of" column to track issue relationships — 27 new ZIs reference prior ZIs as duplicates (e.g., ZI-276 → ZI-183 with 0.71 similarity). **Issue Stats**: 202 total active issues (up from 140), spanning ZI-136 to ZI-337. All 140 prior ZI IDs preserved. **Fuzzy Match Quality**: Spot-checked 5 fuzzy matches, all valid with 0.57-0.80 similarity scores. **Validation**: All checks passed — no duplicate ZIs, all "Duplicate Of" references valid, all ticket links resolve, issue count matches. **Implementation**: Created 7 Python scripts + driver shell script for automated future runs. Fixed title sanitization (newlines → spaces, pipe escaping) and duplicate ID assignment bug. **Product Breakdown**: shopify 36 issues, woocommerce 20 issues, unknown 130 issues, magento 1 issue (unchanged). **Area Breakdown**: other 59 issues, onboarding 14 issues, carrier-config 13 issues, label-generation 18 issues, order-management 11 issues, product-management 10 issues, etc.

## [2026-04-27 10:15] ingest | Ship-Rate-Track-Proxy Service
- Created: `architecture/carrier-api-proxy-pattern.md` — Unified API Gateway pattern with adapter pattern
- Created: `modules/shipping/ship-rate-track-proxy.md` — Ship-rate-track-proxy service module documentation
- Updated: `index.md` — Added carrier API proxy architecture page and ship-rate-track-proxy module to shipping section
- Updated: `log.md`
- Git reference: 0187f5ff1de74aa8b8769b98beef22fc29327b69 (ship-rate-track-proxy submodule)
- Summary: Ingested ship-rate-track-proxy microservice (252 TypeScript files, ~5,886 LOC). Documented unified API Gateway pattern providing consistent REST interface for 18+ carrier integrations (FedEx, UPS, USPS, TForce, PostNord, Amazon Shipping, etc.). Architectural patterns: Adapter pattern (per-carrier modules), API Gateway pattern (single entry point), dynamic provider loading (parseCarrier middleware), middleware pipeline (errorHandler → parseCarrier → publishAnalytics). Key features: 10 service categories (rates, shipment, tracking, pickup, returns, access-points, address-validation, landed-cost, documents, manifest), protocol abstraction (SOAP/REST/XML → unified JSON), OAuth 2.0 token management, error normalization, analytics publishing to SQS. Module structure: consistent pattern across all carriers (auth, rates, shipment, tracking, pickup services), ModuleLoader for DI, provider interfaces. Common infrastructure: carrier-api-client (retry/error handling), external-auth (OAuth), error-actions (5xx wrapper), validatable (schema validation), logger (Winston). Configuration: 122KB config.json with per-carrier sandbox/live URLs, service IDs, provider mappings. Test coverage: 8 tests (395 LOC, 6.7% ratio) — minimal coverage, no carrier integration tests identified as major tech debt. Deployment: Lambda + API Gateway, Node 16.20.2. Identified 8 tech debt items (low test coverage, massive config file, no schema validation, no versioning, SPOF risk, no rate limiting, no caching, no idempotency).

## [2026-04-27 09:45] ingest | Reporting Service
- Created: `architecture/event-driven-reporting.md` — Event-driven architecture pattern for async order aggregation
- Created: `modules/reporting/reporting.md` — Reporting service module documentation
- Updated: `index.md` — Added reporting architecture page and module to index
- Updated: `log.md`
- Git reference: 4728b3d692a83006cf44c6a40c57b06574e49639 (reporting submodule)
- Summary: Ingested reporting microservice (111 TypeScript files, ~3,800 LOC). Documented event-driven architecture with SQS message queues, denormalized order snapshots, async CSV export workflow, and S3/email delivery. Core components: OrderImportUnitaryService (order sync from main system), ReportScheduler (job creation), OrderExportUnitaryService (streaming CSV generation), filter system (composable criteria: Equals/Like/Range), event listeners (JobCreated → export, JobUpdated → email). Test coverage: 46 tests (~4,822 LOC, 1.27:1 test ratio), 6 integration tests covering DB operations and streaming exports. Database: 2 tables (Order with 36 fields, Job with status tracking), 12 migrations. Deployment: Lambda + API Gateway, Terraform/Ansible for QA/Prod environments. Dependencies: main storepep-react (emits order events), TypeORM, pg-query-stream, nodemailer, @phivejs/eventing (custom event bus). Identified 7 tech debt items (no pagination, no resume on failure, no incremental sync, S3 link expiry, no real-time reports, no queue backlog monitoring, no compression).

## [2026-04-27 02:29] sources | Added 7 New Source Repositories
- Added submodules:
  - `raw/carrier-registration` - Carrier registration service (GitLab)
  - `raw/ship-rate-track-proxy` - Ship rate track API implementations (GitLab)
  - `raw/reporting` - Reporting source base (Bitbucket)
  - `raw/order-search` - Order search service (GitLab)
  - `raw/storepep-internal-api` - Internal API service (GitLab)
  - `raw/order-updates` - Order updates service (GitLab)
  - `raw/fulfillment-service` - Fulfillment service (GitLab)
- Created: `architecture/carrier-registration.md` (placeholder stub)
- Created: `architecture/ship-rate-track-proxy.md` (placeholder stub)
- Created: `architecture/reporting.md` (placeholder stub)
- Created: `architecture/order-search.md` (placeholder stub)
- Created: `architecture/storepep-internal-api.md` (placeholder stub)
- Created: `architecture/order-updates.md` (placeholder stub)
- Created: `architecture/fulfillment-service.md` (placeholder stub)
- Updated: `raw/sources.yaml` (added 7 new git-submodule entries)
- Updated: `wiki/index.md` (added Sources section + 7 architecture pages)
- Updated: `wiki/log.md`
- Git reference: 5f4e58990f71acea410996b5e885f82c21e741e2
- Submodule commits:
  - carrier-registration: 8861b97
  - ship-rate-track-proxy: 0187f5f
  - reporting: 4728b3d
  - order-search: 87a25e4
  - storepep-internal-api: 71d57ae
  - order-updates: 95c3fe4
  - fulfillment-service: 4cef4a0
- Summary: Registered 7 additional code repositories as git submodules for future wiki ingestion. Services include: carrier-registration (carrier onboarding workflows), ship-rate-track-proxy (carrier API implementations), reporting (analytics and dashboards), order-search (advanced search/filtering), storepep-internal-api (inter-service communication), order-updates (status changes and notifications), and fulfillment-service (order fulfillment workflows). All submodules successfully cloned and ready for documentation. Created placeholder architecture pages with status=partial, ready for ingestion workflow when needed.

## [2026-04-23 15:00] ingest | Carriers and Adapters Complete Catalog
- Created: `architecture/carriers-and-adapters.md`
- Updated: `index.md` (added carriers-and-adapters.md to Architecture section)
- Updated: `log.md`
- Git reference: e5bf9867ce1e02cdbf9b2da90f081f15fa0be345 (storepep-react submodule)
- Sources analyzed:
  - `storePepConstants.js:41-90` - All carrier codes (C1-C54)
  - `storePepConstants.js:159-203` - Carrier name mappings
  - `shipmentAdaptor.js:1-191` - Adapter factory and class mappings
  - `storepepConfig.js` - API configuration patterns
  - Carrier-specific helper files (fedex, ups, australiaPost, dhl, canadaPost, blueDart, etc.)
- Summary: Comprehensive carrier integration reference cataloging all 45+ shipping carriers with carrier codes, descriptive names (e.g., "eParcel" for Australia Post C8), adapter class names, API protocols (SOAP, REST, XML), and endpoint URLs (sandbox/production where available in code). Organized by region (US/International, Australia/NZ, Canada, India, Europe, Middle East/Asia, Latin America) plus multi-carrier aggregators (EasyPost, Landmark Global). Documented legacy→modern API migrations (FedEx C2→C39, UPS C3→C38, USPS variants), special configurations (FedEx regional credentials, UPS integration modes, EasyPost 100+ carrier accounts, Australia Post eParcel variants), and known issues (SOAP deprecations, OAuth rate limits, regional endpoint complexity). Complete with "Adding a New Carrier" workflow and cross-references to shipping module pages.

## [2026-04-22 10:00] build | ZI Area Coupling Map
- Mode: build (full rebuild)
- Source: `wiki/zendesk/2026-04-20.md` (ZI issues) + `wiki/product/backlog.md` (clusters) + `wiki/architecture/coupling-map.md` (code coupling)
- ZI issues analyzed: 25 from 10 tickets
- Ticket co-occurrence pairs (≥2): 1
- Cluster co-occurrence pairs (≥1): 0
- Written: `wiki/zendesk/area-coupling.md`
- Cache: `.claude/cache/zendesk-overlap-data.json`
- Summary: Top overlap: carrier-config ↔ feature-request (2 tickets, no code co-changes). Most pairs are single-ticket overlaps below reporting threshold. No multi-area clusters detected in current backlog structure.

## [2026-04-16 16:30] ingest | Database Migrations Documentation
- Updated: `wiki/operations/database-migrations.md` (stub → complete)
- Git reference: 0f9b0bc965c82210bf38320d7c5a5ce60cfd44da (storepep-react submodule)
- Summary: Replaced stub with full documentation of the migrate-mongo workflow used by storepepSAAS. Covers tooling (migrate-mongo@^10.0.0, migrate-mongo-config.js targeting `storePep` db with `changelog` collection and `useFileHash: true`), migration anatomy (idempotency guards via mongoDictionary helpers, no-op down patterns, named indexes, background index builds), filename conventions, intent groupings across 108 migrations (31/32/38/7 across 2023-2026 — carrier service-code seeding ≈40% of corpus), runbook commands and required env vars, authoring checklist, and known issues including drift in backend-architecture.md (lists `server/src/db-migrations/migrations/` but actual path is `server/db-migrations/`).

## [2026-04-16 14:30] ingest | Carrier Integration — engineer's reference
- Updated: `wiki/modules/shipping/carrier-integration.md` (stub → complete, status flipped from needs-update → complete)
- Updated: `wiki/modules/shipping/carrier-system-overview.md` (added link in Dependencies)
- Updated: `wiki/modules/shipping/carrier-configuration.md` (added link in Related Pages)
- Updated: `wiki/modules/shipping/label-generation.md` (added link in Related Pages)
- Updated: `wiki/index.md` (replaced stub description with full one-line summary)
- Git reference: current
- Summary: Filled in the carrier-integration.md stub with an engineer-focused reference: three-file pattern per carrier (ShipmentHelper / RequestBuilder / Helper), dispatch checklist, HTTP retry pattern (FedEx httpClientFactory, not yet shared), four auth patterns, carrier-specific errorCodes dictionaries cross-referenced with the 49 centralised storepepErrorEvents, dual API migrations (FedEx C2/C39, UPS C3/C38, USPS variants), aggregator trade-offs (EasyPost, Eshipz), credential encryption notes, recent integration activity (Delhivery Proxy C54, FedEx REST negotiated rates, Australia Post OAuth + chunked manifest, PostNord country of origin, EasyPost sanitization), engineering checklist for adding a new carrier, and tech debt. Content complements but does not duplicate carrier-system-overview / carrier-configuration / label-generation — each claim is unique or explicitly delegated.

## [2026-04-16 10:00] ingest | Slack Source Type + Royal Mail Integration Constraints
- Created: `raw/slack/2026-04-15-royal-mail-easypost-integration.md` (raw Slack conversation)
- Created: `wiki/product/decisions/2026-04-15-royal-mail-integration-constraints.md` (decision record)
- Updated: `wiki/product/stories/ZI-057.md` (added Integration Constraints section)
- Updated: `raw/sources.yaml` (added slack source type)
- Updated: `wiki/index.md` (added decision record entry)
- Updated: `wiki/log.md`
- Git reference: current
- Summary: Added Slack as a new raw source type (manual, markdown with frontmatter). Captured internal Slack discussion (2026-04-15) revealing Royal Mail integration constraints: requires 3PI approval + OBA account + rates card approval from EasyPost/Royal Mail, no free production API for SaaS providers. QA blocked until EasyPost provides test credentials (Abhilash exploring). Decision record created, ZI-057 story card updated with constraints section. Pipeline: raw/slack/*.md → wiki/product/decisions/ + wiki/product/stories/ updates.

## [2026-04-13 20:00] ingest | Zendesk Issue Extraction & Backlog Regeneration
- Created: `zendesk/summaries/*.md` (66 per-ticket structured summaries)
- Created: `zendesk/2026-04-13.md` (daily index: 93 open issues from 66 tickets)
- Updated: `product/backlog.md` (regenerated: 11 clusters from 93 ZI issues)
- Updated: `product/roadmap-april-2026.html` (ZEN_FEATURES updated with ZI refs, 6 new zf entries)
- Updated: `index.md` (added Zendesk section)
- Updated: `log.md`
- Git reference: 5058f2c24d90fbaf9741d9279b8bdc8428a4af5e
- Source: `raw/zendesk/shopify/*.json` (66 valid, 1 corrupt, 2 truncated)
- Summary: Full pipeline run — each Zendesk ticket decomposed into structured summary with timeline, open/resolved issues, and customer context. 93 open issues extracted across 11 feature areas (label-generation 20, carrier-config 11, onboarding 11, order-management 10, international 10, product-management 9, carrier-migration 8, rate-shopping 6, feature-request 4, tracking 2, returns 2). Issues clustered into 11 backlog items with scoring. Roadmap ZEN_FEATURES updated with ZI cross-references. Pipeline: raw JSON → summaries → index → backlog → roadmap.

## [2026-04-10 12:00] ingest | Ground Zero Cross-App Support Triage
- Created: `support/ground-zero/index.md`
- Created: `support/ground-zero/pain-ranking.md`
- Created: `support/ground-zero/by-app.md`
- Created: `support/ground-zero/insights.md`
- Created: `support/ground-zero/sprint-views.md`
- Updated: `index.md` (added Support section, total pages 51→56)
- Updated: `log.md`
- Updated: `product/insights.md` (cross-link to ground-zero)
- Updated: `product/backlog.md` (cross-link to sprint-views)
- Updated: `raw/sources.yaml` (added stage-zero-analysis google-sheet source)
- Updated: `scripts/sync.sh` (added gid support for multi-tab Google Sheets)
- Source: `raw/sheets/stage-zero-analysis.xlsx` (synced 2026-04-10, gid=1368718443)
- Git reference: e14861276df2dcc6f378bc845a9fc74ae5722de0
- Summary: Full cross-app triage of 68 open Zendesk tickets across Shopify (49), WooCommerce (15), BigCommerce (3), Magento (1). Tickets split into discrete issues, categorized into 10 issue types across 4 pain tiers. Top pain clusters: International/Customs (14 tickets, 10/10 pain), Product Import/Variants (11 tickets, 9/10), Carrier Integration/Migration (15 tickets, 8/10). 7 key insights distilled including aging backlog risk (tickets open 16-34 months). 6 sprint views created: Sprint Zero (deploy what's built), Fire Drill (AusPost/PostNord deadlines), Trust Restorers (data integrity), International Sprint (CI/customs batch), Scale Unlockers (variant limits), Carrier Expansion (new integrations).

## [2026-04-09 09:00] dashboard | Weekly Product Dashboard — Week of Apr 7
- Created: `product/dashboards/week-2026-04-07.md`
- Updated: `index.md`
- Git reference: 4f6714a0de70910399b45d628d3930f0404f6374
- Summary: Weekly dashboard synthesising 54 open Shopify MCSL tickets. Sections: Pulse metrics, 3 carrier deadlines (FedEx now, PostNord May 1, Australia Post Jul 7), feature health scorecard, 17 features ranked by customer demand across 3 tiers, carrier breakdown (9 carriers), recommended P0–P3 actions, stale ticket risk list.

## [2026-04-08 22:00] product-management | Product Management Layer Bootstrap

- Created: `product/backlog.md` - Scored backlog with 10 items from 52 Zendesk tickets
- Created: `product/insights.md` - Signal aggregation: 11 Zendesk themes, 7 test coverage gaps, 5 code hotspots, 3 emerging patterns
- Created: `product/metrics.md` - Customer health scorecard with pain index per feature area
- Created: `product/features/carrier-migration-fedex-rest.md` - Feature story with 3 user stories, acceptance criteria, cross-links
- Created: `product/decisions/2026-04-08-product-management-layer.md` - Decision record for PM layer approach
- Updated: `CLAUDE.md` - Added Product Management section with delta-aware resync workflows, templates, ticket categorization, cross-linking rules
- Updated: `index.md` - Added Product Management section
- Updated: `log.md`
- Git reference: b367ffe7e91f3fe5ccc496676bbfee860ed8c003
- Summary: Established source-driven product management layer (wiki/product/) synthesizing 52 open Shopify MCSL Zendesk tickets into actionable insights. **Zendesk Analysis**: Queried live API for tickets matching status<pending + support_type=agent + product=shopify_multi_carrier_shipping_label_app. Categorized into 11 feature areas: onboarding (9), carrier-config (8), label-generation (6), carrier-migration (4), order-management (3), australia-post (2), international (2), rate-shopping (2), tracking (1), feature-requests (1), other (14). **Key Signals**: 65% need dev work (dev_needed tag), FedEx migration is highest pain index (1700), 35% have high agent replies. **Delta-Aware Design**: All product pages use git_reference in frontmatter for delta detection on resync — git diff against raw/ finds new tickets, changed tests, updated sheets. Only delta is processed. **Ticket Categorization**: By product (shopify) and feature area, stored under wiki/product/. **Backlog Scoring**: Impact x Confidence / Effort framework with 10 initial items. **Pain Index**: Composite metric crossing ticket volume x severity with automation confidence — surfaces Carrier Migration, Rate Shopping, Australia Post as top priorities.

## [2026-04-08 20:45] guide | Added Associated Features Section to Carrier Journey Guide
- Updated: `adding-new-carrier-customer-journey.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Added comprehensive "Associated Features" section to carrier journey guide listing all 17 features affected by new carrier addition. **Features Organized**: Categorized by priority - Core (6 features: Carrier Config, Rate Shopping, Label Gen, Tracking, Service Selection, Cancellation), Important (4 features: Multi-Package, International, Return Labels, Special Services), Optional (3 features: Pickup, Manifest, Address Validation), Supporting (4 features: Rate Caching, Error Handling, Reports, Monitoring). **Feature Details**: Each feature includes what it does, customer interaction, code impact, automation percentage, test scenarios count, launch criticality, and related features. **Dependency Map**: ASCII diagram showing feature dependencies from Carrier Configuration as root to all dependent features (Rate Shopping → Service Selection → Automation, Label Generation → Multi-Package/International/Return/Special Services/Documents/Packaging, Tracking → Status Mapping/Email/Cron). **Priority Matrix**: Table showing 17 features across 4 priority levels with total 231 scenarios and 11.4% current automation. **Testing Priority**: Organized as Must Test (5 features before launch), Should Test (4 high-volume features), Can Test Later (4 optional features). **Implementation Complexity**: Effort estimates per feature ranging from 4-8h (special services) to 40-60h (label generation), with total complete implementation 136-212h and minimum viable 80-118h (Config + Rate + Label + Tracking + Errors). This section now serves as quick reference for understanding scope and dependencies when planning carrier integration.

## [2026-04-08 20:15] guide | Adding New Carrier - Customer Journey & Impact Analysis
- Created: `adding-new-carrier-customer-journey.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive guide for adding new carriers from customer perspective covering complete journey, system impacts, gaps, and rollout strategy. **Customer Journey**: Mapped 5 phases (Discovery, Registration, Onboarding, Daily Operations, Reporting) with 4 sub-phases in onboarding, identifying 20 pain points across customer experience from "Does MCSL support this carrier?" through daily label generation and tracking. **Feature Impact Analysis**: Documented 15 features affected by new carrier addition with priority classification (Core: Rate Shopping, Label Gen, Tracking; Optional: Pickup, Manifest, Address Validation) - each feature includes customer touchpoints, code changes needed, testing gaps, estimated scenarios, and criticality for launch. **Testing Requirements**: Per-carrier test matrix showing ~180 scenarios needed across 13 test categories (Registration 15, Rate Shopping 20, Label Generation 30, Tracking 25, Automation 12, International 15, Error Handling 20, etc.) with current coverage gaps (Registration 0%, Rate Shopping 0%, Tracking 7%, overall 11.4%). **Critical Gaps Identified**: 20 gaps categorized by severity - Critical (no carrier registration automation, no tracking status mapping, no post-save validation, no error message mapping, no label format validation), High Priority (no feature detection, no automation dry-run, no rate fetch audit, no tracking engine tests, no service code validation), Medium Priority (no carrier wizard, no comparison tool, no label preview, no health monitoring). **Documentation Needs**: Customer-facing (carrier setup guides per carrier 2-3 pages, comparison chart, troubleshooting guide 5 pages, feature matrix) and internal (integration checklist, API reference, status mapping guide). **Rollout Strategy**: 4-phase approach (Development & Testing 2-4 weeks, Soft Launch invite-only 2 weeks, General Availability 1 week, Post-Launch Maintenance ongoing) with go/no-go criteria, success metrics, and monitoring plan. **Launch Checklist**: Comprehensive 50+ item checklist covering pre-development, development (core features, optional features, advanced, error handling), testing, documentation, launch, and post-launch phases. **Complexity Examples**: Categorized carriers as Simple (Sendle 1-2 weeks, REST JSON, straightforward), Moderate (Canada Post 2-3 weeks, SOAP XML, bilingual, service points), Complex (FedEx 4-6 weeks, 1800+ LOC, 50+ fields, freight, customs). **Customer Pain Point Summary**: Table mapping each journey phase to customer goals, current pain points, and recommended fixes (e.g., Discovery phase: no carrier directory → create public carrier list; Onboarding: 50-field form no validation → multi-step wizard with test connection).

## [2026-04-08 19:30] analysis | System Features Comprehensive Analysis
- Created: `system-features-analysis.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Created comprehensive high-level feature analysis with automation coverage, code complexity assessment, scenario estimation, and confidence scoring. **Analysis Structure**: 20 high-level features analyzed covering Order Management, Label Generation, Carrier Configuration, Rate Shopping, Automation Rules, Tracking, Platform Connectors, Products, Warehouses, Bulk Actions, Packaging, Special Services, Auto Import, Grid Views, Reports, Account, Onboarding, COD, External Fulfillment, and Label Batching. **Complexity Assessment**: Categorized features by code complexity (6 Very High: 1000+ LOC, 9 High: 300-1000 LOC, 5 Medium/Low: <300 LOC) based on LOC counts from wiki documentation - Order Management (2139 LOC routes), Label Generation (1800+ LOC FedEx helper), Tracking (6800 LOC status mapper), Bulk Actions (2500+ LOC). **Scenario Estimation**: Estimated ~509 total test scenarios across all features with 75% confidence based on code analysis, API endpoints, business logic, carrier/platform multipliers, and error cases - ranging from 70 scenarios for Order Management to 5 scenarios for External Fulfillment. **Automation Coverage**: Detailed per-feature automation percentages showing 11.4% overall automation (58/509 scenarios) with breakdown: 100% coverage for 7 features (Label Gen, Packaging, Automation, Onboarding, COD, External Fulfillment, Batching), 0% for 6 critical features (Rate Shopping, Products, Warehouse, Auto Import, Reports). **Confidence Scoring**: 4-tier confidence assessment (High 92%+: 7 features, Medium 70-89%: 6 features, Low 40-69%: 2 features, None 0-39%: 5 features) with detailed justification per feature. **Critical Gaps Identified**: Priority 1 gaps (Auto Import, Rate Shopping, Product Management at 0% automation with high business impact), Priority 2 (Carrier Config 7%, Tracking 7%, Bulk Actions 30%), Priority 3 (Reports, Warehouse). **Recommendations**: Immediate actions (auto import, rate shopping, carrier expansion, product CRUD), short-term (tracking integration, bulk actions expansion, platform integration, warehouse tests), long-term (reports, multi-platform, all carriers, performance, E2E scenarios). **Methodology Documentation**: Included estimation methodology with confidence levels per feature and accuracy factors for transparency.

## [2026-04-08 19:00] test-coverage | Regression Test Matrix Integration
- Updated: `features.md` (complete restructure to align with regression test matrix)
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Restructured features.md to align with MCSL Regression Master Sheet from Google Sheets. **Matrix Structure**: Reorganized from test-type categories to feature area structure matching regression suite (Single Label Gen, Orders Grid, Packaging, SLGP, Quick Ship, General Settings, Views, Rules, Platform Setup, Adding Products, Tracking Page, Products Page, Account, Reports, Auto Import). **Ownership Mapping**: Added ownership assignments from spreadsheet (Ashok + Shahitha: Single Label Gen, Orders Grid, Reports; Basava: Packaging, SLGP, Quick Ship; Preethi + Anuja: General Settings; Preethi: Views). **Product Type Coverage**: Added product type matrix showing which product types (Simple, Digital, Custom, High Value, Dangerous Goods, Multi Product, Variable, Prepackaged) are tested across features. **Feature Area Details**: Each of 17 feature areas now includes purpose, owner, sub-components, automation status tables with product types, confidence scores, and test file mappings. **Automation Summary**: Top-level table showing automation percentage per feature area (100% for packaging, SLGP, quick ship, rules; 58% for orders grid; 0% for products, reports, auto import). **Critical Gaps Section**: Categorized gaps into High Priority (no automation - 8 areas), Medium Priority (partial - 6 areas), Low Confidence (3 areas) with specific recommendations. **Recommendations**: Immediate actions (auto import, product management, carrier coverage, tracking integration, grid filters), short-term (platform expansion, bulk actions, product types), long-term (reports, account, carrier registration, performance). **Test Organization**: Detailed test directory tree with 58 test files organized by functional domain. **Product Type Matrix**: Coverage analysis showing Simple and Multi Product well covered, Variable and Prepackaged not tested. **Maintenance Instructions**: Updated to include regression suite integration workflow for when spreadsheet data is updated.

## [2026-04-08 18:30] test-coverage | Complete Test Coverage Documentation
- Created: `features.md`
- Updated: `modules/orders/order-bulk-actions.md` (added test coverage section)
- Updated: `modules/shipping/label-generation.md` (added test coverage section)
- Updated: `modules/automation/automation-actions.md` (added test coverage section)
- Updated: `modules/shipping/carrier-configuration.md` (added test coverage section)
- Updated: `modules/shipping/shipment-tracking.md` (added test coverage section)
- Updated: `modules/stores/platform-connectors.md` (added test coverage section)
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive analysis of 58 Playwright test files in mcsl-test-automation, extracting 95 distinct user-facing features in plain English. **Features Document**: Created features.md organizing all tested features by category (Automation Rules, Carrier Configuration, COD, External Fulfillment, Label Batching, Onboarding, Order Management, Label Generation, Packaging, Document Management, Shopify Integration, Special Services) with test file references and module mappings. **Test Coverage Added**: Updated 6 module wiki pages with detailed test coverage sections including tested features tables, test file paths, coverage percentages, and lists of untested scenarios. **Statistics**: 58 test files analyzed covering 11 automation tests (100% coverage of tested actions), 3 carrier config tests (UPS only), 2 COD tests, 2 external fulfillment tests, 2 label batch tests, 2 onboarding tests, 22 order grid tests (12 action menu, 3 label generation, 7 advanced features), 5 order summary tests, 6 packaging tests, 1 Shopify test, 3 special services tests. **Coverage Highlights**: Order Bulk Actions 30%, Label Generation 100% (20/20 scenarios), Automation 46% (11/24 actions), Carrier Configuration <10% (UPS only), Tracking 7% (1 test), Platform Connectors (Shopify only). **Test Organization**: Tests organized by functional domain in mcsl-test-automation/tests/ directory with clear categorization for automation rules, carrier details, COD, fulfillment, batching, onboarding, order grid operations, packaging types, and special services.

## [2026-04-08 17:00] ingest | Shipment Tracking System
- Created: `modules/shipping/shipment-tracking.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive documentation of StorePep's shipment tracking system covering 45+ carrier integrations with automatic updates every 6 hours via cron job. **Architecture**: Three-layer data model (TrackingOrders for parent-level, TrackingPackages for individual packages, TrackingHistory for checkpoint timeline) with support for return shipment tracking. **Update Mechanism**: Scheduled cron job runs daily tracking task (storepepTrackingEngine.js:195-216) calling carrier APIs via ShipmentAdaptor pattern, with parallel tracking updates and rate limiting per carrier. **Status Mapping**: Universal status mapping system (storepepMappedTrackingStatus.js - 198KB, 6800+ lines) converts carrier-specific codes to StorePep standards (INITIAL, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED_UC, EXCEPTION_1/2/3) with 6-level attention type classification. **Real-time Updates**: Socket.io integration emits SOCKET_TRACKING_COMPLETED_CODE events to WebSocket server for live frontend notifications. **Email Notifications**: Automatic customer notifications via nodemailer with configurable triggers (trackingEventsEmailHelper.js) - emails sent on location change, status change, or attention type change with prevention of duplicate notifications. **Carrier Implementations**: Detailed documentation of FedEx (SOAP + REST), UPS (XML + OAuth), EasyPost tracking APIs with standardized response format. **Frontend**: React/Redux tracking container with status color coding (green/orange/red), timeline display, and manual re-track capability via POST /api/tracking/retrackall endpoint.

## [2026-04-07 23:00] ingest | Automation, Stores, Products, Warehouses
- Created: `modules/automation/automation-actions.md`
- Created: `modules/stores/store-integration-overview.md`
- Created: `modules/stores/platform-connectors.md`
- Created: `modules/products/product-management.md`
- Created: `modules/products/product-import-export.md`
- Created: `modules/warehouses/warehouse-selection.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive documentation of four critical StorePep domains completing the core feature set. **Automation**: Documented all 24 action types in AutomationActionsManager.js including carrier/service selection with fallback, package dimensions/weight (set/adjust), ship-from/display/sold-to addresses, order meta mapping, third-party billing, duties payer, insurance, delivery confirmation, carrier-specific special services (DHL, Aramex, Canada Post, PostNord, etc.), Saturday delivery, auto label generation, auto address correction, mark as not to ship, default service points (PostNord, DHL Sweden), and address-to-meta mapping. **Stores**: Documented store adapter pattern for 7 e-commerce platforms (Shopify, WooCommerce, Magento 2, Magento 1, BigCommerce, PrestaShop, Amazon India) with webhook management, OAuth/API authentication, order/product mapping, fulfillment sync, and platform-specific details (GraphQL bulk ops for Shopify, variant iteration for WooCommerce, SOAP for Magento 1, report-based for Amazon). **Products**: 191-line product model with physical attributes, customs data, carrier-specific metadata (dangerous goods, delivery signatures, dry ice, alcohol, restricted articles), SKU management, product types (simple, variable, variant, grouped, subscription), inventory tracking, and warehouse integration. **Warehouses**: WMS module with Strategy Pattern for warehouse selection (GeoDistanceStrategy using MongoDB geospatial queries, AddressBasedStrategy with routing rules), inventory-aware filtering, Odoo ERP integration, and automation override behavior where WMS-selected warehouse takes priority over automation-configured ship-from address.

## [2026-04-07 22:00] ingest | Shipping & Carriers System
- Created: `modules/shipping/carrier-system-overview.md`
- Created: `modules/shipping/carrier-configuration.md`
- Created: `modules/shipping/rate-shopping.md`
- Created: `modules/shipping/label-generation.md`
- Created: `modules/shipping/carrier-integrations.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Complete documentation of StorePep's multi-carrier shipping system - the foundation for label generation and fulfillment. Covered adaptor pattern for 43 carriers (46 configurations), parallel rate fetching with service selection, comprehensive label generation flow with multi-format support (PDF, ZPL, PNG), and customs handling for international shipments. Key findings: ShipmentAdaptor factory pattern (shipmentAdaptor.js:48-184), 487-line carrier model with carrier-specific fields, 300+ line addRateInfoToOrder.js for rate shopping, carrier-specific request builders (1800+ lines for FedEx), document stitching for packing slips and commercial invoices, and support for SOAP, REST, OAuth 2.0 authentication across global carriers.

## [2026-04-07 16:00] ingest | Order Management System
- Created: `modules/orders/order-lifecycle.md`
- Created: `modules/orders/order-bulk-actions.md`
- Created: `modules/orders/order-returns.md`
- Created: `modules/orders/order-address-management.md`
- Updated: `index.md`
- Updated: `log.md`
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Comprehensive documentation of order management - the core feature of StorePep. Covered complete order lifecycle (import → process → label → ship → track), 40+ bulk actions for high-volume operations, return label flow with separate tracking, and sophisticated address validation/correction system. Key findings: 2139-line orders route with 69 endpoints, 779-line order model with extensive multi-address support, OrderProcessingService for complex calculations, and event-sourced state transitions.

## [2026-04-07 14:00] bootstrap | Initial Architecture Documentation
- Created: `architecture/overview.md`
- Created: `architecture/frontend-architecture.md`
- Created: `architecture/backend-architecture.md`
- Created: `architecture/technology-stack.md`
- Created: `index.md`
- Created: `log.md` (this file)
- Git reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
- Summary: Initial architecture documentation covering system overview, frontend/backend structure, and complete technology stack. Bootstrap complete - ready for domain-specific ingestion.

## [2026-04-22 14:58] init | Co-Change Coupling Map
- Mode: init (since: 1 year ago)
- Source: `raw/storepep-react` @ `a5405aed`
- Commits analyzed: 599 (22 skipped — >30 files)
- Pairs above threshold (≥3): 5233
- Written: `wiki/architecture/coupling-map.md`
- Summary: Top coupling: featureToggles.json ↔ printSettingsHelperFunctions.js (133×)

## [2026-04-28 01:27] ship | Release MCSL 377
- Release: `wiki/product/releases/mcsl-377.md` (status: shipped, re_shipped_at: 2026-04-28 01:27:16 UTC)
- Cards Ready To Ship: 18
- Cards support-closed: 2
- Cards unsupported partnership: 2
- Cards carrier platform issues: 2
- Cards forced (non-terminal at ship): 5 (1 BUG REPORTED, 1 QA READY, 2 Open, 1 Spill Over)
- Git reference: dfb7ba1ab99a9a1529c4f290b5984244a362c813
- Summary: Re-shipped MCSL 377 with 29 total cards (24 terminal, 5 non-terminal forced through). Updated backlog.md with refreshed summary.

## [2026-05-27 11:30] zendesk-summarize | Delta pull (#392156, #391961)
- Pulled: 2 tickets (392156, 391961) via `scripts/sync-zendesk-by-ids.sh` → `raw/zendesk/other_platforms/`
- Created: `wiki/zendesk/summaries/392156.md` (2 open issues: label-generation, international)
- Created: `wiki/zendesk/summaries/391961.md` (1 open issue: onboarding install blocker)
- Created: `wiki/zendesk/2026-05-27.md` (daily index — ZI-560 → ZI-562)
- Git reference: 67c396dc9cf012c10487eb4cf39e771646ae049b
- Summary: 3 new ZI issues on `other_platforms / woocommerce`. ZI-560 = FedEx customs-value float rounding bug (L3); ZI-561 = FedEx invalid destination postal code (single order, pending customer); ZI-562 = WSS plugin entry "Let's Start Fulfilling" denied to store Admin (L3, full install blocker).

## [2026-05-27 12:00] story-cards | ZI-560, ZI-561, ZI-562
- Created: wiki/product/stories/ZI-560.md, ZI-561.md, ZI-562.md (all validated ✓)
- Pushed to StoryLab:
  - ZI-560 → APR 13-16 (Pain 10) — https://trello.com/c/QEwQokK3
  - ZI-561 → APR 16-18 (Pain 8-9) — https://trello.com/c/msZjZIf7
  - ZI-562 → APR 25-30 (Later)    — https://trello.com/c/MEE76M96
- Git reference: 67c396dc9cf012c10487eb4cf39e771646ae049b
- Summary: 3 WooCommerce cards. ZI-560 = FedEx customs-value float rounding (P10, Label & Document Quality). ZI-561 = FedEx invalid postal code (P8-9, International & Customs, sibling of ZI-560). ZI-562 = WSS "Let's Start Fulfilling" Admin permission deny (P8-9, Onboarding & Retention).

## [2026-05-27 12:15] sl-iteration | release-single ZI-560 → MCSL 380
- Source: ZI-560 on StoryLab (https://trello.com/c/QEwQokK3) — already had MCSL 380 label
- Target lane: SL MCSL 380: Iteration backlog (ph-WIP)
- Mode: 4 (copy single card)
- Duplicate check: passed (23 cards already in lane, no ZI-560 hit)
- Labels mirrored with "SL: " prefix: 5 (Pain 10, Label & Document Quality, WooCommerce, FedEx, MCSL 380)
- ph-WIP card: https://trello.com/c/SxMRyxyy

## [2026-05-27 12:35] sl-iteration | snapshot MCSL 380 (re-run)
- File refreshed: wiki/product/releases/mcsl-380.md
- Board: ph-WIP, lane: SL MCSL 380: Iteration backlog (24 cards)
- State delta vs prior run (10 min earlier): Ready To Ship 11→14 (+3), QA READY 2→1, DEV 1→0, BUG REPORTED 3→2
- git_reference preserved: 55b9e1ad06e4197d6a18fc48fc3460d522536771
- Validation: 1 mismatch (ZI-555 — same Dev-Done + BUG-REPORTED label-precedence quirk as last run; pre-existing script issue, not new)

## [2026-06-03 00:00] ingest | Order Update Scenarios (Functional Business Catalog)
- Created: `wiki/modules/orders/order-update-scenarios.md`
- Updated: `wiki/index.md` (Orders section)
- Sources: storepep-react (webhooks.js, internalOrderWebhook.js, ordersSyncEngine.js, fulfillmentOrderUpdatingListener.js, storePepConstants.js); order-updates microservice (diff engine, versioning, order_lock/shop_lock, SQS/SNS workers); Shopify order-status docs
- Git reference: 67c396dc9cf012c10487eb4cf39e771646ae049b
- Summary: Combined functional catalog of all order-update scenarios — 25 Shopify-initiated (S1-S25), 7 post-fulfilment (P1-P7), 10 MCSL-app-initiated write-back (M1-M10), concurrency (C1-C6), bulk/load (L1-L6), multi-user (U1-U5), error/edge (E1-E6). Documents the change-priority model (30-50 + forced), the MCSL→Shopify echo loop, and the version/diff/lock mechanisms that prevent reprocessing.

## [2026-06-03 00:30] ingest | Order Update QA Scenarios (CSV)
- Created: `wiki/modules/orders/order-update-qa-scenarios.csv` (65 Given/When/Then QA cases)
- Updated: `wiki/modules/orders/order-update-scenarios.md` (added downloadable-CSV section + verification-caveat callout)
- Columns: ID, Section, Scenario, Given, When, Then, DiffPriority, Trigger, Verification, Caveat
- Verification flags: ~20 rows code-Verified (diff def / webhook topics / status constants read this session); remainder Inferred from subagent exploration, flagged draft
- High-priority verify-before-trust rows: U1 (double-fulfilment risk), M6/M8 (write-back + echo), P6/C2 (echo suppression), P1/P3 (no-relabel guarantees)
- Summary: QA spec is behavioral source-of-truth; does NOT track automation status (that stays in features.md) and does NOT touch regression CSV

## [2026-06-03 01:15] query | Order-update QA gap analysis vs regression + bulk fulfilment
- Updated: `wiki/modules/orders/order-update-qa-scenarios.csv` (65→72 rows; added RegressionCoverage + RegressionRef columns; added S26 note, S27 unfulfil, BF1-BF7 bulk fulfilment)
- Updated: `wiki/modules/orders/order-update-scenarios.md` (gap-analysis section, Bulk Fulfilment table, S26/S27)
- Sources read: regression-scenarios.xlsx sheets Order_Update, Orders Grid, Batch Flow; order-diff-definition.json (note absence); features.md
- Key findings:
  - Bulk fulfilment IS well-covered (Orders Grid 45.0/61.0, Batch Flow 11/14/parallel/retry) — NOT a gap; advisor caught that Order_Update sheet alone would have produced false gaps
  - M6/M8 write-back CONFIRMED by regression (Orders Grid 17.0 asserts Shopify/Woo order marked fulfilled) — clears prior caveat
  - order note is NOT a diff-engine field — flows through separate order.note.updating.listener (catalog gap, added S26)
  - Order_Update sheet ~96% manual (only 7.0 AUTO=YES) — automation gap distinct from coverage
  - Tier-1 testable gaps: S5/P5/E2 archive cutoff, S7 auth-expiry, S8 deferred, S10/S11 refund, S15 in-progress, S21 subscription, U1 double-fulfilment, U2 two-operators, BF2 echo storm
- Summary: two-tier gap classification (testable vs N/A-infra); reverse gaps (S26 note, S27 unfulfil) found in regression but missing from catalog

## [2026-06-03 02:30] query | Verify echo/U1/M6/M8 + COD + tracking app + returns
- Cloned + explored: git@bitbucket.org:xadapter-cyd/shopify-tracking-app.git (HEAD 4798bea)
- Read (storepep-react): ordersSyncEngine.js, fulfillmentOrderUpdatingListener.js, shopifyToStorepepOrderMapper.js
- Read (order-updates): OrderComparator.js, DiffSelector.js, OrderUpdateCalculatingService.js
- Updated: order-update-scenarios.md (two→three systems, corrected echo model, §7 Tracking, §8 Returns gap, COD detail) + order-update-qa-scenarios.csv (72→83 rows: +S28 COD-reconfirm, +T1-T8 tracking; corrected M6/M8/U1/P6/C2)
- Verified facts:
  - M6/M8 write-back CONFIRMED in code (syncCurrentStoreOrders loops syncStore per order; bulk = N write-backs)
  - ECHO CORRECTED: shouldApplyUpdate fires when updated_at strictly newer (+ fulfilment-cancellation at equal ts). MCSL fulfilment echo is newer + changes monitored field → NOT suppressed by order-updates (loop broken by MCSL-side idempotency, unverified). Tracking-URL echo: tracking_info not a monitored field → compare() empty → OrderDiffNotDetected. updated_at gate only stops not-newer/duplicate webhooks.
  - U1 CORRECTED: ordersSyncEngine has NO pre-check before syncStore (verified); double-fulfilment depends on untraced upstream order-selection
  - COD: two mechanisms (status+outstanding via isCodCheckEnabled; legacy gateway-name) + Please Reconfirm ambiguity (S28); regression Order_Update 30-32
  - Tracking is a SEPARATE app (shopify-tracking-app) consuming fulfillments/create|update (NOT handled by order-updates); writes back via fulfillmentEventCreate + tracking_info rewrite; status machine INITIAL/IN_TRANSIT/OUT_FOR_DELIVERY/DELIVERED + exceptions
  - RETURNS GAP (verified by grep): NO system subscribes to Shopify returns/* or refunds/* webhooks; tracking app only EXCEPTION_3→FAILURE; MCSL return labels are operator-initiated
- Summary: order updates span THREE systems; echo model corrected; tracking + returns are catalog/coverage blind spots

## [2026-06-03 03:00] query | Shopify Return Management coverage check
- Verified (grep all 3 repos + code-read): Shopify Return Management (returns/* + reverse_* webhooks, returnCreate/ReturnInput GraphQL) is NOT integrated anywhere; order.returns never parsed
- Refunds: only legacy flag-gated path (shopifyToStorepepOrderMapper:285-300) subtracts refunded qty from shippable line items (both partial.fulfilment + orderStatusUpdate must be OFF)
- StorePep returns = operator-initiated carrier RMA reverse labels (carriers.js ReturnLabel/rma; DHL/FedEx/UPS/EasyPost ReturnRequest); separate returnBatchStatus/returnLabel[] data model; order-returns.md
- Updated: order-update-scenarios.md §8 (three-layer table) + CSV (+S29 legacy refund adjust, +S30 Return Management gap) = 85 rows
- Summary: three non-overlapping return/refund worlds; Shopify Return Management is a hard gap

## [2026-06-03 03:40] query | Partial fulfilment scenario completeness
- Read: internalOrderWebhook.js (deriveStorePepStatus), externalFulfilmentEventProcessingListener.js (handlePartialFulfilment), OrderProcessingService.js, ordersSyncEngine.js (isPartiallyAvailable)
- Updated: order-update-scenarios.md (new §9 Partial Fulfilment) + CSV (+PF1-PF12) = 97 rows
- Verified facts:
  - TWO partial-fulfilment paths: diff-driven internalOrderWebhook + externalFulfilmentEventProcessingListener
  - handlePartialFulfilment → OrderProcessingService.process() strips fulfilled items and recomputes totals/discounts/tax/money_set for remaining, re-imports as PARTIALLY_EXTERNALLY_FULFILED
  - RISK PF2: deriveStorePepStatus forces status to INITIAL when partial.fulfilment.enabled is OFF (order looks fully unfulfilled)
  - PF12: cancelled_at precedence over partial (CANCELLED wins)
  - PF5: multi-vendor WCFM isPartiallyAvailable = completedSubOrders != totalSubOrders (ordersSyncEngine:113-126)
  - Inferred/untraced: PF7 partial-then-cancel, PF9 repeated-webhook idempotency, PF11 partial+COD outstanding, plus double-path non-duplication
- Summary: partial fulfilment was under-covered (only S17/M8/P4); now a dedicated 12-row dimension. Two open risks flagged: PF2 forced-INITIAL, and the two-path double-processing question.

## [2026-06-11 15:31] feature-story | Product CSV Export for Large Catalogs
- Created: `wiki/product/features/product-csv-export-large-catalogs.md`
- Updated: `wiki/index.md`
- Git reference: 01898b83a15a8ca9495bf890bcdb47a745792c0d
- Summary: Feature story for ZD #394571 (Biomatik, 78k products) — sync export endpoint is O(n^2) and unbounded, never completes for large catalogs and blocks the imports server event loop. Stories: async export job + notification, streaming linear CSV build, support script `supportScripts/exportProductsToCSV.js` (written, Node v10 compatible), product-count guardrail. Root cause at `routes/products.js:498` / `productsHelperFunctions.js:354`; ops evidence in ops-wiki incident page.
