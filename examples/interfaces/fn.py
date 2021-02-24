from dataclasses import dataclass
from typing import Callable

from magda.module import Module


@dataclass(frozen=True)
class LambdaInterface(Module.Interface):
    fn: Callable[[], str]
