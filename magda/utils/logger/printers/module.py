from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from .base import BasePrinter


class ModulePrinter(BasePrinter):
    def flush(
        self,
        module: Optional[LoggerParts.Module] = None,
        **kwargs,
    ) -> Optional[str]:
        if module is not None:
            return (
                Fore.BLUE + f'{module.kind} '
                + Style.BRIGHT + f'({module.name})'
                + Fore.RESET + Style.NORMAL
            )
        return None
