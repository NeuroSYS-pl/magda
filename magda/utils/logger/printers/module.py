from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers.base import BasePrinter


class ModulePrinter(BasePrinter):
    def _with_colors(self, kind: str, name: str) -> str:
        return (
            Fore.BLUE + f'{kind} '
            + Style.BRIGHT + f'({name})'
            + Fore.RESET + Style.NORMAL
        )

    def flush(
        self,
        colors: bool,
        module: Optional[LoggerParts.Module] = None,
        **kwargs,
    ) -> Optional[str]:
        if module is not None:
            return (
                self._with_colors(module.kind, module.name)
                if colors else f'{module.kind} ({module.name})'
            )
        return None
