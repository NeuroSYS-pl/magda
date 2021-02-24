from dataclasses import dataclass, field
from time import time


@dataclass(frozen=True)
class Request:
    value: str


@dataclass(frozen=True)
class Context:
    prefix: str
    timer: float = field(default_factory=time)
