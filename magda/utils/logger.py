from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from functools import partial
from logging import getLogger
from typing import Any, Callable, List, Optional, TYPE_CHECKING, Type, Union
from weakref import ReferenceType

from colorama import Fore, Style
from datetime import datetime


if TYPE_CHECKING:
    from magda.module.base import BaseModuleRuntime
    from magda.pipeline.base import BasePipeline


def get_default_format() -> List[MagdaLogger.Config.Part]:
    return [
        MagdaLogger.Config.Part.TIMESTAMP,
        MagdaLogger.Config.Part.PIPELINE,
        MagdaLogger.Config.Part.MODULE,
        MagdaLogger.Config.Part.GROUP,
        MagdaLogger.Config.Part.REQUEST,
        MagdaLogger.Config.Part.MESSAGE,
    ]


class MagdaLogger:
    @dataclass(frozen=True)
    class Config:
        class Part(Enum):
            TIMESTAMP = auto()
            PIPELINE = auto()
            MODULE = auto()
            GROUP = auto()
            REQUEST = auto()
            MESSAGE = auto()

        class Output(Enum):
            STDOUT = auto()
            LOGGING = auto()

        enable: bool = True
        log_events: bool = True
        output: Union[Output, Callable[[str], None]] = Output.STDOUT
        format: List[Part] = field(default_factory=get_default_format)

    @classmethod
    def of(
        cls: Type[MagdaLogger],
        config: Optional[MagdaLogger.Config],
        *args,
        **kwargs,
    ) -> MagdaLogger:
        return (
            cls(partial(MagdaLogger._prepare_message, config=config, *args, **kwargs))
            if config is not None else cls()
        )

    def __init__(self, callback: Optional[Callable[[str, Any], None]] = None) -> None:
        self._callback = callback

    def info(self, msg: str) -> None:
        if self._callback:
            self._callback(msg=msg, is_event=False)

    def event(self, msg: str) -> None:
        if self._callback:
            self._callback(msg=msg, is_event=True)

    def chain(self, *args, **kwargs) -> MagdaLogger:
        return (
            MagdaLogger(partial(self._callback, *args, **kwargs))
            if self._callback is not None else self
        )

    @staticmethod
    def _prepare_message(
        msg: str,
        config: MagdaLogger.Config,
        pipeline: Optional[ReferenceType[BasePipeline.Runtime]] = None,
        module: Optional[ReferenceType[BaseModuleRuntime]] = None,
        request: Optional[Any] = None,
        is_event: bool = False,
    ) -> str:
        if not config.enable or (not config.log_events and is_event):
            return

        pipeline_ref = pipeline() if pipeline is not None else None
        module_ref = module() if module is not None else None

        parts = {
            MagdaLogger.Config.Part.TIMESTAMP: (
                Fore.YELLOW
                + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]"
                + Fore.RESET
            ),
            MagdaLogger.Config.Part.PIPELINE: (
                Fore.MAGENTA + f'{pipeline_ref.__class__.__name__} '
                + Style.BRIGHT + f'({pipeline_ref.name})'
                + Fore.RESET + Style.NORMAL
            ) if pipeline_ref is not None else None,
            MagdaLogger.Config.Part.MODULE: (
                Fore.BLUE + f'{module_ref.__class__.__name__} '
                + Style.BRIGHT + f'({module_ref.name})'
                + Fore.RESET + Style.NORMAL
            ) if module_ref is not None else None,
            MagdaLogger.Config.Part.GROUP: (
                Fore.CYAN + Style.BRIGHT
                + f'<{module_ref.group}>'
                + Fore.RESET + Style.NORMAL
            ) if module_ref is not None and module_ref.group is not None else None,
            MagdaLogger.Config.Part.REQUEST: (
                Fore.MAGENTA + f'[{str(request)}]' + Fore.RESET
            ) if request is not None else None,
            MagdaLogger.Config.Part.MESSAGE: (
                (Style.BRIGHT + Fore.GREEN + f'[{msg}]' + Fore.RESET + Style.NORMAL)
                if is_event else msg
            ),
        }

        message = ' '.join([
            parts[key]
            for key in config.format
            if parts[key] is not None
        ])

        if config.output == MagdaLogger.Config.Output.STDOUT:
            print(message)
        elif config.output == MagdaLogger.Config.Output.LOGGING:
            getLogger('magda.runtime').info(message)
        elif callable(config.output):
            config.output(message)
