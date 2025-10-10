"""Tests for ExporterManager."""

import pytest

from base_domain.domains.exporter_manager import ExporterManager
from base_domain.environment import Environment, Mode
from tests.base_test_classes.base_domain_test import BaseDomainTest


class TestExporterManager(BaseDomainTest[dict, bool]):
    """Test ExporterManager using BaseDomainTest.

    ExporterManager exports dict data and returns success indicator.
    """

    DOMAIN_CLASS = ExporterManager

    @pytest.fixture
    def domain_instance(self) -> ExporterManager:
        """Create ExporterManager instance with test environment."""
        env = Environment(MODE=Mode.dev)
        return ExporterManager(env)

    def _create_test_input(self) -> dict:
        """Create test input for ExporterManager."""
        return {"metric": "value", "timestamp": 123456}
