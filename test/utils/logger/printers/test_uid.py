import re
from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers import UidPrinter


class TestUidPrinter:
    COLOR_REGEXP = r'\x1b'

    def test_should_print_complete_uid(self):
        printer = UidPrinter()
        module_name, module_kind = 'test-x', 'TestX'
        group_name, replica = 'GroupG1', 222
        module = LoggerParts.Module(module_name, module_kind)
        group = LoggerParts.Group(group_name, replica)

        output = printer.flush(colors=False, group=group, module=module)

        assert output.find(module_name) != -1
        assert output.find(module_kind) != -1
        assert output.find(group_name) != -1
        assert output.find(str(replica)) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_with_missing_replica(self):
        printer = UidPrinter()
        module_name, module_kind = 'test-x', 'TestX'
        group_name = 'GroupG1'
        module = LoggerParts.Module(module_name, module_kind)
        group = LoggerParts.Group(group_name)

        output = printer.flush(colors=False, group=group, module=module)

        assert output.find(module_name) != -1
        assert output.find(module_kind) != -1
        assert output.find(group_name) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_with_missing_group(self):
        printer = UidPrinter()
        module_name, module_kind = 'test-x', 'TestX'
        module = LoggerParts.Module(module_name, module_kind)

        output = printer.flush(colors=False, module=module)

        assert output.find(module_name) != -1
        assert output.find(module_kind) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_work_with_missing_data(self):
        printer = UidPrinter()
        output = printer.flush(colors=False)
        assert output is None

    def test_should_print_with_colors(self):
        printer = UidPrinter()
        module_name, module_kind = 'test-x', 'TestX'
        group_name, replica = 'GroupG1', 222
        module = LoggerParts.Module(module_name, module_kind)
        group = LoggerParts.Group(group_name, replica)

        output = printer.flush(colors=True, group=group, module=module)

        assert output.find(module_name) != -1
        assert output.find(module_kind) != -1
        assert output.find(group_name) != -1
        assert output.find(str(replica)) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_ignore_extra_arguments(self):
        printer = UidPrinter()
        module_name, module_kind = 'test-x', 'TestX'
        group_name, replica = 'GroupG1', 222
        module = LoggerParts.Module(module_name, module_kind)
        group = LoggerParts.Group(group_name, replica)

        output_base = printer.flush(colors=True, group=group, module=module)
        output_extra = printer.flush(colors=True, group=group, module=module, extra=[1, 2, 3])

        assert output_base == output_extra
