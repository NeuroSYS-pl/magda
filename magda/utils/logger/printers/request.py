from __future__ import annotations
from typing import Optional

from colorama import Fore

from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers.base import BasePrinter


class RequestPrinter(BasePrinter):
    def _with_colors(self, text: str) -> str:
        return Fore.MAGENTA + text + Fore.RESET

    def flush(
        self,
        colors: bool,
        request: Optional[LoggerParts.Request] = None,
        **kwargs,
    ) -> Optional[str]:
        if request is not None:
            text = f'[{request.text}]'
            return self._with_colors(text) if colors else text
        return None
