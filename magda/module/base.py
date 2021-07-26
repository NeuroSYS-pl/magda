from __future__ import annotations

from abc import ABC
from typing import Optional


class BaseModule(ABC):
    def __init__(self, name: str, group: Optional[str] = None):
        self._name = name
        self._group = group

    @property
    def name(self) -> str:
        return self._name

    @property
    def group(self) -> Optional[str]:
        return self._group


class BaseModuleRuntime(BaseModule):
    def __init__(self, name: str, group: Optional[str]):
        super().__init__(name, group)
