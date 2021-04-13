from __future__ import annotations
import asyncio
from typing import Optional

import ray

from magda.module.base import BaseModuleRuntime
from magda.module.results import ResultSet, Result


class ModuleRuntime(BaseModuleRuntime):
    def __init__(
        self,
        *,
        name,
        group,
        input_modules,
        output_modules,
        exposed,
        interface,
        parameters,
        context,
        shared_parameters,
        is_regular_module,
    ):
        super().__init__(name, group)
        self._input_modules = input_modules
        self._output_modules = output_modules
        self._exposed = exposed
        self._interface = interface
        self._context = context
        self._shared_parameters = shared_parameters
        self._is_regular_module = is_regular_module
        self._parameters = parameters

    async def _on_bootstrap(self):
        if callable(self._context):
            self._context = self._context()

        if asyncio.iscoroutinefunction(self.bootstrap):
            await self.bootstrap()
        else:
            self.bootstrap()

    def bootstrap(self):
        """ Bootstrap module on target device """
        pass

    def teardown(self):
        """ Teardown module on target device """
        pass

    def run(self, data: ResultSet, **kwargs):
        """ Request Run """
        raise NotImplementedError

    @property
    def output_modules(self):
        return self._output_modules

    @property
    def input_modules(self):
        return self._input_modules

    @property
    def exposed(self) -> Optional[str]:
        return self._exposed

    @property
    def interface(self):
        return self._interface

    @property
    def context(self):
        return self._context

    @property
    def is_regular_module(self) -> bool:
        return self._is_regular_module

    @property
    def parameters(self) -> dict:
        return self._parameters

    @property
    def shared_parameters(self) -> dict:
        return self._shared_parameters
