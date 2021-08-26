import re
import pytest

from colorama import Fore, Style

from magda.utils.logger.printers import LevelPrinter
from magda.utils.logger.config import LoggerConfig
from magda.utils.logger.parts import LoggerParts


class TestLevelPrinter:
    COLOR_REGEXP = r'\x1b'

    @pytest.mark.parametrize(
        "level,expected_color",
        [
            (LoggerConfig.Level.INFO, Fore.WHITE),
            (LoggerConfig.Level.WARNING, Fore.YELLOW),
            (LoggerConfig.Level.ERROR, Fore.RED),
            (LoggerConfig.Level.DEBUG, Fore.GREEN),
            (LoggerConfig.Level.CRITICAL, Fore.RED)
        ]
    )
    def test_should_print_level_correctly(self, level, expected_color):
        printer = LevelPrinter()
        level = LoggerParts.Level(level)
        output = printer.flush(colors=True, level=level)
        level_msg = (f'{LevelPrinter.LEVEL_START_MARKER}'
                     f'{level.value.name}{LevelPrinter.LEVEL_END_MARKER}')
        assert level_msg in output
        assert expected_color in output

    @pytest.mark.parametrize(
        "level",
        [
            LoggerConfig.Level.WARNING,
            LoggerConfig.Level.ERROR,
            LoggerConfig.Level.DEBUG,
            LoggerConfig.Level.CRITICAL
        ]
    )
    def test_should_log_level_without_color_if_set(self, level):
        printer = LevelPrinter()
        level = LoggerParts.Level(level)
        output = printer.flush(colors=False, level=level)
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_critical_level_in_color_and_bold(self):
        printer = LevelPrinter()
        message = f'{LevelPrinter.LEVEL_START_MARKER}CRITICAL{LevelPrinter.LEVEL_END_MARKER}'
        message_formatted = Style.BRIGHT + Fore.RED + message + Fore.RESET
        output = printer.flush(colors=True, level=LoggerParts.Level(LoggerConfig.Level.CRITICAL))
        assert output.find(message_formatted) != -1

    def test_should_ignore_extra_arguments(self):
        printer = LevelPrinter()
        output_base = printer.flush(colors=False)
        output_extra = printer.flush(colors=False, extra='some extra args')

        assert output_base == output_extra
