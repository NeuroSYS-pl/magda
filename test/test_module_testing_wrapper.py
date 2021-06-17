from dataclasses import dataclass
from typing import Any, Tuple
from unittest.mock import MagicMock

import pytest

from magda.decorators import accept, produce, finalize
from magda.module import Module
from magda.module.results import ResultSet
from magda.testing import ModuleTestingWrapper


@dataclass(frozen=True)
class RawData(Module.Interface):
    data: str

    def __getitem__(self, index):
        return self.data[index]


@dataclass(frozen=True)
class ProcessedData(Module.Interface):
    data: str


@accept(RawData)
@produce(ProcessedData)
@finalize
class ModuleOnlyData(Module.Runtime):
    """
    Module has only 'data' argument in method run(). It is typical, expected use case.
    """
    @dataclass
    class Parameters:
        param: str

    def bootstrap(self, **kwargs):
        self.params: self.Parameters = self.Parameters(**self.parameters)

    def run(self, data: Module.ResultSet, **kwargs):
        return ProcessedData(data.get(RawData)[::-1])


@accept(RawData, ProcessedData)
@produce(ProcessedData)
@finalize
class ModuleManyDataElements(Module.Runtime):
    """
    Module takes 'data' argument which is ResultSet with many elements.
    """
    @dataclass
    class Parameters:
        param: str

    def bootstrap(self, **kwargs):
        self.params: self.Parameters = self.Parameters(**self.parameters)

    def run(self, data: Module.ResultSet, **kwargs):
        text_part_1 = data.get(RawData)[::-1]
        text_part_2 = data.get(ProcessedData).data
        return ProcessedData(text_part_1 + '_' + text_part_2)


@accept(RawData)
@produce(ProcessedData)
@finalize
class ModuleSync(Module.Runtime):
    @dataclass
    class Parameters:
        param: str

    def bootstrap(self, **kwargs):
        self.is_built: bool = True
        self.params: self.Parameters = self.Parameters(**self.parameters)

    def run(self, request, data: Module.ResultSet, **kwargs):
        self.request = request
        self.data = data
        return ProcessedData(data.get(RawData)[::-1])

    def teardown(self):
        self.is_built: bool = False
        return super().teardown()


@accept(RawData)
@produce(ProcessedData)
@finalize
class ModuleAsync(Module.Runtime):
    @dataclass
    class Parameters:
        param: str

    async def bootstrap(self, **kwargs):
        self.is_built: bool = True
        self.params: self.Parameters = self.Parameters(**self.parameters)

    async def run(self, request, data: Module.ResultSet, **kwargs):
        return ProcessedData(data.get(RawData)[::-1])

    async def teardown(self):
        self.is_built: bool = False
        return super().teardown()


def run_mock_sync(self, request, data, **kwargs) -> Tuple[Any, Any]:
    return request, data


async def run_mock_async(self, request, data, **kwargs) -> Tuple[Any, Any]:
    return request, data


@pytest.mark.parametrize('module_cls', [ModuleAsync, ModuleSync])
@pytest.mark.asyncio
class TestModuleTestingWrapper:
    module_params = {'param': 'value'}

    async def test_should_process_correctly(self, module_cls):
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build()

        result = await mock.data(RawData('xyz')).request({'query': 'query'}).run()
        assert result == ProcessedData('zyx')

    async def test_should_process_correctly_many_data_elements(self, module_cls):
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build()

        result = await mock.data(RawData('xyz')).request({'query': 'query'}).run()
        assert result == ProcessedData('zyx')

    async def test_should_correctly_bootstrap(self, module_cls):
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build()
        assert mock.module.is_built

    async def test_should_correctly_teardown(self, module_cls):
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build()
        await mock.close()
        assert not mock.module.is_built

    async def test_should_correctly_set_request(self, module_cls):
        target_request = {'key': 'value'}

        @finalize
        class ModuleTestSetRequest(Module.Runtime):
            def run(self, request, *arg, **kwargs):
                assert request == target_request

        module = ModuleTestSetRequest('test-module')
        mock = await ModuleTestingWrapper(module).build()
        mock = mock.request(target_request)
        await mock.run()

    async def test_should_correctly_set_data(self, module_cls):
        raw_data = RawData('xyz')

        @finalize
        class ModuleTestSetRequest(Module.Runtime):
            def run(self, data, *arg, **kwargs):
                assert data.get(RawData) == raw_data

        module = ModuleTestSetRequest('test-module')
        mock = await ModuleTestingWrapper(module).build()
        mock = mock.data(raw_data)
        await mock.run()

    async def test_should_not_compile(self, module_cls):
        module = module_cls('my-module-a').set_parameters({})   # Missing required params

        with pytest.raises(TypeError):
            await ModuleTestingWrapper(module).build()

    async def test_should_correctly_pass_shared_parameters(self, module_cls):
        shared_parameters = {'shared_param': 'value'}
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build(shared_parameters=shared_parameters)
        assert mock.module.shared_parameters == shared_parameters

    async def test_should_correctly_pass_context(self, module_cls):
        def get_context():
            return 'callable context'

        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build(context=get_context)
        assert mock.module.context() == get_context()


class TestModuleTestingWrapperOnlyData:
    @pytest.mark.asyncio
    async def test_should_process_correctly(self):
        module = ModuleOnlyData('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()

        mock = mock.data(RawData('xyz'))
        result = await mock.run()
        assert result == ProcessedData('zyx')


class TestModuleTestingWrapperManyDataElements:
    @pytest.mark.asyncio
    async def test_should_process_correctly(self):
        module = ModuleManyDataElements('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()

        mock = mock.data(RawData('xyz'), ProcessedData('xyz'))
        result = await mock.run()
        assert result == ProcessedData('zyx_xyz')
