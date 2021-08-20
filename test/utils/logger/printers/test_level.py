import re
import pytest

from colorama import Fore, Style

from magda.utils.logger.printers import LevelPrinter
from magda.utils.logger.parts import LoggerParts


class TestLevelPrinter:
    COLOR_REGEXP = r'\x1b'

    @pytest.mark.parametrize(
        "level,expected_color",
        [
            (LoggerParts.Level.INFO, Fore.WHITE),
            (LoggerParts.Level.WARNING, Fore.YELLOW),
            (LoggerParts.Level.ERROR, Fore.RED),
            (LoggerParts.Level.DEBUG, Fore.GREEN),
            (LoggerParts.Level.CRITICAL, Fore.RED)
        ]
    )
    def test_should_print_correctly_any_level(self, level, expected_color):
        printer = LevelPrinter()
        output = printer.flush(colors=True, level=level)
        level_msg = f'{LevelPrinter.LEVEL_START_MARKER}{level.name}{LevelPrinter.LEVEL_END_MARKER}'
        assert level_msg in output
        assert expected_color in output

    @pytest.mark.parametrize(
        "level",
        [
            LoggerParts.Level.WARNING,
            LoggerParts.Level.ERROR,
            LoggerParts.Level.DEBUG,
            LoggerParts.Level.CRITICAL
        ]
    )
    def test_should_log_any_level_without_color_if_set(self, level):
        printer = LevelPrinter()
        output = printer.flush(colors=False, level=level)
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_critical_level_in_color_and_bold(self):
        printer = LevelPrinter()
        message = f'{LevelPrinter.LEVEL_START_MARKER}CRITICAL{LevelPrinter.LEVEL_END_MARKER}'
        message_formatted = Style.BRIGHT + Fore.RED + message + Fore.RESET
        output = printer.flush(colors=True, level=LoggerParts.Level.CRITICAL)
        assert output.find(message_formatted) != -1

    def test_should_ignore_extra_arguments(self):
        printer = LevelPrinter()
        output_base = printer.flush(colors=False)
        output_extra = printer.flush(colors=False, extra='some extra args')

        assert output_base == output_extra
