import pytest

from magda.pipeline.sequential import SequentialPipeline
from magda.module.factory import ModuleFactory
from magda.module.module import Module
from magda.decorators.accepting import accept
from magda.decorators.finalizing import finalize
from magda.exceptions import ClosedPipelineException


@accept(self=True)
@finalize
class MockModule(Module.Runtime):
    def run(self, **kwargs):
        return 'output'


class MockContext:
    pass


class TestSequentialPipeline:
    def setup_method(self, method):
        ModuleFactory.unregister()
        ModuleFactory.register('MockModule', MockModule)
        self.pipeline = SequentialPipeline()
        self.context = MockContext()

    def teardown_method(self, method):
        ModuleFactory.unregister()

    def test_pipeline_add_module(self):
        module = MockModule('MockName')
        self.pipeline.add_module(module)
        assert len(self.pipeline.modules) == 1

    def test_pipeline_add_not_submodule(self):
        class MockNotSubmodule:
            pass

        module = MockNotSubmodule()
        with pytest.raises(TypeError):
            self.pipeline.add_module(module)

    def test_pipeline_get_module_by_name(self):
        module = MockModule('MockName')
        self.pipeline.add_module(module)
        assert self.pipeline.get_module('MockName') == module

    def test_pipeline_get_module_by_name_not_existing(self):
        assert self.pipeline.get_module('MockName') is None

    @pytest.mark.asyncio
    async def test_pipeline_build_no_modules(self):
        runtime = await self.pipeline.build(MockContext())
        assert len(runtime.modules) == 0

    @pytest.mark.asyncio
    async def test_pipeline_run_no_modules(self):
        assert len(self.pipeline.modules) == 0
        runtime = await self.pipeline.build(MockContext())
        result, _ = await runtime.run()
        assert isinstance(result, dict)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_pipeline_run_single_module(self):
        module = MockModule('MockName').expose_result()
        self.pipeline.add_module(module)
        runtime = await self.pipeline.build(MockContext())
        results, _ = await runtime.run()

        assert isinstance(results, dict)
        assert len(results) == 1
        assert 'MockName' in results
        assert results['MockName'] == 'output'

    @pytest.mark.asyncio
    async def test_pipeline_run_multiple_depending_modules(self):
        module_1 = MockModule('module_1')
        module_2 = MockModule('module_2')
        module_2.depends_on(module_1)
        self.pipeline.add_module(module_1)
        self.pipeline.add_module(module_2)
        runtime = await self.pipeline.build(MockContext())

        assert len(runtime.modules) == 2
        assert runtime.modules[0].name == 'module_1'
        assert runtime.modules[1].name == 'module_2'

        module_3 = MockModule('module_3')
        module_3.depends_on(module_2)
        self.pipeline.add_module(module_3)
        runtime = await self.pipeline.build(MockContext())

        assert len(runtime.modules) == 3
        assert runtime.modules[2].name == 'module_3'

    @pytest.mark.asyncio
    async def test_pipeline_is_regular_flag_shallow(self):
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'process'

        @accept(AggregatorModule)
        @finalize
        class RegularModuleAfterAgg(Module.Runtime):
            def run(self, **kwargs):
                return 'run'

        module_aggregator = AggregatorModule('agg_module')
        module_regular = RegularModule('reg_module')
        module_regular_after_agg = RegularModuleAfterAgg('reg_module_after_agg')

        module_aggregator.depends_on(module_regular)
        module_regular_after_agg.depends_on(module_aggregator)

        self.pipeline.add_module(module_regular)
        self.pipeline.add_module(module_aggregator)
        self.pipeline.add_module(module_regular_after_agg)
        runtime = await self.pipeline.build(MockContext())

        assert len(runtime.modules) == 3
        assert runtime.modules[0].name == 'reg_module' and runtime.modules[0].is_regular_module
        assert runtime.modules[1].name == 'agg_module' and not runtime.modules[1].is_regular_module
        assert runtime.modules[2].name == 'reg_module_after_agg' and \
            not runtime.modules[2].is_regular_module

    @pytest.mark.asyncio
    async def test_pipeline_is_regular_flag_deep(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'process'

        @accept(AggregatorModule, self=True)
        @finalize
        class RegularModuleAfterAgg(Module.Runtime):
            def run(self, **kwargs):
                return 'run'

        module_aggregator = AggregatorModule('agg_module')
        module_regular1 = RegularModule('reg_module1')
        module_regular11 = RegularModule('reg_module11')
        module_regular12 = RegularModule('reg_module12')
        module_regular_after_agg1 = RegularModuleAfterAgg('reg_module_after_agg1')
        module_regular_after_agg11 = RegularModuleAfterAgg('reg_module_after_agg11')
        module_regular_after_agg12 = RegularModuleAfterAgg('reg_module_after_agg12')
        module_regular_after_agg121 = RegularModuleAfterAgg('reg_module_after_agg121')
        module_regular_after_agg2 = RegularModuleAfterAgg('reg_module_after_agg2')

        module_aggregator.depends_on(module_regular1)
        module_regular11.depends_on(module_regular1)
        module_regular12.depends_on(module_regular1)
        module_regular_after_agg1.depends_on(module_aggregator)
        module_regular_after_agg2.depends_on(module_aggregator)
        module_regular_after_agg11.depends_on(module_regular_after_agg1)
        module_regular_after_agg12.depends_on(module_regular_after_agg1)
        module_regular_after_agg121.depends_on(module_regular_after_agg12)

        self.pipeline.add_module(module_regular1)
        self.pipeline.add_module(module_regular11)
        self.pipeline.add_module(module_regular12)
        self.pipeline.add_module(module_aggregator)
        self.pipeline.add_module(module_regular_after_agg1)
        self.pipeline.add_module(module_regular_after_agg2)
        self.pipeline.add_module(module_regular_after_agg11)
        self.pipeline.add_module(module_regular_after_agg12)
        self.pipeline.add_module(module_regular_after_agg121)
        runtime = await self.pipeline.build(MockContext())

        assert len(runtime.modules) == 9
        assert runtime.modules[0].name == 'reg_module1' and runtime.modules[0].is_regular_module
        assert runtime.modules[1].name == 'reg_module12' and runtime.modules[1].is_regular_module
        assert runtime.modules[2].name == 'reg_module11' and runtime.modules[2].is_regular_module
        assert runtime.modules[3].name == 'agg_module' and not runtime.modules[3].is_regular_module
        assert runtime.modules[4].name == 'reg_module_after_agg2' and \
            not runtime.modules[4].is_regular_module
        assert runtime.modules[5].name == 'reg_module_after_agg1' and \
            not runtime.modules[5].is_regular_module
        assert runtime.modules[6].name == 'reg_module_after_agg12' and \
            not runtime.modules[6].is_regular_module
        assert runtime.modules[7].name == 'reg_module_after_agg121' and \
            not runtime.modules[7].is_regular_module
        assert runtime.modules[8].name == 'reg_module_after_agg11' and \
            not runtime.modules[8].is_regular_module

    @pytest.mark.asyncio
    async def test_pipeline_module_depends_on_aggregate_and_regular_error(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'process'

        @accept(AggregatorModule, RegularModule, self=True)
        @finalize
        class RegularModuleFurther(Module.Runtime):
            def run(self, **kwargs):
                return 'run'

        module_regular = RegularModule('1')
        module_aggregator = AggregatorModule('2')
        module_after_agg = RegularModuleFurther('3')
        module_after_regular_and_agg = RegularModuleFurther('4')

        module_after_agg.depends_on(module_aggregator)
        module_after_regular_and_agg.depends_on(module_after_agg)
        module_after_regular_and_agg.depends_on(module_regular)
        module_aggregator.depends_on(module_regular)

        self.pipeline.add_module(module_aggregator)
        self.pipeline.add_module(module_regular)
        self.pipeline.add_module(module_after_regular_and_agg)
        self.pipeline.add_module(module_after_agg)

        with pytest.raises(Exception):
            await self.pipeline.build()

    @pytest.mark.asyncio
    async def test_pipeline_modules_run_only_regular(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'regular run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'aggregator run'

        @accept(AggregatorModule, RegularModule, self=True)
        @finalize
        class ModuleAfterAgg(Module.Runtime):
            def run(self, **kwargs):
                return 'after aggregator run'

        module_regular = RegularModule('regular').expose_result()
        module_aggregator = AggregatorModule('aggregator').expose_result()
        module_after_agg = ModuleAfterAgg('after_agg').expose_result()
        module_after_regular = RegularModule('after_reg').expose_result()

        module_aggregator.depends_on(module_regular)
        module_after_agg.depends_on(module_aggregator)
        module_after_regular.depends_on(module_regular)

        self.pipeline.add_module(module_regular)
        self.pipeline.add_module(module_aggregator)
        self.pipeline.add_module(module_after_agg)
        self.pipeline.add_module(module_after_regular)

        runtime = await self.pipeline.build()
        results, _ = await runtime.run()

        assert len(results) == 2
        assert 'regular' in results
        assert 'aggregator' not in results
        assert 'after_agg' not in results
        assert 'after_reg' in results

    @pytest.mark.asyncio
    async def test_pipeline_modules_run_only_aggregate(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'regular run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'aggregator run'

        @accept(AggregatorModule, RegularModule, self=True)
        @finalize
        class ModuleAfterAgg(Module.Runtime):
            def run(self, **kwargs):
                return 'after aggregator run'

        module_regular = RegularModule('regular').expose_result()
        module_aggregator = AggregatorModule('aggregator').expose_result()
        module_after_agg = ModuleAfterAgg('after_agg').expose_result()
        module_after_regular = RegularModule('after_reg').expose_result()

        module_aggregator.depends_on(module_regular)
        module_after_agg.depends_on(module_aggregator)
        module_after_regular.depends_on(module_regular)

        self.pipeline.add_module(module_regular)
        self.pipeline.add_module(module_aggregator)
        self.pipeline.add_module(module_after_agg)
        self.pipeline.add_module(module_after_regular)

        runtime = await self.pipeline.build()
        results, _ = await runtime.process()

        assert len(results) == 2
        assert 'regular' not in results
        assert 'aggregator' in results
        assert 'after_agg' in results
        assert 'after_reg' not in results

    @pytest.mark.asyncio
    async def test_pipeline_module_aggregate_keeps_state(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'regular run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return self.state

            def aggregate(self, **kwargs):
                self.add_data('state')
                return self.state

        regular = RegularModule('regular').expose_result()
        aggregate = AggregatorModule('aggregate').expose_result()

        aggregate.depends_on(regular)

        self.pipeline.add_module(regular)
        self.pipeline.add_module(aggregate)

        runtime = await self.pipeline.build()

        aggregate_runtime_module = runtime.modules[1]
        assert aggregate_runtime_module.name == 'aggregate'
        assert aggregate_runtime_module.state_size == 0
        assert aggregate_runtime_module.state == []

        await runtime.run()
        assert aggregate_runtime_module.state_size == 1
        assert aggregate_runtime_module.state == ['state']

        await runtime.run()
        assert aggregate_runtime_module.state_size == 2
        assert aggregate_runtime_module.state == ['state', 'state']

    @pytest.mark.asyncio
    async def test_pipeline_module_aggregate_clears_state(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'regular run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                state_copy = self.state.copy()
                self.clear_state()
                return state_copy

            def aggregate(self, **kwargs):
                self.add_data('state')
                return self.state

        regular = RegularModule('regular').expose_result()
        aggregate = AggregatorModule('aggregate').expose_result()

        aggregate.depends_on(regular)

        self.pipeline.add_module(regular)
        self.pipeline.add_module(aggregate)

        runtime = await self.pipeline.build()

        aggregate_runtime_module = runtime.modules[1]
        assert aggregate_runtime_module.name == 'aggregate'

        await runtime.run()
        await runtime.run()
        assert aggregate_runtime_module.state_size == 2
        assert aggregate_runtime_module.state == ['state', 'state']

        await runtime.process()
        assert aggregate_runtime_module.state_size == 0
        assert aggregate_runtime_module.state == []

    @pytest.mark.asyncio
    async def test_pipeline_module_after_gets_aggregated_results(self):
        @accept(self=True)
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'regular run'

        @accept(RegularModule)
        @finalize
        class AggregatorModule(Module.Aggregate):
            def aggregate(self, **kwargs):
                self.add_data('state')
                return self.state

        @accept(AggregatorModule, self=True)
        @finalize
        class ModuleAfterAgg(Module.Runtime):
            def run(self, data, **kwargs):
                return data.of('aggregate')[0] * 2

        regular = RegularModule('regular').expose_result()
        aggregate = AggregatorModule('aggregate').expose_result()
        module_after_agg = ModuleAfterAgg('after_agg').expose_result()

        aggregate.depends_on(regular)
        module_after_agg.depends_on(aggregate)

        self.pipeline.add_module(regular)
        self.pipeline.add_module(aggregate)
        self.pipeline.add_module(module_after_agg)

        runtime = await self.pipeline.build()

        aggregate_runtime_module = runtime.modules[1]
        assert aggregate_runtime_module.name == 'aggregate'

        await runtime.run()
        await runtime.run()
        assert aggregate_runtime_module.state_size == 2
        assert aggregate_runtime_module.state == ['state', 'state']

        results, _ = await runtime.process()

        assert 'after_agg' in results
        assert len(results['after_agg']) == 4
        assert results['after_agg'] == ['state', 'state', 'state', 'state']

    @pytest.mark.asyncio
    async def test_pipeline_set_parameters(self):
        parameters = {'param1': 1}
        module = MockModule('MockName').set_parameters(parameters)
        self.pipeline.add_module(module)

        runtime = await self.pipeline.build()
        module_runtime = runtime.modules[0]

        assert len(module_runtime.parameters) == 1
        assert 'param1' in module_runtime.parameters

    @pytest.mark.asyncio
    async def test_pipeline_runtime_readonly_parameters(self):
        parameters = {'param1': 1}
        module = MockModule('MockName').set_parameters(parameters)
        self.pipeline.add_module(module)

        runtime = await self.pipeline.build()
        module_runtime = runtime.modules[0]

        with pytest.raises(AttributeError):
            module_runtime.parameters = {}

    @pytest.mark.asyncio
    async def test_pipeline_parameters_available_in_run(self):
        @finalize
        class ModuleWithParams(Module.Runtime):
            def run(self, **kwargs):
                return self.parameters

        parameters = {'param1': 1}
        module = ModuleWithParams('module_with_params').expose_result().set_parameters(parameters)

        self.pipeline.add_module(module)
        runtime = await self.pipeline.build()
        results, _ = await runtime.run()

        assert 'module_with_params' in results
        assert results['module_with_params'] == parameters

    @pytest.mark.asyncio
    async def test_pipeline_shared_parameters_available_in_runtime(self):
        shared_parameters = {'shared_param1': 1}
        runtime = await self.pipeline.build(shared_parameters=shared_parameters)

        assert len(runtime.shared_parameters) == 1
        assert runtime.shared_parameters == shared_parameters

    @pytest.mark.asyncio
    async def test_pipeline_same_shared_parameters_in_modules(self):
        @finalize
        class ModuleWithParams(Module.Runtime):
            def run(self, **kwargs):
                return self.shared_parameters

        @accept(ModuleWithParams)
        @finalize
        class ModuleWithParamsOther(Module.Runtime):
            def run(self, **kwargs):
                return self.shared_parameters

        module = ModuleWithParams('module_with_params').expose_result()
        module_other = ModuleWithParamsOther('module_with_params_other').expose_result()

        module_other.depends_on(module)
        self.pipeline.add_module(module)
        self.pipeline.add_module(module_other)

        shared_parameters = {'shared_param1': 1}
        runtime = await self.pipeline.build(shared_parameters=shared_parameters)
        results, _ = await runtime.run()

        assert len(results) == 2
        assert 'module_with_params' in results
        assert 'module_with_params_other' in results
        assert results['module_with_params'] == results['module_with_params_other']

    @pytest.mark.asyncio
    async def test_pipeline_build_run_with_defaults(self):
        module = MockModule('mock_name').expose_result()
        self.pipeline.add_module(module)
        runtime = await self.pipeline.build()
        results, _ = await runtime.run()

        assert 'mock_name' in results
        assert results['mock_name'] == 'output'

    @pytest.mark.asyncio
    async def test_pipeline_with_groups(self):
        self.pipeline.add_module(MockModule('m1', group='g1'))
        self.pipeline.add_module(MockModule('m2').depends_on(self.pipeline.get_module('m1')))

        with pytest.warns(UserWarning):
            await self.pipeline.build(MockContext())

    @pytest.mark.asyncio
    async def test_close_pipeline(self):
        @accept(self=True)
        @finalize
        class TestModule(Module.Runtime):
            def bootstrap(self):
                self.state = 'opened'

            def run(self, **kwargs):
                return 'regular run'

            def teardown(self):
                self.state = 'closed'

        module_1 = TestModule('module_1')
        module_2 = TestModule('module_2')
        module_3 = TestModule('module_3')

        module_2.depends_on(module_1)
        module_3.depends_on(module_2)

        self.pipeline.add_module(module_1)
        self.pipeline.add_module(module_2)
        self.pipeline.add_module(module_3)

        runtime = await self.pipeline.build()

        await runtime.run()
        await runtime.close()

        assert runtime._is_closed
        assert runtime.modules[0].state == 'closed'
        assert runtime.modules[1].state == 'closed'
        assert runtime.modules[2].state == 'closed'
        with pytest.raises(ClosedPipelineException):
            await runtime.run()
        with pytest.raises(ClosedPipelineException):
            await runtime.process()

    @pytest.mark.asyncio
    async def test_should_catch_module_exception(self):
        @accept(self=True)
        @finalize
        class TestModuleError(Module.Runtime):
            def run(self, **kwargs):
                raise Exception()

        @accept(TestModuleError, self=True)
        @finalize
        class TestModuleOk(Module.Runtime):
            def run(self, **kwargs):
                return 'ok'

        module_1_ok = TestModuleOk('module_1_ok').expose_result()
        module_2_error = TestModuleError('module_2_error').expose_result()
        module_3_ok = TestModuleOk('module_3_ok').expose_result()
        module_4_ok = TestModuleOk('module_4_ok').expose_result()

        module_3_ok.depends_on(module_1_ok)
        module_3_ok.depends_on(module_2_error)
        module_4_ok.depends_on(module_3_ok)

        self.pipeline.add_module(module_1_ok)
        self.pipeline.add_module(module_2_error)
        self.pipeline.add_module(module_3_ok)
        self.pipeline.add_module(module_4_ok)

        runtime = await self.pipeline.build()

        result, error = await runtime.run()

        assert result is None
        assert isinstance(error, Exception)
