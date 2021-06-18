from dataclasses import dataclass
from typing import Dict

import pytest

from magda.decorators import accept, produce, finalize
from magda.module import Module
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
class ModuleTakingRequestAndData(Module.Runtime):
    def run(self, request, data: Module.ResultSet, **kwargs):
        return ProcessedData(data.get(RawData)[::-1] + ' ' + request['text'])


@accept(RawData)
@produce(ProcessedData)
@finalize
class ModuleOnlyData(Module.Runtime):
    def run(self, data: Module.ResultSet, **kwargs):
        return ProcessedData(data.get(RawData)[::-1])


@produce(ProcessedData)
@finalize
class ModuleOnlyRequest(Module.Runtime):
    def run(self, request: Dict[str, str], **kwargs):
        return ProcessedData(request['text'])


@accept(RawData, ProcessedData)
@produce(ProcessedData)
@finalize
class ModuleManyDataElements(Module.Runtime):
    """
    Module takes 'data' argument which is ResultSet with many elements.
    """
    def run(self, data: Module.ResultSet, **kwargs):
        text_part_1 = data.get(RawData)[::-1]
        text_part_2 = data.get(ProcessedData).data
        return ProcessedData(text_part_1 + '_' + text_part_2)


@finalize
class ModuleTestForSettingParameters(Module.Runtime):
    @dataclass
    class Parameters:
        param: str

    def bootstrap(self, **kwargs):
        self.params: self.Parameters = self.Parameters(**self.parameters)

    def run(self, data: Module.ResultSet, **kwargs):
        return ProcessedData(data.get(RawData)[::-1])


@finalize
class ModuleSync(Module.Runtime):
    def bootstrap(self, **kwargs):
        self.is_built: bool = True
        self.is_run: bool = False

    def run(self, request, data: Module.ResultSet, **kwargs):
        self.is_run = True
        return None

    def teardown(self):
        self.is_built: bool = False
        return super().teardown()


@finalize
class ModuleAsync(Module.Runtime):
    async def bootstrap(self, **kwargs):
        self.is_built: bool = True
        self.is_run: bool = False

    async def run(self, request, data: Module.ResultSet, **kwargs):
        self.is_run = True
        return None

    async def teardown(self):
        self.is_built: bool = False
        return super().teardown()


@pytest.mark.asyncio
class TestModuleTestingWrapper:
    module_params = {'param': 'value'}

    @pytest.mark.parametrize('module_cls', [ModuleAsync, ModuleSync])
    async def test_should_correctly_bootstrap(self, module_cls):
        module = module_cls('test-module')
        mock = await ModuleTestingWrapper(module).build()
        assert mock.module.is_built

    @pytest.mark.parametrize('module_cls', [ModuleAsync, ModuleSync])
    async def test_should_correctly_teardown(self, module_cls):
        module = module_cls('test-module')
        mock = await ModuleTestingWrapper(module).build()
        await mock.close()
        assert not mock.module.is_built

    @pytest.mark.parametrize('module_cls', [ModuleAsync, ModuleSync])
    async def test_should_correctly_invoke_run(self, module_cls):
        module = module_cls('test-module')
        mock = await ModuleTestingWrapper(module).build()
        await mock.run()
        assert mock.module.is_run

    async def test_should_correctly_set_request(self):
        target_request = {'key': 'value'}

        @finalize
        class ModuleTestSetRequest(Module.Runtime):
            def run(self, request, *arg, **kwargs):
                assert request == target_request

        module = ModuleTestSetRequest('test-module')
        mock = await ModuleTestingWrapper(module).build()
        mock = mock.request(target_request)
        await mock.run()

    async def test_should_correctly_set_data(self):
        raw_data = RawData('xyz')

        @finalize
        class ModuleTestSetRequest(Module.Runtime):
            def run(self, data, *arg, **kwargs):
                assert data.get(RawData) == raw_data

        module = ModuleTestSetRequest('test-module')
        mock = await ModuleTestingWrapper(module).build()
        mock = mock.data(raw_data)
        await mock.run()

    async def test_should_correctly_process_request_and_data(self):
        module = ModuleTakingRequestAndData('test-module')
        mock = await ModuleTestingWrapper(module).build()

        result = await mock.request({'text': 'request_text'}).data(RawData('xyz')).run()
        assert result == ProcessedData('zyx request_text')

    async def test_should_correctly_process_only_data(self):
        module = ModuleOnlyData('test-module')
        mock = await ModuleTestingWrapper(module).build()

        mock = mock.data(RawData('xyz'))
        result = await mock.run()
        assert result == ProcessedData('zyx')

    async def test_should_correctly_process_only_request(self):
        module = ModuleOnlyRequest('test-module')
        mock = await ModuleTestingWrapper(module).build()

        mock = mock.request({'text': 'request_text'})
        result = await mock.run()
        assert result == ProcessedData('request_text')

    async def test_should_correctly_process_many_data_elements(self):
        module = ModuleManyDataElements('test-module')
        mock = await ModuleTestingWrapper(module).build()

        mock = mock.data(RawData('xyz'), ProcessedData('xyz'))
        result = await mock.run()
        assert result == ProcessedData('zyx_xyz')

    async def test_should_build_when_parameters_are_passed(self):
        module = ModuleTestForSettingParameters('test-module').set_parameters({'param': 'value'})
        mock = await ModuleTestingWrapper(module).build()
        assert isinstance(mock, ModuleTestingWrapper)

    async def test_should_not_build_for_empty_parameters(self):
        module = ModuleTestForSettingParameters('test-module').set_parameters({})

        with pytest.raises(TypeError):
            await ModuleTestingWrapper(module).build()

    async def test_should_correctly_pass_shared_parameters(self):
        shared_parameters = {'shared_param': 'value'}
        module = ModuleSync('test-module')
        mock = await ModuleTestingWrapper(module).build(shared_parameters=shared_parameters)
        assert mock.module.shared_parameters == shared_parameters

    async def test_should_correctly_pass_context(self):
        def get_context():
            return 'callable context'

        module = ModuleSync('test-module')
        mock = await ModuleTestingWrapper(module).build(context=get_context)
        assert mock.module.context() == get_context()
