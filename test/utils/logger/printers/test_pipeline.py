import re
from magda.utils.logger.parts import LoggerParts
from magda.utils.logger.printers import PipelinePrinter


class TestPipelinePrinter:
    COLOR_REGEXP = r'\x1b'

    def test_should_print_pipeline(self):
        printer = PipelinePrinter()
        name, kind = 'test-x', 'TestX'

        part = LoggerParts.Pipeline(name, kind)
        output = printer.flush(colors=False, pipeline=part)

        assert output.find(name) != -1
        assert output.find(kind) != -1
        assert re.search(self.COLOR_REGEXP, output) is None

    def test_should_print_pipeline_in_colors(self):
        printer = PipelinePrinter()
        name, kind = 'test-x', 'TestX'

        part = LoggerParts.Pipeline(name, kind)
        output = printer.flush(colors=True, pipeline=part)

        assert output.find(name) != -1
        assert output.find(kind) != -1
        assert re.search(self.COLOR_REGEXP, output) is not None

    def test_should_not_fail_on_empty_pipeline(self):
        printer = PipelinePrinter()
        output = printer.flush(colors=False, pipeline=None)
        assert output is None or output == ''

    def test_should_ignore_extra_arguments(self):
        printer = PipelinePrinter()
        name, kind = 'test-x', 'TestX'

        part = LoggerParts.Pipeline(name, kind)
        output_base = printer.flush(colors=False, pipeline=part)
        output_extra = printer.flush(colors=False, pipeline=part, extra=[1, 2, 3])

        assert output_base == output_extra
