import asyncio
from time import time

from magda.pipeline import SequentialPipeline

from examples.interfaces.common import Context, Request
from examples.modules.a import ModuleA
from examples.modules.b import ModuleB
from examples.modules.c import ModuleC


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

        self.pipeline = await builder.build(lambda: Context(prefix))

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
        for index, result in enumerate(results):
            print(f' {index}:')
            for key, value in result.items():
                print(f'  {key}\t → {value}')


if __name__ == "__main__":
    asyncio.run(ExampleSequential.demo())
