from typing import Optional
from colorama import Fore, Style

from magda.utils.logger.config import LoggerConfig

_default = (Fore.WHITE, Style.NORMAL)
_mapping = {
  LoggerConfig.Level.DEBUG: (Fore.GREEN, Style.NORMAL),
  LoggerConfig.Level.WARNING: (Fore.YELLOW, Style.NORMAL),
  LoggerConfig.Level.ERROR: (Fore.RED, Style.NORMAL),
  LoggerConfig.Level.CRITICAL: (Fore.RED, Style.BRIGHT),
}


def with_log_level_colors(text: str, level: Optional[LoggerConfig.Level]) -> str:
    color, style = _mapping[level] if level in _mapping else _default
    return (
        style + color
        + text
        + Fore.RESET + Style.NORMAL
    )
