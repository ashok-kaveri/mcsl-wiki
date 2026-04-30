# Standing Rules — MCSL Code Analysis

## Rule 1 — Resolve carrier name to Adapter Class before opening any file
Look up the carrier mentioned in the ticket in `wiki/architecture/carriers-and-adapters.md`.
Read the **Adapter Class** column. That class name is your entry point — use it to locate the correct file.
Do not navigate carrier folders by name or intuition.

**Why**: Australia Post has three separate adapters (eParcel, MyPost Business, MyPost OAuth) in the same folder.
In MCSL 377 the AI analyzed MyPost when the ticket was about eParcel, then self-corrected but kept HIGH confidence.
The carrier table would have prevented this before the first file was opened.

## Rule 2 — Resolve UI feature to client component before opening any server file
Look up the feature mentioned in the ticket in the relevant `wiki/modules/frontend/*.md` page.
That page maps UI features to their client-side component paths — use it as the entry point before reading any server models or carrier builders.

| Ticket involves | Consult |
|----------------|---------|
| Order summary, package editing, packing summary | `wiki/modules/frontend/orders-ui.md` |
| Packaging settings, box inventory | `wiki/modules/frontend/packaging-ui.md` |
| Shipping settings, carrier config UI | `wiki/modules/frontend/shipping-ui.md` |
| App settings, general settings | `wiki/modules/frontend/settings-ui.md` |

**Why**: In MCSL 377, ZI-060 (HS code per-package editing) was analysed entirely at the server layer — schema changes, packaging.js, carrier builders. The actual fix was in 3 client-side components (`addOrEditPackage.js`, `OrderSummaryContainerNew.js`, `PackingSummary.js`). Zero overlap with the AI's suggested files. The frontend module pages existed and would have pointed directly to the right components.

## Rule 3 — After identifying the primary fix file, check the coupling map and migration list

Two mandatory checks before declaring an analysis complete:

**Check 1 — Co-change partners**
Look up the primary fix file in `wiki/architecture/coupling-map.md`. Any file that co-changes with it frequently is a candidate companion file. Pay particular attention to `featureLoader.js` entries — they appear as consistent co-change partners across carriers (delhivery, fedex, shopify, batch) and must be updated whenever the domain file they load changes.

**Check 2 — Migration required?**
If the fix touches `config.json` to add a carrier service code, check `server/db-migrations/` for an existing seeding migration (e.g. `add-aupost-services.js`, `add_easypost_service_codes.js`). If the service code needs to exist in the database (not just the config), a new migration is required. Note: migrations are **excluded** from the co-change graph by design — the coupling map will never surface this.

| Fix type | Companion to check |
|----------|--------------------|
| Any domain file with a co-located `featureLoader.js` | Update `featureLoader.js` in the same directory |
| Adding a carrier service code to `config.json` | Add a seeding migration in `server/db-migrations/` |
| Adding a new carrier toggle to `featureToggles.json` | Cross-check `config.json` (co-changes 105 times) |

**Why**: In MCSL 377, ZI-015 correctly identified `processPackingResult.js` but missed `featureLoader.js` — a file that co-changes with packaging domain files. ZI-057 correctly identified the `config.json` change for RoyalMail48 but missed the required seeding migration. The coupling map would have caught ZI-015; only an explicit migration check catches ZI-057 since migrations are excluded from the graph.

## Rule 4 — For order field sync issues, check existing listeners before proposing new architecture

When a ticket is about an order field not syncing (notes, tags, addresses, line items), read `wiki/patterns/event-sourcing.md` and check `server/src/shared/listeners/` for an existing listener before proposing any solution.

The event system already has `OrderUpdatedWebhookReceived` (`server/src/shared/orders/events/index.js`). Listeners subscribe to this event and handle specific field updates. An existing listener may only need extending — not a new service.

```
ls server/src/shared/listeners/
grep -r "OrderUpdated\|orders/updated" server/src/shared/listeners/
```

Only propose a new microservice or external service integration if no existing listener covers the event.

**Why**: In MCSL 377, ZI-007 (order notes not syncing) prompted a suggestion to extend an external order-updates microservice diff contract. The actual fix was extending the existing `orderTagsUpdatingListener.js` (renamed `orderFieldsUpdatingListener.js`) to also handle notes — 5 files, ~60 lines. The listener directory was never checked.

## Rule 5 — For toggle-gated fixes, explicitly trace toggle=OFF before stating confidence

When a fix is behind a feature toggle, write out both paths before assigning a confidence level:

- **toggle=ON**: expected new behaviour
- **toggle=OFF**: must exactly match current production behaviour — does any existing logic (minimum value floors, fallback calculations, default paths) still apply unchanged?

Confidence cannot be HIGH if toggle=OFF behaviour has not been traced. If toggle=OFF interacts with other existing logic, name that interaction explicitly in the analysis.

**Why**: In MCSL 377, ZI-025 and ZI-024 (BlueDart declared value fixes) had files correctly identified, but QA found staging/live mismatches when toggle=OFF because the new code path intersected with the existing minimum customs value floor in ways the analysis never traced.

## Rule 6 — For carrier/label errors, rule out customer configuration before writing code analysis

Before writing a code-level analysis for any carrier error (declared value exceeded, wrong rate, service not found, 0-price issue), check whether existing customer configuration could explain the symptom:

1. Does the account have a custom declared value configured? Is it country-specific?
2. Is there a feature toggle already ON/OFF for this account that changes the behaviour?
3. Does the symptom only affect one store, or multiple stores?

If any answer is "possibly yes", state *"possible configuration issue — verify before code analysis"* and describe which setting to check. Do not produce a full code analysis until a configuration cause has been ruled out.

**Why**: In MCSL 377, ZI-051 (FedEx REST declared value exceeds limit) received a full code analysis suggesting changes to per-package declared value logic. The actual cause was the customer's country-specific custom declared value not matching the recipient country — no code change was required. The analysis produced a misleading user story and wasted dev time.
