from typing import List
from inspect import signature

from magda.testing.utils import wrap_data_into_resultset, call_async_or_sync_func
from magda.module.runtime import ModuleRuntime


class ModuleTestingWrapper:
    def __init__(self, module: ModuleRuntime):
        self.module: ModuleRuntime = module

    async def build(self, shared_parameters={}, context=None, call_bootstrap=True):
        self.module = await call_async_or_sync_func(self.module.build, context=context, shared_parameters=shared_parameters)

        if call_bootstrap:
            await call_async_or_sync_func(self.module.bootstrap)

        return self

    async def run(self, *args, **kwargs):
        arg_names = self._get_module_run_method_arg_names()
        args, kwargs = wrap_data_into_resultset(arg_names, *args, **kwargs)
        results = await call_async_or_sync_func(self.module.run, *args, **kwargs)
        return results

    async def close(self):
        await call_async_or_sync_func(self.module.teardown)

    def _get_module_run_method_arg_names(self) -> List[str]:
        sig = signature(self.module.run)
        return list(sig.parameters.keys())

