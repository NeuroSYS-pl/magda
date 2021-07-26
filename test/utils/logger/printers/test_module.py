import re
from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers import ModulePrinter


class TestModulePrinter:
    COLOR_REGEXP = r'\x1b'

    def test_should_print_module(self):
        printer = ModulePrinter()
        name, kind = 'test-x', 'TestX'

        part = LoggerParts.Module(name, kind)
        output = printer.flush(colors=False, module=part)

        assert output.find(name) != -1
        assert output.find(kind) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_module_in_colors(self):
        printer = ModulePrinter()
        name, kind = 'test-x', 'TestX'

        part = LoggerParts.Module(name, kind)
        output = printer.flush(colors=True, module=part)

        assert output.find(name) != -1
        assert output.find(kind) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_not_fail_on_empty_module(self):
        printer = ModulePrinter()
        output = printer.flush(colors=False, module=None)
        assert output is None or output == ''

    def test_should_ignore_extra_arguments(self):
        printer = ModulePrinter()
        name, kind = 'test-x', 'TestX'

        part = LoggerParts.Module(name, kind)
        output_base = printer.flush(colors=False, module=part)
        output_extra = printer.flush(colors=False, module=part, extra=[1, 2, 3])

        assert output_base == output_extra
