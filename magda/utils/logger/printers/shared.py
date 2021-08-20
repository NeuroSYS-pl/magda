from colorama import Fore, Style

from ..parts import LoggerParts


def with_log_level_colors(text: str, level: LoggerParts.Level) -> str:
    style = Style.NORMAL

    if level == LoggerParts.Level.DEBUG:
        color = Fore.GREEN
    elif level == LoggerParts.Level.WARNING:
        color = Fore.YELLOW
    elif level == LoggerParts.Level.ERROR:
        color = Fore.RED
    elif level == LoggerParts.Level.CRITICAL:
        color = Fore.RED
        style = Style.BRIGHT
    else:
        color = Fore.WHITE
    return (
        style + color
        + text
        + Fore.RESET + Style.NORMAL
    )
