from __future__ import annotations

from uuid import UUID
from typing import List

import ray

from magda.module.module import Module
from magda.pipeline.graph import Graph
from magda.pipeline.parallel.future_result import FutureResult
from magda.utils.logger import MagdaLogger


@ray.remote
class Actor:
    def __init__(self, name, state_type, modules: List[Module]):
        self.name = name
        self.state_type = state_type
        self.graph = Graph(modules)
        self._logger = None

    async def bootstrap(self, logger: MagdaLogger):
        self._logger = logger
        await self.graph.bootstrap(self._logger)

    async def run(self, job_id: UUID, request, results=[], is_regular_runtime=True):
        result = await self.graph.run(request, results, is_regular_runtime)
        return FutureResult(
            job=job_id,
            group=self.name,
            result=result,
        )

    async def teardown(self):
        await self.graph.teardown()
