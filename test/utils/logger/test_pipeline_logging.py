from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from magda.module import Module, ModuleFactory
from magda.decorators import accept, finalize
from magda.pipeline import SequentialPipeline
from magda.config_reader import ConfigReader
from magda.utils.logger import MagdaLogger


MESSAGE = 'TestRun'


class PartialOutput:
    COLOR_REGEXP = r'\x1b'
    color = False

    def __init__(self, pattern):
        self.pattern = pattern

    def with_color(self) -> PartialOutput:
        self.color = True
        return self

    def __eq__(self, other: str):
        return (
            re.search(self.pattern, other) is not None
            and (re.search(self.COLOR_REGEXP, other) is not None) == self.color
        )

    def __str__(self) -> str:
        return self.pattern


@accept(self=True)
@finalize
class ModuleA(Module.Runtime):
    def run(self, logger: MagdaLogger, *args, **kwargs):
        logger.info(MESSAGE)
        return None


@pytest.mark.asyncio
class TestPipelineLogging:
    async def test_should_log_pipeline(self):
        mock = MagicMock()
        pipe_name = 'TestPipeline1'
        module1, module2 = ModuleA('TestModuleA1'), ModuleA('TestModuleA2')

        builder = SequentialPipeline(pipe_name)
        builder.add_module(module1)
        builder.add_module(module2.depends_on(module1))
        pipe = await builder.build(logger=MagdaLogger.Config(colors=False, output=mock))

        await pipe.run()

        assert mock.call_count == 6
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*BOOTSTRAP'))
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*BOOTSTRAP'))
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*RUN'))
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*RUN'))
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*{MESSAGE}'))
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*{MESSAGE}'))

    async def test_should_log_pipeline_from_config(self):
        mock = MagicMock()
        module1_name, module2_name = 'TestModuleA1', 'TestModuleA2'
        config_path = Path(__file__).parent / 'configs' / 'pipeline.yml'
        ModuleFactory.register('LoggerModuleA', ModuleA)

        with open(config_path) as config:
            pipe = await ConfigReader.read(
                config=config.read(),
                module_factory=ModuleFactory,
                config_parameters={"name1": module1_name, "name2": module2_name},
                logger=MagdaLogger.Config(colors=False, output=mock),
            )

        await pipe.run()

        assert mock.call_count == 6
        mock.assert_any_call(PartialOutput(f'{pipe.name}.*{module1_name}.*BOOTSTRAP'))
        mock.assert_any_call(PartialOutput(f'{pipe.name}.*{module2_name}.*BOOTSTRAP'))
        mock.assert_any_call(PartialOutput(f'{pipe.name}.*{module1_name}.*RUN'))
        mock.assert_any_call(PartialOutput(f'{pipe.name}.*{module2_name}.*RUN'))
        mock.assert_any_call(PartialOutput(f'{pipe.name}.*{module1_name}.*{MESSAGE}'))
        mock.assert_any_call(PartialOutput(f'{pipe.name}.*{module2_name}.*{MESSAGE}'))

    async def test_should_log_pipeline_with_colors(self):
        mock = MagicMock()
        pipe_name = 'TestPipeline1'
        module1, module2 = ModuleA('TestModuleA1'), ModuleA('TestModuleA2')

        builder = SequentialPipeline(pipe_name)
        builder.add_module(module1)
        builder.add_module(module2.depends_on(module1))
        pipe = await builder.build(logger=MagdaLogger.Config(output=mock))

        await pipe.run()

        assert mock.call_count == 6
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*BOOTSTRAP').with_color())
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*BOOTSTRAP').with_color())
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*RUN').with_color())
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*RUN').with_color())
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*{MESSAGE}').with_color())
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*{MESSAGE}').with_color())

    async def test_should_log_pipeline_without_events(self):
        mock = MagicMock()
        pipe_name = 'TestPipeline1'
        module1, module2 = ModuleA('TestModuleA1'), ModuleA('TestModuleA2')

        builder = SequentialPipeline(pipe_name)
        builder.add_module(module1)
        builder.add_module(module2.depends_on(module1))
        pipe = await builder.build(
            logger=MagdaLogger.Config(
                colors=False,
                log_events=False,
                output=mock,
            ),
        )

        await pipe.run()

        assert mock.call_count == 2
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module1.name}.*{MESSAGE}'))
        mock.assert_any_call(PartialOutput(f'{pipe_name}.*{module2.name}.*{MESSAGE}'))
