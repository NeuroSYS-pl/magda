from __future__ import annotations

from warnings import warn
from typing import Optional

from magda.module.module import Module


class ModuleFactory:
    module_references = {}

    @classmethod
    def register(cls, tag: str, ref):
        if not issubclass(ref, Module):
            raise TypeError('Cannot register not a Module class!')
        if not isinstance(tag, str):
            raise TypeError('Tag must be a string!')
        cls.module_references[tag] = ref

    @classmethod
    def unregister(cls, tag: Optional[str] = None):
        if tag is None:
            cls.module_references.clear()
        elif tag in cls.module_references:
            cls.module_references.pop(tag, None)
        else:
            warn(f"There is no such module in ModuleFactory as {tag}.")

    @classmethod
    def get(cls, tag: str) -> Module:
        return cls.module_references[tag]

    @classmethod
    def create(
        cls,
        name: str,
        module_type: str,
        module_group: Optional[str] = None
    ):
        if module_type not in cls.module_references:
            raise KeyError(f"'{module_type}' hasn't been registered in the ModuleFactory.")

        return cls.module_references[module_type](name, module_group)
