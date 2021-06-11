import pytest
from magda.module import Module
from magda.testing.utils import wrap_into_result
from test.test_module_testing_wrapper import RawData, ModuleSync


class TestWrapIntoResult:
    def test_should_pass(self):
        data: RawData = RawData('xyz')
        interface = RawData
        name = 'raw_data'
        src_class = ModuleSync
        expose = 'expose'
        result: Module.Result = wrap_into_result(data, name, src_class, expose)

        assert isinstance(result, Module.Result)
        assert result.result == data
        assert result.interface == interface
        assert result.name == name
        assert result.src_class == src_class
        assert result.expose == expose

    def test_should_fail(self):
        with pytest.raises(TypeError):
            wrap_into_result()
