# Coding Standards

## Naming Conventions

- Variables and functions: `camelCase`
- Classes and components: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private/internal helpers: prefix with `_` only when truly internal to a module
- Name functions as verbs: `getUser`, `formatDate`, `validateEmail`
- Name booleans as questions: `isLoading`, `hasError`, `canSubmit`
- Be explicit over clever: `getUserById` not `fetch`, `filteredUsers` not `data2`
- Avoid abbreviations unless universally understood (`id`, `url`, `ctx` are fine; `usrRec` is not)

## Variables

- Use `const` by default
- Use `let` only when reassignment is needed
- Never use `var`
- Destructure early to reduce noise:
  ```js
  // ✅
  const { id, name, email } = user;

  // ❌
  const id = user.id;
  const name = user.name;
  ```
- No magic numbers — name your constants:
  ```js
  // ✅
  const MAX_RETRY_ATTEMPTS = 3;

  // ❌
  if (attempts > 3) { ... }
  ```

## Functions

- Do one thing — if you need "and" to describe it, split it
- Keep functions under ~20 lines where possible
- Limit parameters to 3 max — use an options object beyond that:
  ```js
  // ✅
  function createUser({ name, email, role = 'user' }) { ... }

  // ❌
  function createUser(name, email, role, createdAt, isAdmin) { ... }
  ```
- Prefer pure functions — same input, same output, no side effects
- Prefer `async/await` over `.then()` chains
- Never mix callbacks and promises in the same flow
- Return early to avoid deep nesting:
  ```js
  // ✅
  function process(user) {
    if (!user) return null;
    if (!user.isActive) return null;
    return doWork(user);
  }

  // ❌
  function process(user) {
    if (user) {
      if (user.isActive) {
        return doWork(user);
      }
    }
  }
  ```

## Modules & Exports

- One primary responsibility per module
- Use named exports — avoid default exports:
  ```js
  // ✅
  export function getUser() { ... }
  export function createUser() { ... }

  // ❌
  export default function() { ... }
  ```
- Export only what consumers need — keep internals unexported
- No circular imports — if you need one, the module boundary is wrong

## Error Handling

- Always handle promise rejections — no floating `await` without try/catch
- Throw `Error` objects, never strings:
  ```js
  // ✅
  throw new Error('User not found');

  // ❌
  throw 'User not found';
  ```
- Use specific error types where it matters:
  ```js
  class NotFoundError extends Error {
    constructor(message) {
      super(message);
      this.name = 'NotFoundError';
      this.statusCode = 404;
    }
  }
  ```
- Let errors bubble to a central handler — don't swallow them silently:
  ```js
  // ❌ Never do this
  try {
    await doSomething();
  } catch (err) {
    // nothing
  }
  ```
- Log errors with context, not just the message

## Async & Promises

- Always `async/await` — never raw `.then()` chains
- Never use `new Promise()` wrapper around an already-async function
- Use `Promise.all()` for parallel async operations:
  ```js
  // ✅
  const [user, orders] = await Promise.all([getUser(id), getOrders(id)]);

  // ❌ Sequential when parallel is possible
  const user = await getUser(id);
  const orders = await getOrders(id);
  ```
- Always `await` inside try/catch at the top of the call chain

## Comments

- Write comments that explain *why*, not *what* — the code already shows what
- Use JSDoc for public-facing functions in JS projects (no TypeScript):
  ```js
  /**
   * Fetches a user by ID from the database.
   * Returns null if the user does not exist.
   *
   * @param {string} id
   * @returns {Promise<User|null>}
   */
  async function getUserById(id) { ... }
  ```
- Delete commented-out code — use git history instead
- Mark unfinished work with `// TODO:` and include context

## Formatting

- Formatting is handled by Prettier — do not argue about it, do not override it
- Linting is handled by ESLint — fix lint errors, do not disable rules without discussion
- 2-space indentation
- Single quotes for strings
- Trailing commas in multi-line structures
- Semicolons: follow the project's existing `.eslintrc` — do not mix

## Imports

- Group imports in this order, separated by a blank line:
  1. Node built-ins (`fs`, `path`)
  2. External packages (`express`, `lodash`)
  3. Internal modules (`../services/user`)
- Use absolute imports where the project supports it — avoid `../../..` chains
- Never import from a layer below you:
  - `api/` may import from `services/`
  - `services/` may import from `models/`
  - `utils/` imports from nothing internal

## Low Blast Radius Changes

A good change is localized. Before making changes across many files, ask:

1. **Is this logic duplicated?** → Extract it to utils/ or a shared module
2. **Is this config scattered?** → Centralize it in config/constants
3. **Is this a cross-cutting concern?** → Handle it as middleware or a wrapper
4. **Is this a missing abstraction?** → Create the right layer, then use it

Red flags that a refactor is needed first:
- Same string/value appears in 5+ files
- Same try/catch pattern in every route
- Same transformation applied in multiple services
- A rename requires touching more than 2 files

The test: can you explain this change in one sentence that references one place?
If not, the abstraction is missing.

## Low Blast Radius Changes — Examples

### ❌ High blast radius — logic scattered at call sites

A date format change requires editing 12 files:
// src/api/orders.js
const label = date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });

// src/api/invoices.js
const label = date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });

// src/api/reports.js
const label = date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });

### ✅ Low blast radius — one owner, one change

// src/utils/date.js
export function formatDisplayDate(date) {
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
}

// everywhere else
import { formatDisplayDate } from '../utils/date';
const label = formatDisplayDate(date);

// Now a format change = 1 file, 1 test.

---

### ❌ High blast radius — cross-cutting concern duplicated

Every route handler repeats the same try/catch + logging:
// src/api/users.js
router.get('/:id', async (req, res) => {
  try {
    const user = await getUser(req.params.id);
    res.json(user);
  } catch (err) {
    logger.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Same pattern in orders.js, invoices.js, reports.js ...

### ✅ Low blast radius — wrap it once

// src/middleware/asyncHandler.js
export const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

// src/middleware/errorHandler.js
export function errorHandler(err, req, res, next) {
  logger.error(err);
  res.status(err.statusCode || 500).json({ error: err.message });
}

// src/api/users.js — now clean
router.get('/:id', asyncHandler(async (req, res) => {
  const user = await getUser(req.params.id);
  res.json(user);
}));

// Error handling change = 1 file. Adding a route = 0 boilerplate.

---

### ❌ High blast radius — config scattered

A role rename requires touching every file that checks roles:
if (user.role === 'admin') { ... }      // api/users.js
if (user.role === 'admin') { ... }      // api/orders.js
if (req.user.role === 'admin') { ... }  // middleware/auth.js

### ✅ Low blast radius — centralized constants

// src/config/roles.js
export const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest',
};

// everywhere
import { ROLES } from '../config/roles';
if (user.role === ROLES.ADMIN) { ... }

// A role rename = 1 file.

---

### The refactor-first rule

If Claude needs to change the same pattern in more than 3 files:
1. STOP — do not make the change across all files
2. Create the abstraction (util, middleware, config, wrapper)
3. Replace all existing call sites with the abstraction
4. Make the change once in the abstraction

The change PR and the refactor PR should ideally be separate commits.

## Change Philosophy
- Before making a change across multiple files, stop and identify
  if a missing abstraction would reduce the blast radius
- Prefer refactoring to the right structure first, then making the change once
- A change touching more than 4 files needs a justification comment