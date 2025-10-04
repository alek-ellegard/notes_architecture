# Understanding Async/Sync Architecture Patterns

## The Problem

You're getting this error:
```
Method "_execute" overrides class "BaseDomain" in an incompatible manner
Return type mismatch: base method returns type "str", override returns type "CoroutineType[Any, Any, str]"
```

### What This Means

**BaseDomain defines:**
```python
def _execute(self, data: TInput) -> TOutput:
    """Domain-specific logic"""
```

**ZMQManager defines:**
```python
async def _execute(self, data: bytes) -> str:  # ← async!
    return orjson.loads(data.decode("utf-8"))
```

**The Issue:**
- `async def` returns a **coroutine** (a promise of a future value)
- Regular `def` returns the **actual value**
- These are incompatible types!

**Analogy:**
```python
# Synchronous (immediate)
def get_coffee() -> Coffee:
    return Coffee()  # ← returns Coffee

# Asynchronous (promise)
async def get_coffee() -> Coffee:
    return Coffee()  # ← returns Coroutine[Coffee], not Coffee!

# You must await it:
coffee = await get_coffee()  # ← NOW you have Coffee
```

## Your Architecture Choices

You have **3 main options** to resolve this:

---

## Option 1: Pure Async Architecture (Recommended for I/O-heavy systems)

Make the entire pipeline async from top to bottom.

### BaseDomain (base_domain.py)
```python
from abc import ABC, abstractmethod
from time import time
from typing import Callable, TypeVar, Generic

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseDomain(ABC, Generic[TInput, TOutput]):
    def __init__(self):
        self._callbacks: list[Callable] = []
        self._success_callbacks: list[Callable] = []
        self._error_callbacks: list[Callable] = []

    @abstractmethod
    async def _execute(self, data: TInput) -> TOutput:  # ← async!
        """Domain-specific logic - override this"""
        raise NotImplementedError(
            f"{self.__class__.__name__}._execute() must be implemented"
        )

    async def handle(self, data: TInput) -> None:  # ← async!
        """Template method with timing and error handling"""
        start = time()
        try:
            result = await self._execute(data)  # ← await!
            duration = time() - start

            await self.handled(result)  # ← await!
            await self.success({
                "domain": self.__class__.__name__,
                "operation": "handle",
                "duration": duration,
            })

        except Exception as e:
            duration = time() - start
            await self.error({
                "domain": self.__class__.__name__,
                "operation": "handle",
                "error_type": type(e).__name__,
            })
            raise

    # Callbacks become async
    async def handled(self, data):
        for cb in self._callbacks:
            await cb(data)  # ← await each callback

    async def success(self, event: dict) -> None:
        for cb in self._success_callbacks:
            await cb(event)

    async def error(self, event: dict) -> None:
        for cb in self._error_callbacks:
            await cb(event)

    # Registration stays sync
    def on_handled(self, callback):
        self._callbacks.append(callback)

    def on_success(self, callback) -> None:
        self._success_callbacks.append(callback)

    def on_error(self, callback) -> None:
        self._error_callbacks.append(callback)
```

### ZMQManager (zmq_manager.py)
```python
import zmq
import zmq.asyncio
import orjson
from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class ZMQManager(BaseDomain[bytes, dict]):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env
        self.context = zmq.asyncio.Context()  # ← async context!
        self.socket = self.context.socket(zmq.SUB)
        self.socket.subscribe("")
        self.socket.bind(env.ZMQ_ADDRESS)
        self.running = False

    async def message_loop(self) -> None:
        """Main loop receiving and processing messages"""
        self.running = True
        while self.running:
            message: bytes = await self.socket.recv()
            await self.handle(message)  # ← triggers pipeline!

    async def _execute(self, data: bytes) -> dict:
        """Convert bytes to dict"""
        return orjson.loads(data.decode("utf-8"))

    def shutdown(self) -> None:
        self.running = False
        self.socket.close()
        self.context.term()
```

### Other Domains
```python
# processor_manager.py
class ProcessorManager(BaseDomain[dict, dict]):
    async def _execute(self, data: dict) -> dict:  # ← async
        # Could do async processing here
        return data

# metrics_manager.py
class MetricsManager(BaseDomain[dict, dict]):
    async def _execute(self, data: dict) -> dict:  # ← async
        return data

# exporter_manager.py
class ExporterManager(BaseDomain[dict, bool]):
    async def _execute(self, data: dict) -> bool:  # ← async
        self.exported_data = data
        return True
```

### Monitor (monitor.py)
```python
class Monitor:
    # ... same fields ...

    async def on_success(self, event: dict) -> None:  # ← async
        key = f"{event['domain']}.{event['operation']}"
        self.success_counts[key] += 1
        self.success_durations[key].append(event["duration"])

    async def on_error(self, event: dict) -> None:  # ← async
        key = f"{event['domain']}.{event['operation']}"
        self.error_counts[key] += 1
        self.error_types[key][event["error_type"]] += 1
```

### Orchestrator (orchestrator.py)
```python
class Orchestrator:
    def __init__(self, env: Environment) -> None:
        self.monitor = Monitor()
        self.completed_pipelines = 0
        self.not_completed_pipelines = 0

        self.domains: list[BaseDomain] = [
            ZMQManager(env),
            ProcessorManager(env),
            MetricsManager(env),
            ExporterManager(env),
        ]

    def initialize(self):
        """Wire everything together (still sync - just registration)"""
        self._wire_pipeline()
        self._wire_monitoring()
        self._wire_completion()

    def _wire_pipeline(self):
        for prev, next in zip(self.domains, self.domains[1:]):
            prev.on_handled(next.handle)  # ← registering async callbacks

    def _wire_monitoring(self):
        for domain in self.domains:
            domain.on_success(self.monitor.on_success)
            domain.on_error(self.monitor.on_error)

    def _wire_completion(self):
        self.domains[-1].on_handled(self.on_pipeline_complete)

    async def on_pipeline_complete(self, result: bool) -> None:  # ← async
        if result:
            self.completed_pipelines += 1
        else:
            self.not_completed_pipelines += 1

    async def start(self):
        """Start the ZMQ loop"""
        zmq_manager = self.domains[0]
        await zmq_manager.message_loop()  # ← run forever

    def shutdown(self):
        self.domains[0].shutdown()
```

### Integration Test (tests/integration/test_zmq_pipeline.py)
```python
import pytest
import asyncio
import zmq
import orjson
from base_domain.environment import Environment
from base_domain.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_zmq_pipeline_completion():
    """Test that messages flow through pipeline and count completions"""

    # Setup
    env = Environment(
        MODE="dev",
        ZMQ_HOST="127.0.0.1",
        ZMQ_PORT=5556,
        ZMQ_ADDRESS="tcp://127.0.0.1:5556"
    )

    orchestrator = Orchestrator(env)
    orchestrator.initialize()

    # Start orchestrator in background
    orchestrator_task = asyncio.create_task(orchestrator.start())

    # Give it time to bind
    await asyncio.sleep(0.1)

    # Create publisher
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.connect("tcp://127.0.0.1:5556")

    # Give publisher time to connect
    await asyncio.sleep(0.1)

    # Send test messages
    messages = [
        {"id": 1, "data": "test1"},
        {"id": 2, "data": "test2"},
        {"id": 3, "data": "test3"},
    ]

    for msg in messages:
        publisher.send(orjson.dumps(msg))

    # Wait for processing
    await asyncio.sleep(0.5)

    # Assertions
    assert orchestrator.completed_pipelines == 3
    assert orchestrator.monitor.success_counts["ProcessorManager.handle"] == 3

    # Cleanup
    orchestrator.shutdown()
    orchestrator_task.cancel()
    publisher.close()
    context.term()


if __name__ == "__main__":
    asyncio.run(test_zmq_pipeline_completion())
```

---

## Option 2: Pure Sync Architecture (Simpler, blocking)

Keep everything synchronous and use blocking ZMQ.

### Key Changes:
```python
# zmq_manager.py
import zmq  # ← regular zmq, not asyncio
import orjson
from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class ZMQManager(BaseDomain[bytes, dict]):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env
        self.context = zmq.Context()  # ← sync context
        self.socket = self.context.socket(zmq.SUB)
        self.socket.subscribe("")
        self.socket.bind(env.ZMQ_ADDRESS)
        self.running = False

    def message_loop(self) -> None:  # ← sync!
        """Main loop receiving and processing messages"""
        self.running = True
        while self.running:
            message: bytes = self.socket.recv()  # ← blocks here
            self.handle(message)  # ← triggers pipeline!

    def _execute(self, data: bytes) -> dict:  # ← sync!
        return orjson.loads(data.decode("utf-8"))

    def shutdown(self) -> None:
        self.running = False
        self.socket.close()
        self.context.term()
```

**Pros:**
- Simpler to understand
- No async/await complexity

**Cons:**
- Blocking - can't handle multiple things at once
- Less efficient for I/O-bound operations

---

## Option 3: Hybrid (Advanced - Not Recommended)

Run async code in sync context using `asyncio.run()` or event loops. This is complex and error-prone.

---

## Key Concepts to Understand

### 1. Callbacks in Async vs Sync

**Sync callbacks:**
```python
def callback(data):
    print(data)

# Called directly
callback("hello")
```

**Async callbacks:**
```python
async def callback(data):
    print(data)

# Must be awaited
await callback("hello")
```

### 2. The Event Loop

Async Python uses an **event loop** that manages coroutines:

```python
import asyncio

async def main():
    # All async code runs here
    await some_async_function()

# Start the event loop
asyncio.run(main())
```

### 3. ZMQ Async vs Sync

**Sync ZMQ:**
- `socket.recv()` **blocks** the entire thread
- Simple but can't do anything else while waiting

**Async ZMQ:**
- `await socket.recv()` **yields control** to event loop
- Other tasks can run while waiting for messages
- Better for handling multiple concurrent operations

---

## Recommended Approach for Your Use Case

**Go with Option 1 (Pure Async)** because:

1. **ZMQ is I/O-bound** - you're waiting for network messages
2. **Pipeline pattern benefits from async** - messages can flow concurrently
3. **Scales better** - can handle multiple messages simultaneously
4. **Modern Python pattern** - async is the standard for I/O operations

### Migration Steps:

1. ✅ Make `_execute()` async in `BaseDomain`
2. ✅ Make `handle()` async in `BaseDomain`
3. ✅ Make all callback triggers async (`handled`, `success`, `error`)
4. ✅ Update all domain `_execute()` methods to async
5. ✅ Update `Monitor` callbacks to async
6. ✅ Update `Orchestrator.on_pipeline_complete()` to async
7. ✅ Create async test with `pytest-asyncio`

---

## Common Pitfalls

### 1. Forgetting `await`
```python
# ❌ Wrong - returns coroutine object
result = async_function()

# ✅ Correct - returns actual value
result = await async_function()
```

### 2. Mixing sync/async callbacks
```python
# ❌ Wrong - can't await sync function
async def async_callback(data):
    await sync_function()  # TypeError!

# ✅ Correct - both async
async def async_callback(data):
    await async_function()
```

### 3. Running async code in sync context
```python
# ❌ Wrong - can't await outside async function
result = await async_function()

# ✅ Correct - use asyncio.run()
result = asyncio.run(async_function())
```

---

## Final Architecture Summary

```
┌─────────────────────────────────────────────────────┐
│                  Event Loop                          │
│  ┌────────────────────────────────────────────┐    │
│  │         ZMQManager.message_loop()          │    │
│  │                                             │    │
│  │  while running:                            │    │
│  │    msg = await socket.recv()  ←── blocks   │    │
│  │    await self.handle(msg)     ←── async    │    │
│  └──────────────┬──────────────────────────────┘    │
│                 │                                    │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │   BaseDomain.handle(data)                   │   │
│  │   ├─ result = await self._execute(data)     │   │
│  │   ├─ await self.handled(result)  ───────┐   │   │
│  │   └─ await self.success({...})           │   │   │
│  └───────────────────────────────────────────┘   │
│                                           │       │
│         ┌─────────────────────────────────┘       │
│         │ Chain of callbacks                      │
│         ▼                                          │
│  ProcessorManager.handle() →                      │
│  MetricsManager.handle() →                        │
│  ExporterManager.handle() →                       │
│  Orchestrator.on_pipeline_complete()              │
│                                                    │
└─────────────────────────────────────────────────────┘
```

All operations happen cooperatively - when one awaits, others can run!
