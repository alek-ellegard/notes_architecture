from base_domain.domains.base_domain import BaseDomain
from base_domain.environment import Environment


class ZMQManager(BaseDomain):
    def __init__(self, env: Environment) -> None:
        self.env = env
        pass

    def start(self) -> None:
        pass

    def handle(self, data) -> None:
        # nothing to handle since first in chain
        self.data = data
        pass
