---
title: Adding a New Carrier - Customer Journey & System Impact
category: guide
status: complete
last_updated: 2026-04-08
git_reference: current
---

# Adding a New Carrier - Customer Journey & System Impact

**Purpose**: Complete guide for adding a new carrier to MCSL from customer perspective
**Audience**: Product managers, developers, QA, customer success
**Last Updated**: 2026-04-08

---

## Executive Summary

Adding a new carrier to MCSL impacts **15+ features** across the platform. The customer journey spans from initial carrier registration through daily shipping operations, tracking, and reporting. This document maps the end-to-end experience, identifies gaps, and provides a rollout checklist.

**Key Statistics**:
- **15+ features** require carrier support
- **7 customer touchpoints** for onboarding alone
- **0% automation coverage** for carrier registration flow
- **~45 test scenarios** needed per carrier

---

## Table of Contents

1. [Associated Features](#associated-features)
2. [Customer Journey Map](#customer-journey-map)
3. [Feature-by-Feature Impact](#feature-by-feature-impact)
4. [Identified Gaps & Issues](#identified-gaps--issues)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Needs](#documentation-needs)
7. [Rollout Strategy](#rollout-strategy)

---

## Associated Features

This section lists all 17 features affected when adding a new carrier to MCSL, organized by priority and showing dependencies.

### 🔴 Core Features (MUST HAVE - Customer-Facing)

These features are directly exposed to customers and critical for basic carrier functionality:

#### 1. **Carrier Configuration**
- **What it does**: Registration and setup of carrier credentials
- **Customer interaction**: Settings → Carriers → Add New Carrier
- **Code impact**:
  - Add carrier constant (`storePepConstants.js`)
  - Extend carrier model schema (487 LOC)
  - Create carrier helper class
  - Add to adaptor pattern
- **Automation**: 0%
- **Test scenarios**: ~15
- **Critical for launch**: YES
- **Related to**: All other carrier features depend on this

---

#### 2. **Rate Shopping**
- **What it does**: Fetch shipping rates from carrier for price comparison
- **Customer interaction**: Order Processing → View rates from all carriers
- **Code impact**:
  - Implement `getRates()` method
  - Add service code mapping (`serviceCodes.js`)
  - Parse carrier rate response
  - Currency conversion (if needed)
- **Automation**: 0%
- **Test scenarios**: ~20
- **Critical for launch**: YES
- **Related to**:
  - Service Selection (cheapest/fastest)
  - Automation Rules (auto-select carrier)
  - Order Processing workflow

---

#### 3. **Label Generation**
- **What it does**: Create shipping labels via carrier API
- **Customer interaction**: Click "Generate Label" → Receive PDF/ZPL label
- **Code impact**:
  - Implement `createShipment()` method (largest effort)
  - Request builder (SOAP/REST/XML)
  - Response parser (label URL, tracking number)
  - Multi-package support
  - Document stitching (packing slip + invoice)
- **Automation**: 100% (for tested carriers), 0% for new
- **Test scenarios**: ~30
- **Critical for launch**: YES
- **Related to**:
  - Packaging Types (which boxes to use)
  - Special Services (insurance, signature)
  - International Shipping (customs)
  - Document Generation (packing slip, invoice)

---

#### 4. **Shipment Tracking**
- **What it does**: Fetch tracking updates from carrier
- **Customer interaction**: View Order → Click tracking number → See status timeline
- **Code impact**:
  - Implement `getTracking()` method
  - **Status mapping** (carrier codes → readable statuses) - 6800+ LOC file
  - Email notification triggers
  - Cron job integration
- **Automation**: 7% (UI only)
- **Test scenarios**: ~25
- **Critical for launch**: YES
- **⚠️ HIGH RISK**: Status mapping is complex and customer-facing
- **Related to**:
  - Email Notifications
  - Cron Jobs (automatic updates)
  - Order Status Updates

---

#### 5. **Service Selection & Automation**
- **What it does**: Automatically select carrier/service based on rules
- **Customer interaction**: Automation Settings → Create Rule → Select new carrier
- **Code impact**: None (uses existing automation engine)
- **Automation**: 100% (engine), 0% (per carrier)
- **Test scenarios**: ~12
- **Critical for launch**: YES (if customer uses automation)
- **Related to**:
  - Rate Shopping (needs rates to select from)
  - Carrier Configuration (carrier must be enabled)
  - Rule Engine

---

#### 6. **Shipment Cancellation**
- **What it does**: Void labels and request refunds
- **Customer interaction**: Order Actions → Cancel Shipment
- **Code impact**: Implement `cancelShipment()` method
- **Automation**: 30%
- **Test scenarios**: ~8
- **Critical for launch**: YES (customers need to fix mistakes)
- **Related to**: Label Generation, Order Status

---

### 🟡 Important Features (SHOULD HAVE - Common Use Cases)

#### 7. **Multi-Package Shipments**
- **What it does**: Handle orders with multiple boxes
- **Customer interaction**: Order with 5 packages → Generate 5 labels
- **Code impact**: Loop in `createShipment()`, master tracking number
- **Automation**: 30%
- **Test scenarios**: ~10
- **Critical for launch**: YES for bulk sellers
- **Related to**: Label Generation, Tracking

---

#### 8. **International Shipping & Customs**
- **What it does**: Generate customs forms for cross-border shipments
- **Customer interaction**: International order → Auto-generate commercial invoice
- **Code impact**:
  - Customs data formatting
  - Commercial invoice generation
  - Harmonization codes
  - Duties/taxes payer selection
- **Automation**: 30%
- **Test scenarios**: ~15
- **Critical for launch**: Depends on customer base
- **Related to**:
  - Label Generation
  - Document Generation
  - Product Management (HS codes)

---

#### 9. **Return Labels**
- **What it does**: Generate prepaid return labels for customers
- **Customer interaction**: Order Actions → Create Return Label → Email to customer
- **Code impact**: Use `createShipment()` with return flag
- **Automation**: 30%
- **Test scenarios**: ~8
- **Critical for launch**: NO, but important for e-commerce
- **Related to**: Label Generation, Email

---

#### 10. **Special Services**
- **What it does**: Add insurance, signature, Saturday delivery, etc.
- **Customer interaction**: Label options → Check "Require Signature"
- **Code impact**:
  - Implement special service flags in request
  - Carrier-specific service codes
  - Price calculation
- **Automation**: 30% (3 services tested)
- **Test scenarios**: ~5 per service (~15 total)
- **Critical for launch**: Depends (insurance usually important)
- **Related to**: Label Generation, Rate Shopping
- **Examples**:
  - Insurance
  - Delivery Confirmation (signature)
  - Adult Signature
  - Saturday Delivery
  - Hold at Location
  - Dangerous Goods

---

### 🟠 Optional Features (NICE TO HAVE - Carrier-Dependent)

#### 11. **Pickup Scheduling**
- **What it does**: Request carrier pickup at warehouse
- **Customer interaction**: Bulk select orders → Request Pickup
- **Code impact**: Implement `createPickup()` method
- **Automation**: 0%
- **Test scenarios**: ~10
- **Critical for launch**: NO (many carriers don't support)
- **Related to**: Order Fulfillment
- **Note**: Not all carriers offer pickup API

---

#### 12. **Manifest / End of Day**
- **What it does**: Generate end-of-day manifest for carrier
- **Customer interaction**: End of Day → Generate Manifest → Submit to carrier
- **Code impact**: Implement `createManifest()` method
- **Automation**: 0%
- **Test scenarios**: ~8
- **Critical for launch**: NO (only required for some carriers like USPS)
- **Related to**: Label Generation, Order Fulfillment

---

#### 13. **Address Validation**
- **What it does**: Validate/correct shipping addresses
- **Customer interaction**: Enter address → MCSL suggests correction
- **Code impact**: Implement `validateAddress()` method
- **Automation**: 0%
- **Test scenarios**: ~10
- **Critical for launch**: NO (only some carriers support)
- **Related to**: Order Processing
- **Carriers supporting**: FedEx, UPS, USPS, EasyPost

---

### 🟢 Supporting Features (Backend/Reporting)

#### 14. **Rate Caching**
- **What it does**: Cache carrier rates to reduce API calls
- **Customer interaction**: Transparent (faster rate fetching)
- **Code impact**: None (automatic)
- **Automation**: 0%
- **Test scenarios**: ~5
- **Critical for launch**: NO (but good for performance)
- **Related to**: Rate Shopping, Performance

---

#### 15. **Error Handling & Logging**
- **What it does**: Map carrier errors to user-friendly messages
- **Customer interaction**: See readable error instead of "ERR_001"
- **Code impact**:
  - Error message dictionary per carrier
  - Logging for debugging
  - Retry logic
- **Automation**: 0%
- **Test scenarios**: ~20
- **Critical for launch**: YES (good UX requires good errors)
- **Related to**: All carrier operations

---

#### 16. **Carrier Performance Reports**
- **What it does**: Show shipping costs and delivery times per carrier
- **Customer interaction**: Reports → Carrier Performance
- **Code impact**: Add carrier to report queries
- **Automation**: 0%
- **Test scenarios**: ~5
- **Critical for launch**: NO
- **Related to**: Analytics, Business Intelligence

---

#### 17. **Carrier Health Monitoring** (Internal)
- **What it does**: Track carrier API uptime and performance
- **Customer interaction**: None (internal monitoring)
- **Code impact**: Add carrier to monitoring dashboard
- **Automation**: 0%
- **Test scenarios**: N/A
- **Critical for launch**: NO (but important for operations)
- **Related to**: DevOps, Monitoring

---

### Feature Dependency Map

```
Carrier Configuration (MUST setup first)
    ↓
    ├─→ Rate Shopping (fetch prices)
    │       ↓
    │       └─→ Service Selection (choose cheapest/fastest)
    │               ↓
    │               └─→ Automation Rules (auto-assign)
    │
    ├─→ Label Generation (core feature)
    │       ├─→ Multi-Package
    │       ├─→ International/Customs
    │       ├─→ Return Labels
    │       ├─→ Special Services (insurance, signature)
    │       ├─→ Document Generation (packing slip, invoice)
    │       └─→ Packaging Types (box selection)
    │
    ├─→ Tracking (after label created)
    │       ├─→ Status Mapping (carrier codes → readable)
    │       ├─→ Email Notifications
    │       └─→ Cron Jobs (auto-update)
    │
    ├─→ Shipment Cancellation (void labels)
    │
    ├─→ Pickup Scheduling (optional)
    │
    ├─→ Manifest/EOD (optional)
    │
    ├─→ Address Validation (optional)
    │
    └─→ Reports & Analytics
            └─→ Carrier Performance
```

---

### Feature Priority Matrix

| Priority | Features | Count | Total Scenarios | Current Automation |
|----------|----------|-------|-----------------|-------------------|
| 🔴 **Critical** (Must Have) | Carrier Config, Rate Shopping, Label Gen, Tracking, Service Selection, Cancellation | 6 | ~115 | 18% |
| 🟡 **High** (Should Have) | Multi-Package, International, Return Labels, Special Services | 4 | ~48 | 30% |
| 🟠 **Medium** (Nice to Have) | Pickup, Manifest, Address Validation | 3 | ~28 | 0% |
| 🟢 **Low** (Supporting) | Rate Caching, Error Handling, Reports, Monitoring | 4 | ~40 | 0% |
| **TOTAL** | | **17** | **~231** | **11.4%** |

---

### Testing Priority by Feature

**Minimum Viable Feature Set** for carrier launch:

#### Must Test (Before Launch)
1. ✅ Carrier Configuration - credentials work
2. ✅ Rate Shopping - can fetch rates
3. ✅ Label Generation - can create labels
4. ✅ Tracking - status updates work
5. ✅ Error Handling - errors are readable

#### Should Test (High Volume Features)
6. ✅ Multi-Package - common for bulk orders
7. ✅ International - if global customers
8. ✅ Special Services - insurance at minimum
9. ✅ Cancellation - customers need to fix mistakes

#### Can Test Later (Optional)
10. ⏸️ Pickup - if carrier supports
11. ⏸️ Manifest - if carrier requires
12. ⏸️ Return Labels - common but not critical
13. ⏸️ Address Validation - nice to have

---

### Feature Implementation Complexity

**By Effort (Person-Hours)**:

| Feature | Complexity | Estimated Hours | Dependencies |
|---------|-----------|-----------------|--------------|
| Carrier Configuration | 🟡 Medium | 8-12h | None |
| Rate Shopping | 🟡 Medium | 12-16h | Config |
| Label Generation | 🔴 High | 40-60h | Config, Rate Shopping |
| Tracking + Status Mapping | 🔴 High | 20-30h | Label Generation |
| Multi-Package | 🟡 Medium | 8-12h | Label Generation |
| International/Customs | 🔴 High | 16-24h | Label Generation |
| Special Services | 🟡 Medium | 4-8h per service | Label Generation |
| Pickup | 🟠 Low-Med | 8-12h | Label Generation |
| Manifest | 🟠 Low-Med | 8-12h | Label Generation |
| Error Handling | 🟡 Medium | 12-16h | All features |
| **TOTAL (Complete)** | | **136-212h** | |
| **TOTAL (Minimum Viable)** | | **80-118h** | |

**Minimum Viable = Config + Rate + Label + Tracking + Errors**

---

## Customer Journey Map

### Phase 1: Discovery & Registration (Pre-Onboarding)

#### 1.1 Customer Discovers New Carrier Available

**Customer Question**: "Does MCSL support [CarrierName]?"

**Current Experience**:
- Check website/documentation
- Contact support/sales
- No self-serve carrier availability lookup

**🔴 Gap**: No public-facing carrier availability page showing:
- All supported carriers
- Regional availability
- Feature support matrix (tracking, insurance, etc.)
- Setup difficulty (API credentials, OAuth, etc.)

**Customer Pain Point**: Customers don't know if their preferred carrier is supported until they sign up or ask support.

**Recommendation**: Create public carrier directory at `/carriers` with:
- Carrier logos
- Regional flags
- Feature checkmarks (tracking ✅, pickup ✅, COD ✅)
- "Request Carrier" button for unsupported carriers

---

#### 1.2 Customer Obtains Carrier Account Credentials

**Before MCSL Setup**, customer must:
1. Create account with carrier (FedEx, UPS, etc.)
2. Obtain API credentials from carrier
3. Understand authentication method (API Key, OAuth, SOAP)

**Customer Confusion Points**:
- **"What credentials do I need?"** - Different per carrier
  - FedEx: API Key, Password, Account Number, Meter Number
  - UPS: Username, Password, Access License Key (or OAuth Client ID/Secret)
  - USPS: Just User ID (simple) vs Stamps.com Integration ID + Username + Password (complex)

- **"Test vs Production credentials?"** - Not always clear which environment they're in

**🟡 Gap**: No carrier-specific setup guides within MCSL showing:
- Step-by-step carrier account creation
- Screenshot walkthrough of where to find credentials
- Test vs production credential differences
- Common errors and resolutions

**Recommendation**: Create in-app carrier setup wizards with:
- Carrier-specific instructions
- Screenshots of carrier's developer portal
- Credential validation before saving
- Test API call with instant feedback

---

### Phase 2: Carrier Onboarding in MCSL

#### 2.1 Navigate to Carrier Configuration

**Customer Action**: Settings → Carriers → Add New Carrier

**Current Experience**:
- Dropdown list of 43+ carriers
- No search functionality if list is long
- No carrier logos/icons for visual identification
- No indication of setup complexity

**🟠 UX Issue**: Carriers listed by technical name, not customer-friendly name
- Example: Customer wants "FedEx" but sees "FedEx (SOAP)", "FedEx REST", "FedEx Same Day City"
- Confusing which one to choose

**Recommendation**:
- Add search/filter to carrier dropdown
- Show carrier logos
- Add difficulty badge: 🟢 Easy | 🟡 Moderate | 🔴 Complex
- Show recommended version (e.g., "FedEx REST (Recommended)" vs "FedEx SOAP (Legacy)")

---

#### 2.2 Enter Carrier Credentials

**Customer Action**: Fill out carrier-specific form with credentials

**Current Experience**:
- Form fields dynamically shown based on carrier selection
- Field labels are technical (e.g., "Meter Number", "Access License Key")
- No inline help text explaining what each field is
- No validation until form submission

**🔴 Critical Gap**: **No credential validation before saving**

**Customer Pain Points**:
1. **Typo in credentials** - Not discovered until first label generation fails
2. **Wrong environment** - Production credentials in test mode (or vice versa)
3. **Insufficient permissions** - API key lacks required permissions (e.g., can't create shipments, only fetch rates)
4. **Expired credentials** - OAuth tokens expired
5. **Account not activated** - Carrier account pending approval

**Recommendation**:
- **Real-time validation** as customer types (e.g., format validation)
- **Test Connection** button that:
  - Calls lightweight carrier API (e.g., address validation)
  - Shows: ✅ "Credentials valid (Production mode)" or ❌ "Authentication failed: Invalid API key"
  - Checks permissions: "✅ Can fetch rates, ✅ Can create shipments, ❌ Cannot schedule pickups"
- **Field-level help** with tooltips/popovers:
  - "Meter Number: Find this in your FedEx Developer Portal under 'API Credentials'"
  - Link to carrier's credential page

---

#### 2.3 Configure Carrier Settings

**Customer Action**: Set preferences (label format, pickup times, etc.)

**Fields to Configure** (varies by carrier):
- Label print size (4x6 thermal, 8.5x11 letter)
- Invoice type (commercial invoice template)
- Pickup times (warehouse open/close hours)
- Default services to show
- Negotiated rates enabled (if applicable)
- Special services preferences

**Current Experience**:
- Long form with 20-50 fields depending on carrier
- No defaults pre-filled
- No explanation of what each setting does
- All fields shown at once (overwhelming)

**🟠 UX Issue**: Cognitive overload for new users

**Recommendation**:
- **Wizard approach** with steps:
  1. Basic (credentials, account name)
  2. Label Preferences (format, printer type)
  3. Operational Settings (pickup times, warehouse)
  4. Advanced (special services, negotiated rates)
- **Smart defaults** based on common configurations
- **Progressive disclosure**: Hide advanced settings behind "Advanced Options" toggle
- **Field grouping** with clear sections

---

#### 2.4 Save & Validate

**Customer Action**: Click "Save Carrier"

**Current Behavior**:
- Saves to database
- Shows success message
- **No test API call made**

**What Happens Next**:
- Customer proceeds to create first label
- **First label generation fails** with cryptic error
- Customer confused: "I saved the carrier, why doesn't it work?"

**🔴 Critical Gap**: **No post-save validation**

**Recommendation**:
- **Immediate test after save**:
  - "Carrier saved! Testing connection..."
  - Call carrier API with sample request
  - Show result: ✅ "Test successful - ready to generate labels" or ❌ "Error: [specific message]"
- **Save draft** option for incomplete configurations
- **Validation checklist** showing:
  - ✅ Credentials valid
  - ✅ Can fetch rates
  - ✅ Can create shipment
  - ⚠️ Pickup not configured (optional)

---

### Phase 3: Daily Shipping Operations

#### 3.1 Rate Shopping

**Customer Action**: Order moves to Processing → MCSL fetches rates from all carriers

**Current Experience**:
- Rates fetched from all enabled carriers in parallel
- New carrier's rates appear in dropdown
- Customer sees: "FedEx Ground: $12.50 (5 days)"

**Potential Issues**:
1. **New carrier returns no rates** - Why?
   - Address not serviceable
   - Package exceeds limits
   - Service not available for origin/destination
2. **New carrier rates higher than expected** - Why?
   - Using list rates instead of negotiated rates
   - Missing discount configuration
3. **New carrier slow to respond** - Why?
   - API timeout too long
   - Carrier's API is slow

**🟡 Gap**: **No visibility into rate fetch failures**

**Current Behavior**: If carrier returns no rates, it's silently excluded from dropdown

**Customer Experience**: "Why don't I see [NewCarrier] in the rate list?"

**Recommendation**:
- **Show all carriers** in rate list, even if no rates
- **Indicate failure**: "NewCarrier: ⚠️ No rates available (Address not serviceable)"
- **Hover for details**: Tooltip showing carrier's error message
- **Retry button**: Allow customer to retry rate fetch
- **Rate fetch audit log**: Show all attempted carriers with status

---

#### 3.2 Label Generation

**Customer Action**: Select carrier/service → Click "Generate Label"

**Current Experience**:
- API call to new carrier
- Label URL returned
- Label displayed in MCSL

**Potential Issues**:
1. **Label format not supported** - Carrier returns ZPL but customer needs PDF
2. **Customs form missing** - International shipment, carrier didn't generate commercial invoice
3. **Special service not applied** - Customer requested signature, not on label
4. **Wrong label size** - Label  is 8.5x11 but customer configured 4x6
5. **Label image corrupted** - PDF won't open
6. **Tracking number missing** - Carrier didn't return tracking number

**🔴 Critical Gaps**:
- **No label preview before final generation** (for test mode)
- **No label format conversion** (ZPL → PDF conversion)
- **No document stitching validation** (is packing slip attached correctly?)

**Customer Pain Points**:
- "I generated the label but it's the wrong format for my printer"
- "The label generated but there's no tracking number"
- "International shipment but no customs form"

**Recommendation**:
- **Label preview** in test mode:
  - Generate sample label with test credentials
  - Show preview before final generation
  - Allow format selection override
- **Format validation**:
  - Check carrier's returned format matches configuration
  - Auto-convert if possible (ZPL → PDF via library)
  - Warn if mismatch: "Carrier returned ZPL but you configured PDF. Print anyway or change settings?"
- **Document checklist**:
  - ✅ Shipping label
  - ✅ Packing slip
  - ✅ Commercial invoice (international only)
  - ⚠️ Return label (not requested)

---

#### 3.3 Tracking

**Customer Action**: View order → Check tracking status

**Current Experience**:
- Tracking number displayed
- Click "Track" → Fetches from carrier API
- Shows tracking events timeline

**Potential Issues**:
1. **Tracking not working** - Carrier API not returning data
2. **Status mapping incorrect** - Carrier says "Out for Delivery" but MCSL shows "In Transit"
3. **Tracking delayed** - Carrier hasn't scanned package yet
4. **No tracking available** - Carrier doesn't support tracking for this service

**🟠 Gap**: **No tracking status mapping for new carrier**

**Current Behavior**:
- Tracking status mapper (`storepepMappedTrackingStatus.js`) has 6800+ lines
- New carrier's status codes not mapped
- Shows raw carrier codes to customer: "03" instead of "Out for Delivery"

**Customer Pain Point**: "The tracking shows weird codes instead of status"

**Recommendation**:
- **Status mapping requirement** for all new carriers:
  - Map carrier codes to StorePep standard statuses
  - Map attention types (1-6 levels)
  - Map delivery status (delivered, exception, in transit)
- **Fallback to carrier website** if mapping incomplete:
  - "View on [Carrier] website" link
- **Test tracking** during carrier onboarding:
  - Generate test label
  - Wait for first scan
  - Verify status appears correctly

---

#### 3.4 Pickup Scheduling

**Customer Action**: Bulk select orders → Request Pickup

**Current Experience**:
- Calls carrier's pickup API
- Schedules pickup for selected orders
- Returns confirmation number

**Potential Issues**:
1. **Carrier doesn't support pickup API** - Feature not available
2. **Pickup times conflict** - Carrier can't pickup at customer's preferred time
3. **Pickup fails silently** - API call failed but no user notification

**🔴 Gap**: **No carrier feature detection**

**Customer Pain Point**: "I don't see a pickup button for [NewCarrier]"

**Recommendation**:
- **Feature support matrix** in carrier configuration:
  - ✅ Rate Shopping
  - ✅ Label Generation
  - ✅ Tracking
  - ❌ Pickup Scheduling (not supported)
  - ❌ Manifest/End of Day (not supported)
- **Disable unavailable features** in UI with tooltip:
  - "Pickup not available for this carrier. Contact carrier directly."
- **Alternative workflow** suggestion:
  - "Schedule pickup on [Carrier] website"
  - Link to carrier's pickup page

---

#### 3.5 Manifest / End of Day

**Customer Action**: End of day → Generate manifest

**Current Experience**:
- Generates manifest document
- Uploads to carrier
- Downloads PDF for printing

**Potential Issues**:
1. **Carrier doesn't support manifest** - Not all carriers require end-of-day manifest
2. **Manifest format incorrect** - Carrier rejected manifest
3. **Orders missing from manifest** - Some orders not included

**🟡 Gap**: **No validation of which carriers require manifest**

**Recommendation**:
- **Manifest requirement flag** on carrier:
  - Required (USPS, FedEx for certain services)
  - Optional (UPS)
  - Not Supported (many regional carriers)
- **Auto-generate manifest** at configured time (e.g., 5 PM daily)
- **Manifest preview** before final submission

---

### Phase 4: Automation Rules

#### 4.1 Configure Automation Rule with New Carrier

**Customer Action**: Automation → Create Rule → Set Action "Use [NewCarrier]"

**Current Experience**:
- Carrier appears in dropdown
- Customer selects carrier and service
- Automation runs, assigns new carrier to matching orders

**Potential Issues**:
1. **Service codes not mapped** - Automation sets carrier but service code is wrong
2. **Fallback not working** - Primary carrier unavailable, no fallback configured
3. **Special services not supported** - Automation tries to add signature but new carrier doesn't support it

**🟠 Gap**: **No automation dry-run mode**

**Customer Pain Point**: "I set up automation for [NewCarrier] but it's not working. I don't know why."

**Recommendation**:
- **Test automation** button:
  - Run automation on sample order
  - Show what would happen without applying
  - "This rule would set: NewCarrier - Express Service ($25.00)"
- **Validate service codes** when creating automation:
  - Check if service code exists for carrier
  - Warn if deprecated service
- **Automation audit log** showing:
  - Which rules matched
  - Which carrier was selected
  - Why (condition matched)

---

### Phase 5: Reporting & Analytics

#### 5.1 Carrier Performance Reports

**Customer Action**: Reports → Carrier Performance

**Current Experience**:
- Shows shipping volume per carrier
- Average cost per carrier
- Delivery time analysis

**Potential Issues**:
1. **New carrier not in reports** - Data exists but not shown in dropdown
2. **Carrier name inconsistent** - Shows "C50" instead of "NewCarrier"
3. **No data for new carrier** - Just added, no historical data

**🟠 Gap**: **No carrier onboarding date tracked**

**Customer Pain Point**: "Why doesn't [NewCarrier] show in my reports?"

**Recommendation**:
- **Include carrier in reports immediately** after setup
- **Show "No data yet"** if no shipments
- **Carrier metadata** in reports:
  - Date added
  - Total shipments
  - Last used date
- **Carrier comparison** feature:
  - Compare NewCarrier vs existing carriers
  - Cost analysis
  - Delivery time comparison

---

## Feature-by-Feature Impact

Complete checklist of all features affected when adding a new carrier.

### 1. Carrier Configuration ⚠️ **0% Automated**

**Customer Touchpoints**:
- Carrier dropdown selection
- Credential input form
- Settings configuration
- Save & validate

**Code Changes Needed**:
1. Add carrier code constant to `storePepConstants.js`
2. Create carrier helper class in `server/src/shared/API/carriers/[carrierName]/`
3. Add carrier to `ShipmentAdaptor.getShipmentCreatorBasedOnCarrier()`
4. Add carrier-specific fields to `carriers.js` model (487 LOC schema)
5. Add service codes to `serviceCodes.js` (1500+ LOC file)

**Testing Gaps**:
- 🔴 No automated tests for carrier registration flow
- 🔴 No credential validation tests
- 🔴 No OAuth flow tests

**Estimated Scenarios**: ~15
- Happy path: valid credentials
- Invalid credentials (wrong API key, expired token)
- Test vs production mode
- Partial permissions (can fetch rates but not create shipments)
- Network timeout
- Carrier API down

---

### 2. Rate Shopping ✅ **Core Feature**

**Customer Experience**:
- New carrier rates appear in rate dropdown
- Rates fetched in parallel with other carriers
- Can select new carrier's service

**Code Changes Needed**:
1. Implement `getRates()` method in carrier helper
2. Add rate response parsing logic
3. Add service name mapping
4. Add currency conversion support (if non-USD)

**Testing Gaps**:
- 🔴 **0% automated** for rate shopping
- 🔴 No parallel rate fetch tests
- 🔴 No service selection tests
- 🔴 No currency conversion tests

**Estimated Scenarios**: ~20
- Successful rate fetch
- No rates available (address not serviceable)
- Partial rates (only some services available)
- Rate timeout
- Invalid request (weight exceeds limit)
- Currency conversion (non-USD)
- Negotiated rates vs list rates

**Critical for Launch**: YES - Customers need to see rates before choosing carrier

---

### 3. Label Generation ✅ **Core Feature**

**Customer Experience**:
- Click "Generate Label"
- Label appears (PDF/ZPL/PNG)
- Tracking number assigned
- Packing slip attached (if configured)
- Commercial invoice generated (international)

**Code Changes Needed**:
1. Implement `createShipment()` method in carrier helper
2. Add request builder for carrier's API format (SOAP/REST/XML)
3. Add response parser (extract label URL, tracking number, documents)
4. Add multi-package support
5. Add customs data formatting (international)
6. Add special services support (signature, insurance, etc.)
7. Add document stitching (label + packing slip + invoice)

**Testing Gaps**:
- 🟢 **100% automated** for tested carriers (FedEx, UPS via EasyPost)
- 🔴 **0% automated** for new carriers until tests added

**Estimated Scenarios**: ~30
- Domestic single package
- Domestic multi-package
- International single package (customs required)
- International multi-package
- Different label formats (PDF, ZPL, PNG)
- Special services (signature, insurance, Saturday delivery)
- Return label
- Different package types (letter, parcel, freight)
- Carrier box selection (FedEx One Rate, UPS boxes)
- Document stitching (packing slip, commercial invoice)

**Critical for Launch**: YES - Core functionality

---

### 4. Shipment Tracking ⚠️ **Critical Gap**

**Customer Experience**:
- View tracking status in order details
- Tracking timeline shows events
- Email notifications on status change
- Tracking page updates automatically (cron job)

**Code Changes Needed**:
1. Implement `getTracking()` method in carrier helper
2. Add tracking response parsing
3. **Add status mapping** to `storepepMappedTrackingStatus.js` (6800+ LOC):
   - Map carrier status codes to StorePep standard statuses
   - Map attention types (1-6 levels)
   - Map delivery status
4. Add tracking to cron job schedule
5. Add email notification triggers

**Testing Gaps**:
- 🔴 **7% automated** (1 UI test only)
- 🔴 No tracking engine tests
- 🔴 No carrier API integration tests
- 🔴 No email notification tests
- 🔴 No cron job tests

**Estimated Scenarios**: ~25
- Successful tracking fetch
- No tracking available yet (too early)
- Delivered status
- Out for delivery
- Exception (delivery attempted, customer not home)
- Returned to sender
- In transit (multiple scans)
- Delayed shipment
- Lost package
- Status mapping (carrier codes → StorePep statuses)

**Critical for Launch**: YES - Customers expect tracking

**⚠️ HIGH RISK**: Tracking status mapping is complex and error-prone. Incorrect mapping causes customer confusion.

---

### 5. Pickup Scheduling 🟡 **Optional Feature**

**Customer Experience**:
- Bulk select orders
- Click "Request Pickup"
- Select pickup date/time
- Receive confirmation number

**Code Changes Needed**:
1. Implement `createPickup()` method in carrier helper
2. Add pickup request builder
3. Add pickup response parser (confirmation number)

**Testing Gaps**:
- 🔴 No pickup tests exist

**Estimated Scenarios**: ~10
- Successful pickup scheduling
- No pickup available (carrier doesn't support)
- Pickup time conflict
- Same-day pickup vs next-day
- Pickup cancellation

**Critical for Launch**: NO - Nice to have, many carriers don't support automated pickup

---

### 6. Manifest / End of Day 🟡 **Carrier-Specific**

**Customer Experience**:
- Generate manifest at end of day
- Download manifest PDF
- Submit to carrier

**Code Changes Needed**:
1. Implement `createManifest()` method in carrier helper (if carrier requires)
2. Add manifest request builder
3. Add manifest response parser

**Testing Gaps**:
- 🔴 No manifest tests exist

**Estimated Scenarios**: ~8
- Generate manifest successfully
- Manifest with multiple shipments
- Manifest for single shipment
- Manifest rejection (invalid data)
- Carrier doesn't require manifest

**Critical for Launch**: NO - Only required for certain carriers (USPS, Canada Post)

---

### 7. Address Validation 🟡 **Nice to Have**

**Customer Experience**:
- Enter shipping address
- MCSL validates/corrects address
- Suggests corrections

**Code Changes Needed**:
1. Implement `validateAddress()` method in carrier helper
2. Add address validation request
3. Add address correction parsing

**Testing Gaps**:
- 🔴 No address validation tests exist

**Estimated Scenarios**: ~10
- Valid address
- Invalid address (no suggestion)
- Address suggestion available
- Multiple suggestions
- Apartment/suite missing

**Critical for Launch**: NO - Only some carriers support this (FedEx, UPS, USPS)

---

### 8. Shipment Cancellation 🟡 **Important**

**Customer Experience**:
- Click "Cancel Shipment"
- Label voided
- Refund issued (carrier-dependent)

**Code Changes Needed**:
1. Implement `cancelShipment()` method in carrier helper
2. Add cancellation request
3. Add refund status parsing

**Testing Gaps**:
- 🟡 Partially tested (cancel shipment bulk action exists)
- 🔴 No carrier-specific cancellation tests

**Estimated Scenarios**: ~8
- Successful cancellation
- Cancellation window expired (carrier won't refund)
- Already shipped (can't cancel)
- Partial refund
- No refund available

**Critical for Launch**: YES - Customers need to fix mistakes

---

### 9. Automation Rules ✅ **Important**

**Customer Experience**:
- Create automation rule
- Select new carrier in actions
- Automation assigns new carrier to orders

**Code Changes Needed**:
- None (carrier already in system from configuration step)
- Automation uses existing carrier data

**Testing Gaps**:
- 🟢 **100% automated** for automation engine
- 🔴 **0% automated** for new carrier-specific automation

**Estimated Scenarios**: ~12
- Automation rule with new carrier
- Automation fallback (new carrier unavailable)
- Automation service selection
- Automation with special services
- Automation conflicts (multiple rules)

**Critical for Launch**: YES if customer uses automation (most do)

---

### 10. Return Labels 🟡 **Common Use Case**

**Customer Experience**:
- Create return label
- Email to customer
- Customer prints and ships back

**Code Changes Needed**:
1. Use existing `createShipment()` with return flag
2. Carrier may require different API call

**Testing Gaps**:
- 🟡 Partially tested (return label action exists)
- 🔴 No carrier-specific return label tests

**Estimated Scenarios**: ~8
- Return label generation
- Return label with different service
- Return label email delivery
- Return tracking

**Critical for Launch**: NO - But important for e-commerce customers

---

### 11. Multi-Package Shipments 🟢 **Common**

**Customer Experience**:
- Order with multiple packages
- Generate labels for all packages
- Each package gets tracking number
- Master tracking number (carrier-dependent)

**Code Changes Needed**:
- Implement in `createShipment()` with loop for packages
- Handle master tracking number

**Testing Gaps**:
- 🟡 Partially tested (multi-package label gen exists)
- 🔴 No carrier-specific multi-package tests

**Estimated Scenarios**: ~10
- 2 packages
- 10+ packages
- Master tracking number
- Different services per package (if supported)

**Critical for Launch**: YES - Common for bulk orders

---

### 12. International Shipping 🟢 **Complex**

**Customer Experience**:
- Ship internationally
- Customs form auto-generated
- Commercial invoice attached
- Duties/taxes configured

**Code Changes Needed**:
1. Add customs data formatting in carrier helper
2. Add commercial invoice generation
3. Add harmonization code support
4. Add duties/taxes payer options

**Testing Gaps**:
- 🟡 Partially tested (international label gen exists)
- 🔴 No carrier-specific international tests
- 🔴 No customs form validation

**Estimated Scenarios**: ~15
- International shipment (customs required)
- Duties paid by sender (DDP)
- Duties paid by recipient (DDU)
- Third-party billing
- Restricted destination
- High-value shipment (insurance required)
- Prohibited items

**Critical for Launch**: Depends on customer base (YES for global sellers)

---

### 13. Special Services ⚠️ **Carrier-Specific**

**Customer Experience**:
- Add insurance
- Require signature
- Add Saturday delivery
- Carrier-specific services (hold at location, etc.)

**Code Changes Needed**:
1. Implement special services in `createShipment()` request
2. Add carrier-specific service flags
3. Add service validation (does carrier support this service?)

**Testing Gaps**:
- 🟢 **100% automated** for tested services (insurance, dangerous goods, signature)
- 🔴 **0% automated** for carrier-specific services

**Estimated Scenarios per service**: ~5
- Service applied successfully
- Service not supported for this carrier
- Service not available for destination
- Service cost calculation
- Service on label

**Critical for Launch**: Depends on customer needs (insurance usually important)

---

### 14. Rate Caching 🟢 **Performance**

**Customer Experience**:
- Transparent to customer
- Faster rate fetching on repeat requests

**Code Changes Needed**:
- None (cache system already exists)
- Carrier rates automatically cached

**Testing Gaps**:
- 🔴 No rate caching tests exist

**Estimated Scenarios**: ~5
- Cache hit
- Cache miss
- Cache expiration
- Cache invalidation

**Critical for Launch**: NO - But important for performance

---

### 15. Error Handling & Logging 🔴 **Critical**

**Customer Experience**:
- Clear error messages when things fail
- Ability to retry failed operations
- Support can access error logs

**Code Changes Needed**:
1. Add error mapping (carrier errors → user-friendly messages)
2. Add logging for API requests/responses
3. Add error recovery flows

**Testing Gaps**:
- 🔴 No error handling tests exist

**Estimated Scenarios**: ~20
- Authentication error
- Invalid address
- Package too heavy
- Package too large
- Service not available
- Timeout
- Carrier API down
- Malformed response
- Missing required field
- Rate limit exceeded

**Critical for Launch**: YES - Error handling is critical for good UX

---

## Identified Gaps & Issues

### 🔴 Critical Gaps (Blockers for Launch)

1. **No Carrier Registration Automation** (0% coverage)
   - **Impact**: Every carrier onboarding is manual, error-prone
   - **Risk**: Customers enter wrong credentials, discover during first label
   - **Recommendation**: Add credential validation tests for all carriers

2. **No Tracking Status Mapping** for new carrier
   - **Impact**: Customers see raw carrier codes instead of readable statuses
   - **Risk**: Customer confusion, support tickets
   - **Recommendation**: Require status mapping as part of carrier integration
   - **Effort**: 2-4 hours per carrier (mapping all status codes)

3. **No Post-Save Carrier Validation**
   - **Impact**: Broken carriers saved to database
   - **Risk**: Customers can't generate labels, don't know why
   - **Recommendation**: Add "Test Connection" API call after save

4. **No Error Message Mapping**
   - **Impact**: Customers see technical carrier errors
   - **Risk**: Confusion, support burden
   - **Example**: Carrier returns "ERR_001: INVALID_SHIPPER_ACCOUNT" → Should show "Your carrier account number is invalid. Please check Settings → Carriers."
   - **Recommendation**: Error dictionary per carrier

5. **No Label Format Validation**
   - **Impact**: Customer configures PDF but carrier returns ZPL
   - **Risk**: Label won't print, customer frustrated
   - **Recommendation**: Validate returned format matches configuration

---

### 🟡 High Priority Gaps (Launch Risk)

6. **No Carrier Feature Detection**
   - **Impact**: Customers try to use features carrier doesn't support
   - **Example**: Click "Request Pickup" for carrier without pickup API
   - **Risk**: Confusion, error messages
   - **Recommendation**: Feature support flags on carrier model:
     ```javascript
     {
       supportsRateShopping: true,
       supportsLabelGeneration: true,
       supportsTracking: true,
       supportsPickup: false,  // Hide pickup button
       supportsManifest: false,
       supportsAddressValidation: false
     }
     ```

7. **No Automation Dry-Run**
   - **Impact**: Customers set up automation, don't know if it works
   - **Risk**: Automation silently failing, orders not processed
   - **Recommendation**: "Test Automation" button showing what would happen

8. **No Rate Fetch Audit Trail**
   - **Impact**: Customer doesn't see why carrier returned no rates
   - **Risk**: Think carrier integration is broken
   - **Recommendation**: Show all attempted carriers with status:
     - ✅ FedEx: 3 services, $12.50 - $45.00
     - ❌ NewCarrier: No rates (Address not serviceable)
     - ⏱️ UPS: Timeout

9. **No Tracking Engine Tests** (7% coverage)
   - **Impact**: Tracking bugs not caught before production
   - **Risk**: Customers don't see updated tracking, email notifications fail
   - **Recommendation**: Priority 1 for test automation

10. **No Service Code Validation**
    - **Impact**: Automation sets invalid service code
    - **Risk**: Label generation fails with cryptic error
    - **Recommendation**: Validate service codes when creating automation rules

---

### 🟠 Medium Priority Gaps (UX Improvement)

11. **No Carrier Setup Wizard**
    - **Impact**: Customer overwhelmed by 50-field form
    - **Risk**: Abandoned onboarding
    - **Recommendation**: Multi-step wizard with smart defaults

12. **No Carrier Comparison Tool**
    - **Impact**: Customer doesn't know if new carrier is better
    - **Risk**: Stick with existing carriers, don't try new options
    - **Recommendation**: Reports showing carrier performance comparison

13. **No Label Preview**
    - **Impact**: Customer doesn't know what label looks like until printed
    - **Risk**: Wrong format, wasted labels
    - **Recommendation**: Preview mode in test environment

14. **No Carrier Health Monitoring**
    - **Impact**: Carrier API degraded, customer doesn't know
    - **Risk**: Multiple failed label generations before customer notices
    - **Recommendation**: Carrier status dashboard showing:
      - ✅ FedEx: Operational
      - ⚠️ NewCarrier: Degraded (slow response times)
      - 🔴 UPS: Down

15. **No Bulk Carrier Testing**
    - **Impact**: Can't test carrier with multiple orders at once
    - **Risk**: Find edge cases in production
    - **Recommendation**: Bulk test mode generating sample labels

---

### 🟢 Low Priority Gaps (Nice to Have)

16. **No Carrier Documentation Links**
    - **Impact**: Customer has to search for carrier docs
    - **Recommendation**: Link to carrier API docs from settings

17. **No Carrier Logo/Branding**
    - **Impact**: List of text names, not visual
    - **Recommendation**: Add carrier logos for quick identification

18. **No Carrier Setup Difficulty Indicator**
    - **Impact**: Customer picks complex carrier, gets frustrated
    - **Recommendation**: Show complexity: 🟢 Easy | 🟡 Moderate | 🔴 Complex

19. **No Carrier Onboarding Progress**
    - **Impact**: Customer doesn't know what's left to configure
    - **Recommendation**: Progress bar showing completion %

20. **No Carrier Usage Analytics**
    - **Impact**: Don't know which carriers are popular
    - **Recommendation**: Internal analytics for carrier adoption

---

## Testing Requirements

### Per-Carrier Test Matrix

**Every new carrier needs these tests**:

| Test Category | Scenarios | Priority | Current Coverage |
|---------------|-----------|----------|------------------|
| **Carrier Registration** | 15 scenarios | 🔴 Critical | 0% |
| **Rate Shopping** | 20 scenarios | 🔴 Critical | 0% |
| **Label Generation** | 30 scenarios | 🔴 Critical | 0% (per carrier) |
| **Tracking** | 25 scenarios | 🔴 Critical | 7% |
| **Pickup** | 10 scenarios | 🟡 Medium | 0% |
| **Manifest** | 8 scenarios | 🟡 Medium | 0% |
| **Address Validation** | 10 scenarios | 🟠 Low | 0% |
| **Cancellation** | 8 scenarios | 🟡 Medium | 0% |
| **Automation** | 12 scenarios | 🔴 Critical | 100% (engine), 0% (per carrier) |
| **Special Services** | 5 per service | 🟡 Medium | 30% |
| **International** | 15 scenarios | 🟡 High | 0% (per carrier) |
| **Multi-Package** | 10 scenarios | 🟡 High | 0% (per carrier) |
| **Error Handling** | 20 scenarios | 🔴 Critical | 0% |
| **TOTAL** | **~180 scenarios** per carrier | | **11.4% overall** |

---

### Test Priorities for Launch

**Minimum Viable Tests** (must have before launch):

1. ✅ **Carrier Registration**
   - Valid credentials (production)
   - Valid credentials (test)
   - Invalid credentials
   - Test connection after save

2. ✅ **Rate Shopping**
   - Successful rate fetch
   - No rates available (address error)
   - Timeout handling

3. ✅ **Label Generation**
   - Domestic single package (PDF)
   - Domestic single package (ZPL)
   - Multi-package
   - International with customs
   - Common error scenarios

4. ✅ **Tracking**
   - Fetch tracking successfully
   - Status mapping correct
   - Email notification triggered

5. ✅ **Error Handling**
   - All major error categories mapped to user-friendly messages

**Estimated Test Development Time**: 40-60 hours per carrier for comprehensive suite

---

### Testing Environments

**Needed**:
1. **Carrier Sandbox/Test Environment**
   - Test credentials provided by carrier
   - Ability to generate test labels without charges
   - Tracking simulation

2. **MCSL Test Environment**
   - Isolated from production
   - Test orders and sample data
   - All features enabled

3. **Staging Environment**
   - Production-like setup
   - Final validation before prod deployment

**Current Gap**: Not all carriers provide robust sandbox environments
- Some carriers only have production mode
- Test labels may still cost money
- Tracking may not work in test mode

---

## Documentation Needs

### Customer-Facing Documentation

1. **Carrier Setup Guide** (per carrier)
   - "How to connect [CarrierName] to MCSL"
   - Screenshot walkthrough
   - Where to find credentials
   - Common errors and solutions
   - **Estimated**: 2-3 pages per carrier, 2 hours to write

2. **Carrier Comparison Chart**
   - Which carriers support which features
   - Geographic coverage
   - Special capabilities (COD, hold at location)
   - **Estimated**: 1 page, update for each carrier, 1 hour

3. **Troubleshooting Guide**
   - "Why don't I see rates for [Carrier]?"
   - "Why did label generation fail?"
   - "Why is tracking not updating?"
   - **Estimated**: 5 pages, 4 hours

4. **Feature Support Matrix**
   - Public page showing all carriers and features
   - ✅ = Supported, ❌ = Not supported
   - **Estimated**: 1 page, auto-generated from code, 2 hours

---

### Internal Documentation

5. **Carrier Integration Checklist**
   - Steps to add new carrier
   - Code changes needed
   - Testing requirements
   - **Status**: Exists in wiki (carrier-system-overview.md)
   - **Improvement Needed**: Add testing checklist section

6. **Carrier API Reference**
   - Link to carrier's API docs
   - Authentication method
   - Rate limits
   - Known issues
   - **Estimated**: 1 page per carrier, 1 hour

7. **Status Mapping Guide**
   - How to map carrier status codes
   - StorePep status taxonomy
   - Attention type mapping rules
   - **Estimated**: 2 pages, 2 hours (reusable for all carriers)

---

## Rollout Strategy

### Phase 1: Development & Testing (Pre-Launch)

**Timeline**: 2-4 weeks per carrier

**Steps**:
1. **Week 1: Integration**
   - Implement carrier helper class
   - Add to adaptor pattern
   - Basic rate shopping + label generation

2. **Week 2: Feature Complete**
   - Tracking integration
   - Status mapping
   - Special services
   - Error handling

3. **Week 3: Testing**
   - Internal QA (all scenarios)
   - Staging environment validation
   - Sample label generation

4. **Week 4: Documentation & Beta**
   - Customer setup guide
   - Internal troubleshooting guide
   - Beta test with 2-3 friendly customers

**Go/No-Go Criteria**:
- ✅ All critical tests passing
- ✅ Status mapping complete
- ✅ Error messages user-friendly
- ✅ Documentation complete
- ✅ Beta customers successful

---

### Phase 2: Soft Launch (Limited Availability)

**Timeline**: 2 weeks

**Approach**: **Invite-only** for existing customers

**Steps**:
1. **Announce to subset** of customers (email list)
   - "Try our new [Carrier] integration"
   - Link to setup guide
   - Support priority for early adopters

2. **Monitor closely**:
   - Daily check of carrier error rates
   - Support ticket volume
   - Label generation success rate
   - Tracking update frequency

3. **Collect feedback**:
   - Survey early adopters
   - Setup difficulty
   - Features working well
   - Features needing improvement

4. **Iterate**:
   - Fix reported issues
   - Improve error messages
   - Update documentation

**Success Metrics**:
- <5% error rate on label generation
- >90% positive feedback from early adopters
- <3 support tickets per user

---

### Phase 3: General Availability

**Timeline**: 1 week after soft launch success

**Steps**:
1. **Public announcement**:
   - Blog post: "Now Supporting [Carrier]"
   - Email to all customers
   - Social media announcement

2. **In-app promotion**:
   - Banner in MCSL: "New carrier available: [Carrier]"
   - Tooltip on carrier dropdown: "NEW"

3. **Monitor at scale**:
   - Carrier performance dashboard
   - Error rate tracking
   - Support ticket categorization

4. **Continuous improvement**:
   - Weekly review of metrics
   - Monthly feature enhancements
   - Quarterly carrier relationship review

**Success Metrics**:
- >50 customers onboard carrier in first month
- <3% error rate sustained
- Net Promoter Score >8 for carrier integration

---

### Phase 4: Post-Launch Maintenance

**Ongoing**:
1. **Carrier API monitoring**
   - Uptime tracking
   - Response time tracking
   - Error rate by carrier

2. **Version updates**
   - Carrier API changes
   - New features from carrier
   - Deprecations

3. **Customer success**
   - Onboarding webinars
   - Best practices guides
   - Carrier-specific tips

---

## Launch Checklist

Use this checklist for every new carrier launch:

### Pre-Development
- [ ] Carrier selected based on customer demand
- [ ] Carrier API documentation reviewed
- [ ] Test credentials obtained
- [ ] Sandbox environment access confirmed
- [ ] Complexity estimated (Simple/Moderate/Complex)

### Development
- [ ] Carrier helper class created
- [ ] Added to adaptor pattern
- [ ] Service codes mapped
- [ ] Carrier model schema extended
- [ ] Constants added

**Core Features**:
- [ ] Rate shopping implemented
- [ ] Label generation implemented
- [ ] Multi-package support
- [ ] Tracking implemented
- [ ] Status mapping complete

**Optional Features**:
- [ ] Pickup scheduling (if supported)
- [ ] Manifest generation (if required)
- [ ] Address validation (if supported)
- [ ] Cancellation (if supported)
- [ ] Return labels

**Advanced**:
- [ ] International shipping support
- [ ] Customs form generation
- [ ] Special services support
- [ ] Carrier-specific features

**Error Handling**:
- [ ] All error codes mapped to user-friendly messages
- [ ] Logging comprehensive
- [ ] Retry logic for transient failures

### Testing
- [ ] All critical tests written (rate, label, tracking, errors)
- [ ] All tests passing
- [ ] Manual QA completed
- [ ] Edge cases tested
- [ ] Beta customer testing successful

### Documentation
- [ ] Customer setup guide written
- [ ] Troubleshooting guide updated
- [ ] Carrier comparison chart updated
- [ ] Feature support matrix updated
- [ ] Internal API reference documented

### Launch
- [ ] Soft launch plan confirmed
- [ ] Monitoring dashboard configured
- [ ] Support team trained
- [ ] Announcement drafted
- [ ] Rollback plan documented

### Post-Launch
- [ ] Error rates monitored daily (first week)
- [ ] Customer feedback collected
- [ ] Support tickets reviewed
- [ ] Documentation updated based on feedback
- [ ] Performance optimizations applied

---

## Appendix: Carrier Complexity Examples

### 🟢 Simple Carrier Integration

**Example**: Sendle (C24)

**Why Simple**:
- REST API with JSON
- Straightforward authentication (API Key + Sendle ID)
- Clear documentation
- Standard services (no special cases)
- Good sandbox environment

**Estimated Effort**: 1-2 weeks

---

### 🟡 Moderate Carrier Integration

**Example**: Canada Post (C6)

**Why Moderate**:
- SOAP/XML API (more complex than REST)
- Multiple authentication fields
- Bilingual label support (English/French)
- Service points (FlexDelivery)
- Contract vs non-contract rates
- Special services (proof of age, card for pickup)

**Estimated Effort**: 2-3 weeks

---

### 🔴 Complex Carrier Integration

**Example**: FedEx (C2 SOAP)

**Why Complex**:
- 1800+ LOC helper class
- 50+ carrier-specific fields in model
- Multiple API calls for single label (rate, label, document)
- Complex customs handling
- 50+ service types
- Many special services (dry ice, hold at location, Saturday delivery)
- One Rate packaging (special pricing)
- Freight services
- Complex error codes

**Estimated Effort**: 4-6 weeks

---

## Summary: Customer Journey & Pain Points

| Phase | Customer Goal | Current Pain Points | Recommended Fixes |
|-------|---------------|---------------------|-------------------|
| **Discovery** | Find if carrier is supported | No carrier directory | Public carrier list with feature matrix |
| **Registration** | Get carrier credentials | No guidance on what's needed | Carrier-specific setup wizards |
| **Onboarding** | Add carrier to MCSL | 50-field form, no validation | Multi-step wizard, test connection button |
| **Daily Use - Rates** | See carrier's rates | Silent failures | Show all carriers with status (success/failure) |
| **Daily Use - Labels** | Generate labels | Discover errors late | Label preview, format validation |
| **Daily Use - Tracking** | Track shipments | Raw carrier codes | Complete status mapping required |
| **Automation** | Auto-assign carrier | Don't know if working | Dry-run mode, audit trail |
| **Reporting** | Compare carriers | New carrier not in reports | Immediate inclusion, onboarding date tracking |

**Bottom Line**: Adding a carrier is complex (15+ features, 180+ scenarios) with significant testing gaps (11.4% coverage). Success requires comprehensive planning, testing, and phased rollout.
