from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, List, Union


def get_default_format() -> List[LoggerConfig.Part]:
    return [
        LoggerConfig.Part.LEVEL,
        LoggerConfig.Part.TIMESTAMP,
        LoggerConfig.Part.PIPELINE,
        LoggerConfig.Part.UID,
        LoggerConfig.Part.REQUEST,
        LoggerConfig.Part.MESSAGE,
    ]


@dataclass(frozen=True)
class LoggerConfig:
    class Part(Enum):
        TIMESTAMP = auto()
        PIPELINE = auto()
        UID = auto()
        MODULE = auto()
        GROUP = auto()
        REPLICA = auto()
        REQUEST = auto()
        MESSAGE = auto()
        LEVEL = auto()

    class Output(Enum):
        STDOUT = auto()
        LOGGING = auto()

    class Level(Enum):
        INFO = auto()
        WARNING = auto()
        ERROR = auto()
        DEBUG = auto()
        CRITICAL = auto()

    enable: bool = True
    log_events: bool = True
    colors: bool = True
    output: Union[Output, Callable[[str], None]] = Output.STDOUT
    format: List[Part] = field(default_factory=get_default_format)
