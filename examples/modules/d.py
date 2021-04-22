import asyncio

from magda.module import Module
from magda.decorators import register, accept, finalize, produce

from examples.modules.common import log
from examples.interfaces.common import Context
from examples.interfaces.fn import LambdaInterface


@accept(LambdaInterface)
@produce(LambdaInterface)
@register('D')
@finalize
class ModuleD(Module.Runtime):
    SLEEP_TIME = 1

    def bootstrap(self):
        ctx: Context = self.context
        log(self, ctx.timer, '--- Created!')
        log(self, ctx.timer, f"- Threshold = {self.parameters['threshold']}")

    def teardown(self):
        ctx: Context = self.context
        log(self, ctx.timer, '--- Teardown!')

    async def run(self, data: Module.ResultSet, *args, **kwargs):
        # Mark module's start
        ctx: Context = self.context
        log(self, ctx.timer, '- Start')

        # Access strings (results) from the previous modules
        src = [text.fn() for text in data.of(LambdaInterface)]

        # E.g. some IO operation (delay for example purposes)
        await asyncio.sleep(self.SLEEP_TIME)

        # Mark module's end
        log(self, ctx.timer, '- End')

        # Build output string and produce declared interface
        msg = '(' + ' + '.join(src) + (' = ' if len(src) else '') + f'{self.name})'
        return LambdaInterface(lambda: msg)
