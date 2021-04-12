import asyncio
from time import sleep

import pytest
import ray

from magda.pipeline.parallel.group.actor_pool import ParallelActorPool


@ray.remote
class MultiplyActor:
    def __init__(self, factor: int = 2):
        self.factor = factor

    def run(self, data, delay, *args, **kwargs):
        sleep(delay)
        return self.factor * data


@pytest.fixture(scope='class')
def ray_context():
    ray.init(num_cpus=1)
    yield None
    ray.shutdown()


class TestActorPool:
    @pytest.mark.parametrize('actors', [1, 2, 5])
    @pytest.mark.asyncio
    async def test_can_create(self, actors, ray_context):
        pool = ParallelActorPool([
            MultiplyActor.remote()
            for _ in range(actors)
        ])
        assert pool.replicas == actors

    @pytest.mark.parametrize('runs,actors', [
        (1, 1),
        (3, 1),
        (1, 2),
        (2, 2),
        (5, 2),
        (1, 5),
        (5, 5),
        (8, 5),
    ])
    @pytest.mark.asyncio
    async def test_should_run(self, runs, actors, ray_context):
        pool = ParallelActorPool([
            MultiplyActor.remote()
            for _ in range(actors)
        ])
        await asyncio.gather(*[
            pool.run(data=0, delay=0.0001)
            for _ in range(runs)
        ])

    @pytest.mark.parametrize('score,runs,factor,actors', [
        (2, 1, 2, 1),
        (9, 3, 3, 1),
        (2, 1, 2, 2),
        (6, 2, 3, 2),
        (15, 5, 3, 2),
        (4, 1, 4, 5),
        (10, 5, 2, 5),
        (24, 8, 3, 5),
    ])
    @pytest.mark.asyncio
    async def test_should_process_correctly(self, score, runs, factor, actors, ray_context):
        pool = ParallelActorPool([
            MultiplyActor.remote(factor)
            for _ in range(actors)
        ])
        results = await asyncio.gather(*[
            pool.run(data=1, delay=0.0001)
            for _ in range(runs)
        ])
        assert sum(results) == score
