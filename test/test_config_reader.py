import pytest
from pathlib import Path

from magda.module.module import Module
from magda.module.factory import ModuleFactory
from magda.pipeline.sequential import SequentialPipeline
from magda.config_reader import ConfigReader
from magda.decorators import finalize, accept, produce
from magda.exceptions import (WrongParametersStructureException,
                              WrongParameterValueException, ConfiguartionFileException)


class MockTestInterface(Module.Interface):
    pass


class TestConfigReader:

    def get_config_file(self, config_name):
        return Path(__file__).parent / 'test_configs' / config_name

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_with_nested_structure(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')
        incorrect_parameters = {'ARG1': 'correct', 'ARG2': {'ARG3': 'incorrect'}}

        with open(config_file) as config:
            config = config.read()
            with pytest.raises(WrongParameterValueException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_with_incorrect_values(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')

        incorrect_parameters = {'ARG1': 'correct', 'ARG2': MockTestInterface}
        with open(config_file) as config:
            config = config.read()
            with pytest.raises(WrongParameterValueException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_other_than_dictionary(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')

        incorrect_parameters = [{'ARG1': 'value1'}, {'ARG2': 'value2'}]
        with open(config_file) as config:
            config = config.read()
            with pytest.raises(WrongParametersStructureException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_with_wrong_dict_keys(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')

        incorrect_parameters = {MockTestInterface: 'value1', 2: 'value2'}
        with open(config_file) as config:
            config = config.read()
            with pytest.raises(WrongParameterValueException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_pass_with_correct_variables_in_config(self):

        @produce(MockTestInterface)
        @finalize
        class DependingModule(Module.Runtime):
            def run(self, *args, **kwargs):
                pass

        @accept(MockTestInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        ModuleFactory.register('ModuleSample', ModuleSample)
        ModuleFactory.register('DependingModule', DependingModule)

        config_file = self.get_config_file('correctly_parametrized_config.yaml')

        correct_parameters = {
            'TYPE_1': 'DependingModule',
            'NAME_2': 'mod2',
            'THRESHOLD': 0.2,
            'BIAS': 0.1,
            'group_name': 'group1'
        }

        with open(config_file) as config:
            config = config.read()
            pipeline = await ConfigReader.read(config, ModuleFactory, correct_parameters)

        assert 3 == len(pipeline.modules)
        assert issubclass(pipeline.modules[0].interface, MockTestInterface)
        assert issubclass(pipeline.modules[1].interface, MockTestInterface)
        assert pipeline.modules[2].input_modules == ['mod1', 'mod2']

    @pytest.mark.asyncio
    async def test_should_not_pass_with_excessive_variables_in_config(self):
        config_file_with_excessive_vars = self.get_config_file(
            'incorrectly_parametrized_config.yaml'
        )

        correct_parameters = {
            'NAME_2': 'mod2',
            'THRESHOLD': 0.2
        }

        with open(config_file_with_excessive_vars) as config:
            config = config.read()
            with pytest.raises(ConfiguartionFileException):
                await ConfigReader.read(
                    config,
                    ModuleFactory,
                    correct_parameters
                )
