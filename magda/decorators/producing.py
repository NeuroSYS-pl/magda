from __future__ import annotations

from magda.module.module import Module
from magda.decorators.common import module_typeguard


def produce(interface_class: Module.Interface):
    if not issubclass(interface_class, Module.Interface):
        raise TypeError(
            f'Interface {interface_class} '
            'is not subclass of Module.Interface'
        )

    def wrapper(module_ref: Module):
        module_typeguard(module_ref)
        module_ref._produce_interface = interface_class
        return module_ref

    return wrapper
