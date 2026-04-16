---
title: Database Migrations
category: operation
status: complete
last_updated: 2026-04-16
git_reference: 0f9b0bc965c82210bf38320d7c5a5ce60cfd44da
sources: [storepep-react]
---

# Database Migrations

## Overview

StorePep uses [`migrate-mongo`](https://github.com/seppevs/migrate-mongo) to evolve the MongoDB schema, indexes, and seed data. Each migration is a timestamped JavaScript file with `up` and `down` functions that the tool runs in order, recording state in a `changelog` collection. As of `2026-04-16`, the repo holds **108 migrations** spanning May 2023 → April 2026.

| Year | Migrations |
|------|------------|
| 2023 | 31 |
| 2024 | 32 |
| 2025 | 38 |
| 2026 | 7 (so far) |

## Tooling

- **Tool**: `migrate-mongo@^10.0.0` ([`server/package.json:94`](raw/storepep-react/storepepSAAS/server/package.json:94))
- **Config**: [`server/migrate-mongo-config.js`](raw/storepep-react/storepepSAAS/server/migrate-mongo-config.js)
- **Migrations dir**: [`server/db-migrations/`](raw/storepep-react/storepepSAAS/server/db-migrations/)
- **Helpers**: [`server/migration-utils/mongoDictionary.js`](raw/storepep-react/storepepSAAS/server/migration-utils/mongoDictionary.js)

### Config Highlights

```js
// server/migrate-mongo-config.js
{
  mongodb: {
    url: DB_CONNECTION_STRING,         // built from env: STOREPEP_DB_USERNAME/PASSWORD/HOST
    databaseName: 'storePep',
    options: { useNewUrlParser: true, useUnifiedTopology: true,
               connectTimeoutMS: 60_000, socketTimeoutMS: 60_000 },
  },
  migrationsDir: 'db-migrations',
  changelogCollectionName: 'changelog',
  migrationFileExtension: '.js',
  useFileHash: true,                   // detects edits to already-applied migrations
  moduleSystem: 'commonjs',
}
```

`useFileHash: true` is the important guard — once a migration is applied, editing the file in place will be flagged on the next `status`/`up`. Always create a new migration rather than mutating an existing one.

## Filename Convention

```
YYYYMMDDHHMMSS-<short-description>.js
```

`migrate-mongo` orders files alphanumerically, so the timestamp prefix doubles as the run order. Examples from the current set:

```
20230510083944-create_acceptedagreements.js
20240419053619-add_carrierID_aggregatorID_serviceCode_unique_index_for_carrier_services.js
20260414160258-add-include-duties-and-taxes-for-fedex-rest.js
```

Naming is loosely enforced — both `snake_case` and `kebab-case` appear. Two files even slipped in with a doubled extension (`...In USPSRestCarrier.js.js`); the runner doesn't care, but stick to a single `.js`.

## Migration Anatomy

A typical migration follows this shape:

```js
// db-migrations/20260408000000-add-includeLowerRates-to-fedex-rest-carriers.js
const { collectionExistsIn } = require('../migration-utils/mongoDictionary');
const { infoLoggerFor } = require('../src/storepepLogger');
const { constants } = require('../src/storePepConstants');

const logger = { info: infoLoggerFor(module) };
const COLLECTION = 'carriers';

module.exports = {
  async up(db) {
    if (await collectionExistsIn(db, COLLECTION)) {
      await db.collection(COLLECTION).updateMany(
        { carrierType: constants.FEDEX_REST_CARRIER_CODE,
          includeLowerRates: { $exists: false } },
        { $set: { includeLowerRates: true } },
      );
    }
  },

  async down(db) {
    if (await collectionExistsIn(db, COLLECTION)) {
      logger.info('Reverted includeLowerRates from FedEx REST carriers');
    }
  },
};
```

Conventions worth knowing:

- **Idempotency guards**: every migration that touches a collection or index uses `collectionExistsIn` / `indexExists` from `mongoDictionary.js` so re-runs against partially-migrated environments don't blow up.
- **Down methods exist but are often no-ops**: 106 of 108 migrations declare `down`, but data-mutation rollbacks (e.g. `add-includeLowerRates`) just log "Reverted" without unsetting the field. Treat `down` as best-effort; don't rely on it for production rollback.
- **Field references via constants**: carrier types and similar enums come from `src/storePepConstants.js` rather than string literals in the migration body.
- **Index creation runs in background** when issued against large collections — see [`20230703031445-create_index_with_date_created_status_sore_vendor_account_uuid.js:19`](raw/storepep-react/storepepSAAS/server/db-migrations/20230703031445-create_index_with_date_created_status_sore_vendor_account_uuid.js:19).
- **Named indexes**: newer index migrations pass an explicit `name:` so the down step can drop by name (see [`20260401000000-add-batch-in-progress-index-to-shipment-batches.js`](raw/storepep-react/storepepSAAS/server/db-migrations/20260401000000-add-batch-in-progress-index-to-shipment-batches.js)).

## Helper Module

[`server/migration-utils/mongoDictionary.js`](raw/storepep-react/storepepSAAS/server/migration-utils/mongoDictionary.js) exports three small primitives reused by nearly every migration:

| Function | Purpose |
|----------|---------|
| `collectionExistsIn(db, name)` | Truthy if the collection is present — guard for create/drop/updateMany |
| `indexExists(db, collection, query)` | Truthy if an index with the same key shape already exists |
| `indexName(key)` | Builds the default `field_dir_field_dir` index name used by `dropIndex` |

If a migration needs different scaffolding (cursor-based backfill, batched updates, conditional logic per document), it inlines the logic directly — there is no shared "framework" beyond these three helpers.

## What Migrations Are Used For

A grep across filenames groups the 108 migrations into a handful of recurring intents:

| Intent | Examples |
|--------|----------|
| Create collection | `create_agreement.js`, `create_save_filter.js`, `createOrderDiffs.js`, `createProductDocumentsCollection.js` |
| Add/drop index | `add_accountUUID_index_to_packagingsettings.js`, `drop_carrierID_serviceCode_unique_index_from_carrierservices.js` |
| Seed/extend carrier service codes | `add-stamps-usps-serviceCodes-to-db.js`, `add-aupost-services.js`, `add_easypost_service_codes.js` |
| Carrier service rename | `add-courierplease-service-rename.js`, `add-aramex-service-rename.js` |
| Add field to existing docs | `addCustomOrderStatusFieldsToStoreSettings.js`, `addEnableUSMCAforPurolator.js`, `add-instruction-fields-stamps.js` |
| Field migration / data backfill | `addUspsServiceCodeToDb.js`, `add-itemCategoryType.js`, `easypostIncoterm.js` |

Two patterns dominate: **carrier service-code seeding** (≈40% of the corpus) and **collection/index housekeeping**.

## Running Migrations

From `server/`:

```bash
npx migrate-mongo status        # list applied + pending
npx migrate-mongo up            # apply all pending
npx migrate-mongo down          # roll back the most recent
npx migrate-mongo create <name> # scaffold a new timestamped file
```

Required env vars (read by `migrate-mongo-config.js`):

- `DB_CONNECTION_STRING` — base mongo URL
- `STOREPEP_DB_USERNAME`, `STOREPEP_DB_PASSWORD`, `STOREPEP_DB_HOST` — credentials are spliced into `DB_CONNECTION_STRING` if not already embedded

The config logs the resolved URL on startup, so beware shell history when running against staging/prod.

## Authoring Checklist

When adding a new migration:

1. Run `npx migrate-mongo create <short-description>` to get a correctly-timestamped file.
2. Require helpers from `../migration-utils/mongoDictionary` and the logger from `../src/storepepLogger`.
3. Wrap mutations in `collectionExistsIn` / `indexExists` checks so the migration is idempotent and safe in fresh environments.
4. For document updates, scope the filter by `{ field: { $exists: false } }` (or equivalent) so re-runs don't overwrite values set by later code.
5. Pull enum values (carrier codes, statuses) from `src/storePepConstants.js` rather than hardcoding strings.
6. For large collections, pass `{ background: true }` (or named index options) to `createIndex`.
7. Implement `down` even if it's a logging no-op — keeps the file linter-friendly and signals intent.
8. Never edit a previously-applied migration; create a follow-up file instead (`useFileHash: true` will reject the change).

## Related Maintenance Scripts

`server/db-migrations/` is for schema/data shape changes that should run **once per environment**. For repeatable maintenance — admin/account creation, plan provisioning, ad-hoc cleanups — the codebase uses [`server/src/supportScripts/`](raw/storepep-react/storepepSAAS/server/src/supportScripts/), surfaced as npm scripts in `server/package.json` (`create:storepepadmin`, `delete:dropcollections`, `update:renamemongofields`, etc.). Those run outside the `migrate-mongo` changelog and are not tracked as schema state.

## Known Issues / Tech Debt

- **Inconsistent down implementations**: many `down` methods only log without reversing the change. There is no production rollback story — the working assumption is roll-forward via a new migration.
- **Mixed naming styles**: `snake_case` vs `kebab-case` vs `camelCase` and the occasional `.js.js` extension. Harmless to the runner, noisy in directory listings.
- **Backend architecture page drift**: [`architecture/backend-architecture.md`](../architecture/backend-architecture.md) lists the path as `server/src/db-migrations/migrations/`. The actual location is `server/db-migrations/` directly under the server root — that page should be corrected on its next pass.
- **No migration tests**: there is no automated verification that a freshly-created migration is idempotent or that `down` restores the prior state. Authors verify by hand against a local mongo instance.

## Related Pages

- [Backend Architecture](../architecture/backend-architecture.md) — overall server layout
- [Local Setup](local-setup.md) — environment and DB bootstrap
- [Technology Stack](../architecture/technology-stack.md) — MongoDB version and driver
