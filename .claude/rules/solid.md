# SOLID Principles

## S — Single Responsibility Principle
- Each file/module exports ONE primary concern
- A function does one thing; if you need "and" to describe it, split it
- Route handlers only handle HTTP — delegate business logic to services
- Services contain business logic only — no HTTP, no DB queries directly
- Keep files under 200 lines; if longer, it likely has multiple responsibilities

## O — Open/Closed Principle
- Extend behavior via composition and callbacks, not by editing existing functions
- Use strategy pattern for swappable behaviors (e.g. different payment providers)
- Prefer adding new modules over modifying stable ones
- Configuration objects over hardcoded conditionals for varying behavior
- Never modify a tested, stable function to add a new use case — wrap it instead

## L — Liskov Substitution Principle
- Subclasses/implementations must honor the contract of their parent/interface
- If a function accepts an interface, any implementation must work without changes
- Never throw errors or return different shapes from what the interface declares
- Avoid overriding parent methods in ways that change expected behavior
- Prefer composition over inheritance to avoid fragile hierarchies

## I — Interface Segregation Principle
- Define narrow TypeScript interfaces — only what the consumer needs
- Never force a module to depend on methods it doesn't use
- Split fat interfaces into smaller, focused ones
- A service that only reads should not receive a write-capable repository
- Props/params objects should only contain what the function uses

## D — Dependency Inversion Principle
- High-level modules depend on abstractions (interfaces/types), not concretions
- Inject dependencies — never instantiate services/clients inside functions
- Pass DB clients, loggers, and HTTP clients in via constructor or params
- Use factory functions or DI containers to wire dependencies at the top level
- Never import a concrete implementation deep inside business logic