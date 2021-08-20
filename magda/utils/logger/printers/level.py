from __future__ import annotations
from typing import Optional
from colorama import Fore, Style

from ..parts import LoggerParts
from .base import BasePrinter
from .shared import with_log_level_colors


class LevelPrinter(BasePrinter):
    LEVEL_START_MARKER = '['
    LEVEL_END_MARKER = ']'

    def flush(
        self,
        colors: bool,
        level: LoggerParts.Level = LoggerParts.Level.INFO,
        **kwargs,
    ) -> Optional[str]:
        text = f'{self.LEVEL_START_MARKER}{level.name}{self.LEVEL_END_MARKER}'
        return with_log_level_colors(text, level) if colors else text
