---
title: Redux Patterns
category: pattern
status: complete
last_updated: 2026-04-30
git_reference: 45dd3176f9dfacf353ecea93fc284c8a07d7c020
sources: [storepep-react]
---

# Redux Patterns

## Overview

StorePep's frontend uses Redux for centralized state management with ~100 action types, 30+ action modules, and 26+ reducers. This document describes the patterns, conventions, and architecture of the Redux implementation.

**Redux Version**: 4.0.1
**Middleware**: Redux Thunk 2.3.0, Redux Form 7.4.2

## Store Configuration

**File**: `client/src/reduxStore.js`

```javascript
import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import rootReducer from './reducers/rootReducers';

const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const store = createStore(
  rootReducer,
  composeEnhancers(applyMiddleware(thunk))
);

export default store;
```

**Middleware**:
- **Redux Thunk** - Enables async actions (API calls)
- **Redux DevTools** - Browser extension for debugging (development only)

## Action Type Constants

**File**: `client/src/actions/types.js:1-100`

All action types centralized in a single constants file following the pattern:

```javascript
export const SET_CURRENT_USER = 'SET_CURRENT_USER';
export const UPDATE_ORIGIN_ADDRESS = 'UPDATE_ORIGIN_ADDRESS';
export const FETCH_ORDERS_REQUEST = 'FETCH_ORDERS_REQUEST';
export const FETCH_ORDERS_SUCCESS = 'FETCH_ORDERS_SUCCESS';
export const FETCH_ORDERS_FAILURE = 'FETCH_ORDERS_FAILURE';
// ... ~100 total action types
```

**Convention**:
- Uppercase snake_case (e.g., `UPDATE_STORED_PACKAGES`)
- Domain-prefixed for clarity (e.g., `ORDER_`, `PRODUCT_`, `CARRIER_`)
- Async actions use REQUEST/SUCCESS/FAILURE suffixes

**Benefits**:
- Single source of truth for action types
- Prevents typos (import from constants)
- Easy to grep for all actions related to a domain

## Action Creator Patterns

### Synchronous Actions

Simple state updates:

```javascript
// File: client/src/actions/settingsActions.js
export function updateOriginAddress(address) {
  return {
    type: 'UPDATE_ORIGIN_ADDRESS',
    payload: address
  };
}
```

### Async Actions (Thunk Pattern)

API calls using Redux Thunk:

```javascript
// File: client/src/actions/ordersActions.js
export const getOrders = (requestObject, url) => async (dispatch) => {
  // Dispatch request started
  dispatch({ type: 'FETCH_ORDERS_REQUEST' });

  try {
    // Make API call
    const response = await axios.post(url || '/api/orders', requestObject);

    // Dispatch success
    dispatch({
      type: 'FETCH_ORDERS_SUCCESS',
      payload: response.data.orders
    });

    return response;
  } catch (error) {
    // Dispatch failure
    dispatch({
      type: 'FETCH_ORDERS_FAILURE',
      payload: error.message
    });

    throw error;
  }
};
```

**Pattern**:
1. Dispatch `REQUEST` action (sets loading state)
2. Make async call (axios, fetch, etc.)
3. On success: Dispatch `SUCCESS` action with payload
4. On failure: Dispatch `FAILURE` action with error
5. Return response for component handling

### Action Creators with Metadata

Adding timestamp or other metadata:

```javascript
// File: client/src/actions/ordersActions.js:23-29
const newAction = (type, payload) => ({
  type,
  payload: {
    createdAt: Date.now(),
    ...payload,
  },
});

// Usage
dispatch(newAction(OrderTypes.RECEIVED_ORDERS, {
  orders: response.data.orders
}));
```

**Use case**: Tracking when actions were dispatched for debugging or cache invalidation.

### Conditional Action Dispatch

Actions that dispatch different types based on state:

```javascript
// File: client/src/actions/ordersActions.js:31-74
export function updateStoredPackagesStore(data) {
  if (data.name === 'generatePackage') {
    return {
      type: 'UPDATE_STORED_PACKAGES_GENERATED',
      payload: data,
    };
  }
  if (data.name === 'createShipment') {
    return {
      type: 'UPDATE_STORED_PACKAGES_CREATESHIPMENT',
      payload: data,
    };
  }
  if (data.name === 'resetShipment') {
    return {
      type: 'DELETE_STOREDPACKAGE',
      payload: data,
    };
  }
  // ... more conditions
}
```

**Pattern**: Single action creator that returns different action types based on input. Simplifies component code but adds complexity to action creator.

**Alternative**: Separate action creators per action type (more verbose, clearer intent).

## Action Organization

### Directory Structure

```
client/src/actions/
├── types.js                    # All action type constants
├── authActions.js              # Authentication actions
├── settingsActions.js          # General settings
├── ordersActions.js            # Orders (top-level)
├── productsActions.js          # Products (top-level)
├── orders/                     # Orders sub-module
│   ├── index.js
│   └── ordersTypes.js          # Order-specific types
├── products/                   # Products sub-module
│   └── index.js
├── packaging/                  # Packaging domain
│   └── index.js
├── manifest/                   # Manifest domain
│   └── index.js
├── labels/                     # Label generation
│   └── index.js
├── workflows/                  # Workflows
│   └── index.js
├── automationRule/             # Automation rules
│   └── index.js
├── carrierServices/            # Carrier services
│   └── index.js
└── ... (30+ total modules)
```

**Convention**:
- Top-level files for simple domains
- Subdirectories for complex domains with multiple action files
- `index.js` exports all actions from subdirectory
- `*Types.js` for domain-specific action type constants (in addition to global `types.js`)

### Action Module Pattern

Complex domains use an index.js that re-exports actions:

```javascript
// File: client/src/actions/orders/index.js
export * from './fetchOrders';
export * from './bulkActions';
export * from './statusChanges';
export * from './packageConfiguration';
```

**Usage**:
```javascript
import { getOrders, processBulkOrders, updateOrderStatus } from '../actions/orders';
```

## Reducer Patterns

### Basic Reducer

**File**: Example pattern from reducers

```javascript
// File: client/src/reducers/orders.js
const initialState = {
  ordersList: [],
  loading: false,
  error: null,
};

export const orders = (state = initialState, action) => {
  switch (action.type) {
    case 'FETCH_ORDERS_REQUEST':
      return {
        ...state,
        loading: true,
        error: null,
      };

    case 'FETCH_ORDERS_SUCCESS':
      return {
        ...state,
        loading: false,
        ordersList: action.payload,
      };

    case 'FETCH_ORDERS_FAILURE':
      return {
        ...state,
        loading: false,
        error: action.payload,
      };

    default:
      return state;
  }
};
```

**Pattern**:
- Define `initialState` object
- Use switch statement on `action.type`
- Return new state object (immutability)
- Always return state for unhandled actions (default case)

### Reducer Composition

**File**: `client/src/reducers/rootReducers.js:55-115`

All reducers combined using `combineReducers`:

```javascript
import { combineReducers } from 'redux';

const appReducer = combineReducers({
  auth: storepepUserReducer,
  storepepTeamAuth: storepepTeamReducer,
  orders: ordersReducer,
  products: productsReducer,
  settings: settingsReducer,
  // ... 26+ reducers
});
```

**Aliasing**: Some reducers are imported with descriptive names and aliased in `combineReducers`:

```javascript
import { originAddress } from './settingsData';

combineReducers({
  addressDetails: originAddress,  // Aliased for clarity
});
```

### Root Reducer with Global Actions

**File**: `client/src/reducers/rootReducers.js:117-129`

Wrapper around `combineReducers` handling global actions:

```javascript
const rootReducer = (state, action) => {
  // Handle global logout - clear all state
  if (action.type === 'USER_LOGOUT') {
    state = undefined;
  }

  // Handle admin clearing user data - preserve admin auth
  if (action.type === 'CLEAR_STOREPEP_USER') {
    const retainedState = {
      storepepTeamAuth: state.storepepTeamAuth,
      form: state.form
    };
    state = undefined;
    state = retainedState;
  }

  return appReducer(state, action);
};

export default rootReducer;
```

**Pattern**: Global state reset actions handled before passing to `combineReducers`. Enables:
- Complete state wipe on logout
- Partial state retention when switching users (admin view)

### Immutable Update Patterns

**Array Operations**:

```javascript
// Add item
return {
  ...state,
  items: [...state.items, newItem]
};

// Update item by ID
return {
  ...state,
  items: state.items.map(item =>
    item.id === action.payload.id
      ? { ...item, ...action.payload.updates }
      : item
  )
};

// Remove item
return {
  ...state,
  items: state.items.filter(item => item.id !== action.payload.id)
};
```

**Object Operations**:

```javascript
// Update nested object
return {
  ...state,
  user: {
    ...state.user,
    settings: {
      ...state.user.settings,
      theme: action.payload
    }
  }
};
```

## Redux Form Integration

**Package**: `redux-form` 7.4.2

### Form Reducer

**File**: `client/src/reducers/rootReducers.js:109`

Redux Form manages form state in a dedicated slice:

```javascript
import { reducer as formReducer } from 'redux-form';

combineReducers({
  form: formReducer,  // All forms managed here
  // ... other reducers
});
```

**State Shape**:
```javascript
{
  form: {
    orderForm: {
      values: { /* form field values */ },
      errors: { /* validation errors */ },
      touched: { /* touched fields */ },
      // ... other form state
    },
    settingsForm: { /* ... */ },
    // ... one key per form
  }
}
```

### Form Component Pattern

```javascript
import { Field, reduxForm } from 'redux-form';

class OrderForm extends Component {
  render() {
    const { handleSubmit, submitting } = this.props;

    return (
      <form onSubmit={handleSubmit(this.onSubmit)}>
        <Field
          name="customerName"
          component={renderTextField}
          label="Customer Name"
          validate={[required]}
        />

        <button type="submit" disabled={submitting}>
          Save Order
        </button>
      </form>
    );
  }

  onSubmit = (values) => {
    return this.props.updateOrder(values);
  };
}

export default reduxForm({
  form: 'orderForm',  // Unique form name
  enableReinitialize: true,
})(OrderForm);
```

**Key Features**:
- Declarative field validation (`validate` prop)
- Async validation (server-side checks)
- Field-level and form-level validation
- Submission handling with loading state
- Form reset and initialization

## Selector Patterns

### Basic Selectors

Simple state access functions:

```javascript
// File: Component using connect
const mapStateToProps = (state) => ({
  orders: state.orders.ordersList,
  loading: state.orders.loading,
  currentUser: state.auth.user,
});
```

### Computed Selectors

Derived state calculations:

```javascript
const mapStateToProps = (state) => {
  const { orders, ordersFilters } = state;

  const filteredOrders = orders.ordersList.filter(order =>
    matchesFilters(order, ordersFilters)
  );

  return {
    orders: filteredOrders,
    totalCount: filteredOrders.length,
  };
};
```

**Performance Note**: Computed selectors recalculate on every state change. For expensive calculations, use memoization libraries like `reselect` (not currently used in StorePep).

### Cross-Slice Selectors

Accessing multiple state slices:

```javascript
const mapStateToProps = (state) => ({
  orders: state.orders.ordersList,
  carriers: state.carrierServices,
  userRole: state.auth.userRole,
  subscriptionTier: state.subscriptionUpgrade.tier,
});
```

## Connect Pattern

### mapStateToProps

Maps Redux state to component props:

```javascript
const mapStateToProps = (state) => ({
  orders: state.orders.ordersList,
  loading: state.orders.loading,
});
```

### mapDispatchToProps (Object Shorthand)

```javascript
import { getOrders, updateOrder } from '../actions/orders';

const mapDispatchToProps = {
  getOrders,
  updateOrder,
};

export default connect(mapStateToProps, mapDispatchToProps)(OrdersPage);
```

**Usage in component**:
```javascript
this.props.getOrders({ status: 'initial' });
```

### mapDispatchToProps (Function Form)

For more control:

```javascript
const mapDispatchToProps = (dispatch) => ({
  fetchOrders: (filters) => dispatch(getOrders(filters)),
  updateAndRefresh: (order) => {
    dispatch(updateOrder(order));
    dispatch(getOrders());  // Chain actions
  },
});
```

## Async Flow Pattern

Standard async action flow:

1. **Component** dispatches action
2. **Action creator** (thunk) dispatches REQUEST action
3. **Reducer** sets `loading: true`
4. **Component** shows loading spinner
5. **Action creator** makes API call
6. **API** responds
7. **Action creator** dispatches SUCCESS/FAILURE action
8. **Reducer** updates state with data or error
9. **Component** re-renders with new state

**Example Flow**:

```javascript
// 1. Component
componentDidMount() {
  this.props.getOrders({ status: 'initial' });
}

// 2. Action creator
export const getOrders = (filters) => async (dispatch) => {
  // 3. Dispatch REQUEST
  dispatch({ type: 'FETCH_ORDERS_REQUEST' });

  try {
    // 5. Make API call
    const response = await axios.post('/api/orders', filters);

    // 7. Dispatch SUCCESS
    dispatch({
      type: 'FETCH_ORDERS_SUCCESS',
      payload: response.data.orders
    });
  } catch (error) {
    // 7. Dispatch FAILURE
    dispatch({
      type: 'FETCH_ORDERS_FAILURE',
      payload: error.message
    });
  }
};

// 8. Reducer
switch (action.type) {
  case 'FETCH_ORDERS_REQUEST':
    return { ...state, loading: true };
  case 'FETCH_ORDERS_SUCCESS':
    return { ...state, loading: false, orders: action.payload };
  case 'FETCH_ORDERS_FAILURE':
    return { ...state, loading: false, error: action.payload };
}
```

## Action/Reducer Examples by Domain

### Authentication

**Actions** (`client/src/actions/authActions.js`):
- `setCurrentUser(user)` - Set logged-in user
- `setCurrentUserForStorepepTeam(user)` - Set admin user
- `logout()` - Clear auth state

**Reducer** (`client/src/reducers/auth.js`):
- `storepepUserReducer` - Merchant auth
- `storepepTeamReducer` - Admin auth

### Orders

**Actions** (`client/src/actions/ordersActions.js`, `client/src/actions/orders/`):
- `getOrders(filters)` - Fetch orders
- `importOrders(storeId)` - Import from store
- `updateOrderStatus(orderId, status)` - Change status
- `storedPackagesStore(packages)` - Add package config

**Reducers**:
- `orders` - Order data
- `ordersFilters` - Filter state
- `ordersTab` - Active tab
- `ordersCount` - Count by status

### Settings

**Actions** (`client/src/actions/settingsActions.js`):
- `updateOriginAddress(address)` - Update ship-from
- `updatePackaging(packaging)` - Update packaging settings
- `updateCarrierSettings(carrier, settings)` - Update carrier config

**Reducers** (`client/src/reducers/settingsData.js`):
- `originAddress` - Ship-from address
- `packaging` - Packaging settings
- `label` - Label settings
- `dhlExpress` - DHL settings

## Best Practices

### Do's

1. **Use action type constants** - Prevent typos
2. **Keep reducers pure** - No side effects, no mutations
3. **Normalize state shape** - Avoid deep nesting
4. **Dispatch minimal payload** - Don't send entire objects if only ID needed
5. **Handle loading/error states** - UX feedback for async operations
6. **Use Redux DevTools** - Debug state changes

### Don'ts

1. **Don't mutate state** - Always return new objects
2. **Don't dispatch actions from reducers** - Reducers are pure functions
3. **Don't put functions in state** - State should be serializable
4. **Don't over-normalize** - Balance between normalization and complexity
5. **Don't connect every component** - Connect at page/container level, pass props down

## Performance Considerations

### Expensive Computations

Problem:
```javascript
const mapStateToProps = (state) => ({
  sortedOrders: state.orders.ordersList.sort(/* expensive sort */)
});
```

Every state change recalculates sort, even if orders didn't change.

Solution: Use `reselect` for memoization (not currently implemented in StorePep).

### Too Many Connected Components

Each `connect()` subscribes to store updates. Too many connected components = too many update checks.

**Pattern**: Connect at page/container level, pass data down as props.

### Large State Updates

Problem: Updating large arrays/objects in state causes expensive re-renders.

Solution:
- Normalize state (entities by ID)
- Use `React.PureComponent` or `React.memo`
- Implement `shouldComponentUpdate`

## Migration Considerations

### Redux Toolkit

Modern Redux apps use Redux Toolkit (RTK) which reduces boilerplate:

**Current**:
```javascript
// types.js
export const FETCH_ORDERS_REQUEST = 'FETCH_ORDERS_REQUEST';
export const FETCH_ORDERS_SUCCESS = 'FETCH_ORDERS_SUCCESS';

// actions/orders.js
export const getOrders = () => async (dispatch) => {
  dispatch({ type: FETCH_ORDERS_REQUEST });
  const response = await axios.get('/api/orders');
  dispatch({ type: FETCH_ORDERS_SUCCESS, payload: response.data });
};

// reducers/orders.js
export const orders = (state = initialState, action) => {
  switch (action.type) {
    case FETCH_ORDERS_REQUEST:
      return { ...state, loading: true };
    // ...
  }
};
```

**With RTK**:
```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const getOrders = createAsyncThunk(
  'orders/fetch',
  async () => {
    const response = await axios.get('/api/orders');
    return response.data;
  }
);

const ordersSlice = createSlice({
  name: 'orders',
  initialState: { ordersList: [], loading: false },
  extraReducers: (builder) => {
    builder
      .addCase(getOrders.pending, (state) => { state.loading = true; })
      .addCase(getOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.ordersList = action.payload;
      });
  }
});
```

RTK benefits:
- Less boilerplate (no action types, no switch statements)
- Immer integration (write "mutating" code safely)
- Built-in dev tools
- Better TypeScript support

## Dependencies

- [Frontend Architecture](../architecture/frontend-architecture.md) - Redux setup and store configuration
- [Component Patterns](component-patterns.md) - How components consume Redux state

## Referenced By

- [Orders UI](../modules/frontend/orders-ui.md) - Order management Redux implementation
- All frontend module pages using Redux

## Related Pages

- [Frontend Architecture](../architecture/frontend-architecture.md)
- [Component Patterns](component-patterns.md)
- [API Conventions](api-conventions.md)
