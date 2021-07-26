import re
from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers import GroupPrinter


class TestGroupPrinter:
    COLOR_REGEXP = r'\x1b'

    def test_should_print_group(self):
        printer = GroupPrinter()
        group = 'GroupG1'

        part = LoggerParts.Group(group)
        output = printer.flush(colors=False, group=part)

        assert output.find(group) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_group_in_colors(self):
        printer = GroupPrinter()
        group = 'GroupG1'

        part = LoggerParts.Group(group)
        output = printer.flush(colors=True, group=part)

        assert output.find(group) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_not_fail_on_empty_group(self):
        printer = GroupPrinter()
        output = printer.flush(colors=False, group=None)
        assert output is None or output == ''

    def test_should_ignore_extra_arguments(self):
        printer = GroupPrinter()
        group = 'GroupG1'
        replica = 20

        part = LoggerParts.Group(group, replica)
        output_base = printer.flush(colors=False, group=part)
        output_extra = printer.flush(colors=False, group=part, extra=[1, 2, 3])

        assert output_base == output_extra
