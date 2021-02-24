from time import sleep

from magda.module import Module
from magda.decorators import register, accept, finalize, produce

from examples.modules.common import logger, log
from examples.interfaces.common import Request, Context
from examples.interfaces.string import StringInterface
from examples.interfaces.fn import LambdaInterface


@accept(StringInterface, LambdaInterface)
@produce(StringInterface)
@register('A')
@finalize
class ModuleA(Module.Runtime):
    SLEEP_TIME = 2

    def bootstrap(self):
        ctx: Context = self.context
        log(self, ctx.timer, '--- Created!')

    def teardown(self):
        ctx: Context = self.context
        log(self, ctx.timer, '--- Teardown!')

    @logger
    def run(self, data: Module.ResultSet, request: Request):
        # Access context
        ctx: Context = self.context

        # Access results from the previous modules
        #   `src` is a list of strings
        text = [t.fn() for t in data.of(LambdaInterface)]
        src = [t.data for t in data.of(StringInterface)] + text

        # Some heavy computational operations for example
        sleep(self.SLEEP_TIME)

        # Produce declared interface
        return StringInterface(
            f'{ctx.prefix} ('
            + ' + '.join(src)
            + (' = ' if len(src) else '')
            + f'{self.name}) {request.value}'
        )
