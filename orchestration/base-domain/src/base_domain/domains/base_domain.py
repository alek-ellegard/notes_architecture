from abc import ABC, abstractmethod
from time import time
from typing import Callable, TypeVar, Generic

# Generic types for input/output - subclasses define concrete types
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseDomain(ABC, Generic[TInput, TOutput]):
    def __init__(self):
        self._callbacks: list[Callable] = []
        self._success_callbacks: list[Callable] = []
        self._error_callbacks: list[Callable] = []

    # ---------------------------------------------

    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__}.initialize() must be implemented"
        )

    @abstractmethod
    def shutdown(self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__}.shutdown() must be implemented"
        )

    @abstractmethod
    async def _execute(self, data: TInput) -> TOutput:
        """Domain-specific logic - override this"""
        raise NotImplementedError(
            f"{self.__class__.__name__}._execute() must be implemented"
        )

    async def handle(self, data: TInput) -> None:
        """Template method with timing and error handling"""
        start = time()
        try:
            # calls _execute
            # - domains only need to implement _execute, and the measuring will be automatic
            result = await self._execute(data)
            duration = time() - start

            await self.handled(result)  # auto-forward to next domain
            await self.success(
                {
                    "domain": self.__class__.__name__,
                    "operation": "handle",
                    "duration": duration,
                }
            )

        except Exception as e:
            duration = time() - start
            await self.error(
                {
                    "domain": self.__class__.__name__,
                    "operation": "handle",
                    "error_type": type(e).__name__,
                }
            )
            raise  # Re-raise or handle based on your error strategy

    # ---------------------------------------------
    # - trigger callbacks

    async def handled(self, data):  # shared helper
        for cb in self._callbacks:
            await cb(data)

    async def success(self, event: dict) -> None:
        """Emit success event to all monitoring callbacks"""
        for cb in self._success_callbacks:
            await cb(event)

    async def error(self, event: dict) -> None:
        """Emit error event to all monitoring callbacks"""
        for cb in self._error_callbacks:
            await cb(event)

    # ---------------------------------------------
    # - registration of callbacks

    def on_handled(self, callback):  # concrete shared logic
        self._callbacks.append(callback)

    def on_success(self, callback) -> None:
        self._success_callbacks.append(callback)

    def on_error(self, callback) -> None:
        self._error_callbacks.append(callback)
