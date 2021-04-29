from __future__ import annotations

from abc import ABC
from logging import getLogger
from weakref import ReferenceType
from typing import Optional, Any, Type, TYPE_CHECKING


if TYPE_CHECKING:
    from magda.pipeline.base import BasePipeline
    from magda.utils.logger import MagdaLogger


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
    def __init__(
        self,
        name: str,
        group: Optional[str],
        logger: MagdaLogger,
        parent: ReferenceType[Type[BasePipeline]],
    ):
        super().__init__(name, group)
        self._logger = logger
        self._parent = parent

    def log(self, msg: str, *, request: Optional[Any] = None, event: bool = False):
        if not self._logger.enable or (not self._logger.log_events and event):
            return

        message = self._logger._prepare_message(
            msg=msg, module=self,
            pipeline=self._parent(),
            request=request, is_event=event,
        )

        if self._logger.use_print:
            print(message)
        else:
            getLogger('magda.runtime').info(message)
