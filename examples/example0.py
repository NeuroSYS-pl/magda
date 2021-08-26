import asyncio
from time import time

from magda.pipeline.sequential import SequentialPipeline

from examples.interfaces.common import Request, Context
from examples.modules import *


class ExampleSimpleSequential:
    @classmethod
    async def demo(cls):
        example = cls()
        await example.build()
        await example.run()

    async def build(self, prefix: str = '{CTX}'):
        builder = SequentialPipeline()
        builder.add_module(ModuleC('m1'))
        builder.add_module(ModuleB('m2'))
        builder.add_module(
            ModuleB('m3')
            .depends_on(builder.get_module('m2'))
        )
        builder.add_module(
            ModuleA('m4')
            .depends_on(builder.get_module('m3'))
            .depends_on(builder.get_module('m1'))
            .expose_result('final')
        )

        self.pipeline = await builder.build(lambda: Context(prefix))

    async def run(self):
        # Run one job and measure duration
        start = time()
        result, _ = await self.pipeline.run(Request('R'))
        end = time()

        # Close pipeline (and teardown modules)
        await self.pipeline.close()

        # Print results
        print(f'Duration = {end - start:.2f} s')
        print('Results:')
        for key, value in result.items():
            print(f'  {key}\t → {value}')


if __name__ == "__main__":
    asyncio.run(ExampleSimpleSequential.demo())
