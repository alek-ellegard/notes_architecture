#!/usr/bin/env python3
"""Benchmark comparing dataclass vs native Python class instantiation performance."""

import time
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MetricPointDataclass:
    """Dataclass version of MetricPoint."""

    name: str
    type: str
    value: float
    labels: Dict[str, str]
    timestamp_ns: int

    def __hash__(self) -> int:
        return hash((self.name, tuple(sorted(self.labels.items()))))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricPointDataclass):
            return False
        return self.name == other.name and self.labels == other.labels


class MetricPointNative:
    """Native Python class version of MetricPoint."""

    __slots__ = ("name", "type", "value", "labels", "timestamp_ns")

    def __init__(
        self,
        name: str,
        type: str,
        value: float,
        labels: Dict[str, str],
        timestamp_ns: int,
    ):
        self.name = name
        self.type = type
        self.value = value
        self.labels = labels
        self.timestamp_ns = timestamp_ns

    def __hash__(self) -> int:
        return hash((self.name, tuple(sorted(self.labels.items()))))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricPointNative):
            return False
        return self.name == other.name and self.labels == other.labels


def benchmark_instantiation(class_type, iterations: int = 1_000_000):
    """Benchmark class instantiation."""
    labels = {"service": "test", "environment": "prod"}

    start = time.perf_counter()
    for i in range(iterations):
        obj = class_type(
            name=f"metric_{i % 100}",
            type="counter",
            value=float(i),
            labels=labels,
            timestamp_ns=time.time_ns(),
        )
    end = time.perf_counter()

    total_time = end - start
    time_per_instance = (total_time / iterations) * 1_000_000  # Convert to microseconds

    return total_time, time_per_instance


def main():
    print("Benchmarking dataclass vs native Python class instantiation")
    print("=" * 60)

    # Warm up
    benchmark_instantiation(MetricPointDataclass, 1000)
    benchmark_instantiation(MetricPointNative, 1000)

    # Actual benchmark
    iterations = 1_000_000

    print(f"\nCreating {iterations:,} instances...")
    print("-" * 60)

    # Benchmark dataclass
    dc_total, dc_per = benchmark_instantiation(MetricPointDataclass, iterations)
    print(f"Dataclass:")
    print(f"  Total time: {dc_total:.3f} seconds")
    print(f"  Per instance: {dc_per:.3f} microseconds")

    # Benchmark native class
    native_total, native_per = benchmark_instantiation(MetricPointNative, iterations)
    print(f"\nNative class:")
    print(f"  Total time: {native_total:.3f} seconds")
    print(f"  Per instance: {native_per:.3f} microseconds")

    # Calculate difference
    speedup = (dc_total - native_total) / dc_total * 100
    print(f"\nNative class is {speedup:.1f}% faster than dataclass")

    # Memory usage comparison
    import sys

    dc_instance = MetricPointDataclass("test", "counter", 1.0, {"a": "b"}, 123456789)
    native_instance = MetricPointNative("test", "counter", 1.0, {"a": "b"}, 123456789)

    print(f"\nMemory usage:")
    print(f"  Dataclass instance: {sys.getsizeof(dc_instance)} bytes")
    print(f"  Native instance: {sys.getsizeof(native_instance)} bytes")


if __name__ == "__main__":
    main()
