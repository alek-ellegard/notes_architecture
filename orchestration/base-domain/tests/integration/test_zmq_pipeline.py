import pytest
import asyncio
import logging
from base_domain.domains.exporter_manager import ExporterManager
from base_domain.environment import Environment, Mode
from base_domain.orchestrator import Orchestrator
from .zmq_publisher import ZMQPublisher

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_zmq_pipeline_completion():
    """Test that messages flow through pipeline and count completions"""
    # 1) Arrange

    # Setup orchestrator
    env = Environment(
        MODE=Mode.dev, ZMQ_HOST="127.0.0.1", ZMQ_PORT=5555, ZMQ_ADDRESS=""
    )
    env.ZMQ_ADDRESS = f"tcp://{env.ZMQ_HOST}:{env.ZMQ_PORT}"

    test_logger = logging.getLogger("test")
    orchestrator = Orchestrator(env, test_logger)
    orchestrator.initialize()

    # Give ZMQ time to bind
    await asyncio.sleep(0.2)

    # Setup publisher
    publisher = ZMQPublisher()
    publisher_task = asyncio.create_task(publisher.main())

    # 2) Act

    # Wait for messages to be processed
    await asyncio.sleep(3)

    # Stop publisher
    publisher.running = False
    await asyncio.sleep(0.2)

    # 3) Assertions
    assert orchestrator.completed_pipelines >= 3, (
        f"Expected at least 3 completed pipelines, got {orchestrator.completed_pipelines}"
    )

    assert orchestrator.monitor.success_counts["ZMQManager.handle"] >= 3
    assert orchestrator.monitor.success_counts["ProcessorManager.handle"] >= 3
    assert orchestrator.monitor.success_counts["MetricsManager.handle"] >= 3
    assert orchestrator.monitor.success_counts["ExporterManager.handle"] >= 3

    # Check that last domain has exported data
    exporter = orchestrator.domains[-1]
    assert isinstance(exporter, ExporterManager)
    assert hasattr(exporter, "exported_data")
    assert exporter.exported_data is not None

    # 4) Cleanup
    publisher_task.cancel()
    try:
        await publisher_task
    except asyncio.CancelledError:
        pass

    orchestrator.shutdown()


if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_zmq_pipeline_completion())
    logger.info("✅ Integration test passed!")
