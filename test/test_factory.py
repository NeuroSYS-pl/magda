import pytest

from magda.module.factory import ModuleFactory
from magda.module.module import Module
from magda.decorators.finalizing import finalize


@finalize
class MockModule(Module.Runtime):
    pass


class TestFactory:

    def setup_method(self, method):
        ModuleFactory.unregister()

    def teardown_method(self, method):
        ModuleFactory.unregister()

    def test_factory_empty(self):
        assert len(ModuleFactory.module_references) == 0

    def test_factory_register(self):
        assert len(ModuleFactory.module_references) == 0

        ModuleFactory.register('MockModule', MockModule)
        assert len(ModuleFactory.module_references) == 1

    def test_factory_register_not_submodule(self):
        class NotSubmoduleMock:
            pass

        module_to_register = 'NotSubmoduleMock'
        with pytest.raises(TypeError):
            ModuleFactory.register(module_to_register, NotSubmoduleMock)

    def test_factory_register_same_module_twice(self):
        assert len(ModuleFactory.module_references) == 0

        module_to_register = 'SameModuleName'
        ModuleFactory.register(module_to_register, MockModule)
        assert len(ModuleFactory.module_references) == 1

        ModuleFactory.register(module_to_register, MockModule)
        assert len(ModuleFactory.module_references) == 1

    def test_factory_register_module_decorator(self):
        from test.mocks.module_decorated_mock import ModuleDecoratedMock
        assert len(ModuleFactory.module_references) == 1

    def test_factory_register_module_decorator_not_submodule(self):
        with pytest.raises(TypeError):
            @ModuleFactory.register('NotSubmoduleMock')
            class NotSubmoduleMock:
                pass

    def test_factory_create(self):
        module_name = 'MockModuleName'
        ModuleFactory.register(module_name, MockModule)
        MockModule.__abstractmethods__ = set()

        module_obj = ModuleFactory.create('Some name', module_name)
        assert type(module_obj) == MockModule

    def test_factory_create_module_type_not_registered(self):
        module_name = 'NotRegisteredModuleName'

        with pytest.raises(KeyError):
            ModuleFactory.create('Some name', module_name)

    def test_remove_registered_module(self):
        assert len(ModuleFactory.module_references) == 0
        ModuleFactory.register('MockModule', MockModule)
        assert len(ModuleFactory.module_references) == 1
        ModuleFactory.unregister('MockModule')
        assert len(ModuleFactory.module_references) == 0

    def test_remove_nonregistered_module(self):
        with pytest.warns(UserWarning):
            ModuleFactory.unregister('NotRegisteredModuleName')

    def test_nonstring_tag(self):
        with pytest.raises(TypeError):
            ModuleFactory.register(MockModule, MockModule)
