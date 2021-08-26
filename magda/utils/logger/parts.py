from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from magda.utils.logger.config import LoggerConfig


class LoggerParts:
    @dataclass(frozen=True)
    class Module:
        name: str
        kind: str

    @dataclass(frozen=True)
    class Group:
        name: str
        replica: Optional[int] = None

    @dataclass(frozen=True)
    class Pipeline:
        name: str
        kind: str

    @dataclass(frozen=True)
    class Request:
        text: str

    @dataclass(frozen=True)
    class Level:
        value: LoggerConfig.Level
