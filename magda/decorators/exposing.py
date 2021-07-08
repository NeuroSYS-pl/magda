from __future__ import annotations

from typing import Optional
from magda.decorators.common import module_typeguard


def expose(name: Optional[str] = None):
    def wrapper(module_ref):
        module_typeguard(module_ref)
        module_ref._exposed_name = name
        module_ref._is_exposed = True
        return module_ref
    return wrapper
