from __future__ import annotations

from abc import ABCMeta
from magda.module.module import Module


def finalize(module_ref):
    if not issubclass(module_ref, Module.Runtime):
        raise TypeError('Cannot finalize not a Module.Runtime class!')

    if hasattr(module_ref, '_ancestors'):
        ancestors = module_ref._ancestors
        del module_ref._ancestors
    else:
        ancestors = []

    class ModuleBuilderMeta(ABCMeta):
        def __repr__(self) -> str:
            return f'<class {module_ref.__name__}.Builder>'

    class ModuleBuilder(Module, metaclass=ModuleBuilderMeta):
        _ancestors = ancestors
        _derived_class = module_ref
        _is_regular_module = True if not issubclass(module_ref, Module.Aggregate) else False

        def __repr__(self) -> str:
            return f'<{module_ref.__name__}.Builder object>'

    return ModuleBuilder
