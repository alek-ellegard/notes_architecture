"""Tests for ZMQManager."""

import pytest

from base_domain.domains.zmq_manager import ZMQManager
from base_domain.environment import Environment, Mode
from tests.base_test_classes.base_domain_test import BaseDomainTest


class TestZMQManager(BaseDomainTest[bytes, dict]):
    """Test ZMQManager using BaseDomainTest.

    ZMQManager receives bytes via ZMQ and converts them to dict.
    """

    DOMAIN_CLASS = ZMQManager

    @pytest.fixture
    def domain_instance(self) -> ZMQManager:
        """Create ZMQManager instance with test environment."""
        env = Environment(
            MODE=Mode.dev,
            ZMQ_HOST="127.0.0.1",
            ZMQ_PORT=5555,
            ZMQ_ADDRESS="tcp://127.0.0.1:5555"
        )
        return ZMQManager(env)

    def _create_test_input(self) -> bytes:
        """Create test input for ZMQManager."""
        return b'{"test": "message"}'
