from dataclasses import dataclass
from enum import StrEnum
from os import environ as env


class Mode(StrEnum):
    prod = "prod"
    dev = "dev"
    stagin = "staging"


@dataclass
class Environment:
    MODE: Mode


def get_environment() -> Environment:
    mode = env.get("MODE", "dev")

    return Environment(MODE=Mode(mode))
