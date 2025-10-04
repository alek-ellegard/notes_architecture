from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class ExporterManager(BaseDomain[dict, bool]):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env

    def initialize(self) -> None:
        self.running = False

    async def _execute(self, data: dict) -> bool:
        # export data (end of pipeline)
        self.exported_data = data
        return True  # success indicator

    def shutdown(self) -> None:
        """Clean shutdown"""
        self.running = False
