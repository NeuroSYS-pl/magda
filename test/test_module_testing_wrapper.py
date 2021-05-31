from dataclasses import dataclass

import pytest

from magda.testing import ModuleTestingWrapper
from magda.decorators import accept, produce, finalize
from magda.module import Module
from magda.testing.utils import wrap_data_into_resultset, wrap_into_result, wrap_single_object_into_resultset


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
class TestTestingModule:
    async def test_should_process_correctly(self, module_cls):
        module = module_cls('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()

        result = await mock.run(data=RawData('xyz'), request={'query': 'query'})
        assert result == ProcessedData('zyx')

    async def test_should_not_compile(self, module_cls):
        module = module_cls('my-module-a').set_parameters({}) # Missing required params

        with pytest.raises(TypeError):
            await ModuleTestingWrapper(module).build()

    async def test_should_correctyl_bootstrap(self, module_cls):
        module = module_cls('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()
        assert mock.module.is_built
    
    async def test_should_correctly_teardown(self, module_cls):
        module = module_cls('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()
        await mock.close()
        assert not mock.module.is_built
    
    async def test_should_correctly_pass_shared_parameters(self, module_cls):
        shared_parameters={'shared_param': 'value'}
        module = module_cls('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build(shared_parameters=shared_parameters)
        assert mock.module.shared_parameters == shared_parameters

    async def test_should_correctly_pass_context(self, module_cls):
        def get_context():
            return 'callabel context'

        module = module_cls('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build(context=get_context)
        assert mock.module.context() == get_context()


class TestTestingModuleOnlyData:
    @pytest.mark.asyncio
    async def test_should_process_correctly(self):
        module = ModuleOnlyData('my-module-a').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()

        result = await mock.run(RawData('xyz'))
        assert result == ProcessedData('zyx')


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


class TestWrapDataIntoResultSet:
    params_names = 'arg_names, args, kwargs'
    params_pass = [
        (['request', 'data'], ({'query': 'example_query'}, RawData('xyz')), {}),
        (['request', 'data'], ({'query': 'example_query'},), {'data': RawData('xyz')}),
        (['request', 'data'], (RawData('xyz'),), {'request': {'query': 'example_query'}}),
        (['request', 'data'], tuple(), {'request': {'query': 'example_query'}, 'data': RawData('xyz')}),
        (['data'], (RawData('xyz'),), {}),
        (['data'], tuple(), {'data': RawData('xyz')}),
        (['data'], (RawData('xyz'),), {'request': {'query': 'example_query'}}),
        (['data'], tuple(), {'request': {'query': 'example_query'}, 'data': RawData('xyz')}),
        ([], ({'query': 'example_query'},), {'data': RawData('xyz')}),
        ([], tuple(), {'request': {'query': 'example_query'}, 'data': RawData('xyz')}),
        (['request'], ({'query': 'example_query'},), {}),
        (['request'], tuple(), {'request': {'query': 'example_query'}})
    ]

    @pytest.mark.parametrize(params_names, params_pass)
    def test_should_pass(self, arg_names, args, kwargs):
        target_data = RawData('xyz')
        wrap = wrap_single_object_into_resultset
        target_args = tuple([arg if arg != target_data else wrap(target_data) for arg in args])
        target_kwargs = {key: val if val != target_data else wrap(val) for key, val in kwargs.items()}
        wrapped_args, wrapped_kwargs = wrap_data_into_resultset(arg_names, *args, **kwargs)

        def equals(obj1, obj2):
            if isinstance(obj1, Module.ResultSet) and isinstance(obj2, Module.ResultSet):
                return obj1.collection == obj2.collection
            else:
                return obj1 == obj2
        
        assert all([equals(w, t) for (w, t) in zip(wrapped_args, target_args)])
        assert all([equals(wrapped_kwargs[key], target_kwargs[key]) for key in target_kwargs.keys()])
