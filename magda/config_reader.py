import yaml
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from magda.module.factory import ModuleFactory
from magda.pipeline.sequential import SequentialPipeline
from magda.pipeline.parallel.parallel_pipeline import ParallelPipeline


class ConfigReader:
    @dataclass(frozen=True)
    class ConfigModule:
        name: str
        type: str
        group: Optional[str] = field(default=None)
        depends_on: List[str] = field(default_factory=list)
        parameters: Dict[str, Any] = field(default=None)

    @classmethod
    def read(
        cls,
        config: str,
        module_factory: ModuleFactory,
        context: Optional[Any] = None,
        shared_parameters: Optional[Dict] = None,
    ):
        parsed_yaml = yaml.safe_load(config)
        modules, shared_parameters, group_options = \
            cls._extract_information_from_yaml(parsed_yaml, shared_parameters)

        pipeline = (
            ParallelPipeline()
            if any([m.group is not None for m in modules])
            else SequentialPipeline()
        )

        pipeline = cls._add_modules_to_pipeline(modules, pipeline, module_factory)
        pipeline = cls._add_group_options(group_options, pipeline)

        # connect modules
        for mod in modules:
            curr_mod_obj = pipeline.get_module(mod.name)
            for dependent_mod_name in mod.depends_on:
                dependent_mod_obj = pipeline.get_module(dependent_mod_name)
                if dependent_mod_obj:
                    curr_mod_obj.depends_on(dependent_mod_obj)
                else:
                    raise AttributeError(
                        f"Module '{dependent_mod_name}' hasn't been defined in the config file, "
                        "whereas it's used as a dependency."
                    )
        return pipeline.build(context, shared_parameters)

    @staticmethod
    def _extract_information_from_yaml(parsed_yaml, shared_parameters):
        try:
            modules = [ConfigReader.ConfigModule(**data) for data in parsed_yaml['modules']]
        except TypeError:
            raise Exception("Every module defined in a config file has to have a name and a type.")

        if 'shared_parameters' in parsed_yaml:
            shared_parameters = parsed_yaml['shared_parameters']

        group_options = {}
        if 'groups' in parsed_yaml:
            group_options = {
                group['name']: group['options']
                for group in parsed_yaml['groups']
            }

        return modules, shared_parameters, group_options

    @staticmethod
    def _add_modules_to_pipeline(modules, pipeline, module_factory):
        for mod in modules:
            module = module_factory.create(mod.name, mod.type, mod.group)
            if mod.parameters:
                module.set_parameters(mod.parameters)
            pipeline.add_module(module)
        return pipeline

    @classmethod
    def _add_group_options(cls, group_options, pipeline):
        if group_options and isinstance(pipeline, ParallelPipeline):
            for name, params in group_options.items():
                group = ParallelPipeline.Group(name)
                group.set_replicas(params['replicas'] if 'replicas' in params else 1)
                params.pop('replicas', None)
                if params.keys():
                    group.set_options(**params)
                pipeline.add_group(group)
        return pipeline
