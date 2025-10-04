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
    ZMQ_HOST: str = "127.0.0.1"
    ZMQ_PORT: int = 5555
    ZMQ_ADDRESS: str = f"tcp://{ZMQ_HOST}:{ZMQ_PORT}"


def get_environment() -> Environment:
    mode = env.get("MODE", "dev")
    zmq_host = env.get("ZMQ_HOST", "127.0.0.1")
    zmq_port = int(env.get("ZMQ_PORT", "5555"))

    return Environment(MODE=Mode(mode), ZMQ_HOST=zmq_host, ZMQ_PORT=zmq_port)
