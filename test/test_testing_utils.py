import pytest
from magda.module import Module
from magda.testing.utils import wrap_into_result
from test.test_module_testing_wrapper import RawData, ModuleSync


class TestWrapIntoResult:
    def test_should_wrap_data_into_result(self):
        data: RawData = RawData('xyz')
        error = None
        interface = RawData
        name = 'raw_data'
        src_class = ModuleSync
        expose = 'expose'
        result: Module.Result = wrap_into_result(data, error, name, src_class, expose)

        assert isinstance(result, Module.Result)
        assert result.result == data
        assert result.error is error
        assert result.interface == interface
        assert result.name == name
        assert result.src_class == src_class
        assert result.expose == expose

    def test_should_fail_for_missing_data(self):
        with pytest.raises(TypeError):
            wrap_into_result()

    def test_should_accept_missing_arguments(self):
        data: RawData = RawData('xyz')
        result: Module.Result = wrap_into_result(data)

        assert isinstance(result, Module.Result)
        assert result.result == data
