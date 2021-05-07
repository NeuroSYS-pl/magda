from __future__ import annotations
from functools import partial
from logging import getLogger
from typing import Any, Callable, Optional, Type

from colorama import Fore, Style
from datetime import datetime

from magda.utils.logger.config import LoggerConfig
from magda.utils.logger.parts import LoggerParts


class MagdaLogger:
    Config = LoggerConfig
    Parts = LoggerParts

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
        *,
        pipeline: Optional[MagdaLogger.Parts.Pipeline] = None,
        module: Optional[MagdaLogger.Parts.Module] = None,
        group: Optional[MagdaLogger.Parts.Group] = None,
        request: Optional[MagdaLogger.Parts.Request] = None,
        is_event: bool = False,
    ) -> str:
        if not config.enable or (not config.log_events and is_event):
            return

        parts = {
            MagdaLogger.Config.Part.TIMESTAMP: (
                Fore.YELLOW
                + f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}]"
                + Fore.RESET
            ),
            MagdaLogger.Config.Part.PIPELINE: (
                Fore.MAGENTA + f'{pipeline.kind} '
                + Style.BRIGHT + f'({pipeline.name})'
                + Fore.RESET + Style.NORMAL
            ) if pipeline is not None else None,
            MagdaLogger.Config.Part.MODULE: (
                Fore.BLUE + f'{module.kind} '
                + Style.BRIGHT + f'({module.name})'
                + Fore.RESET + Style.NORMAL
            ) if module is not None else None,
            MagdaLogger.Config.Part.GROUP: (
                Fore.CYAN + Style.BRIGHT
                + f'<{group.name}>'
                + Fore.RESET + Style.NORMAL
            ) if group is not None else None,
            MagdaLogger.Config.Part.REQUEST: (
                Fore.MAGENTA + f'[{request.text}]' + Fore.RESET
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
