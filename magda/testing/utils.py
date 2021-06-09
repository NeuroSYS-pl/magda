import asyncio
from typing import Callable

from magda.module import Module


def wrap_into_result(result, name='', src_class=None, expose=None):
    interface = result.__class__
    return Module.Result(
        result=result,
        interface=interface,
        name=name,
        src_class=src_class,
        expose=expose
    )


async def call_async_or_sync_func(func: Callable, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
