from __future__ import annotations

from colorama import Fore
from datetime import datetime

from magda.utils.logger.printers.base import BasePrinter


class TimestampPrinter(BasePrinter):
    def flush(self, colors: bool, **kwargs) -> str:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        text = f'[{now[:-3]}]'

        return (
            Fore.YELLOW + text + Fore.RESET
            if colors else text
        )
