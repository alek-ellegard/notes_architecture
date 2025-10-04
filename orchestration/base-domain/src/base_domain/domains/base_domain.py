from abc import ABC, abstractmethod


class BaseDomain(ABC):
    def __init__(self):
        self._callbacks = []

    def on_handled(self, callback):  # concrete shared logic
        self._callbacks.append(callback)

    def handled(self, data):  # shared helper
        for cb in self._callbacks:
            cb(data)

    def on_completed(self, callback) -> None: ...
    def on_error(self, callback) -> None: ...

    @abstractmethod
    def handle(self, data): ...  # force implementation


class ZMQManager(BaseDomain):
    def handle(self, data):
        # use inherited on_handled, _trigger_callbacks
        self._trigger_callbacks(data)
