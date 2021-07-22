import re
from magda.utils.logger.printers import TimestampPrinter


class TestTimestampPrinter:
    TIMESTAMP_REGEXP = r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{3})'
    COLOR_REGEXP = r'\x1b'

    def test_should_print_timestamp(self):
        printer = TimestampPrinter()
        output = printer.flush(colors=False)

        assert re.search(self.TIMESTAMP_REGEXP, output) is not None
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_timestamp_in_colors(self):
        printer = TimestampPrinter()
        output = printer.flush(colors=True)

        assert re.search(self.TIMESTAMP_REGEXP, output) is not None
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_accept_extra_arguments(self):
        printer = TimestampPrinter()
        output = printer.flush(colors=False, extra=[1, 2, 3], msg='Test')

        assert re.search(self.TIMESTAMP_REGEXP, output) is not None
        assert re.search(self.COLOR_REGEXP, output) is None
