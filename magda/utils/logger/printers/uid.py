from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers.base import BasePrinter


class UidPrinter(BasePrinter):
    def _with_colors(self, kind: str, name: str, group: str, replica: str) -> str:
        return (
            Fore.BLUE + f'{kind} ' + Style.BRIGHT
            + f'({name}' + Fore.CYAN + group + Style.NORMAL + replica
            + Fore.BLUE + Style.BRIGHT + ')'
            + Fore.RESET + Style.NORMAL
        )

    def flush(
        self,
        colors: bool,
        module: Optional[LoggerParts.Module] = None,
        group: Optional[LoggerParts.Group] = None,
        **kwargs,
    ) -> Optional[str]:
        if module is not None:
            group_str = f':{group.name}' if group is not None else ''
            replica_str = (
                f':{group.replica}'
                if (group is not None and group.replica is not None)
                else ''
            )

            return (
                self._with_colors(module.kind, module.name, group_str, replica_str)
                if colors else f'{module.kind} ({module.name}{group_str}{replica_str})'
            )

        return None
