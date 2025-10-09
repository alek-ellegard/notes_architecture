# Demo Output Summary: Singleton Pattern Comparison

## Overview
This demo reveals critical differences between two singleton implementation approaches by showing their behavior under identical scenarios: data corruption risks, thread safety, and initialization handling.

---

## Part 1: Approach 1 Problems (__new__ Override)

### Problem 1: Silent Data Corruption

**What Happened:**
```python
# Developer A creates config
config_a = SymbolMap({'db': 'postgres', 'port': 5432})
# config_a.data = {'db': 'postgres', 'port': 5432}

# Developer B creates "new" config (same object!)
config_b = SymbolMap({'db': 'mysql', 'port': 3306})
# config_b.data = {'db': 'mysql', 'port': 3306}

# Developer A's data is now corrupted!
# config_a.data = {'db': 'mysql', 'port': 3306}  # ← SILENTLY CHANGED!
```

**Why This Happens:**
1. `__new__()` returns the same instance (correct singleton behavior)
2. BUT `__init__()` runs **every time** `SymbolMap()` is called
3. Each call to `__init__()` overwrites `self.data` with new values
4. Result: Developer A's configuration is silently corrupted
5. `init_count = 2` shows `__init__` ran twice on same instance

**The Danger:**
- No error is raised
- No warning to developers
- Bugs appear far from their source
- Extremely hard to debug in production

### Problem 2: Race Conditions

**What Happened:**
```python
# 3 threads simultaneously create singleton
Thread-0 sets creator = "Thread-0"
Thread-1 sets creator = "Thread-1"  # Overwrites!
Thread-2 sets creator = "Thread-2"  # Overwrites again!

# All threads see: "Thread-2" (last writer wins)
```

**Why This Happens:**
- Basic implementation has no locking in `__new__()`
- Multiple threads can pass the `if cls._instance is None` check
- Even worse: `__init__()` runs without synchronization
- Result: Non-deterministic data corruption

---

## Part 2: Approach 2 Advantages (Module-Level)

### Advantage 1: Explicit Initialization Protection

**What Happened:**
```python
# First initialization succeeds
config1 = get_symbol_map({'db': 'postgres', 'port': 5432})
# ✓ config1.data = {'db': 'postgres', 'port': 5432}

# Attempt to reinitialize with different data
config2 = get_symbol_map({'db': 'mysql', 'port': 3306})
# ✗ ValueError: SymbolMap already initialized. Cannot reinitialize with different data.

# Getting existing instance (no params) works fine
config3 = get_symbol_map()
# ✓ Returns same instance, data still intact
# ✓ init_count = 1 (only initialized once!)
```

**Why This Is Better:**
1. Factory function `get_symbol_map()` controls instantiation
2. Explicitly checks if data would change: `data != _symbol_map.data`
3. Raises `ValueError` **immediately** if reinitialization attempted
4. Prevents silent corruption - fail fast with clear error
5. `__init__()` only runs **once** (init_count = 1)

### Advantage 2: Thread Safety (With Caveat)

**What Happened:**
```python
# 3 threads try to initialize with different data
Thread-2 wins, creates: {"creator": "Thread-2"}
Thread-4 tries: {"creator": "Thread-1"}  # ValueError!
Thread-5 tries: {"creator": "Thread-0"}  # ValueError!

# Only 1 result: ['Thread-2'] - first thread wins
```

**What This Demonstrates:**
1. **Double-checked locking** prevents race conditions
2. Only first thread's data is used
3. Other threads get **explicit errors** (not silent corruption!)
4. The exceptions show the protection is working

**Note:** The demo intentionally shows the strict behavior. In production, threads should either:
- Initialize with same data (no error)
- Call without data parameter after first init
- Handle potential `ValueError` appropriately

---

## Part 3: Managed Singleton (Hybrid Approach)

**What Happened:**
```python
# Using factory method (correct)
instance1 = ManagedSymbolMap.get_instance({'setting': 'value'})
instance2 = ManagedSymbolMap.get_instance()
# instance1 is instance2 = True ✓

# Direct instantiation (bypasses singleton)
instance3 = ManagedSymbolMap()  # Creates NEW instance
# instance3 is instance1 = False ✗
```

**Key Insight:**
- Combines class-based structure with factory pattern
- `get_instance()` enforces singleton behavior
- Direct `ManagedSymbolMap()` still works but creates separate instance
- Shows importance of **convention and documentation**

---

## Part 4: Testing Implications

### Approach 1: Manual Cleanup Required
```python
def test_something():
    map1 = Approach1Map({'test': 'data'})
    # ... test code ...
    Approach1Map.reset()  # ← MUST REMEMBER or tests pollute each other
```

**Problems:**
- Easy to forget cleanup
- Tests can pollute each other
- Hard to mock/inject dependencies

### Approach 2: Clean Injection
```python
def test_something():
    mock = Mock(spec=SymbolMap)
    inject_symbol_map(mock)  # ← Explicit injection
    # ... test with mock ...
    reset_symbol_map()  # or use pytest fixture
```

**Benefits:**
- Explicit dependency injection
- Easy to mock for unit tests
- Clear reset semantics
- Can use fixtures for automatic cleanup

---

## Key Takeaways

### ❌ Approach 1 (__new__ Override) Fails Because:
1. `__init__()` runs on every instantiation → silent data corruption
2. No protection against reinitialization
3. Race conditions without careful locking
4. `init_count = 2, 3, 4...` shows repeated initialization

### ✅ Approach 2 (Module-Level) Succeeds Because:
1. Factory function controls all access
2. Explicit error on reinitialization attempts
3. Thread-safe by design (double-checked locking)
4. `init_count = 1` always (true single initialization)
5. Clean testing with injection support

### Production Recommendation:
```python
# Initialize once at application startup
symbol_map = get_symbol_map({'config': 'data'})

# Everywhere else, just get the instance
symbol_map = get_symbol_map()  # No params, no error
```

---

## The Bottom Line

The demo proves that **Approach 1 creates bugs that appear unrelated to their cause**, while **Approach 2 fails fast with clear errors**. In production systems, explicit failures are infinitely better than silent corruption.

**Use Approach 2 for any real singleton pattern needs.**
