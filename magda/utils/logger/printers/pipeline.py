from __future__ import annotations
from typing import Optional

from colorama import Fore, Style

from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers.base import BasePrinter


class PipelinePrinter(BasePrinter):
    def _with_colors(self, kind: str, name: str) -> str:
        return (
            Fore.MAGENTA + f'{kind} '
            + Style.BRIGHT + f'({name})'
            + Fore.RESET + Style.NORMAL
        )

    def flush(
        self,
        colors: bool,
        pipeline: Optional[LoggerParts.Pipeline] = None,
        **kwargs,
    ) -> Optional[str]:
        if pipeline is not None:
            return (
                self._with_colors(pipeline.kind, pipeline.name)
                if colors else f'{pipeline.kind} ({pipeline.name})'
            )
        return None
