"""Tests for ProcessorManager."""

import pytest

from base_domain.domains.processor_manager import ProcessorManager
from base_domain.environment import Environment, Mode
from tests.base_test_classes.base_domain_test import BaseDomainTest


class TestProcessorManager(BaseDomainTest[str, str]):
    """Test ProcessorManager using BaseDomainTest.

    ProcessorManager processes string data.
    """

    DOMAIN_CLASS = ProcessorManager

    @pytest.fixture
    def domain_instance(self) -> ProcessorManager:
        """Create ProcessorManager instance with test environment."""
        env = Environment(MODE=Mode.dev)
        return ProcessorManager(env)

    def _create_test_input(self) -> str:
        """Create test input for ProcessorManager."""
        return "test_data"
