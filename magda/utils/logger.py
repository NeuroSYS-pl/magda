from __future__ import annotations

from enum import Enum, auto
from typing import Any, List, Optional, TYPE_CHECKING, Type

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
        pipeline: Optional[Type[BasePipeline.Runtime]] = None,
        module: Optional[Type[BaseModuleRuntime]] = None,
        request: Optional[Any] = None,
        is_event: bool = False,
    ) -> str:
        parts = {
            MagdaLogger.RecordParts.TIMESTAMP: (
                Fore.YELLOW
                + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]"
                + Fore.RESET
            ),
            MagdaLogger.RecordParts.PIPELINE: (
                Fore.MAGENTA + f'{pipeline.__class__.__name__} '
                + Style.BRIGHT + f'({pipeline.name})'
                + Fore.RESET + Style.NORMAL
            ) if pipeline is not None else None,
            MagdaLogger.RecordParts.MODULE: (
                Fore.BLUE + f'{module.__class__.__name__} '
                + Style.BRIGHT + f'({module.name})'
                + Fore.RESET + Style.NORMAL
            ) if module is not None else None,
            MagdaLogger.RecordParts.GROUP: (
                Fore.CYAN + Style.BRIGHT
                + f'<{module.group}>'
                + Fore.RESET + Style.NORMAL
            ) if module is not None and module.group is not None else None,
            MagdaLogger.RecordParts.REQUEST: (
                Style.BRIGHT + Fore.MAGENTA
                + f'[{str(request)}]'
                + Fore.RESET + Style.NORMAL
            ) if request is not None else None,
            MagdaLogger.RecordParts.MESSAGE: (
                (Style.BRIGHT + Fore.GREEN + f'[{msg}]' + Fore.RESET + Style.NORMAL)
                if is_event else msg
            ),
        }

        return ' '.join([
            parts[key]
            for key in self.format
            if parts[key] is not None
        ])
