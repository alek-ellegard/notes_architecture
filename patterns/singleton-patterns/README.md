# Singleton Patterns: A Critical Comparison

Demonstration of singleton pattern implementations in Python, explicitly showing pros/cons of different approaches.

-> `make demo`

## Installation

```bash
# Using uv (recommended)
uv venv
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=singleton_patterns

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/ tests/
```

## The Two Approaches

### Approach 1: `__new__` Override

**Status: ⚠️ Problematic**

```python
class SymbolMap:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, data=None):
        # WARNING: Called EVERY time SymbolMap() is called!
        self.data = data or {}
```

**Problems:**

- `__init__` runs on every instantiation → silent data corruption
- Race conditions without explicit locking
- Testing requires manual cleanup
- Initialization parameters silently ignored/overwrite

### Approach 2: Module-level with Factory

**Status: ✅ Recommended**

```python
_symbol_map = None
_lock = threading.Lock()

class SymbolMap:
    def __init__(self, data=None):
        # Only runs once during actual instantiation
        self.data = data or {}

def get_symbol_map(data=None):
    global _symbol_map
    if _symbol_map is None:
        with _lock:
            if _symbol_map is None:
                _symbol_map = SymbolMap(data)
    return _symbol_map
```

**Advantages:**

- Clean separation of concerns
- `__init__` only runs once
- Thread-safe by design
- Explicit lifecycle management
- Easy testing with injection

## Quick Demo

```python
# Run the demo
uv run python demo.py
```

## Test Results Speak

```bash
# See approach 1 problems
uv run pytest tests/test_approach1_problems.py -v

# See approach 2 advantages  
uv run pytest tests/test_approach2_advantages.py -v
```

## Key Insights

### The `__init__` Problem (Approach 1)

```python
config1 = ConfigManager("dev.yml")   # loads dev.yml
config2 = ConfigManager("prod.yml")  # SILENTLY overwrites with prod.yml!
# config1.config is now prod settings - SILENT BUG
```

### The Solution (Approach 2)

```python
config1 = get_config_manager("dev.yml")   # creates with dev
config2 = get_config_manager("prod.yml")  # RAISES ValueError - explicit failure
```

## When To Use Singletons

**Consider alternatives first:**

- Dependency injection
- Module-level constants
- Class variables
- Configuration objects passed explicitly

**Valid use cases:**

- Resource pools (connection pools)
- Hardware interface abstractions
- Application-wide caches
- Logging systems

## Thread Safety Comparison

| Aspect | Approach 1 | Approach 2 |
|--------|------------|------------|
| Basic implementation | ❌ Race conditions | ✅ Safe with lock |
| Double-check locking | Requires modification | ✅ Built-in |
| Import-time safety | ❌ Not applicable | ✅ Python import lock |
| Complexity | High (guards needed) | Low (clean design) |

## Testing Comparison

| Aspect | Approach 1 | Approach 2 |
|--------|------------|------------|
| Reset mechanism | Manual `reset()` | Clean `reset_symbol_map()` |
| Mock injection | Complex | Simple `inject_symbol_map()` |
| Test isolation | Error-prone | Explicit |
| Cleanup required | Always | Optional with injection |

## Recommendations

1. **Avoid singletons when possible** - they're often an anti-pattern
2. **If needed, use module-level approach** - explicit and maintainable
3. **Consider dependency injection instead** - better testability
4. **Document singleton usage clearly** - team awareness critical
5. **Always implement thread safety** - concurrent access is common

## Running Examples

```bash
# See both patterns in action
uv run python demo.py

# Run specific test demonstrations
uv run pytest tests/test_approach1_problems.py::TestApproach1Problems::test_init_called_multiple_times -v
uv run pytest tests/test_approach2_advantages.py::TestApproach2Advantages::test_explicit_reinitialization_protection -v
```

## License

MIT
