from __future__ import annotations

from typing import List, Optional, Any, Dict, Union

from magda.module.base import BaseModule
from magda.module.runtime import ModuleRuntime
from magda.module.interface import ModuleInterface
from magda.module.aggregate import ModuleAggregate
from magda.module.results import Result, ResultSet


class Module(BaseModule):
    """ Generic Module class """
    _ancestors = []
    _is_exposed: bool = False
    _exposed_name: Optional[str] = None
    _produce_interface: Optional[ModuleInterface] = None
    _derived_class: ModuleRuntime = None
    _is_regular_module: bool = True
    _parameters: Dict[str, Any] = {}

    Runtime = ModuleRuntime
    Interface = ModuleInterface
    Aggregate = ModuleAggregate

    Result = Result
    ResultSet = ResultSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._input_modules = []
        self._output_modules = []

    @property
    def output_modules(self) -> List[Module]:
        return self._output_modules

    @property
    def input_modules(self) -> List[Module]:
        return self._input_modules

    @property
    def exposed(self) -> Optional[str]:
        if self._is_exposed:
            return self.name if self._exposed_name is None else self._exposed_name
        return None

    @property
    def is_regular_module(self) -> bool:
        return self._is_regular_module

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters

    @is_regular_module.setter
    def is_regular_module(self, is_regular_module):
        self._is_regular_module = is_regular_module

    def _connect_to(self, module: Module):
        self._output_modules.append(module.name)

    def depends_on(self, module: Module) -> Module:
        if module:
            if module._produce_interface in self._ancestors or module.__class__ in self._ancestors:
                self._input_modules.append(module.name)
                module._connect_to(self)
            else:
                valid_modules = ', '.join([
                    m.Runtime.__name__
                    for m in self._ancestors
                    if issubclass(m, Module)
                ])
                valid_interfaces = ', '.join([
                    i.__name__
                    for i in self._ancestors
                    if issubclass(i, Module.Interface)
                ])
                parent = f'({module.name}: {module._derived_class.__name__})'
                child = f'({self.name}: {self._derived_class.__name__})'
                raise Exception(
                    f'Invalid connection: {parent} -> {child}! Valid ancestors:\n'
                    f' + Modules: [{valid_modules}]\n'
                    f' + Interfaces: [{valid_interfaces}]'
                )
            return self
        else:
            raise TypeError("Dependent module does not exist in the pipeline")

    def set_parameters(self, parameters) -> Module:
        if isinstance(parameters, dict):
            self._parameters = parameters
            return self
        else:
            raise TypeError(f'Parameters must be of type dict but were of type: {type(parameters)}')

    def expose_result(self, name: Optional[str] = None, *, enable: bool = True) -> Module:
        self._exposed_name = name
        self._is_exposed = enable
        return self

    def build(self, *, context: Any = None, shared_parameters: Any = None):
        return self._derived_class(
            name=self.name,
            group=self.group,
            input_modules=self.input_modules,
            output_modules=self.output_modules,
            exposed=self.exposed,
            interface=self._produce_interface,
            context=context,
            shared_parameters=shared_parameters,
            is_regular_module=self.is_regular_module,
            parameters=self._parameters,
        )
