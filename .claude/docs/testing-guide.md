# Testing Guide

## Framework & Tools
- Jest as the test framework
- Testing Library for React component tests
- msw (Mock Service Worker) for mocking HTTP calls
- @faker-js/faker for generating test data
- ts-jest for TypeScript projects (check for tsconfig.json first)

## File Conventions

Tests live in `test/` as a sibling to `src/`, mirroring its structure:

```
my-project/
├── src/
│   ├── services/
│   │   └── user.js
│   └── utils/
│       └── format.js
└── test/
    ├── services/
    │   └── user.test.js
    ├── utils/
    │   └── format.test.js
    ├── helpers/          ← shared factories, mocks
    └── e2e/
```

- `*.test.js` / `*.test.ts` — unit tests
- `*.spec.js` / `*.spec.ts` — integration tests
- `test/helpers/` — factories, shared mocks, custom matchers
- `test/e2e/` — end-to-end tests

## JavaScript vs TypeScript

- Do not assume TypeScript — check if `tsconfig.json` exists before using TS syntax
- In JS projects: use JSDoc for type hints if needed, never TS syntax
- In TS projects: configure ts-jest, enable strict mode in jest config
- Never mix `.js` and `.ts` test files in the same project

## Writing Tests

```js
// ✅ Good
describe('createUser', () => {
  beforeEach(() => jest.clearAllMocks());

  it('should return a user with the given name', async () => {
    const repo = mockUserRepo();
    const mailer = mockMailer();

    const user = await createUser('Alice', repo, mailer);

    expect(user.name).toBe('Alice');
  });

  it('should send a welcome email after creation', async () => {
    const repo = mockUserRepo();
    const mailer = mockMailer();

    await createUser('Alice', repo, mailer);

    expect(mailer.sendWelcome).toHaveBeenCalledTimes(1);
  });

  it('should throw if repo fails', async () => {
    const repo = mockUserRepo({ shouldFail: true });
    const mailer = mockMailer();

    await expect(createUser('Alice', repo, mailer))
      .rejects.toThrow('Failed to save user');
  });
});

// ❌ Bad — tests implementation, no isolation
it('creates a user', async () => {
  const result = await createUser('Alice');   // no injected deps
  expect(db.users.length).toBe(1);            // testing DB state
});
```

- One assertion concept per test
- Use `describe` to group by function or feature
- Use `it('should...')` — describe expected behavior
- No logic in tests (no if/else, no loops) — keep tests declarative
- `toBe` for primitives, `toEqual` for objects/arrays

## Mocking

```js
// Module-level mock — top of file
jest.mock('../services/mailer');

// Spy — original mostly runs
jest.spyOn(logger, 'error');

// Stub — full replacement
const sendEmail = jest.fn().mockResolvedValue({ ok: true });

// Reset between tests
beforeEach(() => jest.clearAllMocks());
```

- Never mock the module under test
- Mock at the boundary: HTTP, DB, file system, timers
- Use msw for HTTP — never let real network calls through in unit/integration tests

## Test Data

```js
// ✅ Factory function
function makeUser(overrides = {}) {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    ...overrides,
  };
}

// ✅ Deterministic when needed
faker.seed(42);

// ❌ Never copy-paste raw objects across tests
const user = { id: '123', name: 'Alice', email: 'alice@example.com' };
```

## Timers & Async

```js
// ✅ Fake timers
beforeEach(() => jest.useFakeTimers());
afterEach(() => jest.useRealTimers());

it('should retry after 1 second', () => {
  startRetry();
  jest.advanceTimersByTime(1000);
  expect(mockFn).toHaveBeenCalledTimes(2);
});

// ❌ Never sleep
await new Promise(r => setTimeout(r, 1000));
```

## Coverage

- Minimum 80% enforced in CI via `--coverage`
- 100% target for `src/utils/` and `src/services/`
- Coverage is a floor, not a goal — don't write hollow tests to hit numbers

## What NOT to Do

- No `test.only` or `describe.only` in committed code
- No reliance on test execution order — every test must be fully independent
- No snapshots for logic-heavy output — snapshots are for UI structure only
- Don't test private functions directly — test via the public API
- Never use `done` callback style for async — always `async/await`
