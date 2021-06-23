from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from .base import BasePrinter


class PipelinePrinter(BasePrinter):
    def flush(
        self,
        pipeline: Optional[LoggerParts.Pipeline] = None,
        **kwargs,
    ) -> Optional[str]:
        if pipeline is not None:
            return (
                Fore.MAGENTA + f'{pipeline.kind} '
                + Style.BRIGHT + f'({pipeline.name})'
                + Fore.RESET + Style.NORMAL
            )
        return None
