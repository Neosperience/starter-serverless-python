import unittest
from unittest.mock import MagicMock
from src.commons.principal import Principal
from src.commons.nsp_error import NspError
from src.entity.logic import Logic

import traceback


class MockRepository:
    def getEntity(self, uuid):
        pass


class LogicSpec(unittest.TestCase):
    def setUp(self):
        self.repository = MockRepository()
        self.sut = Logic(self.repository)

    def test_getEntityNotFound(self):
        'getEntity() should throw ENTITY_NOT_FOUND NspError if repository.getEntity() returns None'
        uuid = 'uuid'
        self.repository.getEntity = MagicMock(return_value=None)
        try:
            self.sut.getEntity(None, uuid)
            self.fail()
        except Exception as error:
            self.assertIsInstance(error, NspError)
            self.assertEqual(error.code, NspError.ENTITY_NOT_FOUND)
            self.assertEqual(error.message, 'Entity "{0}" not found'.format(uuid))
            self.assertEqual(error.causes, [])
            self.repository.getEntity.assert_called_once_with(uuid)

    def test_getEntityNotOwned(self):
        'getEntity() should throw ENTITY_NOT_FOUND NspError if entity is not owned'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        entity = {'uuid': uuid, 'owner': '000'}
        self.repository.getEntity = MagicMock(return_value=entity)
        try:
            self.sut.getEntity(principal, uuid)
            self.fail()
        except Exception as error:
            self.assertIsInstance(error, NspError)
            self.assertEqual(error.code, NspError.ENTITY_NOT_FOUND)
            self.assertEqual(error.message, 'Entity "{0}" not found'.format(uuid))
            self.assertEqual(error.causes, [])
            self.repository.getEntity.assert_called_once_with(uuid)

    def test_getEntityOK(self):
        'getEntity() should return the result of repository.getEntity()'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        entity = {'uuid': uuid, 'owner': '001'}
        self.repository.getEntity = MagicMock(return_value=entity)
        result = self.sut.getEntity(principal, uuid)
        self.assertEqual(result, entity)
        self.repository.getEntity.assert_called_once_with(uuid)
