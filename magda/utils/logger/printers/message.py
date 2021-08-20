from __future__ import annotations
from typing import Optional
from colorama import Fore, Style

from ..parts import LoggerParts
from .base import BasePrinter
from .shared import with_log_level_colors


class MessagePrinter(BasePrinter):
    EVENT_START_MARKER = '['
    EVENT_END_MARKER = ']'

    def _with_event_colors(self, text: str) -> str:
        return (
            Style.BRIGHT + Fore.GREEN
            + text
            + Fore.RESET + Style.NORMAL
        )

    def flush(
        self,
        colors: bool,
        msg: str = None,
        is_event: bool = False,
        level: LoggerParts.Level = LoggerParts.Level.INFO,
        **kwargs,
    ) -> Optional[str]:
        if is_event:
            text = f'{self.EVENT_START_MARKER}{msg}{self.EVENT_END_MARKER}'
            return self._with_event_colors(text) if colors else text
        return with_log_level_colors(msg, level) if colors else msg
