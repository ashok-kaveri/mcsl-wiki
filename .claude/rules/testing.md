# Testing Rules

- Framework: Jest (never Vitest or Mocha)
- Use ts-jest only if `tsconfig.json` exists — do not assume TypeScript
- Tests live in `test/` as a sibling to `src/`, mirroring its structure
  - `src/services/user.js` → `test/services/user.test.js`
- Unit tests: `*.test.js` / `*.test.ts`
- Integration tests: `*.spec.js` / `*.spec.ts`
- Shared helpers and factories live in `test/helpers/`
- Always `beforeEach(() => jest.clearAllMocks())`
- Use `jest.spyOn` when the original mostly runs, `jest.fn()` for pure stubs
- Use `jest.mock('module-name')` at top of file for module-level mocks
- Never use real network calls — use msw to mock HTTP at the boundary
- Use `jest.useFakeTimers()` — never real `setTimeout` or `sleep` in tests
- Always `async/await` — never `done` callback style
- No `test.only` or `describe.only` in committed code
- Test behavior, not implementation details
- Never mock the module under test