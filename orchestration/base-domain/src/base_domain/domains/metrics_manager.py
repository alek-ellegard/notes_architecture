from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class MetricsManager(BaseDomain[str, dict]):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env

    def initialize(self) -> None:
        self.running = False

    async def _execute(self, data: str) -> dict[str, str]:
        # collect metrics from data
        metrics_data: dict[str, str] = {}
        metrics_data["some_metric"] = data
        return metrics_data

    def shutdown(self) -> None:
        """Clean shutdown"""
        self.running = False
