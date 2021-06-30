import asyncio

from magda.module import Module
from magda.decorators import register, accept, finalize, produce

from examples.interfaces.fn import LambdaInterface


@accept(LambdaInterface)
@produce(LambdaInterface)
@register('ModuleB')
@finalize
class ModuleB(Module.Runtime):
    SLEEP_TIME = 1

    async def run(self, data: Module.ResultSet, *args, **kwargs):
        # Access strings (results) from the previous modules
        src = [text.fn() for text in data.of(LambdaInterface)]

        # E.g. some IO operation (delay for example purposes)
        await asyncio.sleep(self.SLEEP_TIME)

        # Build output string and produce declared interface
        msg = '(' + ' + '.join(src) + (' = ' if len(src) else '') + f'{self.name})'
        return LambdaInterface(lambda: msg)
