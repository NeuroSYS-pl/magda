from typing import List

from magda.module.module import Module
from magda.exceptions import DisjointGraphException, CyclicDependenciesException


class GraphValidator:
    def __init__(self, modules: List[Module.Runtime]):
        self.modules = modules
        self.n_modules = len(modules)
        self.neighbours = self.create_neighbours_dict()
        self.successors = self.create_neighbours_dict(successors_only=True)

    def create_neighbours_dict(self, successors_only=False):
        neighbours = {}
        for m in self.modules:
            if m.name not in neighbours:
                neighbours[m.name] = set()
            if not successors_only:
                for input_m in m.input_modules:
                    neighbours[m.name].add(input_m)
            for output_m in m.output_modules:
                neighbours[m.name].add(output_m)
        return neighbours

    def dfs(self, module, visited):
        visited[module] = True

        for neighbour in self.neighbours[module]:
            if not visited[neighbour]:
                self.dfs(neighbour, visited)

    def is_connected(self):
        start_module = self.modules[0].name
        visited = {m.name: False for m in self.modules}
        self.dfs(start_module, visited)
        return all(visited.values())

    def has_cycle(self):
        visited = {m.name: False for m in self.modules}
        start_module = self.modules[0].name
        return self.has_cycle_recursive(start_module, visited, [])

    def has_cycle_recursive(self, module, visited, trace):
        visited[module] = True
        trace.append(module)
        # if any successor is visited and is on recursion stack, there is a cycle
        for neighbour in self.successors[module]:
            if not visited[neighbour]:
                cycle, trace = self.has_cycle_recursive(neighbour, visited, trace)
                if cycle:
                    return True, trace
            elif neighbour in trace:
                trace.append(neighbour)
                return True, trace
        # pop the node from stack
        trace = trace[:-1]
        return False, trace

    def prepare_cycle_string_from_trace(self, trace):
        start_index = trace.index(trace[-1])
        return '->'.join(trace[start_index:])

    def validate(self):
        if len(self.modules) > 1:
            if not self.is_connected():
                raise DisjointGraphException()
            # graph is connected - cycles checked only from start node
            cycle, trace = self.has_cycle()
            if cycle:
                raise CyclicDependenciesException(self.prepare_cycle_string_from_trace(trace))
