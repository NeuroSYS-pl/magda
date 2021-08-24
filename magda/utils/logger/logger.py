from __future__ import annotations
from functools import partial
from logging import getLogger
from typing import Any, Callable, Optional, Type

from magda.utils.logger.config import LoggerConfig
from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers import *


class MagdaLogger:
    Config = LoggerConfig
    Parts = LoggerParts

    _parts_mapping = {
        LoggerConfig.Part.LEVEL: LevelPrinter(),
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

    def log_message(self, msg: str, level: LoggerConfig.Level) -> None:
        if self._callback:
            level = LoggerParts.Level(level)
            self._callback(msg=msg, is_event=False, level=level)

    def info(self, msg: str) -> None:
        self.log_message(msg=msg, level=LoggerConfig.Level.INFO)

    def error(self, msg: str) -> None:
        self.log_message(msg=msg, level=LoggerConfig.Level.ERROR)

    def debug(self, msg: str) -> None:
        self.log_message(msg=msg, level=LoggerConfig.Level.DEBUG)

    def critical(self, msg: str) -> None:
        self.log_message(msg=msg, level=LoggerConfig.Level.CRITICAL)

    def warn(self, msg: str) -> None:
        self.log_message(msg=msg, level=LoggerConfig.Level.WARNING)

    def event(self, msg: str) -> None:
        level = LoggerParts.Level(LoggerConfig.Level.INFO)
        if self._callback:
            self._callback(msg=msg, is_event=True, level=level)

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

        level = kwargs.get('level', LoggerParts.Level(LoggerConfig.Level.INFO))

        if not config.enable or (not config.log_events and is_event):
            return

        message_format = config.format

        hidden_parts = []
        if config.output == MagdaLogger.Config.Output.LOGGING:
            hidden_parts.append(LoggerConfig.Part.LEVEL)

        parts = [
            MagdaLogger._parts_mapping[key].flush(
                colors=config.colors,
                **kwargs,
            )
            for key in message_format
            if key not in hidden_parts
        ]

        message = ' '.join([p for p in parts if p is not None])

        if config.output == MagdaLogger.Config.Output.STDOUT:
            print(message)
        elif config.output == MagdaLogger.Config.Output.LOGGING:
            if level.value == LoggerConfig.Level.DEBUG:
                getLogger('magda.runtime').debug(message)
            elif level.value == LoggerConfig.Level.ERROR:
                getLogger('magda.runtime').error(message)
            elif level.value == LoggerConfig.Level.WARNING:
                getLogger('magda.runtime').warn(message)
            elif level.value == LoggerConfig.Level.CRITICAL:
                getLogger('magda.runtime').critical(message)
            else:
                getLogger('magda.runtime').info(message)
        elif callable(config.output):
            config.output(message)
