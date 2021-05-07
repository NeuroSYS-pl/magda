from __future__ import annotations
from dataclasses import dataclass


class LoggerParts:
    @dataclass(frozen=True)
    class Module:
        name: str
        kind: str

    @dataclass(frozen=True)
    class Group:
        name: str

    @dataclass(frozen=True)
    class Pipeline:
        name: str
        kind: str

    @dataclass(frozen=True)
    class Request:
        text: str
