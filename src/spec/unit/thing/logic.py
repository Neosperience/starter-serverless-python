import unittest
from unittest.mock import MagicMock
from src.commons.principal import Principal
from src.commons.nsp_error import NspError
from src.thing.logic import Logic


class LogicGetThing(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(self.repository)

    def test_ThingNotFound(self):
        'ThingLogic.getThing() should throw THING_NOT_FOUND NspError if repository.getThing() returns None'
        uuid = 'uuid'
        self.repository.getThing.return_value = None
        with self.assertRaises(NspError) as cm:
            self.sut.getThing(None, uuid)
        self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
        self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(uuid)

    def test_ThingNotOwned(self):
        'ThingLogic.getThing() should throw THING_NOT_FOUND NspError if thing is not owned'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        thing = {'uuid': uuid, 'owner': '000'}
        self.repository.getThing.return_value = thing
        with self.assertRaises(NspError) as cm:
            self.sut.getThing(principal, uuid)
            self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
            self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
            self.assertEqual(cm.exception.causes, [])
            self.repository.getThing.assert_called_once_with(uuid)

    def test_ThingOK(self):
        'ThingLogic.getThing() should return the result of repository.getThing()'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        entity = {'uuid': uuid, 'owner': '001'}
        self.repository.getThing.return_value = entity
        result = self.sut.getThing(principal, uuid)
        self.assertEqual(result, entity)
        self.repository.getThing.assert_called_once_with(uuid)
