import asyncio
import logging
import signal

import uvloop

from base_domain.environment import get_environment
from base_domain.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class Application:
    def __init__(self) -> None:
        self.env = get_environment()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.orchestrator = Orchestrator(self.env, logger)
        self.running = False

    def _shutdown_handler(self) -> None:
        """Graceful shutdown handler"""
        logger.info("Shutting down gracefully...")
        self.running = False
        self.orchestrator.shutdown()

    async def main(self) -> None:
        """Main application loop"""
        logger.info(f"Starting application in {self.env.MODE} mode...")
        logger.info(f"Listening on {self.env.ZMQ_ADDRESS}")

        try:
            self.orchestrator.initialize()
            self.running = True
            logger.info("Application started successfully")

            # Setup signal handlers for async
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._shutdown_handler)

            # Keep running until shutdown
            while self.running:
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Application cancelled")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            logger.info("Application shutdown complete")
            logger.info(
                f"Total pipelines completed: {self.orchestrator.completed_pipelines}"
            )


def run() -> None:
    app = Application()
    uvloop.run(app.main())


if __name__ == "__main__":
    run()
