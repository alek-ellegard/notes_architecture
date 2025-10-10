"""Core testing infrastructure for BaseDomain components."""

from abc import ABC
from typing import Generic, TypeVar
from unittest.mock import AsyncMock

import pytest

from base_domain.domains.base_domain import BaseDomain

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseDomainTest(ABC, Generic[TInput, TOutput]):
    """Base test class for all BaseDomain components.

    This provides standardized testing for BaseDomain inheritance patterns.

    Subclasses should:
    1. Set DOMAIN_CLASS class attribute
    2. Override _create_test_input() to return sample input data
    3. Add domain-specific tests as needed

    Example:
        class TestMyDomain(BaseDomainTest[bytes, dict]):
            DOMAIN_CLASS = MyDomain

            def _create_test_input(self) -> bytes:
                return b'{"test": "data"}'
    """

    # Class attribute to be set by subclasses
    DOMAIN_CLASS: type[BaseDomain] | None = None

    # Fixtures

    @pytest.fixture
    def domain_instance(self) -> BaseDomain[TInput, TOutput]:
        """Create a domain instance for testing."""
        if self.DOMAIN_CLASS is None:
            pytest.skip("DOMAIN_CLASS not set in test class")
        return self.DOMAIN_CLASS()

    # Standard tests

    @pytest.mark.asyncio
    async def test_inheritance(self, domain_instance: BaseDomain):
        """Test that domain inherits from BaseDomain."""
        assert isinstance(domain_instance, BaseDomain)

    @pytest.mark.asyncio
    async def test_required_attributes(self, domain_instance: BaseDomain):
        """Test that required attributes exist."""
        assert hasattr(domain_instance, "_callbacks")
        assert hasattr(domain_instance, "_success_callbacks")
        assert hasattr(domain_instance, "_error_callbacks")
        assert isinstance(domain_instance._callbacks, list)
        assert isinstance(domain_instance._success_callbacks, list)
        assert isinstance(domain_instance._error_callbacks, list)

    @pytest.mark.asyncio
    async def test_required_methods_exist(self, domain_instance: BaseDomain):
        """Test that all required methods exist."""
        required_methods = [
            "initialize",
            "shutdown",
            "_execute",
            "handle",
            "handled",
            "success",
            "error",
            "on_handled",
            "on_success",
            "on_error",
        ]

        for method_name in required_methods:
            assert hasattr(domain_instance, method_name), f"Missing method: {method_name}"
            assert callable(getattr(domain_instance, method_name))

    @pytest.mark.asyncio
    async def test_callback_registration(self, domain_instance: BaseDomain):
        """Test callback registration."""
        handled_cb = AsyncMock()
        success_cb = AsyncMock()
        error_cb = AsyncMock()

        domain_instance.on_handled(handled_cb)
        domain_instance.on_success(success_cb)
        domain_instance.on_error(error_cb)

        assert handled_cb in domain_instance._callbacks
        assert success_cb in domain_instance._success_callbacks
        assert error_cb in domain_instance._error_callbacks

    @pytest.mark.asyncio
    async def test_handle_flow(self, domain_instance: BaseDomain):
        """Test the handle() -> _execute() -> handled() flow."""
        test_input = self._create_test_input()

        # Track callbacks
        handled_cb = AsyncMock()
        success_cb = AsyncMock()

        domain_instance.on_handled(handled_cb)
        domain_instance.on_success(success_cb)

        # Execute
        await domain_instance.handle(test_input)

        # Verify callbacks were called
        handled_cb.assert_called_once()
        success_cb.assert_called_once()

        # Verify success callback structure
        success_args = success_cb.call_args[0][0]
        assert "domain" in success_args
        assert "operation" in success_args
        assert "duration" in success_args
        assert success_args["domain"] == domain_instance.__class__.__name__
        assert success_args["operation"] == "handle"

    @pytest.mark.asyncio
    async def test_error_handling(self, domain_instance: BaseDomain):
        """Test error handling flow."""
        test_input = self._create_test_input()

        # Track error callback
        error_cb = AsyncMock()
        domain_instance.on_error(error_cb)

        # Mock _execute to raise error
        original_execute = domain_instance._execute

        async def failing_execute(data):
            raise ValueError("Test error")

        domain_instance._execute = failing_execute

        # Execute and expect error
        with pytest.raises(ValueError, match="Test error"):
            await domain_instance.handle(test_input)

        # Verify error callback was called
        error_cb.assert_called_once()

        # Verify error callback structure
        error_args = error_cb.call_args[0][0]
        assert "domain" in error_args
        assert "operation" in error_args
        assert "error_type" in error_args
        assert error_args["domain"] == domain_instance.__class__.__name__
        assert error_args["operation"] == "handle"
        assert error_args["error_type"] == "ValueError"

        # Restore
        domain_instance._execute = original_execute

    # Template methods for subclasses

    def _create_test_input(self) -> TInput:
        """Create test input data.

        Override this in subclasses to provide appropriate test data.
        """
        return "test_data"  # type: ignore
