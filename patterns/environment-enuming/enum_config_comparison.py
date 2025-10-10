"""Quick comparison of the three enum configuration approaches."""

# APPROACH 1: Mixed-Type Enum
# Simple, but loses type-specific features
from enum import Enum

class Config_v1(Enum):
    symbol = "SOLUSDT"      # string
    buffer_size = 1440      # integer
    
# Usage:
# Config_v1.symbol.value  # "SOLUSDT"
# Config_v1.buffer_size.value  # 1440


# APPROACH 2: Namespace Pattern  
# Type-safe with logical grouping
from enum import StrEnum, IntEnum

class Config_v2:
    class STRINGS(StrEnum):
        symbol = "SOLUSDT"
    
    class SETTINGS(IntEnum):
        buffer_size = 1440

# Usage:
# Config_v2.STRINGS.symbol  # "SOLUSDT" 
# Config_v2.SETTINGS.buffer_size  # 1440


# APPROACH 3: Custom Enum
# Flexible with utility methods
class Config_v3(Enum):
    symbol: str = "SOLUSDT"
    buffer_size: int = 1440
    
    @classmethod
    def as_dict(cls):
        return {m.name: m.value for m in cls}

# Usage:
# Config_v3.symbol.value  # "SOLUSDT"
# Config_v3.as_dict()  # {'symbol': 'SOLUSDT', 'buffer_size': 1440}


"""
Quick Decision Guide:
- Simple project, few configs → Approach 1
- Type safety important → Approach 2 ✓
- Need utility methods → Approach 3
"""
