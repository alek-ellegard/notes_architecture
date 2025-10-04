from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class ProcessorManager(BaseDomain[str, str]):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env

    def initialize(self) -> None:
        self.running = True
        pass

    async def _execute(self, data: str) -> str:
        """async _execute with underlying handle() running with await"""
        # process data
        processed_data = data
        return processed_data

    def shutdown(self) -> None:
        """Clean shutdown"""
        self.running = False
