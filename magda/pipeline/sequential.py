from __future__ import annotations

from warnings import warn
from typing import List, Dict, Optional

from magda.pipeline.base import BasePipeline
from magda.pipeline.graph import Graph
from magda.module.module import Module
from magda.exceptions import ClosedPipelineException
from magda.utils.logger import MagdaLogger


class SequentialPipeline(BasePipeline):
    """ Sequential processing pipeline """

    class Runtime(BasePipeline.Runtime):
        """ Sequential pipeline runner """
        def __init__(self, *, graph: Graph, logger_config: MagdaLogger.Config, **kwargs):
            super().__init__(**kwargs)
            self.graph = graph
            self._is_closed = False
            self._logger = MagdaLogger.of(
                logger_config,
                pipeline=MagdaLogger.Parts.Pipeline(
                    name=self.name,
                    kind='SequentialPipeline',
                ),
            )

        @property
        def modules(self) -> List[Module]:
            return self.graph.modules

        @property
        def closed(self) -> bool:
            return self._is_closed

        async def _bootstrap(self):
            await self.graph.bootstrap(self._logger)

        async def close(self):
            self._is_closed = True
            await self.graph.teardown()

        async def run(self, request=None, is_regular_runtime=True) -> Dict[str, Module.Result]:
            if self._is_closed:
                raise ClosedPipelineException()
            results = await self.graph.run(request=request, is_regular_runtime=is_regular_runtime)
            return self.parse_results(results)

        async def process(self, request=None) -> Dict[str, Module.Result]:
            return await self.run(request=request, is_regular_runtime=False)

    async def build(
        self,
        context=None,
        shared_parameters=None,
        *,
        logger: Optional[MagdaLogger.Config] = None,
    ) -> SequentialPipeline.Runtime:
        self.validate()
        if any([m.group is not None for m in self.modules]):
            msg = ', '.join([
                f'{m.name} ({m.__class__.__name__})'
                for m in self.modules
                if m.group is not None
            ])
            warn(f'The property "group" for modules: ${msg} will be ignored!')
        self._mark_and_validate_modules(modules=self.modules)

        modules = [
            module.build(context=context, shared_parameters=shared_parameters)
            for module in self.modules
        ]
        graph = Graph(modules)

        runtime = self.Runtime(
            graph=graph,
            name=self.name,
            context=context,
            shared_parameters=shared_parameters,
            logger_config=logger,
        )
        await runtime._bootstrap()
        return runtime

    def _mark_and_validate_modules(self, modules):
        aggregate_modules = self._find_aggregate_modules(modules)
        if len(aggregate_modules) > 0:
            for agg_module in aggregate_modules:
                self._mark_aggregate(agg_module)
            self._validate_module_marking(modules)

    def _find_aggregate_modules(self, modules) -> Module:
        return [m for m in modules if issubclass(m._derived_class, Module.Aggregate)]

    def _mark_aggregate(self, module_start):
        if len(module_start.output_modules) > 0:
            module_output_refs = [
                self.get_module(module_name)
                for module_name in module_start.output_modules
            ]
            for module in module_output_refs:
                module.is_regular_module = False
                self._mark_aggregate(module)

    def _validate_module_marking(self, modules):
        modules_marked_not_runtime = [m for m in modules if not m.is_regular_module]
        for module in modules_marked_not_runtime:
            if len(module.input_modules) >= 2:
                input_modules_flags = [
                    self.get_module(input_module_name).is_regular_module
                    for input_module_name in module.input_modules
                ]
                if False in input_modules_flags and True in input_modules_flags:
                    raise Exception(f'This module, named: {module.name} \
                                    relies on both regular and aggregate modules!')
