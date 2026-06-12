/**
 * Migrates FedEx SOAP (C2) dangerous-goods and alcohol settings to FedEx REST (C39).
 *
 * Covers two collections:
 *   - productsnews  : dangerousGoods.C2  → dangerousGoods.C39
 *                     alcohol.C2.recipientType → alcohol.C39.recipientType
 *   - carriers      : hazardousTypeOfPackaging / hazardousPackagingMaterial
 *                     on C2 carrier records → matching C39 carrier records
 *
 * IMPORTANT — this script seeds C39 data ahead of the code/schema switch.
 * The migration is complete only after ALL three steps are done:
 *   1. This script runs with --apply (data copy)
 *   2. The product schema adds dangerousGoods.C39 and alcohol.C39 fields
 *   3. The FedEx REST requestBuilder is updated to read from C39 instead of C2
 * Running this script alone has no runtime effect until steps 2 and 3 land.
 *
 * Usage (run from storepepSAAS/server/):
 *   node supportscripts/migrate-fedex-dg-c2-to-c39.js            # dry-run (default, safe)
 *   node supportscripts/migrate-fedex-dg-c2-to-c39.js --apply    # write C39 data
 *   node supportscripts/migrate-fedex-dg-c2-to-c39.js --verify   # compare C2 vs C39 after apply
 *   node supportscripts/migrate-fedex-dg-c2-to-c39.js --apply --overwrite  # re-copy even if C39 exists
 *
 * Output files (written next to this script):
 *   dg_migration_dryrun.json   — scope report (dry-run)
 *   dg_migration_before.json   — snapshot of all affected docs before apply
 *   dg_migration_result.json   — per-document outcome after apply
 *   dg_migration_verify.json   — diff report after verify
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');

const DB_CONNECTION_STRING = process.env.DB_CONNECTION_STRING;
const DB_USERNAME = process.env.STOREPEP_DB_USERNAME;
const DB_PASSWORD = process.env.STOREPEP_DB_PASSWORD;

if (!DB_CONNECTION_STRING) {
  console.error('DB_CONNECTION_STRING not set in .env');
  process.exit(1);
}

const SOAP_CODE = 'C2';   // FedEx SOAP — being sunset
const REST_CODE = 'C39';  // FedEx REST — migration target

const DG_FIELDS = [
  'regulation',
  'accessibility',
  'batteryMaterialType',
  'batteryPackingType',
  'batteryRegulatorySubType',
  'isCargoAircraftOnly',
  'isOtherDangerousGoods',
  'isBattery',
  'options',
];

const args = process.argv.slice(2);
const MODE_APPLY = args.includes('--apply');
const MODE_VERIFY = args.includes('--verify');
const OVERWRITE = args.includes('--overwrite');
const SCRIPT_DIR = __dirname;

mongoose.Promise = global.Promise;

// ── helpers ───────────────────────────────────────────────────────────────────

function writeJson(filename, data) {
  const outPath = path.join(SCRIPT_DIR, filename);
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2));
  console.log('  Written: ' + outPath);
}

function hasValue(v) {
  return v !== null && v !== undefined;
}

// Returns true if the C2 DG sub-doc has at least one defined field worth copying.
function c2DgHasData(dgC2) {
  if (!dgC2) return false;
  return DG_FIELDS.some(f => hasValue(dgC2[f]));
}

// Builds a $set payload for dangerousGoods.C39 from dangerousGoods.C2.
function buildDgSetPayload(dgC2) {
  var payload = {};
  DG_FIELDS.forEach(function(f) {
    if (hasValue(dgC2[f])) {
      payload['dangerousGoods.' + REST_CODE + '.' + f] = dgC2[f];
    }
  });
  return payload;
}

// ── main ──────────────────────────────────────────────────────────────────────

async function main() {
  const mode = MODE_VERIFY ? 'VERIFY' : (MODE_APPLY ? 'APPLY' : 'DRY-RUN');
  console.log('=== FedEx DG migration: C2 → C39 | mode=' + mode + ' ===\n');

  const readPref = (MODE_APPLY || MODE_VERIFY) ? 'primary' : 'secondary';
  await mongoose.connect(DB_CONNECTION_STRING, {
    useMongoClient: true,
    user: DB_USERNAME,
    pass: DB_PASSWORD,
    db: { readPreference: readPref },
  });
  console.log('Connected (readPreference=' + readPref + ')');

  // Use native collections to bypass Mongoose strict-mode schema validation.
  // dangerousGoods.C39 is not yet defined in the Mongoose schema, so hydrated
  // model methods would silently strip those paths on both read and write.
  const productsColl = mongoose.connection.collection('productsnews');
  const carriersColl = mongoose.connection.collection('carriers');

  if (MODE_VERIFY) {
    await runVerify(productsColl, carriersColl);
  } else {
    await runMigration(productsColl, carriersColl);
  }

  mongoose.connection.close();
}

// ── DRY-RUN / APPLY ───────────────────────────────────────────────────────────

async function runMigration(productsColl, carriersColl) {
  // ── Products: DG (dangerousGoods.C2) ───────────────────────────────────────
  console.log('\nPhase 1: Products — dangerousGoods.C2');
  const dgProductsRaw = await productsColl.find(
    { isDangerousGoodsPresent: true },
    { projection: { _id: 1, productUUID: 1, accountUUID: 1, dangerousGoods: 1 } }
  ).toArray();

  const dgProducts = dgProductsRaw.filter(function(p) {
    return c2DgHasData(p.dangerousGoods && p.dangerousGoods[SOAP_CODE]);
  });
  console.log('  Products with dangerousGoods.C2 data: ' + dgProducts.length + ' (of ' + dgProductsRaw.length + ' isDangerousGoodsPresent)');

  const dgAlreadyHaveC39 = dgProducts.filter(function(p) {
    return c2DgHasData(p.dangerousGoods && p.dangerousGoods[REST_CODE]);
  });
  const dgNeedsCopy = OVERWRITE ? dgProducts : dgProducts.filter(function(p) {
    return !c2DgHasData(p.dangerousGoods && p.dangerousGoods[REST_CODE]);
  });
  console.log('  Already have C39 DG data: ' + dgAlreadyHaveC39.length);
  console.log('  Need copy: ' + dgNeedsCopy.length + (OVERWRITE ? ' (--overwrite: will re-copy all)' : ''));

  // ── Products: Alcohol (alcohol.C2.recipientType) ───────────────────────────
  console.log('\nPhase 2: Products — alcohol.C2.recipientType');
  const alcoholProductsRaw = await productsColl.find(
    { isAlcoholPresent: true, ['alcohol.' + SOAP_CODE + '.recipientType']: { $exists: true, $ne: null } },
    { projection: { _id: 1, productUUID: 1, accountUUID: 1, alcohol: 1 } }
  ).toArray();
  const alcoholAlreadyHaveC39 = alcoholProductsRaw.filter(function(p) {
    return hasValue(p.alcohol && p.alcohol[REST_CODE] && p.alcohol[REST_CODE].recipientType);
  });
  const alcoholNeedsCopy = OVERWRITE ? alcoholProductsRaw : alcoholProductsRaw.filter(function(p) {
    return !hasValue(p.alcohol && p.alcohol[REST_CODE] && p.alcohol[REST_CODE].recipientType);
  });
  console.log('  Products with alcohol.C2.recipientType: ' + alcoholProductsRaw.length);
  console.log('  Already have C39 alcohol data: ' + alcoholAlreadyHaveC39.length);
  console.log('  Need copy: ' + alcoholNeedsCopy.length);

  // ── Per-category account breakdown (mirrors Slack audit queries) ───────────
  // Equivalent to:
  //   db.productsnews.distinct("accountUUID", { "dangerousGoods.C2.isOtherDangerousGoods": true })
  //   db.productsnews.distinct("accountUUID", { "dangerousGoods.C2.isBattery": true })
  //   db.productsnews.distinct("accountUUID", { isAlcoholPresent: true, "alcohol.C2.recipientType": { $exists: true } })
  const otherDgAccounts = Array.from(new Set(
    dgProducts
      .filter(function(p) { return p.dangerousGoods && p.dangerousGoods[SOAP_CODE] && p.dangerousGoods[SOAP_CODE].isOtherDangerousGoods === true; })
      .map(function(p) { return p.accountUUID; })
  ));
  const batteryAccounts = Array.from(new Set(
    dgProducts
      .filter(function(p) { return p.dangerousGoods && p.dangerousGoods[SOAP_CODE] && p.dangerousGoods[SOAP_CODE].isBattery === true; })
      .map(function(p) { return p.accountUUID; })
  ));
  const alcoholAccounts = Array.from(new Set(
    alcoholProductsRaw.map(function(p) { return p.accountUUID; })
  ));

  console.log('\nAudit breakdown (account counts per DG category):');
  console.log('  isOtherDangerousGoods=true : ' + otherDgAccounts.length + ' accounts');
  console.log('  isBattery=true             : ' + batteryAccounts.length + ' accounts');
  console.log('  alcohol.recipientType set  : ' + alcoholAccounts.length + ' accounts');

  // ── Carriers: hazardous packaging settings ─────────────────────────────────
  console.log('\nPhase 3: Carriers — hazardousTypeOfPackaging / hazardousPackagingMaterial');
  const c2HazCarriers = await carriersColl.find(
    {
      carrierCode: SOAP_CODE,
      $or: [
        { hazardousTypeOfPackaging: { $exists: true, $ne: null } },
        { hazardousPackagingMaterial: { $exists: true, $ne: null } },
      ],
    },
    { projection: { _id: 1, accountUUID: 1, carrierCode: 1, hazardousTypeOfPackaging: 1, hazardousPackagingMaterial: 1 } }
  ).toArray();
  console.log('  C2 carriers with hazardous settings: ' + c2HazCarriers.length);

  // Find corresponding C39 carriers for these accounts.
  const c2AccountUUIDs = c2HazCarriers.map(function(c) { return c.accountUUID; }).filter(Boolean);
  const c39Carriers = await carriersColl.find(
    { carrierCode: REST_CODE, accountUUID: { $in: c2AccountUUIDs } },
    { projection: { _id: 1, accountUUID: 1, hazardousTypeOfPackaging: 1, hazardousPackagingMaterial: 1 } }
  ).toArray();

  const c39ByAccount = {};
  c39Carriers.forEach(function(c) { c39ByAccount[c.accountUUID] = c; });

  const carriersWithC39 = c2HazCarriers.filter(function(c) { return !!c39ByAccount[c.accountUUID]; });
  const carriersWithoutC39 = c2HazCarriers.filter(function(c) { return !c39ByAccount[c.accountUUID]; });
  console.log('  Accounts that have a C39 carrier: ' + carriersWithC39.length);
  console.log('  Accounts missing a C39 carrier (cannot auto-copy): ' + carriersWithoutC39.length);

  const carriersNeedsCopy = OVERWRITE
    ? carriersWithC39
    : carriersWithC39.filter(function(c) {
        const c39 = c39ByAccount[c.accountUUID];
        return !hasValue(c39.hazardousTypeOfPackaging) && !hasValue(c39.hazardousPackagingMaterial);
      });
  console.log('  Need copy: ' + carriersNeedsCopy.length);

  // ── Summary ────────────────────────────────────────────────────────────────
  const scope = {
    generatedAt: new Date().toISOString(),
    mode: MODE_APPLY ? 'apply' : 'dry-run',
    overwrite: OVERWRITE,
    auditByCategory: {
      note: 'Account UUIDs per DG type — mirrors the Slack audit queries',
      isOtherDangerousGoods: { accountCount: otherDgAccounts.length, accountUUIDs: otherDgAccounts },
      isBattery: { accountCount: batteryAccounts.length, accountUUIDs: batteryAccounts },
      alcohol: { accountCount: alcoholAccounts.length, accountUUIDs: alcoholAccounts },
    },
    products: {
      dgTotal: dgProductsRaw.length,
      dgWithC2Data: dgProducts.length,
      dgAlreadyHaveC39: dgAlreadyHaveC39.length,
      dgNeedsCopy: dgNeedsCopy.length,
      alcoholWithC2Data: alcoholProductsRaw.length,
      alcoholAlreadyHaveC39: alcoholAlreadyHaveC39.length,
      alcoholNeedsCopy: alcoholNeedsCopy.length,
    },
    carriers: {
      c2WithHazardousSettings: c2HazCarriers.length,
      haveMatchingC39: carriersWithC39.length,
      missingC39_cannotAutoCopy: carriersWithoutC39.length,
      needsCopy: carriersNeedsCopy.length,
      missingC39AccountUUIDs: carriersWithoutC39.map(function(c) { return c.accountUUID; }),
    },
    note: 'This data copy is a prerequisite. The migration is complete only after ' +
          'the product schema adds dangerousGoods.C39 / alcohol.C39 fields AND ' +
          'the FedEx REST requestBuilder is updated to read from C39 instead of C2.',
  };

  if (!MODE_APPLY) {
    writeJson('dg_migration_dryrun.json', scope);
    console.log('\nDry-run complete. Review dg_migration_dryrun.json, then re-run with --apply.');
    return;
  }

  // ── APPLY ──────────────────────────────────────────────────────────────────

  // Snapshot before-state of all affected documents.
  const beforeProducts = [];
  const allProductIds = Array.from(new Set(
    dgNeedsCopy.map(function(p) { return p._id; }).concat(
      alcoholNeedsCopy.map(function(p) { return p._id; })
    )
  ));
  if (allProductIds.length > 0) {
    const beforeDocs = await productsColl.find(
      { _id: { $in: allProductIds } },
      { projection: { productUUID: 1, accountUUID: 1, dangerousGoods: 1, alcohol: 1 } }
    ).toArray();
    beforeProducts.push(...beforeDocs);
  }

  const beforeCarriers = carriersNeedsCopy.length > 0
    ? await carriersColl.find(
        { _id: { $in: carriersNeedsCopy.map(function(c) { return c._id; }) } }
      ).toArray()
    : [];

  writeJson('dg_migration_before.json', {
    generatedAt: new Date().toISOString(),
    products: beforeProducts,
    carriers: beforeCarriers,
  });
  console.log('\nBefore-state snapshot saved.');

  const results = { products: [], carriers: [], errors: [] };

  // Apply DG copy for products.
  console.log('\nApplying product DG copy (' + dgNeedsCopy.length + ' products)...');
  for (var i = 0; i < dgNeedsCopy.length; i++) {
    var prod = dgNeedsCopy[i];
    var dgC2 = prod.dangerousGoods && prod.dangerousGoods[SOAP_CODE];
    var setPayload = buildDgSetPayload(dgC2);
    try {
      await productsColl.updateOne(
        { _id: prod._id },
        { $set: setPayload }
      );
      results.products.push({ productUUID: prod.productUUID, accountUUID: prod.accountUUID, action: 'dg_copied', fields: Object.keys(setPayload) });
      if ((i + 1) % 100 === 0) console.log('  ' + (i + 1) + '/' + dgNeedsCopy.length + ' done');
    } catch (err) {
      results.errors.push({ productUUID: prod.productUUID, error: err.message });
      console.error('  Error on product ' + prod.productUUID + ': ' + err.message);
    }
  }

  // Apply alcohol recipientType copy for products.
  console.log('Applying product alcohol copy (' + alcoholNeedsCopy.length + ' products)...');
  for (var j = 0; j < alcoholNeedsCopy.length; j++) {
    var aProd = alcoholNeedsCopy[j];
    var recipientType = aProd.alcohol && aProd.alcohol[SOAP_CODE] && aProd.alcohol[SOAP_CODE].recipientType;
    try {
      await productsColl.updateOne(
        { _id: aProd._id },
        { $set: { ['alcohol.' + REST_CODE + '.recipientType']: recipientType } }
      );
      results.products.push({ productUUID: aProd.productUUID, accountUUID: aProd.accountUUID, action: 'alcohol_copied', fields: ['alcohol.' + REST_CODE + '.recipientType'] });
    } catch (err) {
      results.errors.push({ productUUID: aProd.productUUID, error: err.message });
      console.error('  Error on product ' + aProd.productUUID + ': ' + err.message);
    }
  }

  // Apply hazardous packaging copy for C39 carriers.
  console.log('Applying carrier hazardous packaging copy (' + carriersNeedsCopy.length + ' carriers)...');
  for (var k = 0; k < carriersNeedsCopy.length; k++) {
    var c2carrier = carriersNeedsCopy[k];
    var c39carrier = c39ByAccount[c2carrier.accountUUID];
    var carrierSet = {};
    if (hasValue(c2carrier.hazardousTypeOfPackaging)) carrierSet.hazardousTypeOfPackaging = c2carrier.hazardousTypeOfPackaging;
    if (hasValue(c2carrier.hazardousPackagingMaterial)) carrierSet.hazardousPackagingMaterial = c2carrier.hazardousPackagingMaterial;
    try {
      await carriersColl.updateOne(
        { _id: c39carrier._id },
        { $set: carrierSet }
      );
      results.carriers.push({ accountUUID: c2carrier.accountUUID, action: 'carrier_copied', fields: Object.keys(carrierSet) });
    } catch (err) {
      results.errors.push({ accountUUID: c2carrier.accountUUID, error: err.message });
      console.error('  Error on carrier for account ' + c2carrier.accountUUID + ': ' + err.message);
    }
  }

  scope.applied = {
    productsDgCopied: dgNeedsCopy.length - results.errors.filter(function(e) { return !!e.productUUID; }).length,
    alcoholCopied: alcoholNeedsCopy.length,
    carriersCopied: carriersNeedsCopy.length,
    errors: results.errors.length,
  };

  writeJson('dg_migration_result.json', { scope: scope, results: results });
  console.log('\nApply complete.');
  console.log('  Product DG copies: ' + (dgNeedsCopy.length));
  console.log('  Alcohol copies:    ' + (alcoholNeedsCopy.length));
  console.log('  Carrier copies:    ' + (carriersNeedsCopy.length));
  console.log('  Errors:            ' + results.errors.length);
  if (results.errors.length > 0) {
    console.error('\n!! Some records failed. Check dg_migration_result.json errors array.');
    process.exitCode = 1;
  }
  console.log('\nNext: run --verify to confirm C39 data matches C2.');
}

// ── VERIFY ────────────────────────────────────────────────────────────────────

async function runVerify(productsColl, carriersColl) {
  console.log('\nVerifying C39 data matches C2...');
  const mismatches = [];
  const missing = [];
  const ok = [];

  // Products — DG
  const dgProds = await productsColl.find(
    { isDangerousGoodsPresent: true },
    { projection: { productUUID: 1, accountUUID: 1, dangerousGoods: 1, alcohol: 1 } }
  ).toArray();

  dgProds.forEach(function(p) {
    const c2dg = p.dangerousGoods && p.dangerousGoods[SOAP_CODE];
    const c39dg = p.dangerousGoods && p.dangerousGoods[REST_CODE];
    if (!c2DgHasData(c2dg)) return; // nothing to verify

    if (!c2DgHasData(c39dg)) {
      missing.push({ type: 'product_dg', productUUID: p.productUUID, accountUUID: p.accountUUID, detail: 'C39 DG missing' });
      return;
    }

    DG_FIELDS.forEach(function(f) {
      if (hasValue(c2dg[f]) && c2dg[f] !== c39dg[f]) {
        mismatches.push({ type: 'product_dg', productUUID: p.productUUID, accountUUID: p.accountUUID, field: f, c2: c2dg[f], c39: c39dg && c39dg[f] });
      }
    });

    if (!missing.find(function(m) { return m.productUUID === p.productUUID; }) &&
        !mismatches.find(function(m) { return m.productUUID === p.productUUID; })) {
      ok.push({ type: 'product_dg', productUUID: p.productUUID });
    }
  });

  // Products — Alcohol
  const alcoholProds = await productsColl.find(
    { isAlcoholPresent: true, ['alcohol.' + SOAP_CODE + '.recipientType']: { $exists: true, $ne: null } },
    { projection: { productUUID: 1, accountUUID: 1, alcohol: 1 } }
  ).toArray();

  alcoholProds.forEach(function(p) {
    const c2rt = p.alcohol && p.alcohol[SOAP_CODE] && p.alcohol[SOAP_CODE].recipientType;
    const c39rt = p.alcohol && p.alcohol[REST_CODE] && p.alcohol[REST_CODE].recipientType;
    if (!hasValue(c2rt)) return;
    if (!hasValue(c39rt)) {
      missing.push({ type: 'product_alcohol', productUUID: p.productUUID, accountUUID: p.accountUUID, detail: 'C39 alcohol.recipientType missing' });
    } else if (c2rt !== c39rt) {
      mismatches.push({ type: 'product_alcohol', productUUID: p.productUUID, accountUUID: p.accountUUID, field: 'alcohol.recipientType', c2: c2rt, c39: c39rt });
    } else {
      ok.push({ type: 'product_alcohol', productUUID: p.productUUID });
    }
  });

  // Carriers
  const c2HazCarriers = await carriersColl.find(
    {
      carrierCode: SOAP_CODE,
      $or: [
        { hazardousTypeOfPackaging: { $exists: true, $ne: null } },
        { hazardousPackagingMaterial: { $exists: true, $ne: null } },
      ],
    },
    { projection: { accountUUID: 1, hazardousTypeOfPackaging: 1, hazardousPackagingMaterial: 1 } }
  ).toArray();

  const c39Carriers = await carriersColl.find(
    { carrierCode: REST_CODE, accountUUID: { $in: c2HazCarriers.map(function(c) { return c.accountUUID; }) } },
    { projection: { accountUUID: 1, hazardousTypeOfPackaging: 1, hazardousPackagingMaterial: 1 } }
  ).toArray();

  const c39ByAcc = {};
  c39Carriers.forEach(function(c) { c39ByAcc[c.accountUUID] = c; });

  c2HazCarriers.forEach(function(c2c) {
    const c39c = c39ByAcc[c2c.accountUUID];
    if (!c39c) {
      missing.push({ type: 'carrier', accountUUID: c2c.accountUUID, detail: 'No C39 carrier exists for this account' });
      return;
    }
    ['hazardousTypeOfPackaging', 'hazardousPackagingMaterial'].forEach(function(f) {
      if (hasValue(c2c[f]) && c2c[f] !== c39c[f]) {
        mismatches.push({ type: 'carrier', accountUUID: c2c.accountUUID, field: f, c2: c2c[f], c39: c39c[f] });
      }
    });
    if (!missing.find(function(m) { return m.accountUUID === c2c.accountUUID && m.type === 'carrier'; }) &&
        !mismatches.find(function(m) { return m.accountUUID === c2c.accountUUID && m.type === 'carrier'; })) {
      ok.push({ type: 'carrier', accountUUID: c2c.accountUUID });
    }
  });

  const report = {
    generatedAt: new Date().toISOString(),
    summary: { ok: ok.length, missing: missing.length, mismatches: mismatches.length },
    missing: missing,
    mismatches: mismatches,
    ok: ok,
    note: 'C39 fields are read via native MongoDB driver. If schema/builder have not yet ' +
          'been updated to C39, mismatches here represent pending code changes, not data errors.',
  };

  writeJson('dg_migration_verify.json', report);
  console.log('\nVerification summary:');
  console.log('  OK:         ' + ok.length);
  console.log('  Missing C39: ' + missing.length);
  console.log('  Mismatches: ' + mismatches.length);
  if (missing.length > 0 || mismatches.length > 0) {
    console.error('\n!! Issues found. Review dg_migration_verify.json');
    process.exitCode = 1;
  } else {
    console.log('\nAll C39 data matches C2. Data migration verified.');
  }
}

main().catch(function(err) {
  console.error(err);
  process.exit(1);
});
