---
title: Rate Shopping
category: module
domain: shipping
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Rate Shopping

## Overview

Rate shopping is the process of fetching shipping rates from multiple carriers simultaneously, comparing prices and transit times, and automatically selecting the best service based on configured criteria. This allows merchants to offer competitive shipping rates and provide customers with delivery estimates.

**Location**: `server/src/shared/addRateInfoToOrder.js` (300+ lines)

**Core Flow**: Fetch rates from all enabled carriers → Normalize responses → Apply currency conversion → Select best service → Store in order

## Rate Shopping Flow

### 1. Trigger

Rate shopping triggers when:
- Order transitions to `PROCESSING` status
- User clicks "Refresh Rates" button
- Automation rule executes
- Bulk action: "Refresh Shipping Rates"

### 2. Fetch Enabled Carriers

```javascript
const carriers = await Carriers.find({
  accountUUID: order.accountUUID,
  isActive: true,
  status: constants.IN_USE
});
```

**Filters**:
- Active carriers only (`isActive: true`)
- Account-specific carriers
- Not archived

### 3. Parallel Rate Fetching

**Function**: `getRates(order, packages, carriers, settings)`

**Location**: `addRateInfoToOrder.js:21-44`

```javascript
const promises = order.availableCarrierAndService.map((carrierAndService) => {
  const carrier = carriers[carrierAndService.carrierId];
  const order = getDeepClonedData(orderFromDb);
  const packagesToSend = getDeepClonedData(packages);

  // Set carrier on order
  order.carrierIdSelected = carrier.carrierID;
  order.carrierTypeSelected = carrier.carrierType;

  // Get rates from carrier
  return getRatesBasedOnCarrierType(
    order,
    packagesToSend,
    carrier,
    settings,
    { type: 'ADD_RATES_TO_ORDER' }
  );
});

const ratesResults = await Promise.all(promises);
```

**Parallel Execution**: All carrier API calls execute concurrently for performance.

### 4. Carrier API Calls

**Per Carrier** (`getRatesBasedOnCarrierType`):
1. Get adaptor: `new ShipmentAdapter().getShipmentCreatorBasedOnCarrier(carrierType)`
2. Call helper: `helper.getRates(order, packages, carrier)`
3. Carrier-specific request building
4. API call (SOAP/REST/XML)
5. Response parsing

**Example FedEx**:
```javascript
// Request to FedEx API
<RateRequest>
  <OriginAddress>...</OriginAddress>
  <DestinationAddress>...</DestinationAddress>
  <PackageLineItems>...</PackageLineItems>
</RateRequest>

// Response from FedEx
{
  rates: {
    'FEDEX_GROUND': { rate: 12.50, transitTime: 5 },
    'PRIORITY_OVERNIGHT': { rate: 45.00, transitTime: 1 },
    'FEDEX_2_DAY': { rate: 25.00, transitTime: 2 }
  }
}
```

### 5. Response Normalization

**Function**: `getProcessedRatesArray(availableCarrierAndService, ratesResult, meta)`

**Location**: `addRateInfoToOrder.js:46-132`

Each carrier's response normalized to:
```javascript
{
  carrierId: "uuid",
  carrierName: "FedEx",
  carrierType: "C2",
  selected: false,
  status: constants.SUCCESS,
  services: [
    {
      serviceType: "FEDEX_GROUND",
      serviceName: "FedEx Ground",
      rate: 12.50,
      currency: "USD",
      transitTime: "5 business days",
      transitType: "BUSINESS_DAYS",
      selected: false,
      packagingType: "YOUR_PACKAGING",  // Optional
      isOneRateApplied: false            // FedEx One Rate
    },
    // ... more services
  ]
}
```

### 6. Service Name Mapping

**Function**: `CarrierServiceService.getDefaultAllServiceAndCodesFor(serviceCode, carrierType, ...)`

**Location**: `modules/carrier-services/services`

**Purpose**: Map carrier codes to friendly names

**Examples**:
- `FEDEX_GROUND` → "FedEx Ground"
- `PRIORITY_OVERNIGHT` → "Fedex Priority Overnight"
- `01` (UPS) → "UPS Next Day Air"
- `D` (DHL) → "DHL EXPRESS WORLDWIDE"

**Data Source**: `server/src/shared/serviceCodes.js` (1500+ lines)

### 7. Transit Time Enhancement

**Function**: `getEnhancedTransitDays(transitTime)`

**Input**: Raw transit time from carrier (number or object)

**Output**: Formatted string

**Examples**:
- `5` → "5 business days"
- `{ days: 3, type: 'BUSINESS_DAYS' }` → "3 business days"
- `{ days: 2, type: 'CALENDAR_DAYS' }` → "2 calendar days"

**Buffer Application**: Add `carrier.bufferDaysToTransitTime` to estimate

### 8. Currency Conversion

**Function**: `runRateConversionToStoreMainCurrency(ratesInfo, storeCurrency)`

**Location**: `addRateInfoToOrder.js:157-180`

**Purpose**: Convert all rates to store's currency

**Flow**:
```javascript
for (const rateItem of ratesInfo) {
  for (const serviceName in rateItem.rates) {
    const service = rateItem.rates[serviceName];

    // Convert from carrier currency to store currency
    const convertedRate = await getConvertedRateBasedOnCountry(
      service.currency,     // "USD"
      storeCurrency,        // "CAD"
      service.rate          // 12.50
    );

    service.rate = convertedRate;   // 16.75 (example)
    service.currency = storeCurrency; // "CAD"
  }
}
```

**API**: Uses external currency conversion API or cached exchange rates

### 9. Store Results

**Order Update**:
```javascript
order.availableCarrierAndService = processedRates;
await order.save();
```

**Automation Summary** (for audit):
```javascript
await addStorepepOrderAutomationSummary({
  accountUUID: order.accountUUID,
  orderId: order.orderId,
  automationId: carrier.carrierID,
  automationName: carrier.carrierName,
  status: constants.SUCCESS,
  services: mappedServices,
  xmlObjects: apiRequestResponse  // For debugging
});
```

## Service Selection

**Location**: `server/src/shared/addServiceInfoToOrder.js`

### Selection Modes

**Field**: `order.serviceSelectionMode`

**Values**:
- `CHEAPEST_RATE` (default) - Lowest cost service
- `FASTEST_DELIVERY` - Shortest transit time
- `PREFERRED_CARRIER` - Specific carrier preference

### Cheapest Rate Selection

**Function**: `getCheapestRateSelectedService(availableCarrierAndService)`

**Location**: `addServiceInfoToOrder.js:94-113`

```javascript
let selectedService = {};
let lowestRate = Infinity;

availableCarrierAndService.forEach((carrierAndService) => {
  carrierAndService.services.forEach((service) => {
    if (service.rate > 0 && service.rate < lowestRate) {
      lowestRate = service.rate;
      selectedService = {
        ...service,
        carrierId: carrierAndService.carrierId
      };

      // Mark as selected
      service.selected = true;
      carrierAndService.selected = true;
    }
  });
});

return selectedService;
```

### Priority-Based Selection

**Function**: `getPriorityBasedSelectedService(availableCarrierAndService, priority)`

**Purpose**: Select based on carrier/service priority list

**Use case**: Merchant prefers FedEx over UPS, even if UPS is slightly cheaper

### Carrier Service Selector

**Location**: `server/src/shared/orders/orderServiceSelector/CarrierServiceSelector.js`

**Advanced selection logic**:
- Preferred carrier feature toggle (`isPreferredCarrierSelectEnabled`)
- Service filtering by available features
- Custom selection rules per account

### Update Order with Selected Service

**Function**: `updateOrderAndPackage(order, carrierAndService, carriers, currentUser)`

**Location**: `addServiceInfoToOrder.js:76-92`

**Updates**:

**Order**:
```javascript
{
  carrier: "FedEx - FedEx Ground",
  carrierTypeSelected: "C2",
  carrierIdSelected: "carrier-uuid",
  serviceIdSelected: "FEDEX_GROUND",
  availableCarrierAndService: [...] // Full rate results
}
```

**Packages**:
```javascript
{
  carrierTypeSelected: "C2",
  carrierIdSelected: "carrier-uuid",
  serviceTypeSelected: "FEDEX_GROUND",
  isCarrierSet: true
}
```

## Rate Caching

**Purpose**: Avoid redundant API calls for same origin/destination/weight

**Implementation**: Redis cache with 15-minute TTL

**Cache Key**:
```javascript
const cacheKey = hash([
  order.shipFromAddress.postalCode,
  order.shipping.postcode,
  totalWeight,
  JSON.stringify(dimensions),
  carrierType
]);
```

**Cache Hit**: Return cached rates, skip API call

**Cache Miss**: Call API, store result for 15 minutes

## Error Handling

### Rate Fetch Errors

**Common Errors**:
1. **No rates returned**: Service not available for destination
2. **Authentication failed**: Invalid carrier credentials
3. **Address invalid**: Undeliverable address
4. **Weight/dimension limits**: Exceeds carrier maximums
5. **Timeout**: Carrier API didn't respond

**Error Response Structure**:
```javascript
{
  status: constants.FAILURE,
  error: {
    errorType: storepepErrorEvents.ERROR_FROM_CARRIER,
    carrierErrorMessage: "Destination not serviceable",
    resolution: "Check shipping address or try different carrier"
  }
}
```

### Error Event Publishing

**Event**: `RateFetchUnsuccessfulForCarrier`

**Location**: Referenced in `addRateInfoToOrder.js:95-102`

**Published when**: Carrier rate fetch fails or no matching services found

**Payload**:
```javascript
{
  rule: { services: [...] },
  rateResult: { error: {...} },
  orderId: order.orderId,
  accountUUID: order.accountUUID,
  storeUUID: order.storeUUID,
  source: 'orderProcessing'
}
```

### Partial Success Handling

**Scenario**: 3 of 5 carriers return rates successfully

**Behavior**:
- Store successful rates in `availableCarrierAndService`
- Mark failed carriers with error
- Proceed with service selection from available rates
- User sees warning: "Rates unavailable from DHL (check credentials)"

## Rate Display

### Frontend Display

**Redux State**: `order.availableCarrierAndService[]`

**UI Components**:
- Rate table showing all carriers/services
- Columns: Carrier, Service, Rate, Transit Time
- Highlight cheapest/fastest
- Allow manual override (user can select different service)

### Rate Sorting

**Default sort**: Price (low to high)

**Alternative sorts**:
- Transit time (fast to slow)
- Carrier name (alphabetical)
- User preference (saved carrier priority)

## Special Rate Scenarios

### Negotiated Rates

**Carriers supporting**: UPS, FedEx

**Field**: `carrier.negotiatedRates: true` (UPS)

**Behavior**: Request account-specific discounted rates instead of list rates

### Commercial vs Retail Rates

**USPS**:
- `carrier.commercialPlusRates: true` - Commercial Plus pricing
- Default: Commercial Base pricing
- Retail rates (higher) for counter service

**Canada Post**:
- `carrier.quoteType: COMMERCIAL | COUNTER`

### Account Rates vs List Rates

**FedEx**:
- `carrier.rateRequestType: 'ACCOUNT' | 'LIST'`
- Default: `'LIST'` - publicly available rates
- `'ACCOUNT'` - contracted rates for account

**DHL**:
- `carrier.accountRates: true`

### Contracted Services

**Canada Post**:
- `carrier.serviceType: CONTRACT | NON_CONTRACT`
- Contracted services have better rates

## Rate Modifications

### Apply Markup

**Account Setting**: `shippingSettings.rateMarkup`

**Types**:
- Flat rate: Add $5 to all rates
- Percentage: Add 20% to all rates
- Per-weight: Add $0.50 per pound

**Applied after** rate fetching, before display to customer

### Free Shipping Threshold

**Setting**: `shippingSettings.freeShippingThreshold`

**Example**: Orders over $100 get free shipping

**Implementation**: Rate shown as $0.00, actual carrier rate used for label

### Rate Filtering

**Hide expensive services**: Don't show services >3x cheapest rate

**Hide slow services**: Filter out services with transit >7 days

**Service whitelist**: Only show specific services (e.g., Ground services only)

## Performance Optimizations

### 1. Parallel API Calls

```javascript
const ratesPromises = carriers.map(carrier => getRates(carrier));
await Promise.all(ratesPromises);  // Execute concurrently
```

**Benefit**: Fetch from 5 carriers in ~2 seconds instead of ~10 seconds

### 2. Timeout per Carrier

**Default**: 10 seconds per carrier API call

**Benefit**: Don't wait indefinitely for slow carriers

**Fallback**: Return other carriers' rates even if one times out

### 3. Request Throttling

**Rate limits respected**:
- FedEx: 1000 requests/hour
- UPS: 250 requests/hour (dev key)

**Implementation**: Token bucket algorithm

### 4. Response Caching

**Cache successful responses** for 15 minutes

**Cache failed responses** for 5 minutes (shorter TTL)

## API Endpoints

**Location**: `server/src/routes/orders.js`

| Endpoint | Purpose |
|----------|---------|
| POST `/api/orders/bulk-action` (refreshRates) | Bulk rate refresh |
| POST `/api/orders/:id/refresh-rates` | Single order rate refresh |
| GET `/api/orders/:id/rates` | Get cached rates for order |

## Dependencies

- [Carrier System Overview](./carrier-system-overview.md) - Adaptor pattern for carrier APIs
- [Carrier Configuration](./carrier-configuration.md) - Carrier credentials and settings
- [Order Lifecycle](../orders/order-lifecycle.md) - Rate shopping in PROCESSING state
- [Order Bulk Actions](../orders/order-bulk-actions.md) - Bulk rate refresh

## Referenced By

- Order processing triggers rate shopping
- Automation rules select services based on rates
- Frontend displays rates to merchants

## Configuration

**Account Settings**:
- `serviceSelectionMode`: CHEAPEST_RATE | FASTEST_DELIVERY | PREFERRED_CARRIER
- `rateMarkup`: Flat or percentage markup
- `freeShippingThreshold`: Order total for free shipping
- Rate caching enabled/disabled

**Carrier Settings**:
- `bufferDaysToTransitTime`: Days to add to carrier estimate
- `negotiatedRates`: Use contracted rates (UPS, FedEx)
- `accountRates`: Use account-specific rates (DHL)

## Common Patterns

### Refresh Rates for Order

```javascript
const carriers = await findCarriersWithLean({
  accountUUID: order.accountUUID,
  isActive: true
});

const packages = await findPackagesWithLean({
  subOrderUUID: order.subOrderUUID,
  packageType: constants.PACKAGE_TYPE_STORED_PACKAGE
});

await addRateInfoToOrder([order], {
  currentUser,
  accountUUID,
  vendorUUID,
  userRole
}, socketEventCallback);
```

### Get Cheapest Service

```javascript
const selectedService = getCheapestRateSelectedService(
  order.availableCarrierAndService
);

// Update order with selection
await addServiceInfoToOrder([order], {
  currentUser,
  accountUUID,
  vendorUUID,
  userRole
}, socketEventCallback);
```

### Display Rates to Customer

```javascript
// Frontend
const rates = order.availableCarrierAndService
  .flatMap(carrier => carrier.services)
  .filter(service => service.rate > 0)
  .sort((a, b) => a.rate - b.rate);

// Show in dropdown
rates.forEach(service => {
  console.log(`${service.serviceName}: ${service.currency} ${service.rate} (${service.transitTime})`);
});
```

## Known Issues / Tech Debt

1. **No parallel limit**: All carrier API calls run simultaneously - could overwhelm system with many carriers
2. **Currency conversion delays**: Sequential currency conversions slow down processing
3. **No rate comparison history**: Can't see if rates increased/decreased over time
4. **Limited error recovery**: Failed rate fetch doesn't auto-retry
5. **Service selection rigidity**: Only supports simple cheapest/fastest logic
6. **No rate expiration**: Cached rates don't check if still valid after 15 min

## Related Pages

- [Carrier System Overview](./carrier-system-overview.md)
- [Carrier Configuration](./carrier-configuration.md)
- [Label Generation](./label-generation.md)
- [Carrier Integrations](./carrier-integrations.md)
- [Order Lifecycle](../orders/order-lifecycle.md)
