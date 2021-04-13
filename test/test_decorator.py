import pytest

from magda.pipeline.sequential import SequentialPipeline
from magda.module.factory import ModuleFactory
from magda.module.module import Module
from magda.decorators.accepting import accept
from magda.decorators.finalizing import finalize
from magda.decorators.exposing import expose


@expose('a')
@accept(self=True)
@finalize
class MockModuleA(Module.Runtime):
    def run(self, **kwargs):
        pass


@accept(MockModuleA, self=True)
@finalize
class MockModuleB(Module.Runtime):
    def run(self, **kwargs):
        pass


class TestDecorator:

    def setup_method(self, method):
        ModuleFactory.unregister()
        ModuleFactory.register('MockModuleA', MockModuleA)
        ModuleFactory.register('MockModuleB', MockModuleB)

    def teardown_method(self, method):
        ModuleFactory.unregister()

    def test_accept_nonmodule(self):
        class SimpleClass:
            pass

        with pytest.raises(TypeError):
            @accept(SimpleClass, self=True)
            @finalize
            class InvalidModule(Module.Runtime):
                def run(self, **kwargs):
                    pass

    def test_module_without_finalize(self):
        with pytest.raises(TypeError):
            @accept()
            class InvalidModule(Module.Runtime):
                def run(self, **kwargs):
                    pass

    def test_module_with_wrong_decorator_order(self):
        with pytest.raises(TypeError):
            @finalize
            @expose('m1')
            class InvalidModule(Module.Runtime):
                def run(self, **kwargs):
                    pass

    def test_decorating_nonmodule_class(self):
        with pytest.raises(TypeError):
            @accept()
            class InvalidModule():
                def run(self, **kwargs):
                    pass

    def test_finalizing_nonmodule_class(self):
        with pytest.raises(TypeError):
            @finalize
            class NonModuleClass():
                pass

    @pytest.mark.asyncio
    async def test_exposing_under_the_same_name(self):

        @expose('a')
        @accept(MockModuleA)
        @finalize
        class MockModuleC(Module.Runtime):
            def run(self, **kwargs):
                pass

        ModuleFactory.register('MockModuleC', MockModuleC)
        builder = SequentialPipeline()
        builder.add_module(MockModuleA('m1'))
        builder.add_module(MockModuleC('m2'))

        with pytest.raises(Exception):
            pipeline = await builder.build()
