import pytest
from pathlib import Path

from magda.module.module import Module
from magda.module.factory import ModuleFactory
from magda.module.interface import ModuleInterface
from magda.pipeline.sequential import SequentialPipeline
from magda.config_reader import ConfigReader
from magda.decorators import finalize
from magda.decorators.accepting import accept
from magda.decorators.producing import produce


class MockCorrectInterface(ModuleInterface):
    pass


class MockCorrectDependingInterface(ModuleInterface):
    pass


class MockIncorrectDependingInterface(ModuleInterface):
    pass


class TestInterfaces:

    def setup_method(self, method):
        @produce(MockCorrectDependingInterface)
        @finalize
        class ModuleDependingCorrect(Module.Runtime):
            def run(self, *args, **kwargs):
                pass

        @produce(MockIncorrectDependingInterface)
        @finalize
        class ModuleDependingIncorrect(Module.Runtime):
            def run(self, *args, **kwargs):
                pass

        ModuleFactory.unregister()
        ModuleFactory.register('ModuleDependingCorrect', ModuleDependingCorrect)
        ModuleFactory.register('ModuleDependingIncorrect', ModuleDependingIncorrect)

    def teardown_method(self, method):
        ModuleFactory.unregister()

    def get_config_file(self, config_name):
        return Path(__file__).parent / 'test_configs' / config_name

    @pytest.mark.asyncio
    async def test_can_build_pipeline_with_module_accepting_interface(self):
        @accept(MockCorrectInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            def run(self, *args, **kwargs):
                pass

        module = ModuleSample('mock')
        builder = SequentialPipeline()
        builder.add_module(module)

        pipeline = await builder.build()
        assert isinstance(pipeline, SequentialPipeline.Runtime)

    def test_cannot_register_interfaces(self):
        with pytest.raises(TypeError):
            ModuleFactory.unregister()
            ModuleFactory.register('MockCorrectDependingInterface', MockCorrectDependingInterface)

    def test_can_accept_correct_interface(self):
        @accept(MockCorrectInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        assert 1 == len(ModuleSample._ancestors)
        assert issubclass(ModuleSample._ancestors[0], MockCorrectInterface)

    def test_cannot_accept_incorrect_interface(self):
        class MockIncorrectInterface:
            pass

        with pytest.raises(TypeError):
            @accept(MockIncorrectInterface)
            @finalize
            class ModuleSample(Module.Runtime):
                pass

    def test_cannot_accept_none_interface(self):
        with pytest.raises(TypeError):
            @accept(None)
            @finalize
            class ModuleSample(Module.Runtime):
                pass

    def test_can_accept_multiple_interfaces(self):
        class MockAdditionalCorrectInterface(ModuleInterface):
            pass

        @accept(MockCorrectInterface, MockAdditionalCorrectInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        assert 2 == len(ModuleSample._ancestors)
        assert issubclass(ModuleSample._ancestors[0], MockCorrectInterface)
        assert issubclass(ModuleSample._ancestors[1], MockAdditionalCorrectInterface)

    def test_can_accept_modules_and_interfaces(self):
        @finalize
        class ModuleClassSample(Module.Runtime):
            pass

        @accept(MockCorrectInterface, ModuleClassSample)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        assert 2 == len(ModuleSample._ancestors)
        assert issubclass(ModuleSample._ancestors[0], MockCorrectInterface)
        assert issubclass(ModuleSample._ancestors[1], ModuleClassSample)

    @pytest.mark.asyncio
    async def test_cannot_read_config_with_wrong_all_submodules_interfaces(self):
        @accept(MockCorrectDependingInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        ModuleFactory.register('ModuleSample', ModuleSample)

        config_file = self.get_config_file('depending_modules_of_invalid_interface.yaml')
        with open(config_file) as config:
            config = config.read()
            with pytest.raises(Exception):
                await ConfigReader.read(config, ModuleFactory)

    @pytest.mark.asyncio
    async def test_cannot_read_config_with_wrong_single_submodule_interface(self):
        @accept(MockCorrectDependingInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        ModuleFactory.register('ModuleSample', ModuleSample)

        config_file = self.get_config_file('depending_modules_partially_invalid_interface.yaml')
        with open(config_file) as config:
            config = config.read()
            with pytest.raises(Exception):
                pipeline = await ConfigReader.read(config, ModuleFactory)

    @pytest.mark.asyncio
    async def test_can_read_config_with_correct_submodule_interfaces(self):
        @accept(MockCorrectDependingInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            def run(self, *args, **kwargs):
                pass

        ModuleFactory.register('ModuleSample', ModuleSample)
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')
        with open(config_file) as config:
            config = config.read()
            pipeline = await ConfigReader.read(config, ModuleFactory)

        assert 3 == len(pipeline.modules)
        assert issubclass(pipeline.modules[0].interface, MockCorrectDependingInterface)
        assert issubclass(pipeline.modules[1].interface, MockCorrectDependingInterface)
        assert pipeline.modules[2].input_modules == ['mod1', 'mod2']

    def test_can_produce_correct_interface(self):
        @produce(MockCorrectInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        assert issubclass(ModuleSample._produce_interface, MockCorrectInterface)

    def test_cannot_produce_multiple_interfaces(self):
        class MockAdditionalCorrectInterface(ModuleInterface):
            pass

        with pytest.raises(TypeError):
            @produce(MockCorrectInterface, MockAdditionalCorrectInterface)
            @finalize
            class ModuleSample(Module.Runtime):
                pass

    def test_cannot_produce_incorrect_interface(self):
        class MockIncorrectInterface:
            pass

        with pytest.raises(TypeError):
            @produce(MockIncorrectInterface)
            @finalize
            class ModuleSample(Module.Runtime):
                pass

    def test_cannot_produce_not_interface(self):
        @finalize
        class ModuleSampleDepending(Module.Runtime):
            pass

        with pytest.raises(TypeError):
            @produce(ModuleSampleDepending)
            @finalize
            class ModuleSample(Module.Runtime):
                pass

    def test_cannot_produce_null(self):
        with pytest.raises(TypeError):
            @produce(None)
            @finalize
            class ModuleSample(Module.Runtime):
                pass

    def test_cannot_produce_empty_interface(self):
        with pytest.raises(TypeError):
            @produce()
            @finalize
            class ModuleSample(Module.Runtime):
                pass
