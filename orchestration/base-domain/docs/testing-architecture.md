# Testing Architecture

## Overview

The test suite uses inheritance-based testing that mirrors the domain architecture. All domain tests inherit from `BaseDomainTest`, providing standardized testing for `BaseDomain` components.

**Test Count**: 25 tests (21 unit + 4 integration)

## BaseDomainTest Base Class

`BaseDomainTest[TInput, TOutput]` provides 6 standard tests:

1. **Inheritance**: Verifies domain inherits from `BaseDomain`
2. **Attributes**: Validates callback lists exist
3. **Methods**: Ensures required methods exist (`initialize`, `shutdown`, `_execute`, `handle`, callbacks)
4. **Callback Registration**: Tests `on_handled()`, `on_success()`, `on_error()`
5. **Handle Flow**: Validates `handle()` → `_execute()` → `handled()` → `success()` chain
6. **Error Handling**: Tests error propagation and `error()` callback emission

Subclasses must:
- Set `DOMAIN_CLASS` to the domain being tested
- Override `_create_test_input()` to return test data
- Optionally override `domain_instance` fixture for custom initialization

## Writing Tests for New Domains

### Minimal Example

```python
from base_domain.domains.my_domain import MyDomain
from tests.base_test_classes.base_domain_test import BaseDomainTest

class TestMyDomain(BaseDomainTest[bytes, dict]):
    """Test MyDomain using BaseDomainTest."""

    DOMAIN_CLASS = MyDomain

    def _create_test_input(self) -> bytes:
        return b'{"test": "data"}'
```

This minimal implementation automatically inherits all 6 standard tests.

### With Custom Initialization

```python
import pytest
from base_domain.domains.processor_manager import ProcessorManager
from base_domain.environment import Environment, Mode
from tests.base_test_classes.base_domain_test import BaseDomainTest

class TestProcessorManager(BaseDomainTest[str, str]):
    DOMAIN_CLASS = ProcessorManager

    @pytest.fixture
    def domain_instance(self) -> ProcessorManager:
        env = Environment(MODE=Mode.dev)
        return ProcessorManager(env)

    def _create_test_input(self) -> str:
        return "test_data"
```

### Adding Domain-Specific Tests

Add custom tests by defining new test methods in your test class. They automatically get access to the `domain_instance` fixture.

## Running Tests

```bash
make test                                    # All tests
make test-f f=tests/test_processor_manager.py  # Specific file
make test-integration                        # Integration tests
make test-setup-show                         # Show test setup details
```

## Current Test Structure

```
tests/
├── base_test_classes/
│   └── base_domain_test.py       # Base test class with 6 standard tests
├── test_zmq_manager.py            # 6 tests (inherited)
├── test_processor_manager.py      # 6 tests (inherited)
├── test_metrics_manager.py        # 6 tests (inherited)
└── test_exporter_manager.py       # 6 tests (inherited)
```

Each concrete test class inherits all 6 standard tests, ensuring consistent testing across all domains.
