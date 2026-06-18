/**
 * Migrates FedEx SOAP (C2) dangerous-goods and alcohol settings to FedEx REST (C39).
 *
 * Covers two collections:
 *   - productsnews  : dangerousGoods.C2  → dangerousGoods.C39
 *                     alcohol.C2.recipientType → alcohol.C39.recipientType
 *   - carriers      : hazardousTypeOfPackaging / hazardousPackagingMaterial
 *                     on C2 carrier records → matching C39 carrier records
 *
 * Query strategy (73M product documents, no index on isDangerousGoodsPresent):
 *   1. Fetch C2 carrier account list from the small carriers collection.
 *   2. Query products PER ACCOUNT using { accountUUID, isDangerousGoodsPresent: true }.
 *      This hits the accountUUID_1_productType_1 index instead of doing a full scan.
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
 *   dg_migration_before.json   — snapshot of affected docs before apply
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

const SOAP_CODE = 'C2';
const REST_CODE = 'C39';

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
const MODE_APPLY  = args.includes('--apply');
const MODE_VERIFY = args.includes('--verify');
const OVERWRITE   = args.includes('--overwrite');
const SCRIPT_DIR  = __dirname;

mongoose.Promise = global.Promise;

// ── helpers ───────────────────────────────────────────────────────────────────

function writeJson(filename, data) {
  var outPath = path.join(SCRIPT_DIR, filename);
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2));
  console.log('  Written: ' + outPath);
}

function hasValue(v) {
  return v !== null && v !== undefined;
}

function c2DgHasData(dgC2) {
  if (!dgC2) return false;
  return DG_FIELDS.some(function(f) { return hasValue(dgC2[f]); });
}

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
  var mode = MODE_VERIFY ? 'VERIFY' : (MODE_APPLY ? 'APPLY' : 'DRY-RUN');
  console.log('=== FedEx DG migration: C2 → C39 | mode=' + mode + ' ===\n');

  var readPref = (MODE_APPLY || MODE_VERIFY) ? 'primary' : 'secondary';
  await mongoose.connect(DB_CONNECTION_STRING, {
    useMongoClient: true,
    user: DB_USERNAME,
    pass: DB_PASSWORD,
    socketTimeoutMS: 0,
    connectTimeoutMS: 30000,
    db: { readPreference: readPref },
  });
  console.log('Connected (readPreference=' + readPref + ')');

  // Use native collections to bypass Mongoose strict-mode schema validation.
  // dangerousGoods.C39 is not yet in the product schema.
  var productsColl = mongoose.connection.collection('productsnews');
  var carriersColl = mongoose.connection.collection('carriers');

  if (MODE_VERIFY) {
    await runVerify(productsColl, carriersColl);
  } else {
    await runMigration(productsColl, carriersColl);
  }

  mongoose.connection.close();
}

// ── get C2 account list ───────────────────────────────────────────────────────
// Using the carriers collection (small) as the entry point so we never do a
// full scan of the 73M-document productsnews collection.

async function getC2AccountUUIDs(carriersColl) {
  var docs = await carriersColl.find({ carrierCode: SOAP_CODE }).toArray();
  return Array.from(new Set(docs.map(function(d) { return d.accountUUID; }).filter(Boolean)));
}

// ── batched product queries (uses accountUUID_1_productType_1 index) ──────────
// Using $in over batches of accountUUIDs reduces 2380 round-trips to ~24,
// avoiding connection timeouts on long sequential loops.

var BATCH_SIZE = 100;

function chunkArray(arr, size) {
  var chunks = [];
  for (var i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

async function getDgProductsForAccounts(productsColl, accountUUIDs) {
  var batches = chunkArray(accountUUIDs, BATCH_SIZE);
  var results = [];
  for (var b = 0; b < batches.length; b++) {
    var docs = await productsColl.find({
      accountUUID: { $in: batches[b] },
      isDangerousGoodsPresent: true,
    }).toArray();
    results = results.concat(docs);
    console.log('  [batch ' + (b + 1) + '/' + batches.length + '] ' + results.length + ' DG products found');
  }
  return results;
}

async function getAlcoholProductsForAccounts(productsColl, accountUUIDs) {
  var batches = chunkArray(accountUUIDs, BATCH_SIZE);
  var results = [];
  for (var b = 0; b < batches.length; b++) {
    var query = { accountUUID: { $in: batches[b] }, isAlcoholPresent: true };
    query['alcohol.' + SOAP_CODE + '.recipientType'] = { $exists: true, $ne: null };
    var docs = await productsColl.find(query).toArray();
    results = results.concat(docs);
  }
  return results;
}

// ── DRY-RUN / APPLY ───────────────────────────────────────────────────────────

async function runMigration(productsColl, carriersColl) {

  // ── Step 1: account list from carriers ────────────────────────────────────
  console.log('Step 1: Loading C2 carrier accounts...');
  var c2AccountUUIDs = await getC2AccountUUIDs(carriersColl);
  console.log('  ' + c2AccountUUIDs.length + ' accounts have C2 carrier configured');
  if (c2AccountUUIDs.length === 0) {
    console.log('Nothing to do.');
    mongoose.connection.close();
    return;
  }

  // ── Step 2: batched DG product scan ───────────────────────────────────────
  console.log('\nStep 2: Scanning DG products in batches of ' + BATCH_SIZE + ' accounts...');
  var allDgProds = await getDgProductsForAccounts(productsColl, c2AccountUUIDs);
  var dgProducts = allDgProds.filter(function(p) {
    return c2DgHasData(p.dangerousGoods && p.dangerousGoods[SOAP_CODE]);
  });
  console.log('  ' + dgProducts.length + ' products with C2 DG data (of ' + allDgProds.length + ' isDangerousGoodsPresent)');

  var dgAlreadyHaveC39 = dgProducts.filter(function(p) {
    return c2DgHasData(p.dangerousGoods && p.dangerousGoods[REST_CODE]);
  });
  var dgNeedsCopy = OVERWRITE ? dgProducts : dgProducts.filter(function(p) {
    return !c2DgHasData(p.dangerousGoods && p.dangerousGoods[REST_CODE]);
  });
  console.log('  Already have C39 DG data: ' + dgAlreadyHaveC39.length);
  console.log('  Need copy:                ' + dgNeedsCopy.length + (OVERWRITE ? ' (--overwrite)' : ''));

  // ── Step 3: batched alcohol scan ──────────────────────────────────────────
  console.log('\nStep 3: Scanning alcohol products in batches of ' + BATCH_SIZE + ' accounts...');
  var alcoholProducts = await getAlcoholProductsForAccounts(productsColl, c2AccountUUIDs);
  console.log('  ' + alcoholProducts.length + ' products with alcohol.C2.recipientType');

  var alcoholAlreadyHaveC39 = alcoholProducts.filter(function(p) {
    return hasValue(p.alcohol && p.alcohol[REST_CODE] && p.alcohol[REST_CODE].recipientType);
  });
  var alcoholNeedsCopy = OVERWRITE ? alcoholProducts : alcoholProducts.filter(function(p) {
    return !hasValue(p.alcohol && p.alcohol[REST_CODE] && p.alcohol[REST_CODE].recipientType);
  });
  console.log('  Already have C39 alcohol data: ' + alcoholAlreadyHaveC39.length);
  console.log('  Need copy:                     ' + alcoholNeedsCopy.length);

  // ── Per-category audit breakdown (mirrors the Slack audit queries) ─────────
  // Equivalent to:
  //   db.productsnews.distinct("accountUUID", { "dangerousGoods.C2.isOtherDangerousGoods": true })
  //   db.productsnews.distinct("accountUUID", { "dangerousGoods.C2.isBattery": true })
  //   db.productsnews.distinct("accountUUID", { isAlcoholPresent: true, "alcohol.C2.recipientType": { $exists: true } })
  var otherDgAccounts = Array.from(new Set(
    dgProducts
      .filter(function(p) { return p.dangerousGoods && p.dangerousGoods[SOAP_CODE] && p.dangerousGoods[SOAP_CODE].isOtherDangerousGoods === true; })
      .map(function(p) { return p.accountUUID; })
  ));
  var batteryAccounts = Array.from(new Set(
    dgProducts
      .filter(function(p) { return p.dangerousGoods && p.dangerousGoods[SOAP_CODE] && p.dangerousGoods[SOAP_CODE].isBattery === true; })
      .map(function(p) { return p.accountUUID; })
  ));
  var alcoholAccounts = Array.from(new Set(
    alcoholProducts.map(function(p) { return p.accountUUID; })
  ));

  console.log('\nAudit breakdown (account counts per DG category):');
  console.log('  isOtherDangerousGoods=true : ' + otherDgAccounts.length + ' accounts');
  console.log('  isBattery=true             : ' + batteryAccounts.length + ' accounts');
  console.log('  alcohol.recipientType set  : ' + alcoholAccounts.length + ' accounts');

  // ── Step 4: hazardous carrier settings ────────────────────────────────────
  console.log('\nStep 4: Carriers — hazardousTypeOfPackaging / hazardousPackagingMaterial');
  var c2HazCarriers = await carriersColl.find({
    carrierCode: SOAP_CODE,
    $or: [
      { hazardousTypeOfPackaging: { $exists: true, $ne: null } },
      { hazardousPackagingMaterial: { $exists: true, $ne: null } },
    ],
  }).toArray();
  console.log('  C2 carriers with hazardous settings: ' + c2HazCarriers.length);

  var hazAccountUUIDs = c2HazCarriers.map(function(c) { return c.accountUUID; }).filter(Boolean);
  var c39Carriers = await carriersColl.find(
    { carrierCode: REST_CODE, accountUUID: { $in: hazAccountUUIDs } }
  ).toArray();

  var c39ByAccount = {};
  c39Carriers.forEach(function(c) { c39ByAccount[c.accountUUID] = c; });

  var carriersWithC39    = c2HazCarriers.filter(function(c) { return !!c39ByAccount[c.accountUUID]; });
  var carriersWithoutC39 = c2HazCarriers.filter(function(c) { return !c39ByAccount[c.accountUUID]; });
  var carriersNeedsCopy  = OVERWRITE
    ? carriersWithC39
    : carriersWithC39.filter(function(c) {
        var c39 = c39ByAccount[c.accountUUID];
        return !hasValue(c39.hazardousTypeOfPackaging) && !hasValue(c39.hazardousPackagingMaterial);
      });

  console.log('  Accounts with matching C39 carrier:           ' + carriersWithC39.length);
  console.log('  Accounts missing C39 (cannot auto-copy):      ' + carriersWithoutC39.length);
  console.log('  Need copy:                                     ' + carriersNeedsCopy.length);

  // ── Scope summary ──────────────────────────────────────────────────────────
  var scope = {
    generatedAt: new Date().toISOString(),
    mode: MODE_APPLY ? 'apply' : 'dry-run',
    overwrite: OVERWRITE,
    auditByCategory: {
      note: 'Account UUIDs per DG type — mirrors the Slack audit queries',
      isOtherDangerousGoods: { accountCount: otherDgAccounts.length, accountUUIDs: otherDgAccounts },
      isBattery:             { accountCount: batteryAccounts.length,  accountUUIDs: batteryAccounts  },
      alcohol:               { accountCount: alcoholAccounts.length,  accountUUIDs: alcoholAccounts  },
    },
    products: {
      dgWithC2Data:        dgProducts.length,
      dgAlreadyHaveC39:    dgAlreadyHaveC39.length,
      dgNeedsCopy:         dgNeedsCopy.length,
      alcoholWithC2Data:   alcoholProducts.length,
      alcoholAlreadyC39:   alcoholAlreadyHaveC39.length,
      alcoholNeedsCopy:    alcoholNeedsCopy.length,
    },
    carriers: {
      c2WithHazardousSettings:        c2HazCarriers.length,
      haveMatchingC39:                carriersWithC39.length,
      missingC39_cannotAutoCopy:      carriersWithoutC39.length,
      needsCopy:                      carriersNeedsCopy.length,
      missingC39AccountUUIDs:         carriersWithoutC39.map(function(c) { return c.accountUUID; }),
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

  // Snapshot before-state (we already have these docs in memory).
  var beforeProductIds = {};
  dgNeedsCopy.forEach(function(p)      { beforeProductIds[p._id] = p; });
  alcoholNeedsCopy.forEach(function(p) { beforeProductIds[p._id] = p; });

  writeJson('dg_migration_before.json', {
    generatedAt: new Date().toISOString(),
    products: Object.keys(beforeProductIds).map(function(k) { return beforeProductIds[k]; }),
    carriers: carriersNeedsCopy,
  });
  console.log('\nBefore-state snapshot saved.');

  var results = { products: [], carriers: [], errors: [] };

  // Apply DG copy for products.
  console.log('\nApplying product DG copy (' + dgNeedsCopy.length + ' products)...');
  for (var di = 0; di < dgNeedsCopy.length; di++) {
    var prod = dgNeedsCopy[di];
    var dgC2 = prod.dangerousGoods && prod.dangerousGoods[SOAP_CODE];
    var setPayload = buildDgSetPayload(dgC2);
    try {
      await productsColl.updateOne({ _id: prod._id }, { $set: setPayload });
      results.products.push({ productUUID: prod.productUUID, accountUUID: prod.accountUUID, action: 'dg_copied', fields: Object.keys(setPayload) });
      if ((di + 1) % 100 === 0) console.log('  ' + (di + 1) + '/' + dgNeedsCopy.length + ' done');
    } catch (err) {
      results.errors.push({ productUUID: prod.productUUID, error: err.message });
      console.error('  Error on product ' + prod.productUUID + ': ' + err.message);
    }
  }

  // Apply alcohol copy for products.
  console.log('Applying product alcohol copy (' + alcoholNeedsCopy.length + ' products)...');
  for (var ai2 = 0; ai2 < alcoholNeedsCopy.length; ai2++) {
    var aProd = alcoholNeedsCopy[ai2];
    var recipientType = aProd.alcohol && aProd.alcohol[SOAP_CODE] && aProd.alcohol[SOAP_CODE].recipientType;
    var alcoholSet = {};
    alcoholSet['alcohol.' + REST_CODE + '.recipientType'] = recipientType;
    try {
      await productsColl.updateOne({ _id: aProd._id }, { $set: alcoholSet });
      results.products.push({ productUUID: aProd.productUUID, accountUUID: aProd.accountUUID, action: 'alcohol_copied', fields: Object.keys(alcoholSet) });
    } catch (err) {
      results.errors.push({ productUUID: aProd.productUUID, error: err.message });
      console.error('  Error on product ' + aProd.productUUID + ': ' + err.message);
    }
  }

  // Apply hazardous packaging copy for C39 carriers.
  console.log('Applying carrier hazardous packaging copy (' + carriersNeedsCopy.length + ' carriers)...');
  for (var ci = 0; ci < carriersNeedsCopy.length; ci++) {
    var c2c = carriersNeedsCopy[ci];
    var c39c = c39ByAccount[c2c.accountUUID];
    var carrierSet = {};
    if (hasValue(c2c.hazardousTypeOfPackaging))  carrierSet.hazardousTypeOfPackaging  = c2c.hazardousTypeOfPackaging;
    if (hasValue(c2c.hazardousPackagingMaterial)) carrierSet.hazardousPackagingMaterial = c2c.hazardousPackagingMaterial;
    try {
      await carriersColl.updateOne({ _id: c39c._id }, { $set: carrierSet });
      results.carriers.push({ accountUUID: c2c.accountUUID, action: 'carrier_copied', fields: Object.keys(carrierSet) });
    } catch (err) {
      results.errors.push({ accountUUID: c2c.accountUUID, error: err.message });
      console.error('  Error on carrier for account ' + c2c.accountUUID + ': ' + err.message);
    }
  }

  scope.applied = {
    productsDgCopied: dgNeedsCopy.length,
    alcoholCopied:    alcoholNeedsCopy.length,
    carriersCopied:   carriersNeedsCopy.length,
    errors:           results.errors.length,
  };

  writeJson('dg_migration_result.json', { scope: scope, results: results });
  console.log('\nApply complete.');
  console.log('  Product DG copies: ' + dgNeedsCopy.length);
  console.log('  Alcohol copies:    ' + alcoholNeedsCopy.length);
  console.log('  Carrier copies:    ' + carriersNeedsCopy.length);
  console.log('  Errors:            ' + results.errors.length);
  if (results.errors.length > 0) {
    console.error('\n!! Some records failed. Check dg_migration_result.json errors array.');
    process.exitCode = 1;
  }
  console.log('\nNext: run --verify to confirm C39 data matches C2.');
}

// ── VERIFY ────────────────────────────────────────────────────────────────────

async function runVerify(productsColl, carriersColl) {
  console.log('\nStep 1: Loading C2 carrier accounts...');
  var c2AccountUUIDs = await getC2AccountUUIDs(carriersColl);
  console.log('  ' + c2AccountUUIDs.length + ' accounts');

  var mismatches = [];
  var missing    = [];
  var ok         = [];

  // Products — DG
  console.log('\nStep 2: Verifying DG data in batches...');
  var verifyDgProds = await getDgProductsForAccounts(productsColl, c2AccountUUIDs);
  verifyDgProds.forEach(function(p) {
    var c2dg  = p.dangerousGoods && p.dangerousGoods[SOAP_CODE];
    var c39dg = p.dangerousGoods && p.dangerousGoods[REST_CODE];
    if (!c2DgHasData(c2dg)) return;

    if (!c2DgHasData(c39dg)) {
      missing.push({ type: 'product_dg', productUUID: p.productUUID, accountUUID: p.accountUUID, detail: 'C39 DG missing' });
      return;
    }
    var matched = true;
    DG_FIELDS.forEach(function(f) {
      if (hasValue(c2dg[f]) && c2dg[f] !== c39dg[f]) {
        mismatches.push({ type: 'product_dg', productUUID: p.productUUID, accountUUID: p.accountUUID, field: f, c2: c2dg[f], c39: c39dg[f] });
        matched = false;
      }
    });
    if (matched) ok.push({ type: 'product_dg', productUUID: p.productUUID });
  });
  console.log('  DG: ok=' + ok.length + ' missing=' + missing.length + ' mismatches=' + mismatches.length);

  // Products — Alcohol
  console.log('\nStep 3: Verifying alcohol data in batches...');
  var verifyAlcProds = await getAlcoholProductsForAccounts(productsColl, c2AccountUUIDs);
  verifyAlcProds.forEach(function(p) {
    var c2rt  = p.alcohol && p.alcohol[SOAP_CODE] && p.alcohol[SOAP_CODE].recipientType;
    var c39rt = p.alcohol && p.alcohol[REST_CODE]  && p.alcohol[REST_CODE].recipientType;
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
  console.log('\nStep 4: Verifying carrier hazardous settings...');
  var c2HazCarriers = await carriersColl.find({
    carrierCode: SOAP_CODE,
    $or: [
      { hazardousTypeOfPackaging: { $exists: true, $ne: null } },
      { hazardousPackagingMaterial: { $exists: true, $ne: null } },
    ],
  }).toArray();

  var c39Carriers = await carriersColl.find(
    { carrierCode: REST_CODE, accountUUID: { $in: c2HazCarriers.map(function(c) { return c.accountUUID; }) } }
  ).toArray();

  var c39ByAcc = {};
  c39Carriers.forEach(function(c) { c39ByAcc[c.accountUUID] = c; });

  c2HazCarriers.forEach(function(c2c) {
    var c39c = c39ByAcc[c2c.accountUUID];
    if (!c39c) {
      missing.push({ type: 'carrier', accountUUID: c2c.accountUUID, detail: 'No C39 carrier exists for this account' });
      return;
    }
    var matched = true;
    ['hazardousTypeOfPackaging', 'hazardousPackagingMaterial'].forEach(function(f) {
      if (hasValue(c2c[f]) && c2c[f] !== c39c[f]) {
        mismatches.push({ type: 'carrier', accountUUID: c2c.accountUUID, field: f, c2: c2c[f], c39: c39c[f] });
        matched = false;
      }
    });
    if (matched) ok.push({ type: 'carrier', accountUUID: c2c.accountUUID });
  });

  var report = {
    generatedAt: new Date().toISOString(),
    summary: { ok: ok.length, missing: missing.length, mismatches: mismatches.length },
    missing: missing,
    mismatches: mismatches,
    ok: ok,
    note: 'C39 fields read via native MongoDB driver. Mismatches before the schema/builder ' +
          'switch are expected — they represent pending code changes, not data errors.',
  };

  writeJson('dg_migration_verify.json', report);
  console.log('\nVerification summary:');
  console.log('  OK:          ' + ok.length);
  console.log('  Missing C39: ' + missing.length);
  console.log('  Mismatches:  ' + mismatches.length);
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
