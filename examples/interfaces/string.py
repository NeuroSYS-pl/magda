from dataclasses import dataclass
from magda.module import Module


@dataclass(frozen=True)
class StringInterface(Module.Interface):
    data: str
