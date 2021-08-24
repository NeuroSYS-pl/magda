from __future__ import annotations
from typing import Optional
from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers.base import BasePrinter
from magda.utils.logger.printers.shared import with_log_level_colors


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
