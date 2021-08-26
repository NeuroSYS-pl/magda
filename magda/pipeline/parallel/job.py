from __future__ import annotations

import asyncio
from magda import module
from uuid import uuid4
from enum import Enum, auto
from typing import List, Dict, Any

import ray

from magda.module.module import Module
from magda.pipeline.parallel.group import Group
from magda.pipeline.parallel.future_result import FutureResult


class Job:
    class GroupStatus(Enum):
        IDLE = auto()
        PROCESSING = auto()
        DONE = auto()
        CANCELLED = auto()

    def __init__(self, request: Any, groups: List[Group], is_regular_runtime: bool):
        self.uuid = uuid4()

        self._request = ray.put(request)
        self._groups = groups
        self._is_regular_runtime = is_regular_runtime
        self._output = asyncio.get_running_loop().create_future()
        self._results: Dict[str, Module.Result] = {}
        self._tasks: Dict[str, ray.ObjectRef] = {}
        self._status: Dict[str, Job.GroupStatus] = {
            group.name: Job.GroupStatus.IDLE
            for group in self._groups
        }

    @property
    def status(self) -> Dict[str, Job.GroupStatus]:
        return self._status.copy()

    @property
    def _ready_groups(self) -> List[Group]:
        return [
            group
            for group in self._groups
            if (self._status[group.name] == Job.GroupStatus.IDLE
                and group.fulfills(self._results.keys()))
        ]

    @property
    def _finished(self) -> bool:
        return all([
            self._status[group.name] in (Job.GroupStatus.DONE, Job.GroupStatus.CANCELLED)
            for group in self._groups
        ])

    async def _run_group(self, group: Group):
        if self._is_regular_runtime:
            module_dependencies = group.module_dependencies
        else:
            module_dependencies = group.module_dependencies_nonregular

        results = [
            result
            for name, result in self._results.items()
            if name in module_dependencies
        ]
        task = await group.run(self.uuid, self._request, results, self._is_regular_runtime)
        self._tasks[group.name] = task
        self._status[group.name] = Job.GroupStatus.PROCESSING

    async def run(self):
        for group in self._groups:
            dependencies = (
                group.dependencies
                if self._is_regular_runtime
                else group.dependencies_nonregular
            )

            if len(dependencies) == 0:
                await self._run_group(group)

        while not self._finished:
            done, _ = await asyncio.wait(
                fs=self._tasks.values(),
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in done:
                future: FutureResult = task.result()
                for module_result in future.result.collection:
                    self._results[module_result.name] = module_result

                self._status[future.group] = Job.GroupStatus.DONE
                del self._tasks[future.group]

                # Check for early error stopping
                if future.result.contains_invalid_result():
                    self._status = dict(
                        (k, Job.GroupStatus.CANCELLED)
                        if v in (Job.GroupStatus.IDLE, Job.GroupStatus.PROCESSING)
                        else (k, v)
                        for k, v in self._status.items()
                    )

            for group in self._ready_groups:
                await self._run_group(group)
        return Module.ResultSet(list(self._results.values()))
