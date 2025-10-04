# Monitoring Integration Pattern

## Core Design

**Principle**: Domains emit standardized events → Central monitor aggregates → export

**Key insight**: `on_completed` and `on_error` as universal hooks for observability without domain pollution.

---

## Enhanced BaseDomain

### `base_domain.py`

```python
from collections import defaultdict
from typing import Callable, Any
from time import time

class BaseDomain:
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self._callbacks = defaultdict(list)
    
    def register_callback(self, event: str, callback: Callable):
        self._callbacks[event].append(callback)
    
    def _emit(self, event: str, data: Any):
        for cb in self._callbacks[event]:
            cb(data)
    
    # Standard monitoring hooks
    def on_completed(self, callback: Callable):
        """Called when domain operation succeeds"""
        self.register_callback('completed', callback)
    
    def on_error(self, callback: Callable):
        """Called when domain operation fails"""
        self.register_callback('error', callback)
    
    # Emit helpers with standard context
    def _emit_completed(self, operation: str, data: Any, duration: float):
        self._emit('completed', {
            'domain': self.domain_name,
            'operation': operation,
            'data': data,
            'duration': duration,
            'timestamp': time()
        })
    
    def _emit_error(self, operation: str, error: Exception, data: Any = None):
        self._emit('error', {
            'domain': self.domain_name,
            'operation': operation,
            'error': error,
            'error_type': type(error).__name__,
            'data': data,
            'timestamp': time()
        })
```

---

## Domain Implementation Pattern

### `processor_manager.py`

```python
from base_domain import BaseDomain
from time import time

class ProcessorManager(BaseDomain):
    def __init__(self, rules):
        super().__init__('processor')
        self.rules = rules
    
    def on_processed(self, callback):
        """Domain-specific callback for processed data"""
        self.register_callback('processed', callback)
    
    def handle(self, raw_bytes):
        start = time()
        try:
            result = self._process(raw_bytes)
            duration = time() - start
            
            # Domain-specific event
            self._emit('processed', result)
            
            # Monitoring event
            self._emit_completed('handle', result, duration)
            
        except Exception as e:
            duration = time() - start
            self._emit_error('handle', e, {'input_size': len(raw_bytes)})
    
    def _process(self, raw_bytes):
        # Actual processing logic
        return {'parsed': raw_bytes, 'type': 'sensor_data'}
```

### `metrics_manager.py`

```python
from base_domain import BaseDomain
from time import time

class MetricsManager(BaseDomain):
    def __init__(self, config):
        super().__init__('metrics')
        self.config = config
    
    def on_recorded(self, callback):
        self.register_callback('recorded', callback)
    
    def record_latency(self, data):
        start = time()
        try:
            latency = self._compute_latency(data)
            self._store_metric('latency', latency)
            duration = time() - start
            
            self._emit_completed('record_latency', latency, duration)
            
        except Exception as e:
            self._emit_error('record_latency', e, data)
    
    def record_size(self, data):
        start = time()
        try:
            size = len(data.get('parsed', b''))
            self._store_metric('size', size)
            duration = time() - start
            
            self._emit_completed('record_size', size, duration)
            
        except Exception as e:
            self._emit_error('record_size', e, data)
```

---

## Central Monitoring Class

### `monitor.py`

```python
from collections import defaultdict
from time import time

class Monitor:
    def __init__(self):
        # Success metrics
        self.operation_counts = defaultdict(int)
        self.operation_durations = defaultdict(list)
        self.data_types = defaultdict(int)
        
        # Error metrics
        self.error_counts = defaultdict(int)
        self.error_types = defaultdict(lambda: defaultdict(int))
        
        self.window_start = time()
    
    def on_completed(self, event: dict):
        """
        event = {
            'domain': str,
            'operation': str, 
            'data': Any,
            'duration': float,
            'timestamp': float
        }
        """
        key = f"{event['domain']}.{event['operation']}"
        
        # Count operations
        self.operation_counts[key] += 1
        
        # Track latency
        self.operation_durations[key].append(event['duration'])
        
        # Track data types if present
        if isinstance(event['data'], dict) and 'type' in event['data']:
            self.data_types[event['data']['type']] += 1
    
    def on_error(self, event: dict):
        """
        event = {
            'domain': str,
            'operation': str,
            'error': Exception,
            'error_type': str,
            'data': Any,
            'timestamp': float
        }
        """
        key = f"{event['domain']}.{event['operation']}"
        
        # Count errors
        self.error_counts[key] += 1
        
        # Track error types per operation
        self.error_types[key][event['error_type']] += 1
    
    def get_metrics(self) -> dict:
        """Return current metrics snapshot"""
        window_duration = time() - self.window_start
        
        return {
            'success_metrics': {
                'operation_counts': dict(self.operation_counts),
                'operation_rates': {
                    k: v / window_duration 
                    for k, v in self.operation_counts.items()
                },
                'latencies': {
                    k: {
                        'p50': self._percentile(v, 0.5),
                        'p95': self._percentile(v, 0.95),
                        'p99': self._percentile(v, 0.99),
                    }
                    for k, v in self.operation_durations.items()
                },
                'data_type_counts': dict(self.data_types)
            },
            'error_metrics': {
                'error_counts': dict(self.error_counts),
                'error_rates': {
                    k: v / window_duration 
                    for k, v in self.error_counts.items()
                },
                'error_types': {
                    k: dict(v) 
                    for k, v in self.error_types.items()
                }
            },
            'window_duration': window_duration
        }
    
    def _percentile(self, values: list, p: float) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * p)
        return sorted_vals[min(idx, len(sorted_vals) - 1)]
    
    def reset(self):
        """Reset metrics for new window"""
        self.operation_counts.clear()
        self.operation_durations.clear()
        self.data_types.clear()
        self.error_counts.clear()
        self.error_types.clear()
        self.window_start = time()
```

---

## Orchestrator Wiring

### `orchestrator.py`

```python
from monitor import Monitor

class Orchestrator:
    def __init__(self, env):
        # Initialize monitor first
        self.monitor = Monitor()
        
        # Initialize domains
        self.zmq = ZMQManager(env.zmq_addr)
        self.processor = ProcessorManager(env.rules)
        self.metrics = MetricsManager(env.metric_config)
        self.exporter = ExporterManager(env.otlp_endpoint)
        
        # Wire everything
        self._wire_data_pipeline()
        self._wire_metrics()
        self._wire_monitoring()  # New: universal monitoring
    
    def _wire_data_pipeline(self):
        self.zmq.on_message(self.processor.handle)
        self.processor.on_processed(self.exporter.send)
    
    def _wire_metrics(self):
        self.processor.on_processed(self.metrics.record_latency)
        self.processor.on_processed(self.metrics.record_size)
    
    def _wire_monitoring(self):
        """Wire all domains to central monitor"""
        for domain in [self.zmq, self.processor, self.metrics, self.exporter]:
            domain.on_completed(self.monitor.on_completed)
            domain.on_error(self.monitor.on_error)
```

---

## Usage Example

### Metrics Export Integration

```python
class Orchestrator:
    def _wire_monitoring(self):
        # Wire domains to monitor
        for domain in [self.zmq, self.processor, self.metrics, self.exporter]:
            domain.on_completed(self.monitor.on_completed)
            domain.on_error(self.monitor.on_error)
        
        # Periodic metrics export (example: every 60s)
        self._start_metrics_export_loop()
    
    def _start_metrics_export_loop(self):
        import threading
        
        def export_metrics():
            while True:
                time.sleep(60)
                snapshot = self.monitor.get_metrics()
                self.exporter.send_metrics(snapshot)
                self.monitor.reset()
        
        thread = threading.Thread(target=export_metrics, daemon=True)
        thread.start()
```

---

## Alternative: Monitor as Domain

**If monitor should participate in pipeline**:

### `monitor.py`

```python
from base_domain import BaseDomain

class Monitor(BaseDomain):
    def __init__(self):
        super().__init__('monitor')
        # ... same metrics tracking
    
    def on_metric_ready(self, callback):
        """Called when metrics are aggregated"""
        self.register_callback('metric_ready', callback)
    
    def flush_metrics(self):
        """Aggregate and emit metrics"""
        snapshot = self.get_metrics()
        self._emit('metric_ready', snapshot)
        self.reset()
```

### `orchestrator.py`

```python
class Orchestrator:
    def __init__(self, env):
        self.monitor = Monitor()
        # ... other domains
        
        self._wire_data_pipeline()
        self._wire_monitoring()
    
    def _wire_monitoring(self):
        # All domains report to monitor
        for domain in [self.processor, self.metrics, self.exporter]:
            domain.on_completed(self.monitor.on_completed)
            domain.on_error(self.monitor.on_error)
        
        # Monitor emits to exporter
        self.monitor.on_metric_ready(self.exporter.send_metrics)
```

---

## Key Benefits

**Separation of concerns**: Domains don't know about monitoring  
**Universal interface**: Same `on_completed`/`on_error` signature everywhere  
**Centralized aggregation**: Single source of truth for metrics  
**No domain pollution**: Monitoring logic lives in monitor, not scattered  
**Easy testing**: Mock monitor to verify domain emissions
