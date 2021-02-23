from __future__ import annotations

from magda.module.factory import ModuleFactory
from magda.decorators.common import module_typeguard


def register(module_type):
    def wrapper(module_ref):
        module_typeguard(module_ref)
        ModuleFactory.register(module_type, module_ref)
        return module_ref
    return wrapper
