"""
Approach 1: __new__ Override Singleton Pattern

This approach intercepts object creation using __new__ method.
"""

import logging
import threading
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SymbolMap:
    """
    Singleton using __new__ override.

    PROBLEMS:
    - __init__ runs on every instantiation
    - Not thread-safe without additional locking
    - Testing requires manual cleanup
    - Initialization parameters ambiguity
    """

    _instance: Optional['SymbolMap'] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> 'SymbolMap':
        """
        Intercepts object creation before __init__.
        Returns existing instance if already created.
        """
        if cls._instance is None:
            # RACE CONDITION: Multiple threads can pass this check
            logger.debug("Creating new SymbolMap instance")
            cls._instance = super().__new__(cls)
        else:
            logger.debug("Returning existing SymbolMap instance")
        return cls._instance

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """
        WARNING: Called EVERY time SymbolMap() is called,
        even when returning existing instance!
        """
        # This leads to unexpected reinitialization
        logger.warning("__init__ called (count: %d) - potential reinitialization",
                      getattr(self, 'init_count', 0) + 1)
        self.data = data or {}
        self.init_count = getattr(self, 'init_count', 0) + 1

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    @classmethod
    def reset(cls) -> None:
        """Required for testing - manual cleanup."""
        logger.debug("Resetting SymbolMap singleton instance")
        cls._instance = None


class ThreadSafeSymbolMap:
    """
    Thread-safe version with double-checked locking.
    Still has __init__ reinitialization problem.
    """

    _instance: Optional['ThreadSafeSymbolMap'] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> 'ThreadSafeSymbolMap':
        if cls._instance is None:
            with cls._lock:
                # Double-check pattern
                if cls._instance is None:
                    logger.debug(
                        "Creating new ThreadSafeSymbolMap instance (thread-safe)"
                    )
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        # Guard against reinitialization
        if not hasattr(self, '_initialized'):
            logger.debug("Initializing ThreadSafeSymbolMap for the first time")
            self._initialized = True
            self.data = data or {}
            self.init_count = 1
        else:
            # Still gets called, but we ignore it
            logger.debug("__init__ called again but ignored (count: %d)",
                        getattr(self, 'init_count', 0) + 1)
            self.init_count = getattr(self, 'init_count', 0) + 1

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    @classmethod
    def reset(cls) -> None:
        """Required for testing."""
        logger.debug("Resetting ThreadSafeSymbolMap singleton instance")
        with cls._lock:
            cls._instance = None
