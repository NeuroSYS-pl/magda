from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from .base import BasePrinter


class GroupPrinter(BasePrinter):
    def flush(
        self,
        group: Optional[LoggerParts.Group] = None,
        **kwargs,
    ) -> Optional[str]:
        if group is not None:
            return (
                Fore.CYAN + Style.BRIGHT
                + f'({group.name})'
                + Fore.RESET + Style.NORMAL
            )
        return None
