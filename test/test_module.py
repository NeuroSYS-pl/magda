import pytest

from magda.module.module import Module
from magda.decorators.accepting import accept
from magda.decorators.finalizing import finalize


@finalize
class DependentModule(Module.Runtime):
    def run(self, data, **kwargs):
        pass


@accept(DependentModule)
@finalize
class ConnectedModule(Module.Runtime):
    def run(self, data, **kwargs):
        pass


@finalize
class MockModule(Module.Runtime):
    def run(self, data, **kwargs):
        pass


class TestModule:

    def test_module_init(self):
        connected_module_name = 'testName'
        connected_module = ConnectedModule(connected_module_name)

        assert len(connected_module.input_modules) == 0
        assert len(connected_module.output_modules) == 0
        assert connected_module.name == 'testName'

    def test_module_depends(self):
        connected_module_name = 'connectedName'
        connected_module = ConnectedModule(connected_module_name)

        dependent_module_name = 'dependentName'
        dependent_module = DependentModule(dependent_module_name)

        connected_module.depends_on(dependent_module)

        assert len(connected_module.input_modules) == 1

        input_module_name = connected_module.input_modules[0]
        assert input_module_name == dependent_module.name

    def test_module_is_connected_to(self):
        connected_module_name = 'connectedName'
        connected_module = ConnectedModule(connected_module_name)

        dependent_module_name = 'dependentName'
        dependent_module = DependentModule(dependent_module_name)

        connected_module.depends_on(dependent_module)

        assert len(dependent_module.output_modules) == 1

        output_module_name = dependent_module.output_modules[0]
        assert output_module_name == connected_module.name

    def test_module_concrete_module(self):
        run_output = 'run'
        concrete_name = 'ConcreteModule'

        @finalize
        class ConcreteModule(Module.Runtime):
            def run(self, **kwargs):
                return 'run'
        concrete_module = ConcreteModule('ConcreteModule').build()

        assert concrete_module.name == concrete_name
        assert concrete_module.run() == run_output

    def test_module_not_concrete_module_raises_run_error(self):
        test_name = 'TestName'

        @finalize
        class NotConcreteModule(Module.Runtime):
            pass
        NotConcreteModule._derived_class.__abstractmethods__ = set()
        test_module = NotConcreteModule(test_name).build()
        with pytest.raises(NotImplementedError):
            test_module.run(data=None)

    def test_module_is_aggregator(self):
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'process'
        test_module = AggregatorModule('test').build()
        assert not test_module.is_regular_module
        assert issubclass(type(test_module), Module.Aggregate)

    def test_module_is_regular(self):
        @finalize
        class RegularModule(Module.Runtime):
            def run(self, **kwargs):
                return 'run'
        test_module = RegularModule('test').build()
        assert test_module.is_regular_module
        assert \
            issubclass(type(test_module), Module.Runtime) \
            and \
            not issubclass(type(test_module), Module.Aggregate)

    def test_module_aggregator_state(self):
        @finalize
        class AggregatorModule(Module.Aggregate):
            def process(self, **kwargs):
                return 'process'
        test_module = AggregatorModule('test').build()
        assert test_module.state_size == 0
        assert test_module.state == []
        test_module.add_data(1)
        test_module.add_data(2)
        assert test_module.state_size == 2
        assert test_module.state == [1, 2]

    def test_module_parameters(self):
        parameters = {'param1': 1}

        module = MockModule('module_name')
        module.set_parameters(parameters)

        assert isinstance(module.parameters, dict)
        assert 'param1' in module.parameters
        assert module.parameters['param1'] == 1

    def test_module_parameters_default(self):
        module = MockModule('module_name')

        assert module.parameters is not None
        assert isinstance(module.parameters, dict)
        assert len(module.parameters) == 0

    def test_module_parameters_wrong_type_error(self):
        module = MockModule('module_name')

        with pytest.raises(TypeError):
            module.set_parameters([])
