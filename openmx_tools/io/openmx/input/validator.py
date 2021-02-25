# -*- coding: utf-8 -*-
"""OpenMX `openmx` input validation tools."""

import os
import json

import numpy as np
import jsonschema

__all__ = ('get_schema', 'validate_parameters')


_DIR = os.path.dirname(os.path.abspath(__file__))


def get_schema(version='3.9'):
    """Get an OpenMX `openmx` input JSON schema."""
    schema_path = os.path.join(_DIR, f'data/schema/{version}.json')
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f'There is no schema available for version {version}')
    
    with open(schema_path, 'r') as stream:
        schema = json.load(stream)

    return schema


def validate_parameters(schema, parameters):
    """Validate OpenMX input parameters using jsonschema.

    The jsonschema Validator is retrieved for the appropriate schema version, and its TypeChecker
    is extended to support Numpy int, float, complex, and array types.

    :param schema: contents of the JSON schema file
    :param parameters: OpenMX input parameters
    :returns: None if validation is successful
    """
    validator = _get_validator(schema)
    return validator.validate(parameters)


def _get_validator(schema):
    """Create a custom validator with numpy support for the given schema."""
    validator = jsonschema.validators.validator_for(schema)
    type_checker = validator.TYPE_CHECKER
    type_checker = type_checker.redefine('integer', _get_is_int(validator))
    type_checker = type_checker.redefine('number', _get_is_number(validator))
    type_checker = type_checker.redefine('array', _get_is_array(validator))
    OpenmxValidator = jsonschema.validators.extend(validator, type_checker=type_checker)
    return OpenmxValidator(schema)


def _get_is_int(validator):
    """Create a integer type checker with numpy support for the given validator."""
    # pylint: disable=unused-argument
    def is_int(checker, instance):
        return (validator.TYPE_CHECKER.is_type(instance, 'integer') or isinstance(instance, (np.int32, np.int64)))

    return is_int


def _get_is_number(validator):
    """Create a number type checker with numpy support for the given validator."""
    # pylint: disable=unused-argument,consider-merging-isinstance
    def is_number(checker, instance):
        return (
            validator.TYPE_CHECKER.is_type(instance, 'number') or isinstance(instance,
                                                                             (np.int16, np.int32, np.int64)) or
            isinstance(instance, (np.float16, np.float32, np.float64, np.float128)) or
            isinstance(instance, (np.complex64, np.complex128, np.complex256))
        )

    return is_number


def _get_is_array(validator):
    """Create an array type checker with numpy support for the given validator."""
    # pylint: disable=unused-argument
    def is_array(checker, instance):
        return (validator.TYPE_CHECKER.is_type(instance, 'array') or isinstance(instance, (tuple, np.ndarray)))

    return is_array
