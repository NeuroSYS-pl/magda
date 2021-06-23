from __future__ import annotations
from functools import partial
from logging import getLogger
from typing import Any, Callable, Optional, Type

from .config import LoggerConfig
from .parts import LoggerParts
from .printers import *


class MagdaLogger:
    Config = LoggerConfig
    Parts = LoggerParts

    _parts_mapping = {
        LoggerConfig.Part.TIMESTAMP: TimestampPrinter(),
        LoggerConfig.Part.PIPELINE: PipelinePrinter(),
        LoggerConfig.Part.MODULE: ModulePrinter(),
        LoggerConfig.Part.GROUP: GroupPrinter(),
        LoggerConfig.Part.REPLICA: ReplicaPrinter(),
        LoggerConfig.Part.UID: UidPrinter(),
        LoggerConfig.Part.REQUEST: RequestPrinter(),
        LoggerConfig.Part.MESSAGE: MessagePrinter(),
    }

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
        config: MagdaLogger.Config,
        **kwargs,
    ) -> None:
        is_event = kwargs.get('is_event', False)

        if not config.enable or (not config.log_events and is_event):
            return

        parts = [
            MagdaLogger._parts_mapping[key].flush(
                colors=config.colors,
                **kwargs,
            )
            for key in config.format
        ]
        message = ' '.join([p for p in parts if p is not None])

        if config.output == MagdaLogger.Config.Output.STDOUT:
            print(message)
        elif config.output == MagdaLogger.Config.Output.LOGGING:
            getLogger('magda.runtime').info(message)
        elif callable(config.output):
            config.output(message)
