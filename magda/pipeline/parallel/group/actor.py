from __future__ import annotations

from uuid import UUID
from typing import List

import ray

from magda.module.module import Module
from magda.pipeline.graph import Graph
from magda.pipeline.parallel.future_result import FutureResult


@ray.remote
class Actor:
    def __init__(self, name, state_type, modules: List[Module]):
        self.name = name
        self.state_type = state_type
        self.graph = Graph(modules)

    async def bootstrap(self):
        await self.graph.bootstrap()

    async def run(self, job_id: UUID, request, results=[], is_regular_runtime=True):
        return FutureResult(
            job=job_id,
            group=self.name,
            result=await self.graph.run(
                request,
                results,
                is_regular_runtime=is_regular_runtime,
            ),
        )

    async def teardown(self):
        await self.graph.teardown()
