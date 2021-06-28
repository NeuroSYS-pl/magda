import re
from colorama import Fore
from magda.utils.logger.printers import *


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
        assert output.find(message) != -1
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
