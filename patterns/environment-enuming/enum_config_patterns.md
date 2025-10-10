# Enum-Based Configuration Patterns

## Problem
Need to organize configuration constants using enums while handling mixed types (strings, integers).
Python enums can't inherit from both `StrEnum` and `IntEnum` simultaneously.

## Three Approaches

### Approach 1: Mixed-Type Enum
```python
class BINANCE_CONFIG(Enum):
    symbol = "SOLUSDT"  # string
    buffer_size = 1440   # integer
```

**pros:**
- single enum class
- simple, minimal code
- direct access pattern

**cons:**
- loses type-specific enum methods
- no type safety at enum level
- mixing types can be confusing

**use when:**
- configuration is simple
- type distinction isn't critical
- want minimal boilerplate

---

### Approach 2: Namespace Pattern
```python
class BINANCE_CONFIG:
    class STRINGS(StrEnum):
        symbol = "SOLUSDT"
    
    class SETTINGS(IntEnum):
        buffer_size = 1440
```

**pros:**
- maintains type separation
- cleaner namespace organization
- preserves type-specific enum features
- logical grouping of related configs

**cons:**
- slightly more verbose
- nested access pattern

**use when:**
- type safety matters
- configuration has natural groupings
- want to preserve enum type features

---

### Approach 3: Custom Enum with Helpers
```python
class BINANCE_CONFIG(Enum):
    symbol: str = "SOLUSDT"
    buffer_size: int = 1440
    
    @classmethod
    def as_dict(cls) -> dict:
        return {k: v.value for k, v in cls.__members__.items()}
```

**pros:**
- single enum with utility methods
- type hints for documentation
- flexible access patterns

**cons:**
- type hints aren't enforced
- requires custom helper methods
- still mixing types internally

**use when:**
- need utility methods for config access
- want single enum with enhanced functionality
- type hints sufficient for documentation

---

## Decision Matrix

| criterion | approach 1 | approach 2 | approach 3 |
|-----------|------------|------------|------------|
| type safety | ❌ | ✅ | ⚠️ |
| simplicity | ✅ | ⚠️ | ⚠️ |
| maintainability | ⚠️ | ✅ | ⚠️ |
| enum features | ❌ | ✅ | ⚠️ |
| grouping | ❌ | ✅ | ❌ |

## Recommendation

**approach 2 (namespace pattern)** for most cases:
- preserves type safety
- logical organization
- maintains enum-specific features
- cleaner when configs grow

**approach 1 (mixed enum)** for simple cases:
- few configuration values
- types don't matter much
- prototype/early development

**approach 3 (custom enum)** when:
- need specific utility methods
- migrating from dict-based config
- want hybrid approach
