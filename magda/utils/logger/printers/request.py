from __future__ import annotations
from typing import Optional

from colorama import Fore

from magda.utils.logger.parts import LoggerParts
from .base import BasePrinter


class RequestPrinter(BasePrinter):
    def flush(
        self,
        request: Optional[LoggerParts.Request] = None,
        **kwargs,
    ) -> Optional[str]:
        if request is not None:
            return Fore.MAGENTA + f'[{request.text}]' + Fore.RESET
        return None
