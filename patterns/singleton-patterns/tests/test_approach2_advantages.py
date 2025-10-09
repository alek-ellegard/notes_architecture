"""
Tests for Approach 2: Module-level Pattern
Demonstrates the advantages and clean design.
"""

import threading
from unittest.mock import Mock

import pytest

from singleton_patterns.approach2_module_level import (
    ManagedSymbolMap,
    SymbolMap,
    get_symbol_map,
    inject_symbol_map,
    reset_symbol_map,
)


class TestApproach2Advantages:
    """Demonstrates advantages of module-level approach."""

    def teardown_method(self):
        """Clean reset after each test."""
        reset_symbol_map()
        ManagedSymbolMap.reset()

    def test_init_only_called_once(self):
        """
        ADVANTAGE: __init__ is only called once during actual instantiation.
        """
        # First access creates instance
        map1 = get_symbol_map({"initial": "data"})
        assert map1.init_count == 1
        assert map1.data == {"initial": "data"}

        # Subsequent calls return same instance without calling __init__
        map2 = get_symbol_map()
        assert map1 is map2
        assert map2.init_count == 1  # Still 1!
        assert map2.data == {"initial": "data"}  # Data preserved

    def test_explicit_reinitialization_protection(self):
        """
        ADVANTAGE: Explicit error when trying to reinitialize with different data.
        """
        # First initialization
        map1 = get_symbol_map({"database": "postgres"})

        # Attempt to reinitialize with different data
        with pytest.raises(ValueError, match="already initialized"):
            get_symbol_map({"database": "mysql"})

        # Original data is safe
        assert map1.data == {"database": "postgres"}

    def test_thread_safe_by_design(self):
        """
        ADVANTAGE: Thread-safe initialization with double-checked locking.
        """
        results: list[SymbolMap] = []
        barrier = threading.Barrier(10)

        def get_instance(thread_id: int):
            try:
                barrier.wait()  # Synchronize threads
                instance = get_symbol_map({"thread": thread_id})
                results.append(instance)
            except ValueError:
                # Expected: other threads will get ValueError
                # when first thread wins initialization
                instance = get_symbol_map()  # Get existing instance
                results.append(instance)

        threads = []
        for i in range(10):
            t = threading.Thread(target=get_instance, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All threads get same instance
        first = results[0]
        assert all(r is first for r in results)
        # First thread wins initialization
        assert "thread" in first.data

    def test_easy_mocking_with_injection(self):
        """
        ADVANTAGE: Easy to inject mocks for testing.
        """
        # Create and inject mock
        mock_map = Mock(spec=SymbolMap)
        mock_map.data = {"mock": "data"}
        mock_map.get.return_value = "mocked_value"

        inject_symbol_map(mock_map)

        # All access points return mock
        result = get_symbol_map()
        assert result is mock_map
        assert result.get("any_key") == "mocked_value"
        mock_map.get.assert_called_with("any_key")

    def test_clean_reset_mechanism(self):
        """
        ADVANTAGE: Clean, explicit reset for testing.
        """
        # Create singleton with data
        map1 = get_symbol_map({"persistent": "data"})
        map1.set("key", "value")

        # Reset clears everything
        reset_symbol_map()

        # Fresh instance
        map2 = get_symbol_map({"fresh": "data"})
        assert map2 is not map1
        assert map2.get("key") is None
        assert map2.data == {"fresh": "data"}

    def test_no_accidental_instantiation(self):
        """
        ADVANTAGE: Can't accidentally create non-singleton instances.
        (Though SymbolMap() is still possible - use ManagedSymbolMap
        for full encapsulation)
        """
        # Intended usage
        singleton = get_symbol_map()

        # Direct instantiation creates different instance (design choice)
        # This allows normal class usage when needed
        normal_instance = SymbolMap({"separate": "instance"})
        assert normal_instance is not singleton

        # This flexibility can be useful for testing


class TestManagedSymbolMap:
    """Tests for the encapsulated factory pattern variant."""

    def teardown_method(self):
        ManagedSymbolMap.reset()

    def test_factory_method_pattern(self):
        """
        ADVANTAGE: Encapsulated singleton with clear API.
        """
        # Cannot use regular constructor (by convention)
        map1 = ManagedSymbolMap.get_instance({"data": "value"})
        map2 = ManagedSymbolMap.get_instance()

        assert map1 is map2
        assert map1.init_count == 1

    def test_prevents_reinitialization(self):
        """
        ADVANTAGE: Explicit error on reinitialization attempt.
        """
        ManagedSymbolMap.get_instance({"initial": "data"})

        with pytest.raises(ValueError, match="already initialized"):
            ManagedSymbolMap.get_instance({"different": "data"})

    def test_thread_safe_initialization(self):
        """
        ADVANTAGE: Built-in thread safety.
        """
        instances = []
        barrier = threading.Barrier(5)

        def create():
            barrier.wait()
            instances.append(ManagedSymbolMap.get_instance())

        threads = [threading.Thread(target=create) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All same instance
        assert all(i is instances[0] for i in instances)

    def test_explicit_lifecycle(self):
        """
        ADVANTAGE: Clear lifecycle management.
        """
        # Create
        instance = ManagedSymbolMap.get_instance({"lifecycle": "start"})
        instance.set("state", "running")

        # Use
        same_instance = ManagedSymbolMap.get_instance()
        assert same_instance.get("state") == "running"

        # Reset
        ManagedSymbolMap.reset()

        # New lifecycle
        new_instance = ManagedSymbolMap.get_instance({"lifecycle": "new"})
        assert new_instance is not instance
        assert new_instance.get("state") is None


class TestComparison:
    """Direct comparison of both approaches."""

    def test_initialization_behavior_comparison(self):
        """
        Compare initialization behavior between approaches.
        """
        # Approach 1: __new__ override
        from singleton_patterns.approach1_new_override import SymbolMap as Approach1

        a1_first = Approach1({"version": "1.0"})
        _ = Approach1({"version": "2.0"})

        # Approach 1: Second call overwrites!
        assert a1_first.data == {"version": "2.0"}  # PROBLEM!
        assert a1_first.init_count == 2  # __init__ called twice

        Approach1.reset()  # Cleanup

        # Approach 2: Module-level
        reset_symbol_map()  # Start fresh

        a2_first = get_symbol_map({"version": "1.0"})
        try:
            _ = get_symbol_map({"version": "2.0"})
        except ValueError:
            # Approach 2: Explicit error - BETTER!
            pass

        assert a2_first.data == {"version": "1.0"}  # Data preserved
        assert a2_first.init_count == 1  # __init__ called once
