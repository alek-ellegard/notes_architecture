"""Environment configuration for sol-vol-exporter.
APPROACH 1: Mixed-type Enum - Simple but loses type-specific features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from os import environ as env

from caesari_logger.std_logger import get_logger


class SolVolMode(StrEnum):
    prod = "prod"
    dev = "dev"
    staging = "staging"


class BINANCE_CONFIG(Enum):
    """Mixed-type enum for Binance configuration.
    
    Simple approach: all config values in one enum regardless of type.
    """
    # String values
    symbol = "SOLUSDT"
    interval = "1m"
    ws_url = "wss://stream.binance.com:9443/ws"
    # Integer values
    buffer_size = 1440  # 24 hours of 1-minute candles
    max_reconnect_attempts = 10


@dataclass
class SolVolEnvironment:
    """Environment configuration for sol-vol-exporter."""
    
    MODE: SolVolMode
    LOG_LEVEL: str = "INFO"
    
    # Store config as dict from enum values
    binance_config: dict = field(default_factory=lambda: {
        "symbol": BINANCE_CONFIG.symbol.value,
        "interval": BINANCE_CONFIG.interval.value,
        "ws_url": BINANCE_CONFIG.ws_url.value,
        "buffer_size": BINANCE_CONFIG.buffer_size.value,
        "max_reconnect_attempts": BINANCE_CONFIG.max_reconnect_attempts.value,
    })
    
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
    
    # Override from environment variables
    binance_config = {
        "symbol": env.get("BINANCE_SYMBOL", BINANCE_CONFIG.symbol.value),
        "interval": env.get("BINANCE_INTERVAL", BINANCE_CONFIG.interval.value),
        "ws_url": env.get("BINANCE_WS_URL", BINANCE_CONFIG.ws_url.value),
        "buffer_size": int(env.get("BINANCE_BUFFER_SIZE", str(BINANCE_CONFIG.buffer_size.value))),
        "max_reconnect_attempts": int(env.get("BINANCE_MAX_RECONNECT", str(BINANCE_CONFIG.max_reconnect_attempts.value)))
    }
    
    return SolVolEnvironment(
        MODE=mode,
        LOG_LEVEL=log_level,
        binance_config=binance_config
    )


# Example usage
if __name__ == "__main__":
    config = get_sol_vol_environment()
    
    # Access via config dict
    print(f"Symbol: {config.binance_config['symbol']}")
    print(f"Buffer size: {config.binance_config['buffer_size']}")
    
    # Direct enum access still possible
    print(f"Default symbol: {BINANCE_CONFIG.symbol.value}")
