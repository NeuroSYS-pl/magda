from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from magda.utils.logger.parts import LoggerParts


class BasePrinter(ABC):
    @abstractmethod
    def flush(
        self,
        colors: bool,
        *,
        msg: str = None,
        pipeline: Optional[LoggerParts.Pipeline] = None,
        module: Optional[LoggerParts.Module] = None,
        group: Optional[LoggerParts.Group] = None,
        request: Optional[LoggerParts.Request] = None,
        is_event: bool = False,
        level: Optional[LoggerParts.Level] = None,
        **kwargs,
    ) -> Optional[str]:
        raise NotImplementedError()
