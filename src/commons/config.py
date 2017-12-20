import json
import jsonschema

from src.commons.nsp_error import NspError

CONFIG_FILE_NAME = 'config/config.json'
SCHEMA_FILE_NAME = 'config/schema.json'


def loadConfig():
    try:
        config = json.load(open(CONFIG_FILE_NAME))
        schema = json.load(open(SCHEMA_FILE_NAME))
    except Exception as error:
        print(error)
        raise NspError(NspError.INTERNAL_SERVER_ERROR, 'Could not load configuration', [str(error), repr(error)])
    try:
        jsonschema.Draft4Validator.check_schema(schema)
    except jsonschema.SchemaError as error:
        raise NspError(NspError.INTERNAL_SERVER_ERROR, 'Invalid configuration schema', [error])
    validator = jsonschema.Draft4Validator(schema, format_checker=jsonschema.FormatChecker())
    if not validator.is_valid(config):
        causes = [e.message for e in validator.iter_errors(config)]
        raise NspError(NspError.INTERNAL_SERVER_ERROR, 'Invalid configuration', causes)
    return config
