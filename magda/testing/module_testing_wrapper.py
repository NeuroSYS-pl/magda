from __future__ import annotations
from typing import Any

from magda.module.results import ResultSet
from magda.module.runtime import ModuleRuntime
from magda.testing.utils import wrap_into_result, call_async_or_sync_func


class ModuleTestingWrapper:
    def __init__(self, module: ModuleRuntime):
        self.module: ModuleRuntime = module
        self._request: Any = None
        self._data: ResultSet = None

    async def build(self, shared_parameters={}, context=None, call_bootstrap=True):
        self.module = await call_async_or_sync_func(
            self.module.build,
            context=context,
            shared_parameters=shared_parameters
        )

        if call_bootstrap:
            await call_async_or_sync_func(self.module.bootstrap)

        return self

    def request(self, request: Any) -> ModuleTestingWrapper:
        self._request = request
        return self

    def data(self, *data) -> ModuleTestingWrapper:
        results = list(map(wrap_into_result, data))
        self._data = ResultSet(results)
        return self

    async def run(self):
        results = await call_async_or_sync_func(
            self.module.run,
            data=self._data,
            request=self._request
        )
        return results

    async def close(self):
        await call_async_or_sync_func(self.module.teardown)
