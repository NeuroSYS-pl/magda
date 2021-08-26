import asyncio
from time import time
from pathlib import Path

from magda import ConfigReader
from magda.module.factory import ModuleFactory
from magda.utils.logger.logger import MagdaLogger

from examples.interfaces.common import Request, Context
from examples.modules import *


class ExampleSimpleSequentialConfigReader:
    @classmethod
    async def demo(cls):
        example = cls()
        await example.build()
        await example.run()

    def get_config_file(self, config_name):
        return Path(__file__).parent / 'configs' / config_name

    async def build(self, prefix: str = '{CTX}'):
        config_file = self.get_config_file('sample_config_sequential.yaml')
        with open(config_file, 'r') as config:
            config = config.read()
            config_params = {
                'THRESHOLD_1': 0.2,
                'THRESHOLD_2': 0.5,
            }

            self.pipeline = await ConfigReader.read(
                config,
                ModuleFactory,
                name='CustomName',
                config_parameters=config_params,
                context=lambda: Context(prefix),
                logger=MagdaLogger.Config(),
            )

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
    asyncio.run(ExampleSimpleSequentialConfigReader.demo())
