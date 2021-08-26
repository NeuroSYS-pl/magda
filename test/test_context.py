import pytest
import ray

from magda.pipeline.parallel import ParallelPipeline
from magda.pipeline.sequential import SequentialPipeline
from magda.module.module import Module
from magda.decorators.accepting import accept
from magda.decorators.finalizing import finalize
from magda.decorators.exposing import expose


@finalize
class MockModule(Module.Runtime):
    def run(self, *args, **kwargs):
        return self.context


@expose()
@accept(MockModule, self=True)
@finalize
class MockModuleReturningContext(Module.Runtime):
    def run(self, *args, **kwargs):
        return self.context


@pytest.fixture(scope='class')
def ray_context():
    ray.init(num_cpus=1)
    yield None
    ray.shutdown()


class TestContext:
    """ NOTE that a method _on_bootstrap() from magda/module/runtime.py calls a context
        if it's callable - a function will turn into a value, a class into an object etc.
        That's why callable objects are tested differently here.
        It's to be checked whether this is expected behavior.
    """

    def mock_function(x=-1, y=-1):
        return x + y

    class MockSimpleContext():
        def __init__(self, param=-1):
            self.param = param

    class MockContext():
        def __init__(self, param=-1, obj=None):
            self.param = param
            self.obj = obj

    noncallable_contexts = [
        None,
        dict(key='val'),
        dict(key_str='sth', key_int=123, key_list=[1, 2, 3]),
        list((1, 2, 3, 'a', 'b', 'c')),
        mock_function(1, 2)
    ]

    object_contexts = [
        (MockSimpleContext(param=13), 13),
        (MockContext(param=28), 28),
        (MockContext(param=10, obj=MockSimpleContext()), 10)
    ]

    callable_contexts = [
        (mock_function, int),
        (MockSimpleContext, MockSimpleContext)
    ]

    @pytest.mark.parametrize('context', noncallable_contexts)
    @pytest.mark.asyncio
    async def test_should_accept_noncallable_context(self, context):
        builder = SequentialPipeline()
        m1 = MockModule('m1')
        m2 = MockModuleReturningContext('m2').depends_on(m1)
        builder.add_module(m1)
        builder.add_module(m2)
        pipeline = await builder.build(context)

        assert pipeline.context == context
        assert pipeline.modules[0].context == context
        assert pipeline.modules[0].context == pipeline.modules[1].context

        results, _ = await pipeline.run()
        assert results['m2'] == context

    @pytest.mark.parametrize('context', noncallable_contexts)
    @pytest.mark.asyncio
    async def test_parallel_should_accept_noncallable_context(self, context, ray_context):
        builder = ParallelPipeline()
        m1 = MockModule('m1', group='g1')
        m2 = MockModuleReturningContext('m2', group='g2').depends_on(m1)
        builder.add_module(m1)
        builder.add_module(m2)
        pipeline = await builder.build(context)

        assert pipeline.context == context
        assert pipeline.modules[0].context == pipeline.modules[1].context
        results, _ = await pipeline.run()
        assert results['m2'] == context

    @pytest.mark.parametrize('context,param', object_contexts)
    @pytest.mark.asyncio
    async def test_object_context(self, context, param):
        builder = SequentialPipeline()
        m1 = MockModule('m1')
        m2 = MockModuleReturningContext('m2').depends_on(m1)
        builder.add_module(m1)
        builder.add_module(m2)
        pipeline = await builder.build(context)

        assert pipeline.context == context
        assert pipeline.modules[0].context == context
        assert pipeline.modules[0].context == pipeline.modules[1].context
        assert pipeline.modules[0].context.param == param

        results, _ = await pipeline.run()
        assert results['m2'] == context

    @pytest.mark.parametrize('context,param', object_contexts)
    @pytest.mark.asyncio
    async def test_object_parallel_context(self, context, param, ray_context):
        builder = ParallelPipeline()
        m1 = MockModule('m1', group='g1')
        m2 = MockModuleReturningContext('m2', group='g2').depends_on(m1)
        builder.add_module(m1)
        builder.add_module(m2)
        pipeline = await builder.build(context)

        assert pipeline.context.param == param
        results, _ = await pipeline.run()
        assert results['m2'].param == param

    @pytest.mark.parametrize('context,context_type', callable_contexts)
    @pytest.mark.asyncio
    async def test_callable_context(self, context, context_type):
        builder = SequentialPipeline()
        m1 = MockModule('m1')
        m2 = MockModuleReturningContext('m2').depends_on(m1)
        builder.add_module(m1)
        builder.add_module(m2)
        pipeline = await builder.build(context)

        assert pipeline.context == context
        assert isinstance(pipeline.modules[0].context, context_type)

        results, _ = await pipeline.run()
        assert isinstance(results['m2'], context_type)

    @pytest.mark.parametrize('context,context_type', callable_contexts)
    @pytest.mark.asyncio
    async def test_callable_parallel_context(self, context, context_type, ray_context):
        builder = ParallelPipeline()
        m1 = MockModule('m1', group='g1')
        m2 = MockModuleReturningContext('m2', group='g2').depends_on(m1)
        builder.add_module(m1)
        builder.add_module(m2)
        pipeline = await builder.build(context)

        assert pipeline.context == context
        results, _ = await pipeline.run()
        assert isinstance(results['m2'], context_type)
