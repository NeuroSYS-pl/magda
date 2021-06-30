import asyncio
from dataclasses import dataclass

from magda.module import Module
from magda.decorators import register, accept, finalize, produce
from magda.utils.logger.logger import MagdaLogger

from examples.interfaces.common import Context
from examples.interfaces.fn import LambdaInterface


@accept(LambdaInterface)
@produce(LambdaInterface)
@register('ModuleD')
@finalize
class ModuleD(Module.Runtime):
    SLEEP_TIME = 1

    @dataclass
    class Parameters:
        threshold: float

    def bootstrap(self, logger: MagdaLogger):
        ctx: Context = self.context
        params = self.Parameters(**self.parameters)
        logger.info(f'Context.timer = {ctx.timer} | Threshold = {params.threshold}')

    async def run(self, data: Module.ResultSet, *args, **kwargs):
        # Access strings (results) from the previous modules
        src = [text.fn() for text in data.of(LambdaInterface)]

        # E.g. some IO operation (delay for example purposes)
        await asyncio.sleep(self.SLEEP_TIME)

        # Build output string and produce declared interface
        msg = '(' + ' + '.join(src) + (' = ' if len(src) else '') + f'{self.name})'
        return LambdaInterface(lambda: msg)
