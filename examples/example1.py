from time import time

from magda.pipeline.sequential import SequentialPipeline

from examples.interfaces.common import Request, Context
from examples.modules.a import ModuleA
from examples.modules.b import ModuleB
from examples.modules.c import ModuleC


class ExampleSequential:
    def build(self, prefix: str = '{CTX}'):
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

        self.pipeline = builder.build(lambda: Context(prefix))

    def run(self, value: str = 'R'):
        # Run 1 job and measure duration
        start = time()
        result = self.pipeline.run(Request(value))
        end = time()

        # Close pipeline (and teardown modules)
        self.pipeline.close()

        # Print results
        print(f'Duration = {end - start:.2f} s')
        print('Results:')
        for key, value in result.items():
            print(f'  {key}\t → {value}')


if __name__ == "__main__":
    example = ExampleSequential()
    example.build()
    result = example.run()
