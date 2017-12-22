from datetime import datetime
import unittest
from unittest.mock import MagicMock
from src.commons.principal import Principal
from src.commons.nsp_error import NspError
from src.thing.logic import Logic
from spec.helper import mockLoggerFactory

UUIDV4_REGEX = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'


class LogicCreateThing(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(mockLoggerFactory, self.repository)

    def testThingAlreadyExists(self):
        'ThingLogic.createThing() should raise THING_ALREADY_EXISTS NspError if repository.getThing() returns a thing'
        thing = {'uuid': 'uuid'}
        self.repository.getThing.return_value = 'a thing'
        with self.assertRaises(NspError) as cm:
            self.sut.createThing(None, thing)
        self.assertEqual(cm.exception.code, NspError.THING_ALREADY_EXISTS)
        self.assertEqual(cm.exception.message, 'Thing "{0}" already exists'.format(thing['uuid']))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(thing['uuid'])

    def testAssignedAttributesWithUUID(self):
        'ThingLogic.createThing() should assign created, lastModified and uuid if uuid is None and preserve the rest'
        thing = {'anything else': 'hello'}
        self.repository.getThing.return_value = None
        self.repository.createThing.side_effect = lambda x: x
        result = self.sut.createThing(None, thing)
        self.assertRegex(result['uuid'], UUIDV4_REGEX)
        self.assertIsInstance(result['created'], datetime)
        self.assertIsInstance(result['lastModified'], datetime)
        self.assertEqual(result['lastModified'], thing['created'])
        self.assertIs(result['anything else'], thing['anything else'])

    def testAssignedAttributesWithoutUUID(self):
        'ThingLogic.createThing() should assign created and lastModified if uuid is not None and preserve the rest'
        thing = {'uuid': 'uuid', 'anything else': 'hello'}
        self.repository.getThing.return_value = None
        self.repository.createThing.side_effect = lambda x: x
        result = self.sut.createThing(None, thing)
        self.assertIs(result['uuid'], thing['uuid'])
        self.assertIsInstance(result['created'], datetime)
        self.assertIsInstance(result['lastModified'], datetime)
        self.assertEqual(result['lastModified'], result['created'])
        self.assertIs(result['anything else'], thing['anything else'])


class LogicGetThing(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(mockLoggerFactory, self.repository)

    def testThingNotFound(self):
        'ThingLogic.getThing() should raise THING_NOT_FOUND NspError if repository.getThing() returns None'
        uuid = 'uuid'
        self.repository.getThing.return_value = None
        with self.assertRaises(NspError) as cm:
            self.sut.getThing(None, uuid)
        self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
        self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(uuid)

    def testThingNotOwned(self):
        'ThingLogic.getThing() should raise THING_NOT_FOUND NspError if thing is not owned'
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

    def testThingOK(self):
        'ThingLogic.getThing() should return the result of repository.getThing()'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        thing = {'uuid': uuid, 'owner': '001'}
        self.repository.getThing.return_value = thing
        result = self.sut.getThing(principal, uuid)
        self.assertEqual(result, thing)
        self.repository.getThing.assert_called_once_with(uuid)


class LogicUpdateThing(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(mockLoggerFactory, self.repository)

    def testThingNotFound(self):
        'ThingLogic.updateThing() should raise THING_NOT_FOUND NspError if repository.getThing() returns None'
        uuid = 'uuid'
        newThing = {}
        self.repository.getThing.return_value = None
        with self.assertRaises(NspError) as cm:
            self.sut.updateThing(None, uuid, newThing)
        self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
        self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(uuid)

    def testThingNotOwned(self):
        'ThingLogic.updateThing() should raise THING_NOT_FOUND NspError if thing is not owned'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        newThing = {}
        thing = {'uuid': uuid, 'owner': '000'}
        self.repository.getThing.return_value = thing
        with self.assertRaises(NspError) as cm:
            self.sut.updateThing(principal, uuid, newThing)
        self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
        self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(uuid)

    def testReadOnlyAttributesForNonAdmin(self):
        '''
        ThingLogic.updateThing() should raise THING_UNPROCESSABLE NspError if writing read-only properties
        [non admin principal]
        '''
        principal = Principal({
            'organizationId': 'owner',
            'roles': []
        })
        uuid = 'uuid'
        thing = {
            'uuid': uuid,
            'owner': 'owner',
            'created': datetime(2012, 12, 26),
            'lastModified': datetime(2012, 12, 26),
            'name': 'name'
        }
        newThing = {
            'uuid': 'another uuid',
            'owner': 'another owner',
            'created': datetime(2013, 12, 26),
            'lastModified': datetime(2014, 12, 26),
            'name': 'another name'
        }
        self.repository.getThing.return_value = thing
        with self.assertRaises(NspError) as cm:
            self.sut.updateThing(principal, uuid, newThing)
        self.assertEqual(cm.exception.code, NspError.THING_UNPROCESSABLE)
        self.assertEqual(cm.exception.message, 'Cannot change read-only properties'.format(uuid))
        self.assertEqual(cm.exception.causes, [
            'Cannot change read-only property "uuid" from "uuid" to "another uuid"',
            'Cannot change read-only property "created" from "2012-12-26 00:00:00" to "2013-12-26 00:00:00"',
            'Cannot change read-only property "lastModified" from "2012-12-26 00:00:00" to "2014-12-26 00:00:00"',
            'Cannot change read-only property "owner" from "owner" to "another owner"'
        ])
        self.repository.getThing.assert_called_once_with(uuid)


    def testReadOnlyAttributesForAdmin(self):
        '''
        ThingLogic.updateThing() should raise THING_UNPROCESSABLE NspError if writing read-only properties
        [admin principal]
        '''
        principal = Principal({
            'organizationId': 'admin',
            'roles': ['ROLE_ADMIN']
        })
        uuid = 'uuid'
        thing = {
            'uuid': uuid,
            'owner': 'owner',
            'created': datetime(2012, 12, 26),
            'lastModified': datetime(2012, 12, 26),
            'name': 'name'
        }
        newThing = {
            'uuid': 'another uuid',
            'owner': 'another owner',
            'created': datetime(2013, 12, 26),
            'lastModified': datetime(2014, 12, 26),
            'name': 'another name'
        }
        self.repository.getThing.return_value = thing
        with self.assertRaises(NspError) as cm:
            self.sut.updateThing(principal, uuid, newThing)
        self.assertEqual(cm.exception.code, NspError.THING_UNPROCESSABLE)
        self.assertEqual(cm.exception.message, 'Cannot change read-only properties'.format(uuid))
        self.assertEqual(cm.exception.causes, [
            'Cannot change read-only property "uuid" from "uuid" to "another uuid"',
            'Cannot change read-only property "created" from "2012-12-26 00:00:00" to "2013-12-26 00:00:00"',
            'Cannot change read-only property "lastModified" from "2012-12-26 00:00:00" to "2014-12-26 00:00:00"'
        ])
        self.repository.getThing.assert_called_once_with(uuid)


    def testReturnsUpdatedThing(self):
        'ThingLogic.updateThing() should return the result of repository.updateThing()'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        thing = {
            'uuid': uuid,
            'owner': '001',
            'created': datetime(2012, 12, 26),
            'lastModified': datetime(2012, 12, 26),
            'name': 'name'
        }
        newThing = thing.copy()
        newThing['name'] = 'another name'
        self.repository.getThing.return_value = thing
        self.repository.updateThing.side_effect = lambda x: x
        result = self.sut.updateThing(principal, uuid, newThing)
        self.assertEqual(result, newThing)
        self.repository.getThing.assert_called_once_with(uuid)
        self.repository.updateThing.assert_called_once_with(newThing)

    def testUpdatesLastModified(self):
        'ThingLogic.updateThing() should update lastModified'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        thing = {
            'uuid': uuid,
            'owner': '001',
            'created': datetime(2012, 12, 26),
            'lastModified': datetime(2012, 12, 26),
            'name': 'name'
        }
        newThing = thing.copy()
        newThing['name'] = 'another name'
        self.repository.getThing.return_value = thing
        self.repository.updateThing.side_effect = lambda x: x
        result = self.sut.updateThing(principal, uuid, newThing)
        self.assertEqual(result['uuid'], newThing['uuid'])
        self.assertEqual(result['owner'], newThing['owner'])
        self.assertEqual(result['created'], newThing['created'])
        self.assertEqual(result['name'], newThing['name'])
        self.assertGreater(result['lastModified'], thing['lastModified'])


class LogicDeleteThing(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(mockLoggerFactory, self.repository)

    def testThingNotFound(self):
        'ThingLogic.deleteThing() should raise THING_NOT_FOUND NspError if repository.getThing() returns None'
        uuid = 'uuid'
        self.repository.getThing.return_value = None
        with self.assertRaises(NspError) as cm:
            self.sut.deleteThing(None, uuid)
        self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
        self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(uuid)

    def testThingNotOwned(self):
        'ThingLogic.deleteThing() should raise THING_NOT_FOUND NspError if thing is not owned'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        thing = {'uuid': uuid, 'owner': '000'}
        self.repository.getThing.return_value = thing
        with self.assertRaises(NspError) as cm:
            self.sut.deleteThing(principal, uuid)
        self.assertEqual(cm.exception.code, NspError.THING_NOT_FOUND)
        self.assertEqual(cm.exception.message, 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(cm.exception.causes, [])
        self.repository.getThing.assert_called_once_with(uuid)

    def testThingOK(self):
        'ThingLogic.deleteThing() should return the result of repository.deleteThing()'
        principal = Principal({
            'organizationId': '001',
            'roles': []
        })
        uuid = 'uuid'
        thing = {'uuid': uuid, 'owner': '001'}
        self.repository.getThing.return_value = thing
        self.repository.deleteThing.return_value = 'result'
        result = self.sut.deleteThing(principal, uuid)
        self.assertEqual(result, 'result')
        self.repository.getThing.assert_called_once_with(uuid)
        self.repository.deleteThing.assert_called_once_with(uuid)


class LogicListThings(unittest.TestCase):
    def setUp(self):
        self.repository = MagicMock()
        self.sut = Logic(mockLoggerFactory, self.repository)

    def testReturn(self):
        'ThingLogic.listThings() should return the result of repository.listThings()'
        self.repository.listThings.return_value = 'value'
        result = self.sut.listThings(None, 'owner')
        self.assertEqual(result, 'value')
        self.repository.listThings.assert_called_once_with('owner')
