import os
import asyncio
from time import time

from magda.pipeline.parallel import init
from magda.module.factory import ModuleFactory
from magda.config_reader import ConfigReader

from examples.interfaces.common import Context, Request
from examples.modules.a import ModuleA
from examples.modules.b import ModuleB
from examples.modules.c import ModuleC


class ExampleParallelConfigReader:
    def __init__(self):
        init()

    @classmethod
    async def demo(cls):
        example = cls()
        await example.build()
        await example.run()

    def get_config_file(self, config_name):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        return os.path.join(__location__, 'configs', config_name)

    async def build(self, prefix: str = '{CTX}'):
        ModuleFactory.register('ModuleA', ModuleA)
        ModuleFactory.register('ModuleB', ModuleB)
        ModuleFactory.register('ModuleC', ModuleC)

        config_file = self.get_config_file('sample_config_parallel.yaml')
        with open(config_file, 'r') as config:
            config = config.read()
            self.pipeline = await ConfigReader.read(
                config,
                ModuleFactory,
                {'GROUP_M1': 'g1', 'GROUP_M4': 'g3'},
                context=lambda: Context(prefix)
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
        await asyncio.sleep(0.5)

        # Print results
        print(f'Duration = {end - start:.2f} s')
        print('Results:')
        for index, result in enumerate(results):
            print(f' {index}:')
            for key, value in result.items():
                print(f'  {key}\t → {value}')


if __name__ == "__main__":
    asyncio.run(ExampleParallelConfigReader.demo())
