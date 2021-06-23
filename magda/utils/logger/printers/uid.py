from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from .base import BasePrinter


class UidPrinter(BasePrinter):
    def flush(
        self,
        module: Optional[LoggerParts.Module] = None,
        group: Optional[LoggerParts.Group] = None,
        **kwargs,
    ) -> Optional[str]:
        if module is not None:
            group_str = (
                Fore.CYAN + Style.BRIGHT + f':{group.name}' + Style.NORMAL
                if group is not None else ''
            )
            replica_str = (
                f':{group.replica}'
                if (group is not None and group.replica is not None)
                else ''
            )

            return (
                Fore.BLUE + f'{module.kind} ' + Style.BRIGHT + '('
                + f'{module.name}' + group_str + replica_str
                + Fore.BLUE + Style.BRIGHT + ')'
                + Fore.RESET + Style.NORMAL
            )
        return None
