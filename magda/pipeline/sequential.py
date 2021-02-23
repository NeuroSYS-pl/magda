from __future__ import annotations

from warnings import warn
from typing import List, Dict

from magda.pipeline.base import BasePipeline
from magda.pipeline.graph import Graph
from magda.module.module import Module
from magda.exceptions import ClosedPipelineException


class SequentialPipeline(BasePipeline):
    """ Synchronous processing pipeline """

    class Runtime(BasePipeline.Runtime):
        """ Synchronous pipeline runner """
        def __init__(self, graph: Graph, context=None, shared_parameters=None):
            super().__init__(context, shared_parameters)
            self.graph = graph
            self._is_closed = False

        @property
        def modules(self) -> List[Module]:
            return self.graph.modules

        @property
        def closed(self) -> bool:
            return self._is_closed

        def close(self):
            self._is_closed = True
            self.graph.teardown()

        def run(self, request=None, is_regular_runtime=True) -> Dict[str, Module.Result]:
            if self._is_closed:
                raise ClosedPipelineException()
            results = self.graph.run(request=request, is_regular_runtime=is_regular_runtime)
            return self.parse_results(results)

        def process(self, request=None) -> Dict[str, Module.Result]:
            return self.run(request=request, is_regular_runtime=False)

    def build(self, context=None, shared_parameters=None) -> SequentialPipeline.Runtime:
        self.validate()
        if any([m.group is not None for m in self.modules]):
            msg = ', '.join([
                f'{m.name} ({m.__class__.__name__})'
                for m in self.modules
                if m.group is not None
            ])
            warn(f'The property "group" for modules: ${msg} will be ignored!')

        self._mark_and_validate_modules(modules=self.modules)

        modules = [module.build(context, shared_parameters) for module in self.modules]

        graph = Graph(modules)
        return self.Runtime(graph, context, shared_parameters)

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
