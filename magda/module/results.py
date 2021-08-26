from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Any, Union, Iterable

from magda.module.base import BaseModule, BaseModuleRuntime
from magda.module.interface import ModuleInterface


ResultSetInput = Union[str, BaseModule, BaseModuleRuntime, ModuleInterface]


@dataclass(frozen=True)
class Result:
    """ Module output class """
    result: Any
    error: Any
    interface: ModuleInterface
    name: str
    src_class: BaseModule
    expose: Optional[str] = None

    def is_successful(self):
        return self.error is None


class ResultSet:
    """ Container Type for Module Results

    Basic usage: `has`, `filter`, `of` and `get`. Each of them accepts both string
    (referring to results `expose` name) and `Module` class or it's subclass
    (referring to that module results).

    The direct access to the results list is available via `.collection`.
    """
    def __init__(self, collection: Iterable[Result]):
        self._collection = list(collection)

    @property
    def collection(self) -> List[Result]:
        """ Direct access to underlaying results collection. """
        return self._collection.copy()

    def __len__(self) -> int:
        return len(self._collection)

    def has(self, src: ResultSetInput) -> bool:
        """ Return if results from specific modules are available """
        if isinstance(src, str):
            return any([r.expose == src for r in self._collection])
        elif issubclass(src, ModuleInterface):
            return any([r.interface is src for r in self._collection])
        elif issubclass(src, BaseModule):
            unified_src = src if issubclass(src, BaseModuleRuntime) else src._derived_class
            return any([r.src_class is unified_src for r in self._collection])
        raise KeyError(
            f'Invalid argument: {src}. '
            'Expecting string, Module or Module.Interface class.'
        )

    def filter(self, src: ResultSetInput) -> List[Result]:
        """ List results (with metadata) from specific modules """
        if isinstance(src, str):
            return [r for r in self._collection if r.expose == src]
        elif issubclass(src, ModuleInterface):
            return [r for r in self._collection if r.interface is src]
        elif issubclass(src, BaseModule):
            unified_src = src if issubclass(src, BaseModuleRuntime) else src._derived_class
            return [r for r in self._collection if r.src_class is unified_src]
        raise KeyError(
            f'Invalid argument: {src}. '
            'Expecting string, Module or Module.Interface class.'
        )

    def of(self, src: ResultSetInput) -> List[Any]:
        """ List plain results (without metadata) from specific modules. """
        return [r.result for r in self.filter(src)]

    def get(self, src: ResultSetInput) -> Any:
        """ Return single plain result (without matadata) from specific module.
        Raises Exception when `src` refers to many results.
        """
        results = self.of(src)
        if len(results) > 1:
            raise Exception(
                f'{src} refers to many result. '
                'Expecting selector with only one solution.'
            )
        return results[0]

    def contains_invalid_result(self) -> bool:
        """ Returns whether there exists a Module Result that resulted in an exception """
        return any([res for res in self._collection if not res.is_successful()])

    def get_error_if_exists(self) -> Result:
        """ Returns a Result if any Module resulted in an exception,
        or returns None if there is no error Results.
        """
        return next((result for result in self.collection if not result.is_successful()), None)
