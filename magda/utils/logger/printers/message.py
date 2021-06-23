from __future__ import annotations
from typing import Optional
from colorama import Fore, Style
from .base import BasePrinter


class MessagePrinter(BasePrinter):
    def flush(
        self,
        msg: str = None,
        is_event: bool = False,
        **kwargs,
    ) -> Optional[str]:
        return (
            Style.BRIGHT + Fore.GREEN + f'[{msg}]' + Fore.RESET + Style.NORMAL
            if is_event else msg
        )
