from __future__ import annotations

from magda.module.runtime import ModuleRuntime
from magda.module.results import ResultSet


class ModuleAggregate(ModuleRuntime):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_state = []

    def process(self, data: ResultSet, **kwargs):
        """ Request Process """
        state_copy = self._current_state.copy()
        self.clear_state()
        return state_copy

    def aggregate(self, data: ResultSet, **kwargs):
        """ Request Aggregate """
        self.add_data(data)
        return self.state

    def clear_state(self):
        self._current_state = []

    def add_data(self, data):
        self._current_state.append(data)

    @property
    def state(self):
        return self._current_state

    @property
    def state_size(self):
        return len(self._current_state)
