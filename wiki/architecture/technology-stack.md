---
title: Technology Stack
category: architecture
status: complete
last_updated: 2026-04-07
git_reference: 01e683142eab5eeb25e98dadfdc499e984aff1f8
---

# Technology Stack

## Overview

Complete listing of technologies, frameworks, and libraries used in the StorePep React application.

**Sources**:
- `client/package.json:1-121`
- `server/package.json:1-145`

## Core Platform

| Technology | Version | Layer | Purpose |
|-----------|---------|-------|---------|
| Node.js | 14+ | Runtime | JavaScript runtime environment |
| React | 16.10.2 | Frontend | UI framework |
| Express.js | 4.15.3 | Backend | Web application framework |
| MongoDB | - | Database | NoSQL document database |
| Mongoose | 4.11.10 | Backend | MongoDB object modeling |

## Frontend Stack

### UI Framework & Components

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | 16.10.2 | Core UI library |
| `react-dom` | 16.10.2 | React DOM rendering |
| `@material-ui/core` | 3.9.0 | Material Design component library (v3) |
| `@material-ui/icons` | 3.0.1 | Material Design icons |
| `material-ui` | 0.20.2 | Legacy Material-UI (v0) components |
| `ag-grid-community` | 28.2.1 | High-performance data grid |
| `ag-grid-react` | 28.2.1 | AG-Grid React wrapper |

### State Management

| Package | Version | Purpose |
|---------|---------|---------|
| `redux` | 4.0.1 | State container |
| `react-redux` | 5.1.1 | React bindings for Redux |
| `redux-thunk` | 2.3.0 | Async action middleware |
| `redux-form` | 7.4.2 | Form state management |
| `recompose` | 0.30.0 | Higher-order component utilities |

### Routing & Navigation

| Package | Version | Purpose |
|---------|---------|---------|
| `react-router` | 4.3.1 | Routing library |
| `react-router-dom` | 4.3.1 | DOM bindings for React Router |

### HTTP & Communication

| Package | Version | Purpose |
|---------|---------|---------|
| `axios` | 0.19.0 | HTTP client |
| `socket.io-client` | 2.2.0 | Real-time bidirectional communication |

### Forms & Inputs

| Package | Version | Purpose |
|---------|---------|---------|
| `redux-form` | 7.4.2 | Redux-integrated form management |
| `react-datepicker` | 2.0.0 | Date picker component |
| `react-dates` | 18.3.1 | Airbnb date picker components |
| `react-dates-presets` | 1.1.0 | Date range presets |
| `react-date-range` | 1.4.0 | Date range picker |
| `react-phone-number-input` | 2.3.3 | Phone number input |
| `react-select` | 1.3.0 | Select dropdown component |
| `draft-js` | 0.11.1 | Rich text editor framework |
| `react-draft-wysiwyg` | 1.13.2 | WYSIWYG editor built on Draft.js |
| `draftjs-to-html` | 0.8.4 | Draft.js to HTML converter |
| `html-to-draftjs` | 1.4.0 | HTML to Draft.js converter |

### UI Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `classnames` | 2.2.6 | Conditional CSS class names |
| `react-outside-click-handler` | 1.2.2 | Detect clicks outside elements |
| `react-dnd` | 7.0.2 | Drag and drop |
| `react-dnd-html5-backend` | 7.0.2 | HTML5 drag-drop backend |
| `react-joyride` | 2.2.1 | Guided tours for users |
| `react-s-alert` | 1.4.1 | Alert/notification system |

### Data Handling

| Package | Version | Purpose |
|---------|---------|---------|
| `lodash` | 4.17.11 | Utility functions |
| `moment` | 2.23.0 | Date/time manipulation |
| `validator` | 10.9.0 | String validation |
| `query-string` | 6.2.0 | URL query string parsing |
| `shortid` | 2.2.14 | Short unique ID generation |
| `jszip` | 3.1.5 | ZIP file creation/reading |

### Payment Integration

| Package | Version | Purpose |
|---------|---------|---------|
| `react-stripe-elements` | 6.1.2 | Stripe payment elements |

### Code Editor

| Package | Version | Purpose |
|---------|---------|---------|
| `@uiw/react-codemirror` | 4.17.1 | Code editor component |
| `@uiw/codemirror-extensions-langs` | 4.18.2 | Language support for CodeMirror |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `base-64` | 1.0.0 | Base64 encoding/decoding |
| `jwt-decode` | 2.2.0 | JWT token decoding |
| `prop-types` | 15.6.2 | React prop type checking |
| `currency-symbol-map` | 4.0.4 | Currency symbol lookup |
| `postcode-validator` | 3.7.0 | Postal code validation |
| `pretty-data` | 0.40.0 | XML/JSON formatting |
| `vkbeautify` | 0.99.3 | XML/JSON/CSS beautification |
| `qz-tray` | 2.2.4 | Printer communication |

### Monitoring & Error Tracking

| Package | Version | Purpose |
|---------|---------|---------|
| `@sentry/react` | 7.43.0 | Error tracking for React |
| `@sentry/tracing` | 7.43.0 | Performance monitoring |
| `web-vitals` | 3.4.0 | Web performance metrics |

### Build Tools (Frontend DevDependencies)

| Package | Version | Purpose |
|---------|---------|---------|
| `webpack` | 4.28.1 | Module bundler |
| `webpack-cli` | 3.1.2 | Webpack command-line interface |
| `webpack-dev-server` | 3.1.10 | Development server |
| `webpack-md5-hash` | 0.0.6 | MD5 hashes for bundles |
| `webpack-s3-plugin` | 1.2.0-rc.0 | Upload bundles to S3 |
| `html-webpack-plugin` | 3.2.0 | Generate HTML files |
| `clean-webpack-plugin` | 1.0.0 | Clean build directories |
| `copy-webpack-plugin` | 4.6.0 | Copy static assets |
| `uglifyjs-webpack-plugin` | 2.0.1 | JavaScript minification |

### Babel (Frontend DevDependencies)

| Package | Version | Purpose |
|---------|---------|---------|
| `@babel/core` | 7.2.2 | Babel compiler core |
| `@babel/preset-env` | 7.2.3 | ES2015+ preset |
| `@babel/preset-react` | 7.0.0 | JSX/React preset |
| `babel-loader` | 8.0.4 | Webpack loader for Babel |
| Various Babel plugins | - | Transform async, class properties, etc. |

### Linting (Frontend DevDependencies)

| Package | Version | Purpose |
|---------|---------|---------|
| `eslint` | 5.10.0 | JavaScript linter |
| `eslint-config-airbnb` | 17.1.0 | Airbnb style guide |
| `eslint-plugin-react` | 7.11.1 | React-specific linting rules |
| `eslint-plugin-jsx-a11y` | 6.1.2 | Accessibility linting |
| `eslint-plugin-import` | 2.14.0 | Import/export linting |
| `babel-eslint` | 10.0.1 | Babel parser for ESLint |

### Loaders (Frontend DevDependencies)

| Package | Version | Purpose |
|---------|---------|---------|
| `css-loader` | 2.0.1 | Load CSS files |
| `style-loader` | 0.23.1 | Inject CSS into DOM |
| `file-loader` | 3.0.1 | Load files as modules |
| `url-loader` | 1.1.2 | Load files as data URLs |

### Other Frontend DevDependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `nodemon` | 1.18.9 | Auto-restart on file changes |
| `react-hot-loader` | 4.6.3 | Hot module replacement for React |

## Backend Stack

### Core Framework

| Package | Version | Purpose |
|---------|---------|---------|
| `express` | 4.15.3 | Web framework |
| `body-parser` | 1.17.2 | Request body parsing middleware |
| `cors` | 2.8.4 | Cross-origin resource sharing |
| `helmet` | 3.12.1 | Security headers |
| `compression` | 1.7.1 | Response compression |

### Database & ODM

| Package | Version | Purpose |
|---------|---------|---------|
| `mongoose` | 4.11.10 | MongoDB object modeling |
| `mongoose-sequence` | 6.0.1 | Auto-increment sequences |
| `migrate-mongo` | 10.0.0 | Database migration tool |

### Authentication & Authorization

| Package | Version | Purpose |
|---------|---------|---------|
| `jsonwebtoken` | 7.4.1 | JWT creation/verification |
| `jwks-rsa` | 3.0.1 | JWT key set for Auth0 |
| `bcrypt` | 3.0.7 | Password hashing |

### Real-time & Caching

| Package | Version | Purpose |
|---------|---------|---------|
| `socket.io` | 2.0.4 | Real-time bidirectional communication |
| `redis` | 2.8.0 | Redis client |
| `node-cache` | 5.1.2 | In-memory caching |
| `global-cache` | 1.2.1 | Global cache management |

### Shipping Carrier APIs

| Package | Version | Purpose |
|---------|---------|---------|
| `@easypost/api` | 5.6.1 | Multi-carrier shipping API |

### E-commerce Platform APIs

| Package | Version | Purpose |
|---------|---------|---------|
| `@phivejs/shopify-api` | 0.1.14 | Custom Shopify API wrapper |
| `shopify-api-node` | 2.25.1 | Official Shopify Node.js client |
| `woocommerce-api` | 1.4.2 | WooCommerce REST API client |

### Payment Gateway APIs

| Package | Version | Purpose |
|---------|---------|---------|
| `stripe` | 8.156.0 | Stripe payment API |
| `paypal-rest-sdk` | 1.8.1 | PayPal REST API |
| `razorpay` | 2.0.4 | Razorpay payment gateway (India) |

### Email

| Package | Version | Purpose |
|---------|---------|---------|
| `nodemailer` | 4.4.0 | Email sending library |
| `nodemailer-mailgun-transport` | 1.4.0 | Mailgun transport for Nodemailer |
| `nodemailer-juice` | 1.0.0 | Inline CSS in emails |
| `nodemailer-plugin-inline-base64` | 2.1.1 | Inline base64 images |

### PDF & Document Generation

| Package | Version | Purpose |
|---------|---------|---------|
| `puppeteer` | 13.5.2 | Headless Chrome for PDF generation |
| `html-pdf` | 3.0.1 | HTML to PDF conversion |
| `hummus` | 1.0.105 | PDF manipulation |
| `jimp` | 0.2.28 | Image processing |
| `bwip-js` | 3.0.4 | Barcode generation |

### Templating

| Package | Version | Purpose |
|---------|---------|---------|
| `handlebars` | 4.7.7 | Template engine |

### XML/JSON Processing

| Package | Version | Purpose |
|---------|---------|---------|
| `xml2js` | 0.4.19 | XML to JavaScript object conversion |
| `xml2json` | 0.11.0 | XML to JSON conversion |
| `xmlbuilder` | 10.0.0 | XML builder |
| `xmldom` | 0.6.0 | XML DOM parser |
| `xpath` | 0.0.32 | XPath query |
| `js2xmlparser` | 4.0.0 | JS object to XML conversion |
| `jsonpath` | 1.1.1 | JSONPath query |
| `jsonpath-plus` | 9.0.0 | Extended JSONPath |
| `jsonschema` | 1.4.1 | JSON schema validation |

### SOAP

| Package | Version | Purpose |
|---------|---------|---------|
| `soap` | 0.23.0 | SOAP client |
| `strong-soap` | 1.19.1 | Enhanced SOAP client |

### HTTP & Networking

| Package | Version | Purpose |
|---------|---------|---------|
| `axios` | 0.16.1 | HTTP client (main version) |
| `axios-latest` | ^1.6.0 | Latest Axios (aliased) |
| `axios-retry` | 3.3.1 | Retry failed requests |
| `request-ip` | 2.1.3 | Get client IP address |

### Data Processing

| Package | Version | Purpose |
|---------|---------|---------|
| `lodash` | 4.17.4 | Utility functions |
| `moment` | 2.19.3 | Date/time manipulation |
| `moment-business-days` | 1.2.0 | Business day calculations |
| `moment-timezone` | 0.5.25 | Timezone support |
| `validator` | 7.0.0 | String validation |
| `qs` | 6.10.3 | Query string parsing |
| `query-string` | 5.0.1 | URL query string utilities |
| `csv-parse` | 4.16.3 | CSV parsing |
| `csv-writer` | 1.6.0 | CSV writing |

### Background Jobs

| Package | Version | Purpose |
|---------|---------|---------|
| `cron` | 1.3.0 | Cron job scheduling |

### Monitoring & Logging

| Package | Version | Purpose |
|---------|---------|---------|
| `winston` | 3.3.4 | Logging library |
| `winston-logrotate` | 1.3.0 | Log rotation for Winston |
| `winston-syslog` | 2.5.0 | Syslog transport for Winston |
| `express-winston` | 4.2.0 | Express middleware for Winston |
| `newrelic` | 8.7.1 | Application performance monitoring |
| `prom-client` | 11.1.2 | Prometheus metrics client |
| `response-time` | 2.3.2 | Response time header |

### AWS Services

| Package | Version | Purpose |
|---------|---------|---------|
| `aws-sdk` | 2.1048.0 | AWS SDK for JavaScript |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `dotenv` | 6.1.0 | Environment variable loading |
| `base-64` | 0.1.0 | Base64 encoding/decoding |
| `base64-stream` | 1.0.0 | Base64 streaming |
| `js-base64` | 2.3.2 | Base64 encoding |
| `uuid` | 3.2.1 | UUID generation |
| `string-hash` | 1.1.3 | String hashing |
| `currency-symbol-map` | 4.0.3 | Currency symbols |
| `decode-html` | 2.0.0 | HTML entity decoding |
| `he` | 1.2.0 | HTML entity encoder/decoder |
| `in-array` | 0.1.2 | Array membership check |
| `extend` | 3.0.1 | Object extension |
| `hal` | 1.2.0 | HAL (Hypertext Application Language) |
| `pretty-data` | 0.40.0 | XML/JSON formatting |
| `sanitize-filename` | 1.6.3 | Filename sanitization |
| `selfsigned` | 2.4.1 | Self-signed certificate generation |
| `multer` | 1.4.3 | Multipart form data handling |
| `dicer` | 0.3.1 | Multipart parser |
| `memory-streams` | 0.1.3 | In-memory streams |
| `path` | 0.12.7 | Path utilities |
| `util` | 0.10.3 | Node.js util |
| `i` | 0.3.6 | Inflection library |

### Webhooks

| Package | Version | Purpose |
|---------|---------|---------|
| `svix` | 1.24.0 | Webhook delivery platform |

### Slack Integration

| Package | Version | Purpose |
|---------|---------|---------|
| `slack-node` | 0.1.8 | Slack API client |

### HTTP Context

| Package | Version | Purpose |
|---------|---------|---------|
| `express-http-context` | 1.0.2 | HTTP context for Express |

### Custom Internal Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `@phivejs/config` | 0.0.11 | Configuration management |
| `@phivejs/eventing` | 1.0.9 | Event handling |
| `@phivejs/eventsourcing-support` | 1.1.7 | Event sourcing support |
| `@phivejs/feature-switch` | 0.0.9 | Feature toggle system |
| `@phivejs/shopify-api` | 0.1.14 | Custom Shopify API wrapper |

### Backend DevDependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `nodemon` | 1.14.1 | Auto-restart on file changes |
| `eslint` | 5.6.0 | JavaScript linter |
| `eslint-config-airbnb-base` | 13.1.0 | Airbnb style guide (base) |
| `eslint-config-google` | 0.10.0 | Google style guide |
| `eslint-plugin-import` | 2.14.0 | Import/export linting |
| `eslint-plugin-react` | 7.7.0 | React linting |
| `chalk` | 2.4.2 | Terminal color output |
| `jest` | 28.1.0 | Testing framework |
| `jest-when` | 3.5.2 | Jest conditional mocking |

## Infrastructure & Deployment

| Technology | Purpose |
|-----------|---------|
| Docker | Containerization |
| Jenkins | CI/CD pipelines |
| MongoDB | Database |
| Redis | Caching and session storage |
| S3 | Static asset storage |
| Mailgun | Email delivery |
| Sentry | Error tracking |
| New Relic | APM monitoring |
| Prometheus | Metrics collection |

## Development Tools

| Tool | Purpose |
|------|---------|
| npm | Package manager |
| Git | Version control |
| ESLint | Code linting |
| Webpack | Module bundling |
| Babel | JavaScript transpilation |
| Jest | Testing framework |
| Nodemon | Development auto-restart |

## API Integrations

### Shipping Carriers (15+)
- FedEx
- UPS
- DHL
- Canada Post
- USPS
- Stamps.com
- Australia Post
- TNT
- Aramex
- And more via EasyPost

### E-commerce Platforms
- Shopify
- WooCommerce
- Magento (v1 & v2)
- BigCommerce
- PrestaShop

### Payment Gateways
- Stripe
- PayPal
- Razorpay

### Monitoring & Analytics
- Sentry (error tracking)
- New Relic (APM)
- Prometheus (metrics)

### Communication
- Mailgun (email)
- Socket.io (real-time)
- Slack (notifications)

## Version Notes

### Frontend Version Concerns
- **React**: 16.10.2 is several major versions behind (current: 18+)
- **Axios**: 0.19.0 has known security vulnerabilities
- **Material-UI**: Mixing v0 and v3 (current: v5+)
- **Webpack**: 4.x (current: 5+)

### Backend Version Concerns
- **Mongoose**: 4.11.10 is very outdated (current: 7+)
- **Express**: 4.15.3 is old (current: 4.18+)
- **JWT**: 7.4.1 (current: 9+)
- **Node.js**: 14+ (current LTS: 18+, 20+)

**Recommendation**: Plan dependency update strategy to address security vulnerabilities and access new features.

## Dependencies

- [Overview](./overview.md) - High-level system architecture
- [Frontend Architecture](./frontend-architecture.md) - How frontend dependencies are used
- [Backend Architecture](./backend-architecture.md) - How backend dependencies are used

## Referenced By

- All architecture and module pages reference this stack
- [Deployment Pipeline](./deployment-pipeline.md) (to be created)
- [Local Setup](../operations/local-setup.md) (to be created)

## Related Pages

- [API Integrations](../patterns/api-conventions.md) (to be created)
- [Security Considerations](../patterns/security.md) (to be created)
