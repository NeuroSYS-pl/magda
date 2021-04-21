import os
import pytest

from magda.module.module import Module
from magda.module.factory import ModuleFactory
from magda.module.interface import ModuleInterface
from magda.pipeline.sequential import SequentialPipeline
from magda.config_reader import ConfigReader
from magda.decorators import finalize
from magda.decorators.accepting import accept
from magda.decorators.producing import produce
from magda.exceptions import WrongParametersStructureException, \
    WrongParameterValueException, ConfiguartionFileException


class MockCorrectDependingInterface(ModuleInterface):
    pass


class TestConfigReader:

    def setup_method(self, method):
        @produce(MockCorrectDependingInterface)
        @finalize
        class ModuleDependingCorrect(Module.Runtime):
            def run(self, *args, **kwargs):
                pass

        ModuleFactory.unregister()
        ModuleFactory.register('ModuleDependingCorrect', ModuleDependingCorrect)

    def teardown_method(self, method):
        ModuleFactory.unregister()

    def get_config_file(self, config_name):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )

        return os.path.join(__location__, 'test_configs', config_name)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_with_nested_structure(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')
        incorrect_parameters = {'ARG1': 'correct', 'ARG2': {'ARG3': 'incorrect'}}

        with open(config_file) as config:
            with pytest.raises(WrongParameterValueException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_with_incorrect_values(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')

        incorrect_parameters = {'ARG1': 'correct', 'ARG2': MockCorrectDependingInterface}
        with open(config_file) as config:
            with pytest.raises(WrongParameterValueException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_other_than_dictionary(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')

        incorrect_parameters = [{'ARG1': 'value1'}, {'ARG2': 'value2'}]
        with open(config_file) as config:
            with pytest.raises(WrongParametersStructureException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_not_read_config_parameters_with_wrong_dict_keys(self):
        config_file = self.get_config_file('depending_modules_of_correct_interface.yaml')

        incorrect_parameters = {MockCorrectDependingInterface: 'value1', 2: 'value2'}
        with open(config_file) as config:
            config = config.read()
            with pytest.raises(WrongParameterValueException):
                await ConfigReader.read(config, ModuleFactory, incorrect_parameters)

    @pytest.mark.asyncio
    async def test_should_pass_with_correct_variables_in_config(self):
        @accept(MockCorrectDependingInterface)
        @finalize
        class ModuleSample(Module.Runtime):
            pass

        ModuleFactory.register('ModuleSample', ModuleSample)

        config_file = self.get_config_file('correctly_parametrized_config.yaml')

        correct_parameters = {
            'TYPE_1': 'ModuleDependingCorrect',
            'NAME_2': 'mod2',
            'THRESHOLD': 0.2,
            'BIAS': 0.1,
            'group_name': 'group1'
        }

        with open(config_file) as config:
            config = config.read()
            pipeline = await ConfigReader.read(config, ModuleFactory, correct_parameters)

        assert 3 == len(pipeline.modules)
        assert issubclass(pipeline.modules[0].interface, MockCorrectDependingInterface)
        assert issubclass(pipeline.modules[1].interface, MockCorrectDependingInterface)
        assert pipeline.modules[2].input_modules == ['mod1', 'mod2']

    @pytest.mark.asyncio
    async def test_should_not_pass_with_redundant_variables_in_config(self):
        config_file_with_redundant_vars = self.get_config_file(
            'incorrectly_parametrized_config.yaml'
        )

        correct_parameters = {
            'TYPE_1': 'ModuleDependingCorrect',
            'NAME_2': 'mod2',
            'THRESHOLD': 0.2
        }

        with open(config_file_with_redundant_vars) as config:
            config = config.read()
            with pytest.raises(ConfiguartionFileException):
                await ConfigReader.read(
                    config,
                    ModuleFactory,
                    correct_parameters
                )
