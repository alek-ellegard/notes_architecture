# base-domain

[details](./analysis.md) | [testing](./docs/testing-architecture.md)

## architecture

**[Orchestrator](./src/base_domain/orchestrator.py)** wires domains via callbacks:

- `_wire_pipeline()`: chains domains → `prev.on_handled(next.handle)`
- `_wire_monitoring()`: hooks monitor → `domain.on_success(monitor.on_success)` + `on_error`
- `_wire_completion()`: final domain → `domains[-1].on_handled(monitor.on_pipeline_complete)`

**[BaseDomain](./src/base_domain/domains/base_domain.py)** (ABC, Generic[TInput, TOutput]):

- Template: `handle()` → `_execute()` → `handled()` → `success()`/`error()`
- Callback registration: `on_handled()`, `on_success()`, `on_error()`
- Callback emission: `handled()`, `success()`, `error()`

**[Monitor](./src/base_domain/domains/monitor.py)**:

- Tracks success/error counts, durations, pipeline completions
- Callbacks: `on_success()`, `on_error()`, `on_pipeline_complete()`

**Pipeline flow**: ZMQ → Processor → Metrics → Exporter (each domain forwards via `handled()`)

## testing

**Base class**: `BaseDomainTest[TInput, TOutput]` provides 6 standard tests for all domains:
- Inheritance, attributes, methods existence
- Callback registration (`on_handled`, `on_success`, `on_error`)
- Handle flow (`handle()` → `_execute()` → `handled()` → `success()`)
- Error handling and error callback emission

**Writing tests**: Set `DOMAIN_CLASS`, override `_create_test_input()`, inherit all standard tests automatically.

**Run tests**: `make test` (all) | `make test-f f=<file>` (specific) | `make test-integration` (integration)
