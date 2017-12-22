import tempfile
import json
import unittest

import jsonschema

import src.commons.config
from src.commons.nsp_error import NspError


class ConfigLoadConfig(unittest.TestCase):
    def setUp(self):
        self.sut = src.commons.config.loadConfig

    def testSchemaFileError(self):
        'config.loadConfig() should raise if it cannot open the schema file'
        with self.assertRaises(FileNotFoundError) as cm:
            config = self.sut(schemaFileName='wrong file name')

    def testConfigFileError(self):
        'config.loadConfig() should raise if it cannot open the config file'
        with self.assertRaises(FileNotFoundError) as cm:
            config = self.sut(configFileName='wrong file name')

    def testSchemaNotJSON(self):
        'config.loadConfig() should raise if the schema is not JSON'
        content = 'Hello!'
        tempFile = tempfile.NamedTemporaryFile(mode='w+t')
        tempFile.write(content)
        tempFile.flush()
        with self.assertRaises(json.JSONDecodeError) as cm:
            config = self.sut(schemaFileName=tempFile.name)
        tempFile.close()

    def testConfigNotJSON(self):
        'config.loadConfig() should raise if the config is not JSON'
        content = 'Hello!'
        tempFile = tempfile.NamedTemporaryFile(mode='w+t')
        tempFile.write(content)
        tempFile.flush()
        with self.assertRaises(json.JSONDecodeError) as cm:
            config = self.sut(configFileName=tempFile.name)
        tempFile.close()

    def testInvalidSchema(self):
        'config.loadConfig() should raise if the schema is not valid'
        content = '{"type": "hello"}'
        tempFile = tempfile.NamedTemporaryFile(mode='w+t')
        tempFile.write(content)
        tempFile.flush()
        with self.assertRaises(jsonschema.SchemaError) as cm:
            config = self.sut(schemaFileName=tempFile.name)
        tempFile.close()

    def testInvalidConfiguration(self):
        'config.loadConfig() should raise if the config is not valid'
        content = '{"type":"object","properties":{"a":{"type":"string"}, "b":{"type":"number"}}}'
        schemaFile = tempfile.NamedTemporaryFile(mode='w+t')
        schemaFile.write(content)
        schemaFile.flush()
        content = '{"a":1,"b":"x"}'
        configFile = tempfile.NamedTemporaryFile(mode='w+t')
        configFile.write(content)
        configFile.flush()
        with self.assertRaises(jsonschema.ValidationError) as cm:
            config = self.sut(schemaFileName=schemaFile.name, configFileName=configFile.name)
        schemaFile.close()
        configFile.close()

    def testOK(self):
        'config.loadConfig() should return the config'
        content = '{"type": "object"}'
        schemaFile = tempfile.NamedTemporaryFile(mode='w+t')
        schemaFile.write(content)
        schemaFile.flush()
        content = '{"hello": "goodbye"}'
        configFile = tempfile.NamedTemporaryFile(mode='w+t')
        configFile.write(content)
        configFile.flush()
        config = self.sut(schemaFileName=schemaFile.name, configFileName=configFile.name)
        schemaFile.close()
        configFile.close()
        self.assertEqual(config, json.loads(content))
