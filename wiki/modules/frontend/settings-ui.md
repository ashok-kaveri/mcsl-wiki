---
title: Settings UI (Frontend)
category: module
domain: settings
sources: [storepep-react]
status: complete
last_updated: 2026-04-30
git_reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020
---

# Settings UI (Frontend)

## Overview

The settings UI provides comprehensive account configuration across stores, carriers, shipping, automation, users, and general preferences. Organized into logical sections with dedicated forms and workflows, it allows merchants to customize their StorePep experience.

**Main Component**: `client/src/components/pages/settings/settings.js`
**Route Base**: `/home/settings/*`
**Settings Sections**: 12 major sections (stores, carriers, automation, users, shipping, general, etc.)

## Settings Architecture

### Settings Navigation

**Main Settings Page**: Hub with links to all settings sections

**Sections** (from directory structure):
1. **Stores** - E-commerce platform connections
2. **Carriers** - Shipping carrier accounts
3. **Shipper** - Origin address, packaging, shipping zones
4. **Automation** - Automation rules and exceptions
5. **Users** - User management and permissions
6. **General** - Account-wide preferences
7. **Messages** - Email templates and notifications
8. **Tax Settings** - Tax calculation configuration
9. **Frontend Rates** - WooCommerce live rate API
10. **Vendors** - Vendor management (marketplace)
11. **Agreement Policy** - Terms and conditions
12. **Carrier Rename** - Custom carrier display names

### Settings Routes

**Route Pattern**: `/home/settings/<section>/<subsection>`

**Examples**:
- `/home/settings/stores/shopify`
- `/home/settings/carriers/fedex`
- `/home/settings/shipper/originaddress`
- `/home/settings/shipper/packaging`
- `/home/settings/automation`
- `/home/settings/users`
- `/home/settings/frontend-rates/keys`

## Store Settings

**Components**: `client/src/components/form/settings/stores/`

**Main File**: `stores.js` - Store connection manager

**Supported Platforms**:
- Shopify (`shopify.js`)
- WooCommerce (`woocommerce.js`)
- Magento 2 (`magento.js`)
- Magento 1 (`magentoOne.js`)
- BigCommerce (`bigCommerce.js`)
- PrestaShop (`prestashop.js`)
- Amazon India (`amazonIndia.js`)

### Store Connection Flow

**Common Pattern** (OAuth-based: Shopify, BigCommerce):
1. User clicks "Connect Store"
2. OAuth flow initiated
3. User authorizes app on platform
4. OAuth callback with access token
5. Store connected and saved
6. Initial order sync triggered

**API Key Pattern** (WooCommerce, Magento):
1. User enters store URL
2. User generates API keys in platform admin
3. User enters consumer key/secret (WooCommerce) or API token (Magento)
4. StorePep validates credentials
5. Store connected
6. User configures sync preferences

### Store Configuration Components

**Shopify** (`shopify.js`):
- OAuth connection status
- Store name and URL
- Location selection (for multi-location stores)
- Order sync preferences:
  - Sync frequency (hourly, daily, manual)
  - Order statuses to sync
  - Date range for initial sync
- Webhook configuration (automatic)
- Fulfillment settings
- Product sync toggle

**WooCommerce** (`woocommerce.js`):
- Store URL input
- Consumer Key / Secret fields
- Connection test button
- Order sync settings
- Product sync settings
- Weight/dimension unit mapping
- Custom field mapping

**Magento** (`magento.js`, `magentoOne.js`):
- Magento version selector (1.x or 2.x)
- Store URL
- API token/username/password
- REST API vs SOAP API selector
- Attribute mapping (Magento → StorePep)
- Order status mapping
- Product synchronization

**BigCommerce** (`bigCommerce.js`):
- OAuth connection
- Store hash
- Access token management
- Webhook subscriptions
- Order sync rules

### Store Branding

**Component**: `branding.js`

**Features**:
- Custom logo upload
- Brand color selection
- Email template branding
- Packing slip customization
- Tracking page branding

### Webhook Management

**Component**: `webhook.js`

**Purpose**: Configure webhooks for real-time order updates

**Webhook Events**:
- Order created
- Order updated
- Order cancelled
- Product created
- Product updated
- Fulfillment created

**Webhook Configuration**:
- Endpoint URL (auto-generated)
- Secret key (for signature verification)
- Event subscriptions (checkboxes)
- Retry policy
- Status monitoring (success/failure counts)

## Automation Settings

**Components**: `client/src/components/form/settings/automation/`

**Main Component**: `setup.js` - Automation rule management

**Route**: `/home/settings/automation`

### Automation Rule Components

**Automation Table** (`automationTable.js`):
- List of all automation rules
- Enable/Disable toggle per rule
- Priority ordering (drag-and-drop)
- Edit/Delete actions
- Rule execution count

**Add/Edit Automation** (`addOrEditAutomationDetails.js`):
- Multi-step wizard for rule creation
- Step 1: Conditions
- Step 2: Actions
- Step 3: Review and save

### Automation Conditions

**Component**: `automationConditionsManager.js`

**Condition Manager UI**:
- AND/OR logic builder
- Nested condition groups
- Visual condition tree

**Available Conditions** (`AutomationConditions.js`):
- Order value (total, subtotal, shipping cost)
- Order weight (total weight)
- Destination (country, state, zip code)
- Product attributes (SKU, category, tag)
- Order attributes (gift message, customer notes)
- Shipping class
- Store source
- Customer type (new, returning)

**Condition Component** (`AutomationConditions.js`):
- Condition type selector (dropdown)
- Operator selector (equals, not equals, greater than, less than, contains, etc.)
- Value input (text, number, dropdown based on condition type)
- Add/Remove condition buttons

### Automation Actions

**Component**: `automationActionsManager.js`

**Actions Manager UI**:
- Sequential action list
- Add action button
- Reorder actions (priority)
- Action configuration forms

**Available Actions** (`automationActionsCarrierAndServices.js`):
- Set carrier
- Set service level
- Set package dimensions
- Set shipping address
- Apply discount
- Add order tag
- Set signature requirement
- Set insurance value
- Send notification
- Skip automation (manual processing)

**Carrier Selection Action** (`carrierSelection.js`):
- Select carrier from active carriers
- Service level selection
- Special services checkboxes

**Carrier Priority Action** (`carrierPriority.js`):
- Define carrier fallback order
- If carrier 1 fails, try carrier 2, then carrier 3, etc.
- Priority list with drag-and-drop

**Services Based on Carrier** (`servicesBasedOnCarrier.js`):
- Dynamically load service levels when carrier selected
- Service availability based on destination
- Special services per carrier/service combination

### Automation Validation

**Component**: `validateAutomationRules.js`

**Validation Rules**:
- At least one condition required
- At least one action required
- No conflicting actions (e.g., set carrier to FedEx and UPS)
- Condition values valid (zip code format, weight > 0, etc.)
- Carrier/service combinations valid

**Validation Feedback**:
- Real-time field validation
- Form-level validation on submit
- Clear error messages

### Automation Exceptions

**Component**: `addOrEditExceptions.js`

**Purpose**: Define exceptions that override automation rules

**Exception Manager** (`exceptionConditionsManager.js`):
- Exception conditions (similar to rule conditions)
- Exception actions (typically "skip automation")
- Priority (exceptions evaluated before rules)

**Use Cases**:
- Exclude certain customers from automation
- Manual processing for high-value orders
- Skip automation for international orders
- VIP customer handling

### Automation Zones

**Component**: `automationZones.js`

**Purpose**: Geographic zone-based automation

**Features**:
- Define zones (countries, states, zip ranges)
- Per-zone automation rules
- Zone-specific carrier availability

## User Management Settings

**Components**: `client/src/components/form/settings/usersSetup/`

**Main Component**: `usersSetup.js` - User management interface

**Route**: `/home/settings/users`

### User Management Features

**User List** (`usersSetupTable.js`):
- Table of all users in account
- User name, email, role, status
- Last login timestamp
- Edit/Delete actions
- Invite new user button

**User Roles**:
- **Owner** - Full access, billing, user management
- **Admin** - Full operational access, no billing
- **Manager** - Order management, settings (limited)
- **Staff** - Order processing only, read-only settings

**Add/Edit User** (`addOrEditUser.js`):
- Email address input
- Role selector
- Permission checkboxes (granular overrides)
- Invitation email sent on creation

### User Permissions

**Component**: `permissions.js`

**Permission System**:
- Role-based defaults
- Granular permission overrides
- Permission categories: Orders, Products, Settings, Reports, Users

**Permission Component** (`permissionsComponent.js`):
- Checkbox grid: Features × Permissions
- Permissions: View, Create, Edit, Delete
- Features: Orders, Products, Labels, Manifests, Reports, Settings, Users

**Permission Matrix Example**:
```
                View  Create  Edit  Delete
Orders          ✓     ✓       ✓     ✗
Products        ✓     ✗       ✗     ✗
Labels          ✓     ✓       ✗     ✗
Settings        ✓     ✗       ✗     ✗
```

**User List Dialog** (`UserListDialog.js`):
- Modal for selecting users in permission assignment
- Search/filter users
- Bulk permission assignment

## General Settings

**Component**: `client/src/components/form/settings/general/`

**Route**: `/home/settings/general`

**General Settings Include**:

### Account Information
- Account name
- Company name
- Company logo
- Timezone
- Date format preference
- Number format (comma vs period)

### Notification Preferences
- Email notifications (order events, tracking updates, errors)
- SMS notifications (optional)
- Notification frequency (real-time, daily digest, weekly)

### Default Settings
- Default carrier
- Default service level
- Default package dimensions
- Default ship-from address
- Currency

### Advanced Settings
- API rate limiting
- Webhook retry policy
- Order import frequency
- Data retention policy
- Debug mode toggle

## Tax Settings

**Component**: `client/src/components/form/settings/tax-settings/index.js`

**Route**: `/home/settings/tax-settings`

**Tax Configuration**:
- Tax calculation method (origin-based, destination-based)
- Tax provider integration (Avalara, TaxJar, manual)
- Tax exemption rules
- Tax codes per product category
- Nexus configuration (states with tax obligation)

## Frontend Rates Settings

**Components**: `client/src/components/form/settings/frontEndRates/`

**Route**: `/home/settings/frontend-rates`

**Purpose**: Configure live shipping rates for WooCommerce checkout

**Components**:
- `keys.js` - API key management
- `shippingClass.js` - WooCommerce shipping class mapping
- `carriersList.js` - Carriers to display in checkout
- `ratesAPIAutomationContainer.js` - Rate automation rules
- `addOrEditAutomationRules.js` - Rate rule editor

**Features**:
- Generate API keys for WooCommerce plugin
- Map WooCommerce shipping classes to StorePep services
- Configure rate markups/discounts
- Carrier filtering (show only certain carriers in checkout)
- Rate caching configuration

**API Keys** (`keys.js`):
- Generate production API key
- Generate sandbox API key
- Regenerate keys (revokes old keys)
- Usage statistics (API calls per day)

**Shipping Class Mapping** (`shippingClass.js`):
- WooCommerce shipping class list
- StorePep service mapping per class
- Fallback service if primary unavailable

**Rate Automation** (`ratesAPIAutomationContainer.js`):
- Conditional rate display
- Hide carriers based on cart conditions
- Markup/discount rules
- Free shipping thresholds

## Origin Address Settings

**Component**: `client/src/components/form/settings/shipper/originAddress.js`

**Route**: `/home/settings/shipper/originaddress`

**Fields** (Redux Form):
- Company name
- Address line 1
- Address line 2
- City
- State/Province (dropdown)
- Zip/Postal code
- Country (dropdown)
- Phone number
- Email

**Validation**:
- Required fields marked
- Address validation via carrier APIs (optional)
- Phone number format validation
- Email format validation

**Multiple Origin Addresses**:
- Some accounts support multiple warehouses
- Default address selection
- Per-order address override

## Shipping Zones Settings

**Components**:
- `shippingZones.js` - Zone manager
- `addOrEditShippingZone.js` - Zone editor
- `shippingZoneManager.js` - Zone business logic
- `shippingZoneValidator.js` - Zone validation

**Route**: `/home/settings/shipper/shippingzones`

See [Packaging UI](packaging-ui.md#shipping-zones) for details (zones used in packaging and carrier selection).

## Carrier Rename Settings

**Component**: `client/src/components/form/settings/carrier-rename/index.js`

**Route**: `/home/settings/carrier-rename`

**Purpose**: Customize carrier display names in UI

**Use Cases**:
- Rename "FedEx Ground" to "Standard Shipping"
- Rename "FedEx 2Day" to "Express Shipping"
- Hide carrier names, show generic "Economy", "Standard", "Express"
- White-label carrier names

**Configuration**:
- Carrier selector
- Service selector
- Custom display name input
- Preview of renamed services

## Messages Settings

**Component**: `client/src/components/form/settings/messages/`

**Route**: `/home/settings/messages`

**Email Templates**:
- Order confirmation email
- Shipping notification email
- Delivery notification email
- Exception notification email
- Return label email

**Template Editor**:
- Rich text editor (Draft-JS)
- Variable insertion ({{orderNumber}}, {{trackingNumber}}, etc.)
- Preview functionality
- HTML/Plain text toggle
- From name and email configuration

**SMS Templates** (if enabled):
- Similar to email templates
- Character count (SMS limit)
- Variable support

## Vendor Settings

**Component**: `client/src/components/form/settings/vendors/`

**Route**: `/home/settings/vendors`

**Purpose**: Multi-vendor marketplace configuration

**Features**:
- Vendor registration approval
- Vendor-specific shipping rates
- Commission configuration
- Vendor payout settings
- Vendor dashboard access

**Use Cases**:
- Marketplace platforms (multiple sellers)
- Dropshipping workflows
- Consignment inventory

## Agreement Policy Settings

**Component**: `client/src/components/form/settings/agreementPolicy/`

**Route**: `/home/settings/agreement-policy`

**Purpose**: Terms of service and privacy policy management

**Features**:
- Upload terms of service document
- Upload privacy policy document
- Require agreement on signup
- Version tracking (user agrees to v1.2 on date X)
- Notification of policy updates

## Redux State Management

### Settings Reducers

**General Settings Reducer**: `generalSettings` (`client/src/reducers/common.js`)

State shape (inferred):
```javascript
{
  generalSettings: {
    accountName: "Acme Corp",
    timezone: "America/New_York",
    dateFormat: "MM/DD/YYYY",
    currency: "USD",
    // ... other general settings
  }
}
```

**Origin Address Reducer**: `addressDetails` (aliased from `originAddress`, `client/src/reducers/settingsData.js:48-56`)

State shape:
```javascript
{
  addressDetails: {
    companyName: "Acme Corp",
    address1: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001",
    country: "US",
    phone: "555-1234",
    email: "shipping@acme.com"
  }
}
```

**Label Settings Reducer**: `label` (`client/src/reducers/settingsData.js:38-45`)

**Tracking Settings Reducer**: `tracking` (`client/src/reducers/settingsData.js:78-85`)

**Tax Settings Reducer**: Tax settings stored in general settings or separate reducer (not read in detail).

**Vendor Reducer**: `vendorDetails` (`client/src/reducers/common.js`)

### Settings Actions

**File**: `client/src/actions/settingsActions.js:1-433` (433 lines)

**Key Actions** (already documented in [Shipping UI](shipping-ui.md)):
- Carrier management actions
- `shipFromAddressDetails(data)` - Update origin address
- `accountSetupCompleted(data)` - Track setup status
- Packaging actions (see [Packaging UI](packaging-ui.md))

**Additional Actions** (inferred from usage):
- `updateGeneralSettings(data)`
- `updateLabelSettings(data)`
- `updateTrackingSettings(data)`
- `updateTaxSettings(data)`
- `updateUserPermissions(userId, permissions)`
- `addStoreConnection(platform, credentials)`
- `updateAutomationRule(ruleId, rule)`

## UI Patterns

### Settings Form Pattern

**Common Pattern** across all settings sections:

```javascript
// Redux Form configuration
@reduxForm({
  form: 'settingsForm',
  enableReinitialize: true,
  validate: validateSettings,
})
@connect(mapStateToProps, mapDispatchToProps)
class SettingsForm extends Component {
  componentDidMount() {
    this.props.fetchSettings();
  }

  onSubmit = (values) => {
    return this.props.updateSettings(values)
      .then(() => alertSuccess('Settings saved'))
      .catch(() => alertError('Failed to save'));
  };

  render() {
    const { handleSubmit, pristine, submitting } = this.props;
    return (
      <form onSubmit={handleSubmit(this.onSubmit)}>
        <Field name="setting1" component={TextField} label="Setting 1" />
        <Field name="setting2" component={SelectField} label="Setting 2" />
        <Button type="submit" disabled={pristine || submitting}>
          Save Settings
        </Button>
      </form>
    );
  }
}
```

**Features**:
- Redux Form for state management
- Auto-save indicator (pristine flag)
- Validation before submit
- Success/error alerts
- Disable submit during save

### Multi-Step Settings Wizard

**Pattern** (used in automation, carrier OAuth):

```javascript
class SettingsWizard extends Component {
  state = { step: 1 };

  nextStep = () => this.setState({ step: this.state.step + 1 });
  prevStep = () => this.setState({ step: this.state.step - 1 });

  render() {
    const { step } = this.state;
    return (
      <div>
        <Stepper activeStep={step - 1}>
          <Step><StepLabel>Step 1</StepLabel></Step>
          <Step><StepLabel>Step 2</StepLabel></Step>
          <Step><StepLabel>Step 3</StepLabel></Step>
        </Stepper>
        {step === 1 && <Step1Form onNext={this.nextStep} />}
        {step === 2 && <Step2Form onNext={this.nextStep} onBack={this.prevStep} />}
        {step === 3 && <Step3Form onBack={this.prevStep} />}
      </div>
    );
  }
}
```

**Use Cases**:
- Automation rule creation
- Store connection (OAuth)
- Carrier registration (multi-step)
- User onboarding

### Tab-Based Settings

**Pattern** (used in carriers, stores):

```javascript
<Tabs value={activeTab} onChange={this.handleTabChange}>
  <Tab label="General" />
  <Tab label="Advanced" />
  <Tab label="Notifications" />
</Tabs>
{activeTab === 0 && <GeneralSettings />}
{activeTab === 1 && <AdvancedSettings />}
{activeTab === 2 && <NotificationSettings />}
```

**Benefits**:
- Organize complex settings
- Progressive disclosure
- Avoid overwhelming users

## Integration with Backend

### Settings API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/settings/general` | GET/POST | General settings |
| `/api/settings/carrier/*` | POST | Carrier management (see [Shipping UI](shipping-ui.md)) |
| `/api/settings/packaging/*` | GET/POST | Packaging settings (see [Packaging UI](packaging-ui.md)) |
| `/api/settings/origin-address` | GET/POST | Ship-from address |
| `/api/settings/automation/*` | GET/POST/DELETE | Automation rules |
| `/api/settings/users/*` | GET/POST/PUT/DELETE | User management |
| `/api/settings/stores/*` | GET/POST/DELETE | Store connections |
| `/api/settings/tax` | GET/POST | Tax configuration |
| `/api/settings/frontend-rates/*` | GET/POST | Frontend rates API |

### Account Setup Status

**Flow**:
1. User completes initial setup (add carrier, origin address, etc.)
2. Backend calculates `accountSetupStatus` (% complete)
3. Redux action `accountSetupCompleted(status)` dispatched
4. Status stored in Redux: `state.accountSetupStatus`
5. Setup wizard overlay shown if incomplete
6. Redirects to setup steps based on status

**Setup Steps**:
1. Add store connection (20%)
2. Add carrier (40%)
3. Configure origin address (60%)
4. Set packaging preferences (80%)
5. Create first order (100%)

## Dependencies

**Frontend**:
- [Frontend Architecture](../../architecture/frontend-architecture.md) - Redux Form integration
- [Redux Patterns](../../patterns/redux-patterns.md) - Settings state management
- [Access Control](../../patterns/access-control.md) - Permission system

**Related UI Modules**:
- [Shipping UI](shipping-ui.md) - Carrier settings
- [Packaging UI](packaging-ui.md) - Packaging and zones

**Backend**:
- [Automation Overview](../automation/automation-overview.md) - Automation rule engine
- [Platform Connectors](../stores/platform-connectors.md) - Store integration
- [Carrier Configuration](../shipping/carrier-configuration.md) - Carrier management

## Referenced By

- [Shipping UI](shipping-ui.md) - Carrier and origin settings
- [Packaging UI](packaging-ui.md) - Packaging settings
- [Orders UI](orders-ui.md) - Automation and user settings

## Known Issues / Tech Debt

1. **Settings Organization**: 12 sections can be overwhelming, needs better IA
2. **Form Performance**: Large forms with many fields slow on older devices
3. **Validation Inconsistency**: Some forms use client validation, others server-only
4. **Permission Granularity**: Permission matrix complex, could simplify to role templates
5. **Automation UI**: Condition/action builder UX challenging for non-technical users
6. **Store Sync Settings**: Per-store sync settings scattered, should be centralized
7. **Settings Search**: No search functionality across all settings
8. **Settings Export/Import**: No bulk export/import for account migration

## Test Coverage

See [Features](../../features.md) for test coverage of settings workflows.

**Automated E2E Tests** (Playwright):
- Origin address configuration
- Carrier addition and configuration
- Store connection (Shopify, WooCommerce)
- Automation rule creation (basic)
- User addition and permission assignment

**Coverage**: Low-Medium (40-60%) - Core settings tested, complex workflows (automation, advanced carrier config) manual verification.

## Future Enhancements

**Suggested Improvements**:
1. **Settings Wizard**: Guided onboarding for new users
2. **Settings Templates**: Pre-configured settings for common use cases
3. **Settings Versioning**: Track changes, rollback capability
4. **Settings Search**: Global search across all settings sections
5. **Settings Recommendations**: AI suggests optimal settings based on usage
6. **Bulk Operations**: Bulk user import, bulk automation rule creation
7. **Settings Audit Log**: Track who changed what and when
8. **Settings Comparison**: Compare settings between accounts (for multi-account users)
