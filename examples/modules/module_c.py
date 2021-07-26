from time import sleep

from magda.module import Module
from magda.decorators import register, accept, expose, finalize, produce

from examples.interfaces.string import StringInterface


@accept(StringInterface)
@produce(StringInterface)
@expose()
@register('ModuleC')
@finalize
class ModuleC(Module.Runtime):
    async def run(self, data: Module.ResultSet, *args, **kwargs):
        # Access strings (results) from the previous modules
        src = [t.data for t in data.of(StringInterface)]

        # Add delay for example purposes
        #   delay duration is taken from optional parameter `sleep`
        #   and is 2 seconds by default (if the parameter is not provided)
        sleep(self.parameters.get('sleep', 2))

        # Build output string and produce declared interface
        return StringInterface(
            '(' + ' + '.join(src) + (' = ' if len(src) else '') + f'{self.name})'
        )
