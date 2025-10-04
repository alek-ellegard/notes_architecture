from __future__ import annotations

from base_domain.environment import Environment

from base_domain.domains.base_domain import BaseDomain
from base_domain.domains.exporter_manager import ExporterManager
from base_domain.domains.metrics_manager import MetricsManager
from base_domain.domains.monitor import Monitor
from base_domain.domains.processor_manager import ProcessorManager
from base_domain.domains.zmq_manager import ZMQManager


class Orchestrator:
    def __init__(self, env: Environment) -> None:
        # infra
        self.monitor = Monitor()

        # domains
        self.domains: list[BaseDomain] = [
            ZMQManager(env),
            ProcessorManager(env),
            MetricsManager(env),
            ExporterManager(env),
        ]

    def initialize(self):
        self._wire_pipeline()
        self._wire_monitoring()

    def _wire_pipeline(self):
        """
        data flow
        1. zmq
        2. processor
        3. metrics
        4. exporter

        callbacks :
        - on_handled -- when data ready for next domain
        - handle -- activate domain with data
        """
        for prev, next in zip(self.domains, self.domains[1:]):
            prev.on_handled(next.handle)

    def _wire_monitoring(self):
        """Monitoring hooks for Domains"""
        for domain in self.domains:
            domain.on_completed(self.monitor.on_completed)
            domain.on_error(self.monitor.on_error)
