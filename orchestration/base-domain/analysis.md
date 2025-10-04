# Architecture Analysis: Orchestrator & Monitor Pattern

## Overview
This codebase implements a **pipeline orchestration pattern** using domain-driven design with callback-based communication and centralized monitoring.

## Key Components

### 1. Orchestrator (`orchestrator.py`)
**Purpose**: Coordinates multiple domain managers in a sequential pipeline

**Architecture Pattern**: Chain of Responsibility + Observer

**Key Responsibilities**:
- **Domain Management**: Initializes and manages lifecycle of 4 domains:
  1. `ZMQManager` - Message ingestion
  2. `ProcessorManager` - Data processing
  3. `MetricsManager` - Metrics collection
  4. `ExporterManager` - Data export

- **Pipeline Wiring** (`_wire_pipeline`):
  - Links domains sequentially using callbacks
  - Each domain's `on_handled()` callback triggers next domain's `handle()` method
  - Data flows: ZMQ → Processor → Metrics → Exporter

- **Monitoring Wiring** (`_wire_monitoring`):
  - Attaches centralized Monitor to all domains
  - Captures success/error events via callbacks
  - Enables cross-domain observability

- **Completion Tracking** (`_wire_completion`):
  - Tracks completed vs failed pipelines
  - **Bug Found**: Line 72 references undefined `self.not_completed_pipelines` (should be initialized in `__init__`)

### 2. Monitor (`monitor.py`)
**Purpose**: Centralized metrics aggregation and performance tracking

**Pattern**: Observer + Metrics Collector

**Data Structures**:
```python
success_counts: defaultdict(int)           # Counter per operation
success_durations: defaultdict(deque)      # Rolling window (1000 samples)
error_counts: defaultdict(int)             # Error frequency
error_types: defaultdict(defaultdict(int)) # Nested error type breakdown
```

**Event Format**:
```python
# Success event
{
    'domain': 'processor',
    'operation': 'handle',
    'duration': 100  # milliseconds
}

# Error event
{
    'domain': 'processor',
    'operation': 'handle',
    'error_type': 'ValueError'
}
```

**Metrics Output**:
- **counts**: Success operation counts
- **errors**: Error operation counts
- **avg_duration**: Rolling average of durations (last 1000 samples)

## Architecture Strengths

1. **Loose Coupling**: Domains communicate via callbacks, not direct references
2. **Separation of Concerns**: Each domain has single responsibility
3. **Centralized Observability**: Monitor aggregates metrics from all domains
4. **Extensibility**: Easy to add new domains to pipeline
5. **Async-Ready**: Uses `async def` for non-blocking operations

## Observed Issues

### 1. Missing Attribute (Bug)
**Location**: `orchestrator.py:72`
```python
self.not_completed_pipelines += 1  # ❌ Never initialized
```
**Fix**: Add to `__init__`:
```python
self.not_completed_pipelines = 0
```

### 2. Empty Metrics Output
**Observation**: From logs, `get_metrics()` returns empty dict `{}`

**Root Cause**: Monitor callbacks might not be firing or events not structured correctly

**Debug Steps**:
1. Verify domains emit events via `on_success()`/`on_error()`
2. Check event dict structure matches expected format
3. Add logging in Monitor callbacks to trace event flow

### 3. Logging Pattern Issue
**Location**: `orchestrator.py:73`
```python
self.logger.info("metrics: ", self.monitor.get_metrics())
```
**Problem**: Second argument not interpolated in log message
**Fix**: Use f-string or proper formatting:
```python
self.logger.info(f"metrics: {self.monitor.get_metrics()}")
```

## Data Flow Diagram

```
┌─────────────┐
│ ZMQManager  │ ← Receives messages
└──────┬──────┘
       │ on_handled() callback
       ↓
┌─────────────────┐
│ProcessorManager │ ← Processes data
└────────┬────────┘
         │ on_handled() callback
         ↓
┌────────────────┐
│MetricsManager  │ ← Collects metrics
└───────┬────────┘
        │ on_handled() callback
        ↓
┌────────────────┐
│ExporterManager │ ← Exports results
└───────┬────────┘
        │ on_handled() callback
        ↓
┌──────────────────────┐
│on_pipeline_complete()│ ← Tracks completion
└──────────────────────┘

       ┌─────────┐
       │ Monitor │ ← Observes all domains
       └─────────┘
         ↑     ↑
    on_success  on_error
         │     │
    (all domains emit events)
```

## Recommendations

1. **Fix Critical Bug**: Initialize `not_completed_pipelines` counter
2. **Fix Logging**: Use proper string formatting for metrics output
3. **Debug Monitoring**: Add instrumentation to verify event emission
4. **Add Type Hints**: BaseDomain interface not shown but should define callback contracts
5. **Error Handling**: Add exception handling in pipeline callbacks to prevent cascade failures
6. **Metrics Persistence**: Consider exporting Monitor data periodically (currently in-memory only)
