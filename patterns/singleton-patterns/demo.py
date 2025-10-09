#!/usr/bin/env python
"""
Interactive demonstration of singleton pattern approaches.
Shows the critical differences between implementations.
"""

import threading
import time
from typing import List

# Approach 1: __new__ override
from singleton_patterns.approach1_new_override import (
    SymbolMap as Approach1Map,
    ThreadSafeSymbolMap,
)

# Approach 2: Module-level
from singleton_patterns.approach2_module_level import (
    get_symbol_map,
    reset_symbol_map,
    ManagedSymbolMap,
)


def separator(title: str) -> None:
    """Print a formatted section separator."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_approach1_problems():
    """Demonstrate problems with __new__ override approach."""
    separator("APPROACH 1: __new__ Override - THE PROBLEMS")
    
    print("1. SILENT DATA CORRUPTION")
    print("-" * 40)
    
    # Developer A initializes configuration
    print("Developer A: config = SymbolMap({'db': 'postgres', 'port': 5432})")
    config_a = Approach1Map({"db": "postgres", "port": 5432})
    print(f"  → config.data = {config_a.data}")
    print(f"  → init_count = {config_a.init_count}")
    
    # Developer B in another module
    print("\nDeveloper B: config = SymbolMap({'db': 'mysql', 'port': 3306})")
    config_b = Approach1Map({"db": "mysql", "port": 3306})
    print(f"  → config.data = {config_b.data}")
    print(f"  → init_count = {config_b.init_count}")
    
    # The disaster
    print("\nDeveloper A checks their config:")
    print(f"  → config_a.data = {config_a.data}  # WTF?! Data corrupted!")
    print(f"  → config_a is config_b = {config_a is config_b}")
    
    # Reset for next demo
    Approach1Map.reset()
    
    print("\n2. RACE CONDITIONS (Basic Implementation)")
    print("-" * 40)
    
    results: List[str] = []
    
    def create_singleton(name: str):
        instance = Approach1Map()
        instance.set("creator", name)
        time.sleep(0.001)  # Simulate work
        results.append(instance.get("creator"))
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=create_singleton, args=(f"Thread-{i}",))
        threads.append(t)
    
    print("Starting 3 threads simultaneously...")
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print(f"Results seen by threads: {results}")
    print(f"All same? {len(set(results)) == 1}")
    print("(Race condition: last writer wins)")
    
    Approach1Map.reset()


def demo_approach2_advantages():
    """Demonstrate advantages of module-level approach."""
    separator("APPROACH 2: Module-Level - THE SOLUTION")
    
    print("1. EXPLICIT INITIALIZATION PROTECTION")
    print("-" * 40)
    
    # First initialization
    print("config1 = get_symbol_map({'db': 'postgres', 'port': 5432})")
    config1 = get_symbol_map({"db": "postgres", "port": 5432})
    print(f"  → config1.data = {config1.data}")
    print(f"  → init_count = {config1.init_count}")
    
    # Attempt reinitialization
    print("\nconfig2 = get_symbol_map({'db': 'mysql', 'port': 3306})")
    try:
        config2 = get_symbol_map({"db": "mysql", "port": 3306})
    except ValueError as e:
        print(f"  → ValueError: {e}")
        print("  → Original data is protected!")
    
    # Getting existing instance works
    print("\nconfig3 = get_symbol_map()  # No params")
    config3 = get_symbol_map()
    print(f"  → config3.data = {config3.data}")
    print(f"  → init_count = {config3.init_count}  # Still 1!")
    print(f"  → config1 is config3 = {config1 is config3}")
    
    reset_symbol_map()
    
    print("\n2. THREAD SAFETY BY DESIGN")
    print("-" * 40)
    
    results: List[str] = []
    barrier = threading.Barrier(3)
    
    def create_singleton(name: str):
        barrier.wait()  # Synchronize start
        instance = get_symbol_map({"creator": name})
        results.append(instance.data.get("creator"))
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=create_singleton, args=(f"Thread-{i}",))
        threads.append(t)
    
    print("Starting 3 threads with barrier synchronization...")
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print(f"Results seen by threads: {results}")
    print(f"All same? {len(set(results)) == 1}  # First thread wins!")
    print(f"Winner: {results[0]}")
    
    reset_symbol_map()


def demo_managed_singleton():
    """Demonstrate the encapsulated factory pattern."""
    separator("BONUS: Managed Singleton (Best of Both)")
    
    print("Using ManagedSymbolMap.get_instance()")
    print("-" * 40)
    
    # Clean API
    print("instance1 = ManagedSymbolMap.get_instance({'setting': 'value'})")
    instance1 = ManagedSymbolMap.get_instance({"setting": "value"})
    print(f"  → data: {instance1.data}")
    
    print("\ninstance2 = ManagedSymbolMap.get_instance()")
    instance2 = ManagedSymbolMap.get_instance()
    print(f"  → Same instance: {instance1 is instance2}")
    
    # Attempting direct instantiation (discouraged but possible)
    print("\n# Direct instantiation (not recommended):")
    print("instance3 = ManagedSymbolMap()  # Creates separate instance")
    instance3 = ManagedSymbolMap()
    print(f"  → Same as singleton? {instance3 is instance1}  # No!")
    
    ManagedSymbolMap.reset()


def demo_testing_differences():
    """Show testing implications."""
    separator("TESTING IMPLICATIONS")
    
    print("APPROACH 1: Manual cleanup required")
    print("-" * 40)
    print("def test_something():")
    print("    map1 = Approach1Map({'test': 'data'})")
    print("    # ... test code ...")
    print("    Approach1Map.reset()  # MUST REMEMBER!")
    
    print("\nAPPROACH 2: Clean injection")
    print("-" * 40)
    print("def test_something():")
    print("    mock = Mock(spec=SymbolMap)")
    print("    inject_symbol_map(mock)")
    print("    # ... test with mock ...")
    print("    reset_symbol_map()  # or use fixture")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print(" SINGLETON PATTERNS: A CRITICAL COMPARISON")
    print("="*60)
    
    demo_approach1_problems()
    demo_approach2_advantages()
    demo_managed_singleton()
    demo_testing_differences()
    
    separator("CONCLUSION")
    print("✅ Use Approach 2 (Module-level) for singletons")
    print("✅ Consider dependency injection instead")
    print("❌ Avoid Approach 1 (__new__ override) - too many pitfalls")
    print("\nRun tests for more examples:")
    print("  uv run pytest -v")


if __name__ == "__main__":
    main()
