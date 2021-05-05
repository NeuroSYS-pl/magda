from __future__ import annotations

from enum import Enum, auto
from functools import partial
from logging import getLogger
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Type
from weakref import ReferenceType

from colorama import Fore, Style
from datetime import datetime


if TYPE_CHECKING:
    from magda.module.base import BaseModuleRuntime
    from magda.pipeline.base import BasePipeline


class MagdaLogger:
    class RecordParts(Enum):
        TIMESTAMP = auto()
        PIPELINE = auto()
        MODULE = auto()
        GROUP = auto()
        REQUEST = auto()
        MESSAGE = auto()

    class Facade:
        def __init__(self, callback: Optional[Callable[[str, Any], None]]) -> None:
            self._callback = callback

        def info(self, msg: str) -> None:
            if self._callback:
                self._callback(msg=msg, is_event=False)

        def event(self, msg: str) -> None:
            if self._callback:
                self._callback(msg=msg, is_event=True)

        @classmethod
        def of(cls, logger: MagdaLogger, *args, **kwargs) -> MagdaLogger.Facade:
            return cls(partial(logger._prepare_message, *args, **kwargs))

        def chain(self, *args, **kwargs) -> MagdaLogger.Facade:
            return (
                MagdaLogger.Facade(partial(self._callback, *args, **kwargs))
                if self._callback is not None
                else MagdaLogger.Facade()
            )

    @classmethod
    def get_default(cls: Type[MagdaLogger]) -> MagdaLogger:
        return cls(enable=False)

    def __init__(
        self,
        *,
        enable: bool = True,
        use_print: bool = False,
        log_events: bool = True,
        format: Optional[List[RecordParts]] = None,
    ) -> None:
        self.enable = enable
        self.use_print = use_print
        self.log_events = log_events
        self.log_message = enable
        self.format = format if format is not None else [
            self.RecordParts.TIMESTAMP,
            self.RecordParts.PIPELINE,
            self.RecordParts.MODULE,
            self.RecordParts.GROUP,
            self.RecordParts.REQUEST,
            self.RecordParts.MESSAGE,
        ]

    def _prepare_message(
        self,
        *,
        msg: str,
        pipeline: Optional[ReferenceType[BasePipeline.Runtime]] = None,
        module: Optional[ReferenceType[BaseModuleRuntime]] = None,
        request: Optional[Any] = None,
        is_event: bool = False,
    ) -> str:
        if not self.enable or (not self.log_events and is_event):
            return

        pipeline_ref = pipeline() if pipeline is not None else None
        module_ref = module() if module is not None else None

        parts = {
            MagdaLogger.RecordParts.TIMESTAMP: (
                Fore.YELLOW
                + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]"
                + Fore.RESET
            ),
            MagdaLogger.RecordParts.PIPELINE: (
                Fore.MAGENTA + f'{pipeline_ref.__class__.__name__} '
                + Style.BRIGHT + f'({pipeline_ref.name})'
                + Fore.RESET + Style.NORMAL
            ) if pipeline_ref is not None else None,
            MagdaLogger.RecordParts.MODULE: (
                Fore.BLUE + f'{module_ref.__class__.__name__} '
                + Style.BRIGHT + f'({module_ref.name})'
                + Fore.RESET + Style.NORMAL
            ) if module_ref is not None else None,
            MagdaLogger.RecordParts.GROUP: (
                Fore.CYAN + Style.BRIGHT
                + f'<{module_ref.group}>'
                + Fore.RESET + Style.NORMAL
            ) if module_ref is not None and module_ref.group is not None else None,
            MagdaLogger.RecordParts.REQUEST: (
                Fore.MAGENTA + f'[{str(request)}]' + Fore.RESET
            ) if request is not None else None,
            MagdaLogger.RecordParts.MESSAGE: (
                (Style.BRIGHT + Fore.GREEN + f'[{msg}]' + Fore.RESET + Style.NORMAL)
                if is_event else msg
            ),
        }

        message = ' '.join([
            parts[key]
            for key in self.format
            if parts[key] is not None
        ])

        if self.use_print:
            print(message)
        else:
            getLogger('magda.runtime').info(message)
