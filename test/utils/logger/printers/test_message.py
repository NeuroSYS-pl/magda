import re
import pytest

from colorama import Fore, Style

from magda.utils.logger.printers import *
from magda.utils.logger.config import LoggerConfig
from magda.utils.logger.parts import LoggerParts


class TestMessagePrinter:
    COLOR_REGEXP = r'\x1b'

    def test_should_print_standard_message(self):
        printer = MessagePrinter()
        message = 'Hello World!'
        output = printer.flush(colors=False, msg=message, is_event=False)
        assert output.find(message) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_accept_empty_message(self):
        printer = MessagePrinter()
        message = ''
        output = printer.flush(colors=False, msg=message, is_event=False)
        assert output == ''
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_standard_message_with_colors(self):
        printer = MessagePrinter()
        message = Fore.RED + 'Hello World!' + Fore.RESET
        output = printer.flush(colors=False, msg=message, is_event=False)
        assert output.find(message) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_print_event(self):
        printer = MessagePrinter()
        event = 'TEST'
        output = printer.flush(colors=False, msg=event, is_event=True)
        assert output.find(event) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_accept_empty_event(self):
        printer = MessagePrinter()
        event = ''
        output = printer.flush(colors=False, msg=event, is_event=True)
        assert output == f'{MessagePrinter.EVENT_START_MARKER}{MessagePrinter.EVENT_END_MARKER}'
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_event_with_colors(self):
        printer = MessagePrinter()
        event = 'TEST'
        output = printer.flush(colors=True, msg=event, is_event=True)
        assert output.find(event) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_event_should_be_different_than_standard_message(self):
        printer = MessagePrinter()
        base = 'TEST'
        standard = printer.flush(colors=False, msg=base, is_event=False)
        event = printer.flush(colors=False, msg=base, is_event=True)
        assert standard != event

    def test_should_ignore_extra_arguments(self):
        printer = MessagePrinter()
        message = 'Hello World!'

        output_base = printer.flush(colors=False, msg=message, is_event=False)
        output_extra = printer.flush(colors=False, msg=message, extra=[1, 2, 3], is_event=False)

        assert output_base == output_extra

    @pytest.mark.parametrize(
        "level,expected_color",
        [
            (LoggerConfig.Level.WARNING, Fore.YELLOW),
            (LoggerConfig.Level.ERROR, Fore.RED),
            (LoggerConfig.Level.DEBUG, Fore.GREEN),
            (LoggerConfig.Level.CRITICAL, Fore.RED)
        ]
    )
    def test_should_log_non_info_level_in_color(self, level, expected_color):
        printer = MessagePrinter()
        level = LoggerParts.Level(level)
        base = 'TEST'
        message_formatted = expected_color + base + Fore.RESET
        output = printer.flush(colors=True, msg=base, is_event=False, level=level)
        assert output.find(message_formatted) != -1

    def test_should_print_critical_in_color_and_bold(self):
        printer = MessagePrinter()
        base = 'TEST'
        message_formatted = Style.BRIGHT + Fore.RED + base + Fore.RESET
        output = printer.flush(
            colors=True,
            msg=base,
            is_event=False,
            level=LoggerParts.Level(LoggerConfig.Level.CRITICAL)
        )
        assert output.find(message_formatted) != -1

    @pytest.mark.parametrize(
        "level",
        [
            LoggerConfig.Level.WARNING,
            LoggerConfig.Level.ERROR,
            LoggerConfig.Level.DEBUG,
            LoggerConfig.Level.CRITICAL
        ]
    )
    def test_should_log_non_info_level_without_color_if_set(self, level):
        printer = MessagePrinter()
        level = LoggerParts.Level(level)
        base = 'TEST'
        output = printer.flush(colors=False, msg=base, is_event=False, level=level)
        assert re.search(self.COLOR_REGEXP, output) is None
