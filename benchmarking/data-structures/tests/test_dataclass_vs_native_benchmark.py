#!/usr/bin/env python3
"""Pytest benchmark tests for dataclass vs native class performance."""

import time

import pytest

from data_structures.dataclass_vs_native import (
    MetricPointDataclass,
    MetricPointNative,
)


@pytest.fixture
def sample_labels():
    """Sample labels for testing."""
    return {"service": "test", "environment": "prod"}


def test_benchmark_dataclass_instantiation(benchmark, sample_labels):
    """Benchmark dataclass instantiation."""

    def create_instance():
        return MetricPointDataclass(
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=time.time_ns(),
        )

    result = benchmark(create_instance)
    assert result.name == "metric_test"


def test_benchmark_native_instantiation(benchmark, sample_labels):
    """Benchmark native class instantiation."""

    def create_instance():
        return MetricPointNative(
            name="metric_test",
            type="counter",
            value=42.0,
            labels=sample_labels,
            timestamp_ns=time.time_ns(),
        )

    result = benchmark(create_instance)
    assert result.name == "metric_test"


def test_benchmark_dataclass_hash(benchmark, sample_labels):
    """Benchmark dataclass hash operation."""
    instance = MetricPointDataclass(
        name="metric_test",
        type="counter",
        value=42.0,
        labels=sample_labels,
        timestamp_ns=time.time_ns(),
    )

    result = benchmark(hash, instance)
    assert isinstance(result, int)


def test_benchmark_native_hash(benchmark, sample_labels):
    """Benchmark native class hash operation."""
    instance = MetricPointNative(
        name="metric_test",
        type="counter",
        value=42.0,
        labels=sample_labels,
        timestamp_ns=time.time_ns(),
    )

    result = benchmark(hash, instance)
    assert isinstance(result, int)


def test_benchmark_dataclass_equality(benchmark, sample_labels):
    """Benchmark dataclass equality comparison."""
    instance1 = MetricPointDataclass(
        name="metric_test",
        type="counter",
        value=42.0,
        labels=sample_labels,
        timestamp_ns=time.time_ns(),
    )
    instance2 = MetricPointDataclass(
        name="metric_test",
        type="counter",
        value=43.0,
        labels=sample_labels,
        timestamp_ns=time.time_ns(),
    )

    result = benchmark(lambda: instance1 == instance2)
    assert result is True


def test_benchmark_native_equality(benchmark, sample_labels):
    """Benchmark native class equality comparison."""
    instance1 = MetricPointNative(
        name="metric_test",
        type="counter",
        value=42.0,
        labels=sample_labels,
        timestamp_ns=time.time_ns(),
    )
    instance2 = MetricPointNative(
        name="metric_test",
        type="counter",
        value=43.0,
        labels=sample_labels,
        timestamp_ns=time.time_ns(),
    )

    result = benchmark(lambda: instance1 == instance2)
    assert result is True
