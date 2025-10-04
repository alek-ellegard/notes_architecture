from collections import defaultdict, deque
from logging import Logger


class Monitor:
    """
    counting: success and error types
    - frequency
    - nested
    accumulating:
    - duration times
    exposing: with get_stats()
    """

    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        # counting
        self.success_counts = defaultdict(int)
        self.success_durations = defaultdict(lambda: deque(maxlen=1000))
        self.MS = 1000000
        self.error_counts = defaultdict(int)
        self.error_types = defaultdict(lambda: defaultdict(int))
        # counts for completed_pipelines
        self.count: int = 0
        self.completed_pipelines: int = 0
        self.not_completed_pipelines: int = 0

    async def on_success(self, event: dict) -> None:
        """
        event: [
            domain: "processor",
            operation: "handle",
            duration: 100
        ]
        """
        key = f"{event['domain']}.{event['operation']}"
        self.success_counts[key] += 1
        self.success_durations[key].append(event["duration"])

    async def on_error(self, event: dict) -> None:
        """
        event: [
            domain: "processor",
            operation: "handle",
            error_type: Exception.xyz
        ]
        """
        key = f"{event['domain']}.{event['operation']}"
        self.error_counts[key] += 1
        self.error_types[key][event["error_type"]] += 1

    async def on_pipeline_complete(self, result: bool) -> None:
        """Called when pipeline completes successfully"""
        self.count += 1
        if result:
            self.completed_pipelines += 1
            self.logger.info(f"pipeline completed: {self.completed_pipelines}")
        else:
            self.not_completed_pipelines += 1
            self.logger.info(f"pipeline not completed: {self.not_completed_pipelines}")
        if self.count % 5 == 0:
            self.logger.info(f"metrics: {self.get_metrics()}")

    def get_metrics(self) -> dict:
        averages = {
            # average and round
            key: round((sum(durations) / len(durations)) * self.MS, 2)
            for key, durations in self.success_durations.items()
            if durations
        }
        return {
            "counts": dict(self.success_counts),
            "errors": dict(self.error_counts),
            "avg_duration_ms": averages,
        }
