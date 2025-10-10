"""Benchmark tests comparing dataclass vs native Python class performance."""

import time

import pytest

from data_structures.dataclass_vs_native import (
    MetricPointDataclass,
    MetricPointNative,
)


@pytest.fixture
def sample_labels():
    """Sample labels for metric points."""
    return {"service": "test", "environment": "prod"}


@pytest.fixture
def timestamp():
    """Current timestamp in nanoseconds."""
    return time.time_ns()


class TestDataclassInstantiation:
    """Benchmark dataclass instantiation."""

    def test_dataclass_instantiation(self, benchmark, sample_labels, timestamp):
        """Benchmark creating dataclass instances."""
        result = benchmark(
            MetricPointDataclass,
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=timestamp,
        )
        assert result.name == "metric_test"

    def test_dataclass_with_varied_names(self, benchmark, sample_labels, timestamp):
        """Benchmark dataclass with varied metric names."""

        def create_instance(i):
            return MetricPointDataclass(
                name=f"metric_{i % 100}",
                type="counter",
                value=float(i),
                labels=sample_labels,
                timestamp_ns=timestamp,
            )

        result = benchmark(create_instance, 50)
        assert result.name == "metric_50"


class TestNativeInstantiation:
    """Benchmark native class instantiation."""

    def test_native_instantiation(self, benchmark, sample_labels, timestamp):
        """Benchmark creating native class instances."""
        result = benchmark(
            MetricPointNative,
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=timestamp,
        )
        assert result.name == "metric_test"

    def test_native_with_varied_names(self, benchmark, sample_labels, timestamp):
        """Benchmark native class with varied metric names."""

        def create_instance(i):
            return MetricPointNative(
                name=f"metric_{i % 100}",
                type="counter",
                value=float(i),
                labels=sample_labels,
                timestamp_ns=timestamp,
            )

        result = benchmark(create_instance, 50)
        assert result.name == "metric_50"


class TestHashingPerformance:
    """Benchmark hashing performance."""

    def test_dataclass_hashing(self, benchmark, sample_labels, timestamp):
        """Benchmark dataclass __hash__ performance."""
        instance = MetricPointDataclass(
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=timestamp,
        )
        result = benchmark(hash, instance)
        assert isinstance(result, int)

    def test_native_hashing(self, benchmark, sample_labels, timestamp):
        """Benchmark native class __hash__ performance."""
        instance = MetricPointNative(
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=timestamp,
        )
        result = benchmark(hash, instance)
        assert isinstance(result, int)


class TestEqualityComparison:
    """Benchmark equality comparison performance."""

    def test_dataclass_equality(self, benchmark, sample_labels, timestamp):
        """Benchmark dataclass __eq__ performance."""
        instance1 = MetricPointDataclass(
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=timestamp,
        )
        instance2 = MetricPointDataclass(
            name="metric_test",
            type="counter",
            value=43.0,
            labels=sample_labels,
            timestamp_ns=timestamp + 1000,
        )
        result = benchmark(instance1.__eq__, instance2)
        assert result is True

    def test_native_equality(self, benchmark, sample_labels, timestamp):
        """Benchmark native class __eq__ performance."""
        instance1 = MetricPointNative(
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=timestamp,
        )
        instance2 = MetricPointNative(
            name="metric_test",
            type="counter",
            value=43.0,
            labels=sample_labels,
            timestamp_ns=timestamp + 1000,
        )
        result = benchmark(instance1.__eq__, instance2)
        assert result is True
