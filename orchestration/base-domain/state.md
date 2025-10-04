# Architecture Analysis - Async Event-Driven Pipeline

## Pattern: Async Observable Pipeline with Template Method

The architecture implements an **async callback-based data processing pipeline** with cross-cutting observability concerns separated via dual callback chains. The entire system runs on Python's asyncio event loop.

---

## Core Components

### 1. BaseDomain (base_domain.py:10-86)

Abstract base class implementing **Template Method** + **Observer** patterns with async/await:

**Generic Typing:**
```python
class BaseDomain(ABC, Generic[TInput, TOutput]):
```
- Type-safe domain contracts using TypeVar
- Each domain specifies its input/output types explicitly
- Architecture remains agnostic to concrete types

**Lifecycle Methods:**
- `initialize()` - Abstract sync initialization hook (domain-specific setup)
- `_execute(data: TInput) -> TOutput` - Abstract async business logic

**Template Method (handle):**
```python
async def handle(self, data: TInput) -> None:
    result = await self._execute(data)  # 1. Execute domain logic
    await self.handled(result)          # 2. Forward to next domain
    await self.success({...})           # 3. Report success metrics
```
- Automatic timing, error handling, and callback orchestration
- Domains only implement `_execute()` - framework handles rest

**Data Flow Callbacks (async):**
- `on_handled(callback)` - Register next stage in pipeline (sync registration)
- `handled(data)` - Trigger all registered data callbacks (async)

**Monitoring Callbacks (async):**
- `on_success(callback)` / `on_error(callback)` - Register observers (sync)
- `success(event)` / `error(event)` - Emit monitoring events (async)

**Key Design:** Separates "data flow" from "observability" using two independent async callback chains.

---

### 2. Orchestrator (orchestrator.py:13-65)

**Responsibility:** Wire up the async system at initialization

**Three-phase initialization:**

1. **`_wire_pipeline()`** (line 34-47) - Creates async data pipeline chain:
   ```
   ZMQManager → ProcessorManager → MetricsManager → ExporterManager
   ```
   Each domain's `on_handled` connects to next domain's async `handle` method

2. **`_wire_monitoring()`** (line 49-53) - Attaches Monitor to all domains:
   ```
   All domains → Monitor.on_success & Monitor.on_error (async callbacks)
   ```

3. **`_wire_completion()`** (line 55-57) - Wires final domain completion:
   ```
   ExporterManager → Orchestrator.on_pipeline_complete (async)
   ```
   Tracks successful pipeline completions via `completed_pipelines` counter

4. **Domain initialization** (line 31-32) - Calls `initialize()` on each domain

**Async Methods:**
- `on_pipeline_complete(result: bool)` - Async callback counting completions
- No `start()` method here - managed by Application layer

**Note:** Missing initialization of `not_completed_pipelines` counter (used in line 64)

---

### 3. Domain Pipeline (4 async domains)

| Domain | Type Signature | Initialization | Responsibility |
|--------|---------------|----------------|----------------|
| **ZMQManager** | `BaseDomain[bytes, dict]` | Binds socket, creates message_loop task | Receives ZMQ messages, deserializes JSON |
| **ProcessorManager** | `BaseDomain[str, str]` | Pass | Processes string data (currently passthrough) |
| **MetricsManager** | `BaseDomain[str, dict]` | Pass | Extracts metrics into dict |
| **ExporterManager** | `BaseDomain[dict, bool]` | Pass | Exports data, returns success bool |

**ZMQManager Special Features:**
- Uses `zmq.asyncio.Context()` for async socket operations
- `initialize()` creates background task: `asyncio.create_task(self.message_loop())`
- `message_loop()` runs continuously: `await socket.recv()` → `await self.handle(message)`
- Binds to `env.ZMQ_ADDRESS` (tcp://host:port)

**Type Flow:**
```
bytes → dict → str → str → dict → bool
 ZMQ     ZMQ    Proc  Proc  Metrics  Export
```

**Note:** Type mismatch between ZMQManager output (`dict`) and ProcessorManager input (`str`)

---

### 4. Monitor (monitor.py:4-54)

**Centralized async observability collector** using:

- `defaultdict(int)` for counters
- `deque(maxlen=1000)` for bounded duration tracking (memory-safe)
- Nested `defaultdict` for error type breakdown

**Async Callbacks:**
```python
async def on_success(event: dict) -> None:
    key = f"{event['domain']}.{event['operation']}"
    self.success_counts[key] += 1
    self.success_durations[key].append(event["duration"])

async def on_error(event: dict) -> None:
    key = f"{event['domain']}.{event['operation']}"
    self.error_counts[key] += 1
    self.error_types[key][event["error_type"]] += 1
```

**Event Structure:**
```python
{
    "domain": "ProcessorManager",
    "operation": "handle",
    "duration": 0.0023  # seconds
}
```

**Sync Method:**
- `get_metrics()` - Compute and return aggregated metrics

---

### 5. Application Lifecycle (entrypoint.py:12-65)

**Async application using `asyncio.run()`:**

```python
class Application:
    async def run(self) -> None:
        # 1. Setup logging
        # 2. Initialize orchestrator (wire callbacks)
        # 3. Register async signal handlers (SIGINT/SIGTERM)
        # 4. Start orchestrator (runs ZMQ message loop)
        # 5. On shutdown: cleanup and log metrics
```

**Key Features:**
- `asyncio.get_running_loop().add_signal_handler()` for graceful async shutdown
- Main loop is `await orchestrator.start()` which runs ZMQ message_loop indefinitely
- Logs `completed_pipelines` count on exit
- Structured logging with timestamps

**Entry point:**
```python
def main() -> None:
    app = Application()
    asyncio.run(app.run())  # Starts event loop
```

---

## Current State

### ✅ Complete

- **Async architecture** - Entire pipeline runs on asyncio event loop
- **Generic typing** - Type-safe domain contracts with TypeVar
- **Template method pattern** - `handle()` orchestrates execution, callbacks, monitoring
- **Dual callback chains** - Data flow separate from observability
- **Auto-forwarding** - `handle()` automatically calls `handled(result)`
- **Auto-monitoring** - `handle()` automatically emits success/error events
- **ZMQ integration** - Async message receiving with `zmq.asyncio`
- **Domain initialization** - `initialize()` hook for setup
- **Pipeline completion tracking** - Counts successful completions
- **Graceful shutdown** - Async signal handlers
- **Integration testing** - Full test with ZMQ publisher
- **Make commands** - `test-integration`, `test-integration-zmq`, `publish`

### ⚠️ Issues/Improvements Needed

1. **Type mismatch in pipeline:**
   - ZMQManager outputs `dict` (bytes → dict)
   - ProcessorManager expects `str` (str → str)
   - Need to align types or fix domain signatures

2. **Missing counter initialization:**
   - `orchestrator.py:64` uses `self.not_completed_pipelines`
   - Never initialized in `__init__`

3. **Domain logic stubs:**
   - ProcessorManager: passthrough
   - MetricsManager: basic dict creation
   - All domains have placeholder logic

4. **ZMQManager shutdown:**
   - `shutdown()` exists but orchestrator doesn't have `start()` method
   - Application handles start/shutdown directly

---

## Async Architecture Flow

```
┌─────────────────────────────────────────────────────┐
│              asyncio Event Loop                      │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │   Application.run() (async)                │    │
│  │   ├─ orchestrator.initialize()  (sync)     │    │
│  │   └─ await orchestrator.start() (async)    │    │
│  └──────────────┬─────────────────────────────┘    │
│                 │                                    │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │   ZMQManager.message_loop() (background)    │   │
│  │                                              │   │
│  │   while running:                            │   │
│  │     msg = await socket.recv()  ◄─── blocks  │   │
│  │     await self.handle(msg)     ◄─── async   │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                    │
│                 │ Triggers async callback chain     │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │   BaseDomain.handle(data) (template)        │   │
│  │   ├─ result = await _execute(data)          │   │
│  │   ├─ await handled(result) ─────────┐       │   │
│  │   └─ await success({...})           │       │   │
│  └───────────────────────────────────────────── │   │
│                                           │       │
│         Pipeline flow (all async)         │       │
│         ┌─────────────────────────────────┘       │
│         ▼                                          │
│  ProcessorManager.handle() →                      │
│  MetricsManager.handle() →                        │
│  ExporterManager.handle() →                       │
│  Orchestrator.on_pipeline_complete()              │
│         │                                          │
│         │ Parallel: Monitoring callbacks           │
│         ▼                                          │
│  Monitor.on_success() (async)                     │
│  Monitor.on_error() (async)                       │
│                                                    │
└─────────────────────────────────────────────────────┘
```

All operations are async - cooperative multitasking allows:
- ZMQ to receive messages while pipeline processes
- Multiple messages in flight simultaneously
- Non-blocking I/O throughout

---

## Design Strengths

1. **Async I/O efficiency** - Non-blocking ZMQ, concurrent message processing
2. **Type safety** - Generic types enforce contracts at domain boundaries
3. **Template method** - Domains focus on `_execute()`, framework handles rest
4. **Separation of concerns** - Data flow ≠ Monitoring (different callback chains)
5. **Open/Closed principle** - Add domains without modifying existing code
6. **Inversion of control** - Orchestrator controls wiring, domains decoupled
7. **Memory safety** - Monitor uses bounded `deque(maxlen=1000)`
8. **Testability** - Integration test validates full async pipeline
9. **Graceful shutdown** - Async signal handlers stop message loop cleanly

---

## Testing

**Make Commands:**
```bash
make test-integration          # All integration tests
make test-integration-zmq      # Specific ZMQ pipeline test
make publish                   # Manual publisher (run 'make run' first)
make run                       # Start application
```

**Integration Test:** `tests/integration/test_zmq_pipeline.py`
- Creates orchestrator with test port (5556)
- Starts async message loop in background task
- Publishes 3 test messages via ZMQ
- Asserts pipeline completion count
- Validates all domain success counts
- Checks exported data exists

**Manual Testing:**
1. Terminal 1: `make run` (starts async app on port 5555)
2. Terminal 2: `make publish` (sends 5 test messages)
3. App logs show pipeline completions

---

## Next Steps

1. **Fix type alignment** - Decide on pipeline data types (dict or str?)
2. **Initialize missing counter** - Add `self.not_completed_pipelines = 0`
3. **Implement domain logic** - Add real processing/metrics/export
4. **Error handling** - Test error path with invalid messages
5. **Performance testing** - Benchmark async throughput
6. **Monitoring dashboard** - Expose `monitor.get_metrics()` via API
