import asyncio
from typing import List, Tuple, Callable

from magda.module import Module


def wrap_into_result(result, name='', src_class=None, expose=None):
    interface = result.__class__
    return Module.Result(result=result, interface=interface, name=name, src_class=src_class, expose=expose)


def wrap_single_object_into_resultset(obj, name='', src_class=None, expose=None):
    result = wrap_into_result(result=obj, name=name, src_class=src_class, expose=expose)
    return Module.ResultSet([result])


def wrap_data_into_resultset(arg_names: List[str], *args, **kwargs) -> Tuple[tuple, dict]:
    """
    Inspects given arguments and wraps argument called 'data' into Module.ResultSet.
    """    
    if 'data' in kwargs:
        kwargs['data'] = wrap_single_object_into_resultset(kwargs['data'])
        return args, kwargs

    if 'data' in arg_names:
        remaining_arg_names = list(filter(lambda x: x not in kwargs.keys(), arg_names))
        data_index = remaining_arg_names.index('data')
        args_list = list(args)
        args_list[data_index] = wrap_single_object_into_resultset(args_list[data_index])
        return tuple(args_list), kwargs

    # run does not expect 'data' argument and it has not been given
    return args, kwargs


async def call_async_or_sync_func(func: Callable, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)