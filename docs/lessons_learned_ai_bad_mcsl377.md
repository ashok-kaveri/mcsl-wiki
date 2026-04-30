# AI Analysis Failures — MCSL 377 Lessons Learned

**Source**: 8 cards labeled `AI: BAD` in the SL MCSL 377: Iteration backlog lane on ph-WIP  
**Date**: 2026-04-30

---

## Card-by-Card Summary

| Card | AI Suggested | What Actually Happened | Gap |
|------|-------------|----------------------|-----|
| **ZI-058** — eParcel bulk label delay | 5-sec hardcoded delay in `helperFunctions.js`; `Promise.all` for bulk | Analysis was initially for **MyPost**, not eParcel; had to be corrected mid-analysis | Confused two similar components in the same carrier folder |
| **ZI-025** — Shipping charges in declared value | Correct files (blueDartRequestBuilder, helperFunctions, labelBuilder, customLabel) | Files matched but QA found: staging/live mismatch when toggle=OFF; multi-package+0-price showed `0` for both packages instead of `100+shipping` and `0` | Did not trace toggle=OFF interaction with the existing minimum customs value logic |
| **ZI-024** — Incorrect declared value for 0-price items | Same file set; `ZERO_PRICE_DECLARED_VALUE = 0.1` | Constant changed from `0.1` → `1` after QA; multi-package distribution needed adjustment | Wrong constant value; didn't trace multi-package arithmetic through the distribution path |
| **ZI-060** — HS code editing at package level | Add `harmonizationCodeOverride` to `Packages` schema; modify `packaging.js`; update carrier builders | Actual fix: 3 **client-side** files (`addOrEditPackage.js`, `OrderSummaryContainerNew.js`, `PackingSummary.js`) + `printSettingsHelperFunctions.js` + toggle. No schema change, no carrier changes | Analysed server models and carrier builders; missed the client-side UI layer entirely. QA also found a field swap (HS code showed price, price showed HS code) |
| **ZI-015** — Declared value resets after manual package edit | Fix `processPackingResult.js:155`; import `getEnhanceDeclaredValue` | `processPackingResult.js` was correct, but also needed `featureLoader.js` (missed). QA found additional bug: product-level custom value overridden by shipping settings % after edit | Missed the feature loader; one acceptance criterion (checkout-discounted price) was left unimplemented |
| **ZI-007** — Order notes not synced after import | Extend **external** order-updates microservice diff contract to include `note` field | Actual fix: extend the **existing in-app** `orderTagsUpdatingListener.js` (renamed to `orderFieldsUpdatingListener.js`) — no microservice change | Did not search for existing listeners before proposing new architecture |
| **ZI-057** — RoyalMail48ParcelDailyRateService missing | Add one entry to `config.json` (correct) | `config.json` +1 line (correct), but also required a **migration** that was not identified | Config change identified correctly; missed the required migration step to deploy it |
| **ZI-051** — FedEx REST declared value exceeds limit | Code analysis framing: "fix per-package declared value logic in FedEx REST" | Customer configuration issue — no code change required; ticket was misread as a bug | Accepted the customer's symptom description at face value without validating whether existing config (country-specific custom declared value) could explain it |

---

## Failure Patterns

### Pattern 1 — Wrong carrier/component when similar files co-exist (ZI-058)
When a carrier folder contains multiple similar API files (e.g., `australiaPost/` has both eParcel and MyPost files), the AI latched onto the wrong one. Confidence was marked HIGH after self-correction, hiding the initial error.

### Pattern 2 — Did not trace the toggle=OFF / edge-case interaction paths (ZI-025, ZI-024)
The AI traced the happy path (toggle ON, single package, non-zero price) correctly but did not trace what happens when the new code intersects with *other* existing logic: the minimum customs value floor, multi-package value splitting, or the case where shipping is also 0.

### Pattern 3 — Analysed the wrong layer of the stack (ZI-060)
The AI focused on server-side models and carrier request builders. The actual fix was in client-side React components. Three of the five changed files were front-end UI components the AI never examined.

### Pattern 4 — Missed a required companion file (ZI-015, ZI-057)
In both cases the primary file was identified correctly, but a second required file was missed: a feature loader (`featureLoader.js`) and a deployment migration. The AI stopped after finding the logical fix and did not check what else needed to change for the fix to take effect.

### Pattern 5 — Missed existing infrastructure and proposed over-engineering (ZI-007)
The AI proposed extending an external microservice when an existing in-app listener (`orderTagsUpdatingListener.js`) already handled the same event and only needed a small extension. The correct fix was ~60 lines; the AI's approach would have required cross-service contract changes.

### Pattern 6 — Accepted wrong bug framing without validation (ZI-051)
The customer described a symptom that sounded like a code bug. The AI produced a code analysis accordingly. The actual root cause was a mis-configured customer setting. The AI should have checked whether the existing config model could explain the behaviour before writing code-level suggestions.

---

## Prompting Guidelines for Next Analysis

### Rule 1 — Name the exact file you are analysing before anything else
When a carrier (or feature) has multiple similar files in the same folder, open each one and explicitly state at the top: *"This analysis is for `australiaPostShipmentHelper.js` (eParcel), not `myPostShipmentHelper.js`."* Do not rely on folder-level context.

### Rule 2 — Trace toggle=OFF and multi-instance paths before declaring confidence HIGH
For any toggle-gated fix, write out explicitly:
- Behaviour when toggle=ON: …
- Behaviour when toggle=OFF: … (does it interact with minimum-value logic, fallback paths, or other toggles?)
- Behaviour for N=2 packages where one has price=0: …

Only mark HIGH confidence if all three are traced.

### Rule 3 — Before analysing a server file, check for a client-side counterpart
When the issue involves the Order Summary UI, package editing, or any field displayed to the user, **always read the corresponding client component** before writing the analysis:
- `client/src/components/form/views/summary/order-summary/`
- `client/src/components/form/views/bulkActions/`

Do not submit a HIGH-confidence analysis of a UI-visible feature based on server files alone.

### Rule 4 — After identifying the primary fix file, search for its loaders and callers
Run `grep -r "<filename>" server/src/shared/` to find initializers, feature loaders, and event registrations that also reference the file. If a `featureLoader.js` or `listeners/index.js` imports the file, it likely needs updating too.

### Rule 5 — Before proposing new architecture, search for existing handlers
Before suggesting any new service, webhook, or microservice integration, grep for:
```
grep -r "orderTagsUpdating\|orderFieldsUpdating\|listener\|event.*order" server/src/shared/listeners/
grep -r "events/index" server/src/shared/orders/
```
If a listener or event already handles the same Shopify webhook, extend it — do not propose a new integration.

### Rule 6 — For config.json changes, check for a migration requirement
After proposing a `config.json` or `featureToggles.json` change, check:
```
ls server/src/migrations/  (or equivalent)
grep -r "config\.carriers\." server/src/shared/  # find if config values are cached/seeded
```
If values are seeded into a database at deploy time, a migration entry is required alongside the config change.

### Rule 7 — Validate bug framing before writing code analysis
For carrier label errors (declared value, rate errors), before starting code analysis, check:
1. Is there a custom declared value configured in the account settings?
2. Is the issue country-specific or carrier-specific only for that account?
3. Does changing configuration (not code) resolve the symptom for the affected store?

If the answer to any of these is "possibly yes", state *"possible configuration issue — verify before code fix"* in the analysis.

### Rule 8 — After stating a HIGH confidence, list what you did NOT check
Every HIGH-confidence analysis must end with a short "Not verified" list:
- Files I did not read (and why they may be relevant)
- Code paths I did not trace (toggle=OFF, multi-package, edge values)
- Required deployment artefacts (migrations, config seeds, client components)

This prevents false confidence from being propagated to the dev picking up the card.
