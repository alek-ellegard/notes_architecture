"""
Singleton Patterns: Comparing different implementation approaches.
"""

from singleton_patterns.approach1_new_override import (
    SymbolMap as Approach1SymbolMap,
)
from singleton_patterns.approach1_new_override import (
    ThreadSafeSymbolMap,
)
from singleton_patterns.approach2_module_level import (
    ManagedSymbolMap,
    get_symbol_map,
    inject_symbol_map,
    reset_symbol_map,
)
from singleton_patterns.approach2_module_level import (
    SymbolMap as Approach2SymbolMap,
)

__all__ = [
    # Approach 1: __new__ override
    "Approach1SymbolMap",
    "ThreadSafeSymbolMap",
    # Approach 2: module-level
    "Approach2SymbolMap",
    "ManagedSymbolMap",
    "get_symbol_map",
    "reset_symbol_map",
    "inject_symbol_map",
]
