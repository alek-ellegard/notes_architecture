"""
Simple ZMQ Publisher for manual testing

Usage:
    python tests/integration/zmq_publisher.py

This will publish test messages to the ZMQ pipeline.
Run the main application first to receive these messages.
"""

import zmq
import orjson
import asyncio
import signal
import uvloop
import logging

logger = logging.getLogger(__name__)


class ZMQPublisher:
    def __init__(self) -> None:
        self.running = False
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.message_count = 0

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _shutdown_handler(self) -> None:
        """Graceful shutdown handler"""
        logger.info("\nShutting down gracefully...")
        self.running = False

    async def main(self) -> None:
        try:
            # Setup publisher
            self.publisher.connect("tcp://127.0.0.1:5555")
            logger.info("Publisher started. Connecting...")

            # Wait for slow joiner problem
            await asyncio.sleep(1)

            self.running = True
            logger.info("Starting to send messages...")

            # Setup signal handlers for async
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._shutdown_handler)

            # Test messages
            messages = [
                {"id": 1, "type": "event", "data": "first message"},
                {"id": 2, "type": "event", "data": "second message"},
                {"id": 3, "type": "event", "data": "third message"},
                {"id": 4, "type": "metric", "value": 42},
                {"id": 5, "type": "metric", "value": 100},
            ]

            # Keep running and publishing
            while self.running:
                for msg in messages:
                    if not self.running:
                        break
                    self.message_count += 1
                    msg_with_count = {**msg, "msg_num": self.message_count}
                    self.publisher.send(orjson.dumps(msg_with_count))
                    logger.info(f"  [{self.message_count}] Sent: {msg_with_count}")
                    await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            logger.info("Publisher cancelled")
        except Exception as e:
            logger.info(f"Error in publisher: {e}")
        finally:
            logger.info(
                f"Publisher shutdown complete. Total messages sent: {self.message_count}"
            )
            self.publisher.close()
            self.context.term()


def run() -> None:
    app = ZMQPublisher()
    uvloop.run(app.main())


if __name__ == "__main__":
    run()
