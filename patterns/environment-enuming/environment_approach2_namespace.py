"""Environment configuration for sol-vol-exporter.
APPROACH 2: Namespace Pattern - Type-safe with logical grouping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from os import environ as env

# from caesari_logger.std_logger import get_logger
import logging

logger = logging.getLogger(__name__)


class SolVolMode(StrEnum):
    prod = "prod"
    dev = "dev"
    staging = "staging"


class BINANCE_CONFIG:
    """Namespace for Binance configuration using typed enums.

    Groups related configs while maintaining type safety.
    """

    class STRINGS(StrEnum):
        """String-based configuration values."""

        symbol = "SOLUSDT"
        interval = "1m"
        ws_url = "wss://stream.binance.com:9443/ws"

    class SETTINGS(IntEnum):
        """Integer-based configuration values."""

        buffer_size = 1440  # 24 hours of 1-minute candles
        max_reconnect_attempts = 10

    @classmethod
    def as_dict(cls) -> dict:
        """Convert all configs to dictionary."""
        result = {}
        # Add string configs
        for member in cls.STRINGS:
            result[member.name] = member.value
        # Add integer configs
        for member in cls.SETTINGS:
            result[member.name] = member.value
        return result


@dataclass
class SolVolEnvironment:
    """Environment configuration for sol-vol-exporter."""

    MODE: SolVolMode
    LOG_LEVEL: str = "INFO"

    # Store config as dict from namespace
    binance_config: dict = field(default_factory=BINANCE_CONFIG.as_dict)

    volatility_windows_minutes: list[int] = field(default_factory=lambda: [15, 30, 60])

    # Database configuration (optional - for future persistence)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sol_vol_exporter"
    db_user: str = "postgres"
    db_password: str = ""


def get_sol_vol_environment() -> SolVolEnvironment:
    """Get environment configuration with overrides from env vars."""
    mode = SolVolMode(env.get("MODE", "dev"))
    log_level = env.get("LOG_LEVEL", "DEBUG")

    # Override from environment variables with type-safe access
    binance_config = {
        "symbol": env.get("BINANCE_SYMBOL", BINANCE_CONFIG.STRINGS.symbol),
        "interval": env.get("BINANCE_INTERVAL", BINANCE_CONFIG.STRINGS.interval),
        "ws_url": env.get("BINANCE_WS_URL", BINANCE_CONFIG.STRINGS.ws_url),
        "buffer_size": int(
            env.get("BINANCE_BUFFER_SIZE", str(BINANCE_CONFIG.SETTINGS.buffer_size))
        ),
        "max_reconnect_attempts": int(
            env.get(
                "BINANCE_MAX_RECONNECT",
                str(BINANCE_CONFIG.SETTINGS.max_reconnect_attempts),
            )
        ),
    }

    return SolVolEnvironment(
        MODE=mode, LOG_LEVEL=log_level, binance_config=binance_config
    )


# Example usage
if __name__ == "__main__":
    config = get_sol_vol_environment()

    # Access via config dict
    print(f"Symbol: {config.binance_config['symbol']}")
    print(f"Buffer size: {config.binance_config['buffer_size']}")

    # Direct namespace access with type safety
    print(f"Default symbol: {BINANCE_CONFIG.STRINGS.symbol}")
    print(f"Default buffer: {BINANCE_CONFIG.SETTINGS.buffer_size}")

    # Type-specific enum features preserved
    print(f"All string configs: {list(BINANCE_CONFIG.STRINGS)}")
    print(f"All settings: {list(BINANCE_CONFIG.SETTINGS)}")
