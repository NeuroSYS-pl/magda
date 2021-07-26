from __future__ import annotations
from typing import List, Optional, Set

from magda.module.module import Module
from magda.pipeline.base import BasePipeline
from magda.pipeline.parallel.runtime import Runtime
from magda.pipeline.parallel.group import Group
from magda.pipeline.parallel.group.state_type import StateType
from magda.utils.logger import MagdaLogger


class ParallelPipeline(BasePipeline):
    Runtime = Runtime
    Group = Group

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._groups: List[Group] = []

    def add_group(self, group: Group) -> ParallelPipeline:
        self._groups.append(group)
        return self

    def _list_dependencies(self, module: Module) -> List[Module]:
        return [self.get_module(dep) for dep in module.input_modules]

    def _list_group_dependencies(self, group: str) -> Set[str]:
        return set([
            dep.group
            for m in self.modules
            for dep in self._list_dependencies(m)
            if m.group == group and dep.group != group
        ])

    async def build(
        self,
        context=None,
        shared_parameters=None,
        *,
        logger: Optional[MagdaLogger.Config] = None,
    ) -> Runtime:
        self.validate()
        if any([m.group is None for m in self.modules]):
            raise Exception('At least one module does not have a group property')

        self._mark_and_validate_modules(modules=self.modules)
        runtime_modules = [
            module.build(context=context, shared_parameters=shared_parameters)
            for module in self.modules
        ]

        required_groups = set([m.group for m in runtime_modules])
        defined_groups = set([g.name for g in self._groups])
        missing_groups = required_groups.difference(defined_groups)
        self._groups.extend([
            self.Group(name)
            for name in missing_groups
        ])

        non_pipeline_groups = [g.name for g in self._groups if g.name not in required_groups]
        if non_pipeline_groups:
            raise Exception(
                f"There are groups without any modules: {non_pipeline_groups}. "
                "Please make sure that all groups have at least one module in them."
            )

        self._mark_groups_state(self._groups, runtime_modules)

        runtime_groups: List[Group.Runtime] = []
        for group in self._groups:
            modules = [m for m in runtime_modules if m.group == group.name]
            dependent_modules_names = [m for module in modules for m in module.input_modules]
            dependent_modules = self._exclude_own_modules(
                [m for m in runtime_modules if m.name in dependent_modules_names],
                modules
            )
            dependent_modules_nonregular = self._exclude_own_modules(
                [m for m in dependent_modules if not m.is_regular_module],
                modules
            )
            runtime_group = group.build(
                modules=modules,
                dependent_modules=dependent_modules,
                dependent_modules_nonregular=dependent_modules_nonregular
            )
            runtime_groups.append(runtime_group)

        runtime = Runtime(
            name=self.name,
            groups=runtime_groups,
            context=context,
            shared_parameters=shared_parameters,
            logger_config=logger,
        )
        await runtime._bootstrap()
        return runtime

    @staticmethod
    def _exclude_own_modules(module_dependencies, modules):
        return set(module_dependencies).difference(set([mod for mod in modules]))

    def _mark_groups_state(self, groups, runtime_modules):
        for group in groups:
            group_modules = [m for m in runtime_modules if m.group == group.name]
            if all([m.is_regular_module for m in group_modules]):
                group.state_type = StateType.REGULAR
            elif all([not m.is_regular_module for m in group_modules]):
                group.state_type = StateType.AGGREGATE
            else:
                group.state_type = StateType.MIXED

    def _mark_and_validate_modules(self, modules):
        aggregate_modules = self._find_aggregate_modules(modules)
        if len(aggregate_modules) > 0:
            for agg_module in aggregate_modules:
                self._mark_aggregate(agg_module)
            self._validate_module_marking(modules)

    @staticmethod
    def _find_aggregate_modules(modules) -> Module:
        return [m for m in modules if issubclass(m._derived_class, Module.Aggregate)]

    def _mark_aggregate(self, module_start):
        if len(module_start.output_modules) > 0:
            module_output_refs = [
                self.get_module(module_name)
                for module_name in module_start.output_modules
            ]
            for module in module_output_refs:
                if module is not None:
                    module.is_regular_module = False
                    self._mark_aggregate(module)

    def _validate_module_marking(self, modules):
        modules_marked_not_runtime = [m for m in modules if not m.is_regular_module]
        for module in modules_marked_not_runtime:
            input_modules_flags = [
                self.get_module(input_module_name).is_regular_module
                for input_module_name in module.input_modules
            ]
            if self._has_multiple_items(input_modules_flags):
                raise Exception(f"Module '{module.name}' relies on both "
                                "regular and aggregate modules!")

    @staticmethod
    def _has_multiple_items(input_modules):
        return len(set(input_modules)) > 1
