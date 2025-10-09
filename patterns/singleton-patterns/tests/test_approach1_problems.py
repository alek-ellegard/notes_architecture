"""
Tests for Approach 1: __new__ Override Pattern
Demonstrates the problems and limitations.
"""

import threading
import time
from unittest.mock import patch

from singleton_patterns.approach1_new_override import (
    SymbolMap,
    ThreadSafeSymbolMap,
)


class TestApproach1Problems:
    """Demonstrates problems with __new__ override approach."""

    def teardown_method(self):
        """Reset singletons after each test."""
        SymbolMap.reset()
        ThreadSafeSymbolMap.reset()

    def test_init_called_multiple_times(self):
        """
        PROBLEM: __init__ is called on every instantiation,
        even when returning the same instance.
        """
        # First instantiation
        map1 = SymbolMap({"initial": "data"})
        assert map1.init_count == 1
        assert map1.data == {"initial": "data"}

        # Second instantiation - same instance, but __init__ runs again!
        map2 = SymbolMap({"different": "data"})
        assert map1 is map2  # Same instance
        assert map2.init_count == 2  # __init__ called twice!
        assert map2.data == {"different": "data"}  # Data overwritten!

        # The original data is lost - SILENT BUG!
        assert map1.data == {"different": "data"}

    def test_parameters_silently_ignored(self):
        """
        PROBLEM: After first instantiation, parameters appear to be accepted
        but actually overwrite existing state.
        """
        # Developer A creates singleton
        config_a = SymbolMap({"database": "postgres", "port": 5432})

        # Developer B (in different module) thinks they're initializing
        _ = SymbolMap({"database": "mysql", "port": 3306})

        # Silent corruption - A's config is now B's config!
        assert config_a.data["database"] == "mysql"  # WTF moment
        assert config_a.data["port"] == 3306

    def test_race_condition_potential(self):
        """
        PROBLEM: Basic __new__ approach has race conditions.
        """
        results: list[int] = []

        def create_and_set(value: int):
            # Multiple threads creating "first" instance
            instance = SymbolMap()
            instance.set("thread_id", value)
            time.sleep(0.001)  # Simulate some work
            results.append(instance.get("thread_id"))

        SymbolMap.reset()
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_and_set, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All threads should see same value if truly singleton
        # But last write wins due to race conditions
        assert len(set(results)) == 1  # Often fails without thread safety

    def test_testing_requires_explicit_cleanup(self):
        """
        PROBLEM: Forgetting reset() causes test pollution.
        Without reset(), the same instance persists across "tests".
        """
        # Simulate test 1 - set up some state
        map1 = SymbolMap({"config": "test1"})
        map1.set("custom_key", "test1_value")
        id1 = id(map1)

        # Do NOT call reset() here (simulating forgetting to clean up)

        # Simulate test 2 - expecting fresh instance but gets polluted one
        # Even if we "initialize" with different data, same instance returned
        map2 = SymbolMap({"config": "test2"})
        id2 = id(map2)

        # POLLUTION: Same instance is returned (same memory address)
        assert map2 is map1
        assert id1 == id2

        # The custom_key still exists because it's the same object
        # (though data dict was replaced by __init__)
        # This demonstrates instance pollution even though data was reset

        # Must remember to reset for clean tests
        SymbolMap.reset()
        map3 = SymbolMap()
        id3 = id(map3)

        # Now we get a truly new instance
        assert map3 is not map1
        assert id3 != id1

    def test_mocking_difficulty(self):
        """
        PROBLEM: Hard to mock for testing.
        """
        # Cannot easily inject mock
        original = SymbolMap({"real": "data"})

        # Try to mock __new__ - but it's complex
        with patch.object(SymbolMap, '__new__', return_value=original):
            map2 = SymbolMap({"mock": "data"})
            # Init was called on existing instance
            assert map2 is original
            # Mock doesn't prevent __init__ from modifying the original
            assert map2.data == {"mock": "data"}  # Overwritten original!

        # The original instance has been modified
        assert original.data == {"mock": "data"}


class TestThreadSafeVersion:
    """Tests for the thread-safe version with initialization guard."""

    def teardown_method(self):
        ThreadSafeSymbolMap.reset()

    def test_initialization_guard(self):
        """
        Thread-safe version uses initialization guard,
        but __init__ is still called multiple times.
        """
        map1 = ThreadSafeSymbolMap({"initial": "data"})
        assert map1.init_count == 1
        assert map1.data == {"initial": "data"}

        # Second call - __init__ runs but is ignored
        map2 = ThreadSafeSymbolMap({"different": "data"})
        assert map1 is map2
        assert map2.init_count == 2  # Still incremented!
        assert map2.data == {"initial": "data"}  # Data preserved

        # __init__ is called but must be guarded - complexity!

    def test_thread_safety(self):
        """Thread-safe version handles concurrent access correctly."""
        created_instances = []
        barrier = threading.Barrier(10)

        def create_instance():
            barrier.wait()  # Synchronize start
            instance = ThreadSafeSymbolMap()
            created_instances.append(instance)

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same
        first = created_instances[0]
        assert all(inst is first for inst in created_instances)

    def test_still_requires_reset(self):
        """Even thread-safe version needs manual cleanup."""
        _ = ThreadSafeSymbolMap({"persistent": "data"})

        # Without reset, data persists
        map2 = ThreadSafeSymbolMap()
        assert map2.data == {"persistent": "data"}

        ThreadSafeSymbolMap.reset()
        map3 = ThreadSafeSymbolMap()
        assert map3.data == {}
