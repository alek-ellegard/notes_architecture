"""Tests for MetricsManager."""

import pytest

from base_domain.domains.metrics_manager import MetricsManager
from base_domain.environment import Environment, Mode
from tests.base_test_classes.base_domain_test import BaseDomainTest


class TestMetricsManager(BaseDomainTest[str, dict]):
    """Test MetricsManager using BaseDomainTest.

    MetricsManager collects metrics from string data and returns dict.
    """

    DOMAIN_CLASS = MetricsManager

    @pytest.fixture
    def domain_instance(self) -> MetricsManager:
        """Create MetricsManager instance with test environment."""
        env = Environment(MODE=Mode.dev)
        return MetricsManager(env)

    def _create_test_input(self) -> str:
        """Create test input for MetricsManager."""
        return "test_metric_data"
