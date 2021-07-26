from __future__ import annotations

import asyncio
from typing import List

from magda.module.module import Module
from magda.pipeline.base import BasePipeline
from magda.pipeline.parallel.group import Group
from magda.pipeline.parallel.job import Job
from magda.pipeline.parallel.group.state_type import StateType
from magda.exceptions import ClosedPipelineException
from magda.utils.logger import MagdaLogger


class Runtime(BasePipeline.Runtime):
    def __init__(
        self,
        *,
        groups: List[Group.Runtime],
        logger_config: MagdaLogger.Config,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.groups = groups
        self._jobs: List[Job] = []
        self._is_closed = False
        self._idle_flag = asyncio.Event()
        self._idle_flag.set()
        self._logger = MagdaLogger.of(
            logger_config,
            pipeline=MagdaLogger.Parts.Pipeline(
                name=self.name,
                kind='ParallelPipeline',
            )
        )

    @property
    def context(self):
        return super().context

    @property
    def shared_parameters(self):
        return super().shared_parameters

    @property
    def modules(self) -> List[Module.Runtime]:
        return [
            module
            for group in self.groups
            for module in group.modules
        ]

    @property
    def jobs(self) -> List[Job]:
        return self._jobs

    @property
    def closed(self) -> bool:
        return self._is_closed

    async def _bootstrap(self):
        await asyncio.gather(*[
            group.bootstrap(self._logger)
            for group in self.groups
        ])

    async def close(self):
        self._is_closed = True
        await self._idle_flag.wait()
        await asyncio.gather(*[
            group.teardown()
            for group in self.groups
        ])

    def get_group(self, name: str) -> Group:
        return next(iter(filter(lambda group: group.name == name, self.groups)), None)

    def _filter_groups(self, is_regular_runtime=True):
        groups = list(self.groups)
        if is_regular_runtime:
            for group in self.groups:
                if (group.state_type == StateType.AGGREGATE and
                   not any([issubclass(type(mod), Module.Aggregate) for mod in group.modules])):
                    groups.remove(group)
        else:
            for group in self.groups:
                if group.state_type == StateType.REGULAR:
                    groups.remove(group)
        return groups

    async def run(self, request=None, is_regular_runtime=True):
        if self._is_closed:
            raise ClosedPipelineException

        groups = self._filter_groups(is_regular_runtime)
        job = Job(request, groups, is_regular_runtime)

        self._jobs.append(job)
        self._idle_flag.clear()

        results = await job.run()

        self._jobs.remove(job)
        if len(self._jobs) == 0:
            self._idle_flag.set()

        return self.parse_results(results)

    async def process(self, request=None):
        return await self.run(request=request, is_regular_runtime=False)
