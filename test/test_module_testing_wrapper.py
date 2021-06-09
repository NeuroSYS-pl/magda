from dataclasses import dataclass

import pytest

from magda.decorators import accept, produce, finalize
from magda.module import Module
from magda.module.results import ResultSet
from magda.testing import ModuleTestingWrapper
from magda.testing.utils import wrap_into_result


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
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build()
        request = {'key': 'value'}
        mock = mock.request(request)
        assert isinstance(mock, ModuleTestingWrapper)
        assert mock._request == request

    async def test_should_correctly_set_data(self, module_cls):
        module = module_cls('my-module-a').set_parameters(TestModuleTestingWrapper.module_params)
        mock = await ModuleTestingWrapper(module).build()
        data: RawData = RawData('xyz')
        mock = mock.data(data)

        assert isinstance(mock, ModuleTestingWrapper)
        assert isinstance(mock._data, ResultSet)
        assert mock._data.collection[0].result.data == data.data

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
