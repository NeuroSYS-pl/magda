from __future__ import annotations

from magda.module.module import Module


def module_typeguard(module_ref):
    if not issubclass(module_ref, Module):
        if issubclass(module_ref, Module.Runtime):
            raise TypeError(
                'Cannot decorate Module.Runtime class. '
                'Check decorators order: the @finalize '
                'must be first from the bottom!'
            )
        else:
            raise TypeError('The decorated class is not a Module!')
