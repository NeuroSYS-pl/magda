import pytest

from magda.module.factory import ModuleFactory
from magda.pipeline.sequential import SequentialPipeline
from magda.module.module import Module
from magda.decorators.accepting import accept
from magda.decorators.finalizing import finalize
from magda.decorators.exposing import expose
from magda.decorators.producing import produce


@expose()
@accept(self=True)
@finalize
class MockModuleContext(Module.Runtime):
    def run(self, **kwargs):
        return self.context


@expose()
@accept(MockModuleContext, self=True)
@finalize
class MockModuleData(Module.Runtime):
    def run(self, data, **kwargs):
        return data


class TestResults:

    def setup_method(self, method):
        ModuleFactory.unregister()
        ModuleFactory.register('MockModuleContext', MockModuleContext)
        ModuleFactory.register('MockModuleData', MockModuleData)
        self.builder = SequentialPipeline()
        self.mod_c = MockModuleContext('mod_c')
        self.mod_d1 = MockModuleData('mod_d1')
        self.mod_d2 = MockModuleData('mod_d2')

    def teardown_method(self, method):
        del self.mod_c
        del self.mod_d1
        del self.mod_d2
        ModuleFactory.unregister()

    @pytest.mark.asyncio
    async def test_string_results(self):
        self.builder.add_module(self.mod_c)
        self.builder.add_module(self.mod_d1)
        self.builder.add_module(self.mod_d2.depends_on(self.mod_c).depends_on(self.mod_d1))
        pipeline = await self.builder.build([1, 2, 3])
        runtime, _ = await pipeline.run()

        assert runtime['mod_d1'].of('mod_c') == []
        assert runtime['mod_d2'].of('mod_c') == [[1, 2, 3]]
        assert runtime['mod_d2'].get('mod_c') == [1, 2, 3]
        assert not runtime['mod_d1'].has('mod_c')
        assert runtime['mod_d2'].has('mod_c')
        assert len(runtime['mod_d1']) == 0
        assert len(runtime['mod_d2']) == 2

    @pytest.mark.asyncio
    async def test_module_results(self):
        self.builder.add_module(self.mod_c)
        self.builder.add_module(self.mod_d1)
        self.builder.add_module(self.mod_d2.depends_on(self.mod_c).depends_on(self.mod_d1))
        pipeline = await self.builder.build([1, 2, 3])
        runtime, _ = await pipeline.run()

        assert runtime['mod_d1'].of(MockModuleContext) == []
        assert runtime['mod_d2'].of(MockModuleContext) == [[1, 2, 3]]
        assert runtime['mod_d2'].get(MockModuleContext) == [1, 2, 3]
        assert not runtime['mod_d1'].has(MockModuleContext)
        assert runtime['mod_d2'].has(MockModuleContext)

    @pytest.mark.asyncio
    async def test_collection_copy(self):
        self.builder.add_module(self.mod_c)
        self.builder.add_module(self.mod_d1.depends_on(self.mod_c))
        pipeline = await self.builder.build([1, 2, 3])
        runtime, _ = await pipeline.run()

        assert runtime['mod_d1'].collection
        assert runtime['mod_d1'].collection is not runtime['mod_d1']._collection
        assert runtime['mod_d1'].collection[0] is runtime['mod_d1']._collection[0]

    @pytest.mark.asyncio
    async def test_module_invalid_has(self):
        class InvalidModuleClass():
            pass

        self.builder.add_module(self.mod_c)
        self.builder.add_module(self.mod_d1.depends_on(self.mod_c))
        pipeline = await self.builder.build('abc')
        runtime, _ = await pipeline.run()

        assert runtime['mod_d1'].has(MockModuleContext)
        with pytest.raises(KeyError):
            assert runtime['mod_d1'].has(InvalidModuleClass)

    @pytest.mark.asyncio
    async def test_module_invalid_filter_of(self):
        class InvalidModuleClass():
            pass

        self.builder.add_module(self.mod_c)
        self.builder.add_module(self.mod_d1.depends_on(self.mod_c))
        pipeline = await self.builder.build('abc')
        runtime, _ = await pipeline.run()

        assert runtime['mod_d1'].of(MockModuleContext) == ['abc']
        with pytest.raises(KeyError):
            assert runtime['mod_d1'].of(InvalidModuleClass) == []

    @pytest.mark.asyncio
    async def test_module_invalid_get(self):
        self.builder.add_module(self.mod_c)
        self.builder.add_module(self.mod_d1.depends_on(self.mod_c))
        self.builder.add_module(self.mod_d2.depends_on(self.mod_d1))
        self.builder.add_module(
            MockModuleData('mod_d3')
            .depends_on(self.mod_d1)
            .depends_on(self.mod_d2)
        )
        pipeline = await self.builder.build('abc')
        runtime, _ = await pipeline.run()

        assert runtime['mod_d3'].has(MockModuleData)
        with pytest.raises(Exception):
            assert runtime['mod_d3'].get(MockModuleData)

    @pytest.mark.asyncio
    async def test_module_interface_results(self):
        class MockCorrectInterface(Module.Interface):
            pass

        @expose()
        @produce(MockCorrectInterface)
        @accept(self=True)
        @finalize
        class MockModuleDataInterface(Module.Runtime):
            def run(self, data, **kwargs):
                data.result = 'abc'
                return data

        self.builder.add_module(MockModuleDataInterface('mod_i1'))
        self.builder.add_module(
            MockModuleDataInterface('mod_i2')
            .depends_on(self.builder.get_module('mod_i1'))
        )
        pipeline = await self.builder.build()
        runtime, _ = await pipeline.run()

        assert not runtime['mod_i1'].has(MockCorrectInterface)
        assert runtime['mod_i2'].has(MockCorrectInterface)
        assert runtime['mod_i2'].get(MockCorrectInterface).result == 'abc'
