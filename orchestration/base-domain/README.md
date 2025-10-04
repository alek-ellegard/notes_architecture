# base-domain

[details](./analysis.md)

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
