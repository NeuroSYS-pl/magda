import re
from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers import RequestPrinter


class TestRequestPrinter:
    COLOR_REGEXP = r'\x1b'

    def test_should_print_request(self):
        printer = RequestPrinter()
        request = 'Request(variable=5)'

        part = LoggerParts.Request(request)
        output = printer.flush(colors=False, request=part)

        assert output.find(request) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_request_in_colors(self):
        printer = RequestPrinter()
        request = 'Request(variable=5)'

        part = LoggerParts.Request(request)
        output = printer.flush(colors=True, request=part)

        assert output.find(request) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_not_fail_on_empty_request(self):
        printer = RequestPrinter()
        output = printer.flush(colors=False, request=None)
        assert output is None or output == ''

    def test_should_ignore_extra_arguments(self):
        printer = RequestPrinter()
        request = 'Request(variable=5)'

        part = LoggerParts.Request(request)
        output_base = printer.flush(colors=False, request=part)
        output_extra = printer.flush(colors=False, request=part, extra=[1, 2, 3])

        assert output_base == output_extra
