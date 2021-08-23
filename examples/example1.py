import asyncio
import logging
from time import time

from magda.pipeline.sequential import SequentialPipeline
from magda.utils import MagdaLogger

from examples.interfaces.common import Context, Request
from examples.modules import *


# Enable logging
logging.basicConfig()
logging.getLogger('magda').setLevel(logging.INFO)


class ExampleSequential:
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

        self.pipeline = await builder.build(
            context=lambda: Context(prefix),
            logger=MagdaLogger.Config(
                output=MagdaLogger.Config.Output.LOGGING,
            ),
        )

    async def run(self, value: str = 'R', n_jobs: int = 3):
        # Run jobs and measure duration
        start = time()
        results = await asyncio.gather(*[
            asyncio.create_task(
                self.pipeline.run(Request(value=f'{value}{i}'))
            )
            for i in range(n_jobs)
        ])
        end = time()

        # Close pipeline and teardown modules
        await self.pipeline.close()

        # Print results
        print(f'Duration = {end - start:.2f} s')
        print('Results:')
        for index, (result, _) in enumerate(results):
            print(f' {index}:')
            for key, value in result.items():
                print(f'  {key}\t → {value}')


if __name__ == "__main__":
    asyncio.run(ExampleSequential.demo())
