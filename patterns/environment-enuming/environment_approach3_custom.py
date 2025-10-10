"""Environment configuration for sol-vol-exporter.
APPROACH 3: Custom Enum with Helper Methods - Flexible with utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from os import environ as env
from typing import Any, Dict, Type, TypeVar, Union

from caesari_logger.std_logger import get_logger


T = TypeVar('T')


class SolVolMode(StrEnum):
    prod = "prod"
    dev = "dev"
    staging = "staging"


class ConfigEnum(Enum):
    """Base enum with helper methods for configuration."""
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Convert enum to dictionary."""
        return {member.name: member.value for member in cls}
    
    @classmethod
    def get_typed(cls, name: str, type_: Type[T], default: T = None) -> T:
        """Get typed value from enum."""
        try:
            value = cls[name].value
            return type_(value)
        except (KeyError, ValueError, TypeError):
            return default
    
    @classmethod
    def from_env(cls, prefix: str = "") -> Dict[str, Any]:
        """Load configuration from environment variables."""
        result = {}
        for member in cls:
            env_key = f"{prefix}_{member.name.upper()}" if prefix else member.name.upper()
            env_value = env.get(env_key)
            if env_value is not None:
                # Try to preserve type
                if isinstance(member.value, int):
                    result[member.name] = int(env_value)
                elif isinstance(member.value, float):
                    result[member.name] = float(env_value)
                elif isinstance(member.value, bool):
                    result[member.name] = env_value.lower() in ('true', '1', 'yes')
                else:
                    result[member.name] = env_value
            else:
                result[member.name] = member.value
        return result


class BINANCE_CONFIG(ConfigEnum):
    """Binance configuration with type hints and utilities.
    
    Mixed-type enum with helper methods for flexible access.
    """
    # Type hints for documentation (not enforced)
    symbol: str = "SOLUSDT"
    interval: str = "1m"
    ws_url: str = "wss://stream.binance.com:9443/ws"
    buffer_size: int = 1440  # 24 hours of 1-minute candles
    max_reconnect_attempts: int = 10
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration values."""
        try:
            assert cls.buffer_size.value > 0, "Buffer size must be positive"
            assert cls.max_reconnect_attempts.value >= 0, "Reconnect attempts must be non-negative"
            assert cls.symbol.value.endswith("USDT"), "Symbol must be USDT pair"
            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    @classmethod
    def get_ws_endpoint(cls, stream_type: str = "kline") -> str:
        """Build WebSocket endpoint URL."""
        base_url = cls.ws_url.value
        symbol = cls.symbol.value.lower()
        interval = cls.interval.value
        return f"{base_url}/{symbol}@{stream_type}_{interval}"


@dataclass
class SolVolEnvironment:
    """Environment configuration for sol-vol-exporter."""
    
    MODE: SolVolMode
    LOG_LEVEL: str = "INFO"
    
    # Store config using helper method
    binance_config: dict = field(default_factory=lambda: BINANCE_CONFIG.from_env("BINANCE"))
    
    volatility_windows_minutes: list[int] = field(default_factory=lambda: [15, 30, 60])
    
    # Database configuration (optional - for future persistence)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sol_vol_exporter"
    db_user: str = "postgres"
    db_password: str = ""
    
    def validate(self) -> bool:
        """Validate entire environment configuration."""
        return BINANCE_CONFIG.validate()


def get_sol_vol_environment() -> SolVolEnvironment:
    """Get environment configuration with automatic env var loading."""
    mode = SolVolMode(env.get("MODE", "dev"))
    log_level = env.get("LOG_LEVEL", "DEBUG")
    
    environment = SolVolEnvironment(
        MODE=mode,
        LOG_LEVEL=log_level
    )
    
    # Validate configuration
    if not environment.validate():
        raise ValueError("Invalid environment configuration")
    
    return environment


# Example usage
if __name__ == "__main__":
    config = get_sol_vol_environment()
    
    # Access via config dict
    print(f"Symbol: {config.binance_config['symbol']}")
    print(f"Buffer size: {config.binance_config['buffer_size']}")
    
    # Use helper methods
    print(f"All config: {BINANCE_CONFIG.as_dict()}")
    print(f"WS Endpoint: {BINANCE_CONFIG.get_ws_endpoint()}")
    
    # Typed access
    buffer = BINANCE_CONFIG.get_typed('buffer_size', int, default=1000)
    print(f"Typed buffer: {buffer}")
    
    # Validation
    print(f"Config valid: {BINANCE_CONFIG.validate()}")
