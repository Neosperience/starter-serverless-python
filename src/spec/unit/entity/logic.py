import unittest
from unittest.mock import MagicMock
from src.commons.principal import Principal
from src.commons.nsp_error import NspError
from src.entity.logic import Logic


class LogicGetEntity(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(self.repository)

    def test_EntityNotFound(self):
        'EntityLogic.getEntity() should throw ENTITY_NOT_FOUND NspError if repository.getEntity() returns None'
        uuid = 'uuid'
        self.repository.getEntity.return_value = None
        try:
            self.sut.getEntity(None, uuid)
            self.fail()
        except Exception as error:
            self.assertIsInstance(error, NspError)
            self.assertEqual(error.code, NspError.ENTITY_NOT_FOUND)
            self.assertEqual(error.message, 'Entity "{0}" not found'.format(uuid))
            self.assertEqual(error.causes, [])
            self.repository.getEntity.assert_called_once_with(uuid)

    def test_EntityNotOwned(self):
        'EntityLogic.getEntity() should throw ENTITY_NOT_FOUND NspError if entity is not owned'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        entity = {'uuid': uuid, 'owner': '000'}
        self.repository.getEntity.return_value = entity
        try:
            self.sut.getEntity(principal, uuid)
            self.fail()
        except Exception as error:
            self.assertIsInstance(error, NspError)
            self.assertEqual(error.code, NspError.ENTITY_NOT_FOUND)
            self.assertEqual(error.message, 'Entity "{0}" not found'.format(uuid))
            self.assertEqual(error.causes, [])
            self.repository.getEntity.assert_called_once_with(uuid)

    def test_EntityOK(self):
        'EntityLogic.getEntity() should return the result of repository.getEntity()'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        entity = {'uuid': uuid, 'owner': '001'}
        self.repository.getEntity.return_value = entity
        result = self.sut.getEntity(principal, uuid)
        self.assertEqual(result, entity)
        self.repository.getEntity.assert_called_once_with(uuid)
