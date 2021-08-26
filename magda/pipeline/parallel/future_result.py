from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
from typing import List

from magda.module.module import Module


@dataclass(frozen=True)
class FutureResult:
    job: UUID
    group: str
    result: Module.ResultSet
