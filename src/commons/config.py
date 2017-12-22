import json
import jsonschema

CONFIG_FILE_NAME = 'config/config.json'
SCHEMA_FILE_NAME = 'config/schema.json'


def loadConfig(configFileName=CONFIG_FILE_NAME, schemaFileName=SCHEMA_FILE_NAME):
    with open(schemaFileName) as infile:
        schema = json.load(infile)
    with open(configFileName) as infile:
        config = json.load(infile)
    jsonschema.Draft4Validator.check_schema(schema)
    validator = jsonschema.Draft4Validator(schema, format_checker=jsonschema.FormatChecker())
    try:
        validator.validate(config)
    except jsonschema.ValidationError as error:
        causes = [e.message for e in validator.iter_errors(config)]
        error.message = ', '.join(causes)
        raise
    return config
