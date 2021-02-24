from time import time
from functools import wraps

from magda.module import Module

from examples.interfaces.common import Context


def log(ref: Module.Runtime, t0: float, msg: str):
    print(f'{ref.__class__.__name__}::{ref.name} [{time() - t0:8.3f}] {msg}')


def logger(fn):
    @wraps(fn)
    def wrapper(ref: Module.Runtime, *args, **kwargs):
        ctx: Context = ref.context
        log(ref, ctx.timer, '- Start')
        output = fn(ref, *args, **kwargs)
        log(ref, ctx.timer, '- End')
        return output
    return wrapper
