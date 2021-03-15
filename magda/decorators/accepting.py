from __future__ import annotations
from typing import Iterable, Type

from magda.module.module import Module
from magda.decorators.common import module_typeguard


def accept(*ancestors: Iterable[Type[Module]], self=False):
    """ Set module valid ancestors. """
    def wrapper(module_ref):
        module_typeguard(module_ref)

        if not hasattr(module_ref, '_ancestors'):
            module_ref._ancestors = []

        for input_cls in ancestors:
            if not issubclass(input_cls, Module) and not issubclass(input_cls, Module.Interface):
                raise TypeError('The provided argument is not a Module or Module interface class!')
            module_ref._ancestors += [input_cls]

        if self:
            module_ref._ancestors += [module_ref]

        return module_ref

    return wrapper
