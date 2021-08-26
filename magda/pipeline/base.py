from __future__ import annotations

from collections import Counter
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Dict, Tuple, Any, Optional

from magda.module.module import Module
from magda.pipeline.graph_validator import GraphValidator


class BasePipelineMeta(ABCMeta):
    _counter = 0

    @property
    def idx(self):
        idx, self._counter = self._counter, self._counter + 1
        return idx


class BasePipeline(metaclass=BasePipelineMeta):
    class Runtime(ABC):
        def __init__(
            self,
            *,
            name: str,
            context: Any,
            shared_parameters: Any,
        ):
            self._name = name
            self._context = context
            self._shared_parameters = shared_parameters

        def parse_results(self, results: Module.ResultSet) -> Tuple[
            Optional[Dict[str, Any]],
            Optional[Exception]
        ]:
            if results.contains_invalid_result():
                raised_exception = results.get_error_if_exists()
                result_tuple = (None, raised_exception.error)
            else:
                result_tuple = ({
                    r.expose: r.result
                    for r in results.collection
                    if r.expose is not None
                }, None)
            return result_tuple

        @property
        def name(self) -> str:
            return self._name

        @property
        def context(self):
            return self._context

        @property
        def shared_parameters(self):
            return self._shared_parameters

        @abstractmethod
        async def run(self, request):
            raise NotImplementedError()

        @abstractmethod
        async def close(self):
            raise NotImplementedError()

        @property
        @abstractmethod
        def modules(self):
            raise NotImplementedError()

    def __init__(self, name: Optional[str] = None):
        self.modules: List[Module] = []
        self.name = (
            name if name is not None
            else f'Pipeline-{BasePipeline.idx}'
        )

    def add_module(self, module) -> BasePipeline:
        if not issubclass(type(module), Module):
            raise TypeError
        self.modules.append(module)
        return self

    def get_module(self, module_name):
        return next((mod for mod in self.modules if mod.name == module_name), None)

    def validate_names(self):
        module_names = [mod.name for mod in self.modules]
        duplicated_modules = [m for m, count in Counter(module_names).items() if count > 1]
        if duplicated_modules:
            raise Exception(
                "Modules must have unique names! "
                f"Found duplicated modules names: {duplicated_modules}"
            )

    def validate_exposition(self):
        exposed = [m.exposed for m in self.modules if m.exposed is not None]
        duplicated_expositions = [ex for ex, count in Counter(exposed).items() if count > 1]
        if duplicated_expositions:
            raise Exception(
                'Each module has to expose results with unique names! '
                f'Found duplicated registration for names: {duplicated_expositions}'
            )

    def validate(self):
        self.validate_names()
        self.validate_exposition()
        GraphValidator(self.modules).validate()

    @abstractmethod
    def build(self, context: Any, shared_parameters: Any) -> BasePipeline.Runtime:
        raise NotImplementedError()
