"""
Approach 2: Module-level Singleton Pattern

This approach uses module-level variables with factory functions.
"""

import logging
import threading
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Module-level singleton holder
_symbol_map: Optional['SymbolMap'] = None
_lock: threading.Lock = threading.Lock()


class SymbolMap:
    """
    Normal class without singleton logic.

    ADVANTAGES:
    - Clean separation of concerns
    - __init__ only runs once
    - Explicit lifecycle management
    - Easy testing with clear reset
    """

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """
        Standard initialization - runs only when explicitly instantiated.
        """
        logger.debug("Initializing SymbolMap instance")
        self.data = data or {}
        self.init_count = 1  # Will always be 1 for each instance

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value


def get_symbol_map(data: dict[str, Any] | None = None) -> SymbolMap:
    """
    Factory function for singleton access.
    Thread-safe lazy initialization.

    Args:
        data: Initial data (only used on first call)

    Returns:
        The singleton SymbolMap instance

    Raises:
        ValueError: If attempting to reinitialize with different data
    """
    global _symbol_map

    if _symbol_map is None:
        with _lock:
            if _symbol_map is None:  # Double-check
                logger.info("Creating singleton SymbolMap instance via factory")
                _symbol_map = SymbolMap(data)
    elif data is not None and data != _symbol_map.data:
        # Explicit about not changing existing data
        logger.error("Attempted to reinitialize SymbolMap with different data")
        raise ValueError(
            "SymbolMap already initialized. "
            "Cannot reinitialize with different data."
        )
    else:
        logger.debug("Returning existing SymbolMap singleton instance")

    return _symbol_map


def reset_symbol_map() -> None:
    """
    Reset singleton for testing.
    Clean and explicit.
    """
    global _symbol_map
    logger.debug("Resetting SymbolMap singleton instance")
    with _lock:
        _symbol_map = None


def inject_symbol_map(instance: SymbolMap) -> None:
    """
    Inject a specific instance (useful for testing).

    Args:
        instance: The SymbolMap instance to use as singleton
    """
    global _symbol_map
    logger.debug("Injecting custom SymbolMap instance for testing")
    with _lock:
        _symbol_map = instance


# Alternative: Class with factory method
class ManagedSymbolMap:
    """
    Encapsulated singleton with class-level factory.
    Combines benefits of both approaches.
    """

    _instance: Optional['ManagedSymbolMap'] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """Private constructor - use get_instance() instead."""
        logger.debug("Initializing ManagedSymbolMap instance")
        self.data = data or {}
        self.init_count = 1

    @classmethod
    def get_instance(cls, data: dict[str, Any] | None = None) -> 'ManagedSymbolMap':
        """
        Factory method for singleton access.

        Args:
            data: Initial data (only used on first call)

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    logger.info("Creating singleton ManagedSymbolMap instance")
                    cls._instance = cls(data)
        elif data is not None:
            logger.error("Attempted to reinitialize ManagedSymbolMap")
            raise ValueError("ManagedSymbolMap already initialized")
        else:
            logger.debug("Returning existing ManagedSymbolMap instance")

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset for testing."""
        logger.debug("Resetting ManagedSymbolMap singleton instance")
        with cls._lock:
            cls._instance = None

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
