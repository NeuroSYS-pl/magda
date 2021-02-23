from __future__ import annotations

from typing import List

from magda.module.module import Module
from magda.pipeline.parallel.group.runtime import GroupRuntime


class Group:
    Runtime = GroupRuntime

    def __init__(
        self, name: str,
        *,
        replicas: int = 1,
        state_type=None,
        **options,
    ):
        self.name = name
        self.replicas = replicas
        self.options = options
        self._state_type = state_type

    def set_replicas(self, replicas: int) -> Group:
        self.replicas = replicas
        return self

    def set_options(self, **options) -> Group:
        self.options = options
        return self

    @property
    def state_type(self):
        return self._state_type

    @state_type.setter
    def state_type(self, state_type):
        self._state_type = state_type

    def build(
        self,
        modules: List[Module],
        dependent_modules: List[Module],
        dependent_modules_nonregular: List[Module],
    ) -> Group.Runtime:
        return self.Runtime(
            name=self.name,
            modules=modules,
            dependent_modules=dependent_modules,
            dependent_modules_nonregular=dependent_modules_nonregular,
            replicas=self.replicas,
            state_type=self.state_type,
            options=self.options,
        )
