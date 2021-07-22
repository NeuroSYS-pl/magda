from __future__ import annotations

import asyncio
import inspect
from typing import Optional

from magda.module.base import BaseModuleRuntime


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

    async def _on_bootstrap(self, **kwargs):
        """ Helper function for calling bootstrap method.

        The main idea is to keep the method backward-compatible
        by removing all extra arguments, which were missing
        in the previous versions of MAGDA. Moreover, it supports
        both sync and async versions of the bootstraps.
        """
        if callable(self._context):
            self._context = self._context()

        signature = inspect.signature(self.bootstrap)
        parameters = [p.name for p in signature.parameters.values()]
        fn_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key in parameters
        }

        if asyncio.iscoroutinefunction(self.bootstrap):
            await self.bootstrap(**fn_kwargs)
        else:
            self.bootstrap(**fn_kwargs)

    async def _on_teardown(self, **kwargs):
        """ Helper function for calling teardown method.

        The main idea is to keep the method backward-compatible
        by removing all extra arguments, which were missing
        in the previous versions of MAGDA. Moreover, it supports
        both sync and async versions of the bootstraps.
        """
        signature = inspect.signature(self.teardown)
        parameters = [p.name for p in signature.parameters.values()]
        fn_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key in parameters
        }

        if asyncio.iscoroutinefunction(self.teardown):
            await self.teardown(**fn_kwargs)
        else:
            self.teardown(**fn_kwargs)

    def bootstrap(self, *args, **kwargs):
        """ Bootstrap module on target device """
        pass

    def teardown(self, *args, **kwargs):
        """ Teardown module on target device """
        pass

    def run(self, *args, **kwargs):
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
