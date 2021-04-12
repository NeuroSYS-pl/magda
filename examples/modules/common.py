from time import time
from magda.module import Module


def log(ref: Module.Runtime, t0: float, msg: str):
    print(f'{ref.__class__.__name__}::{ref.name} [{time() - t0:8.3f}] {msg}')
