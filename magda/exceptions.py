class CyclicDependenciesException(Exception):
    def __init__(self, trace):
        super().__init__(f'The Graph has a cycle: {trace}')


class DisjointGraphException(Exception):
    def __init__(self):
        super().__init__('The Graph is not connected')


class ClosedPipelineException(Exception):
    def __init__(self):
        super().__init__('The pipeline was closed and cannot be run')


class WrongParametersStructureException(Exception):
    pass


class WrongParameterValueException(Exception):
    pass


class ConfiguartionFileException(Exception):
    pass
