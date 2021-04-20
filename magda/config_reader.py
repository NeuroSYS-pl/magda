import yaml
import re
import warnings
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from numbers import Number

from magda.module.factory import ModuleFactory
from magda.pipeline.sequential import SequentialPipeline
from magda.pipeline.parallel.parallel_pipeline import ParallelPipeline
from magda.exceptions import WrongParameterStructureException, ParametrizationException


class ConfigReader:
    @dataclass(frozen=True)
    class ConfigModule:
        name: str
        type: str
        group: Optional[str] = field(default=None)
        depends_on: List[str] = field(default_factory=list)
        parameters: Dict[str, Any] = field(default=None)

    @classmethod
    async def read(
        cls,
        config: str,
        module_factory: ModuleFactory,
        config_parameters: Optional[Dict] = None,
        context: Optional[Any] = None,
        shared_parameters: Optional[Dict] = None
    ):
        if config_parameters:
            cls._validate_config_parameters_structure(config_parameters)

            with open(config, 'r') as config_file:
                config = config_file.read()

            config = cls._substitute_parameters(config, config_parameters)

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

        runtime = await pipeline.build(context, shared_parameters)
        return runtime

    @staticmethod
    def _substitute_parameters(config_str, config_parameters):
        variables = list(set(re.findall(r'\${\w*}', config_str)))
        variable_names_dict = {variable[2:-1]: variable for variable in variables}
        config_variables = list(config_parameters.keys())

        for declared_var in variable_names_dict.keys():
            if declared_var not in config_variables:
                raise ParametrizationException(
                    f"Config file containes a declared variable"
                    " that was not specified in parameters: {declared_var}"
                )

        for config_var in config_variables:
            if config_var not in variable_names_dict.keys():
                warnings.warn(
                    f"Parameters contain an additional "
                    "variable that is not used in config file: {config_var}"
                )
            else:
                config_str = config_str.replace(
                    variable_names_dict[config_var],
                    str(config_parameters[config_var])
                )

        return config_str

    @staticmethod
    def _validate_config_parameters_structure(config_parameters):
        if not isinstance(config_parameters, Dict):
            raise WrongParameterStructureException(
                "Configuration parameters should be passed in a dictionary"
            )
        for key, value in config_parameters.items():
            if not isinstance(key, (str, Number)):
                raise WrongParameterStructureException(
                    f"Configuration parameters contains a key that is not alphanumeric: {key}."
                )
            if not isinstance(value, (str, Number)):
                raise WrongParameterStructureException(
                    f"Configuration parameters contains a value that is not alphanumeric: {value}."
                )

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
