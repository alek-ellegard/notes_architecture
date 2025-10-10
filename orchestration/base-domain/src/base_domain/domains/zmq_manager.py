import zmq
import zmq.asyncio
import asyncio
import orjson
from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class ZMQManager(BaseDomain[bytes, dict]):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env
        self.running = False
        self.context = None
        self.socket = None
        self._task = None

    def initialize(self) -> None:
        """initialize by binding and creating task"""
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.subscribe("")  # Subscribe to all messages
        self.socket.bind(self.env.ZMQ_ADDRESS)
        self._task = asyncio.create_task(self.message_loop())
        self.running = True

    async def message_loop(self) -> None:
        """Simple message processing loop - receives and triggers pipeline"""
        while self.running:
            message: bytes = await self.socket.recv()
            await self.handle(message)  # triggers the pipeline

    async def _execute(self, data: bytes) -> dict:
        """Convert bytes to dict"""
        return orjson.loads(data.decode("utf-8"))

    def shutdown(self) -> None:
        """Clean shutdown"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
