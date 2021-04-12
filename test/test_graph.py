import pytest

from magda.pipeline.sequential import SequentialPipeline
from magda.module.module import Module
from magda.decorators.accepting import accept
from magda.decorators.finalizing import finalize
from magda.exceptions import DisjointGraphException, CyclicDependenciesException


@accept(self=True)
@finalize
class SkipModule(Module.Runtime):
    def run(self, *args, **kwargs):
        return 'test module'


class TestGraph:
    @pytest.mark.asyncio
    async def test_should_fail_on_not_connected_graph(self):
        builder = SequentialPipeline()
        builder.add_module(SkipModule('A'))
        builder.add_module(
            SkipModule('B')
            .depends_on(builder.get_module('A'))
        )
        builder.add_module(
            SkipModule('C')
            .depends_on(builder.get_module('A'))
            .depends_on(builder.get_module('B'))
        )
        builder.add_module(
            SkipModule('D')
        )
        with pytest.raises(DisjointGraphException):
            results = await builder.build()

    @pytest.mark.asyncio
    async def test_should_not_fail_on_graph_without_cycle(self):
        builder = SequentialPipeline()
        builder.add_module(SkipModule('A'))
        builder.add_module(
            SkipModule('B')
            .depends_on(builder.get_module('A'))
        )
        builder.add_module(
            SkipModule('C')
            .depends_on(builder.get_module('B'))
        )
        builder.add_module(
            SkipModule('D')
            .depends_on(builder.get_module('C'))
        )

        pipeline = await builder.build()
        assert 4 == len(pipeline.modules)

    @pytest.mark.asyncio
    async def test_should_not_fail_on_branched_graph_without_cycle(self):
        builder = SequentialPipeline()
        builder.add_module(SkipModule('A'))
        builder.add_module(
            SkipModule('B')
            .depends_on(builder.get_module('A'))
        )
        builder.add_module(
            SkipModule('C')
            .depends_on(builder.get_module('A'))
        )
        builder.add_module(
            SkipModule('D')
            .depends_on(builder.get_module('B'))
            .depends_on(builder.get_module('C'))
        )

        pipeline = await builder.build()
        assert 4 == len(pipeline.modules)

    @pytest.mark.asyncio
    async def test_should_fail_on_simple_cycle(self):
        builder = SequentialPipeline()
        module_a = SkipModule('A')
        module_b = SkipModule('B')
        module_a.depends_on(module_b)
        module_b.depends_on(module_a)
        builder.add_module(module_a)
        builder.add_module(module_b)

        with pytest.raises(CyclicDependenciesException):
            await builder.build()

    @pytest.mark.asyncio
    async def test_should_fail_on_long_cycle(self):
        builder = SequentialPipeline()
        module_a = SkipModule('A')
        module_side_a = SkipModule('side_A')
        module_b = SkipModule('B')
        module_c = SkipModule('C')
        module_d = SkipModule('D')
        module_side_d = SkipModule('side_D')
        module_e = SkipModule('E')
        module_f = SkipModule('F')
        module_g = SkipModule('G')
        module_side_g = SkipModule('side_G')

        # circular dependency
        module_b.depends_on(module_a)
        module_c.depends_on(module_b)
        module_d.depends_on(module_c)
        module_e.depends_on(module_d)
        module_f.depends_on(module_e)
        module_g.depends_on(module_f)
        module_a.depends_on(module_g)
        module_side_a.depends_on(module_a)
        module_side_d.depends_on(module_d)
        module_side_g.depends_on(module_g)

        builder.add_module(module_a)
        builder.add_module(module_b)
        builder.add_module(module_c)
        builder.add_module(module_d)
        builder.add_module(module_e)
        builder.add_module(module_f)
        builder.add_module(module_g)
        builder.add_module(module_side_a)
        builder.add_module(module_side_d)
        builder.add_module(module_side_g)

        with pytest.raises(CyclicDependenciesException):
            await builder.build()

    @pytest.mark.asyncio
    async def test_should_fail_on_multiple_cycles(self):
        builder = SequentialPipeline()
        module_a = SkipModule('A')
        module_side_a = SkipModule('side_A')
        module_b = SkipModule('B')
        module_c = SkipModule('C')
        module_d = SkipModule('D')
        module_side_d = SkipModule('side_D')
        module_e = SkipModule('E')
        module_f = SkipModule('F')
        module_g = SkipModule('G')
        module_side_g = SkipModule('side_G')

        # circular dependency with 4 additional side cycles
        module_b.depends_on(module_a)
        module_c.depends_on(module_b)
        module_d.depends_on(module_c)
        module_e.depends_on(module_d)
        module_f.depends_on(module_e)
        module_g.depends_on(module_f)
        module_a.depends_on(module_g)
        # additional cycle 1
        module_side_a.depends_on(module_a)
        module_c.depends_on(module_side_a)
        # additional cycle 2
        module_side_d.depends_on(module_d)
        module_g.depends_on(module_side_d)
        # additional cycle 3
        module_side_g.depends_on(module_g)
        module_b.depends_on(module_side_g)
        # additional cycle 4
        module_g.depends_on(module_side_g)

        builder.add_module(module_a)
        builder.add_module(module_b)
        builder.add_module(module_c)
        builder.add_module(module_d)
        builder.add_module(module_e)
        builder.add_module(module_f)
        builder.add_module(module_g)
        builder.add_module(module_side_a)
        builder.add_module(module_side_d)
        builder.add_module(module_side_g)

        with pytest.raises(CyclicDependenciesException):
            await builder.build()
