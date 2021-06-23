from __future__ import annotations

from colorama import Fore
from datetime import datetime

from .base import BasePrinter


class TimestampPrinter(BasePrinter):
    def flush(self, **kwargs) -> str:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return Fore.YELLOW + f'[{now[:-3]}]' + Fore.RESET
