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
        level: Optional[LoggerParts.Level] = None,
        **kwargs,
    ) -> Optional[str]:
        if level:
            text = f'{self.LEVEL_START_MARKER}{level.value.name}{self.LEVEL_END_MARKER}'
            return with_log_level_colors(text, level.value) if colors else text
        else:
            return None
