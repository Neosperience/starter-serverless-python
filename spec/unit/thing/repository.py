import unittest

from src.thing.repository import Repository
from spec.helper import mockLoggerFactory


class RepositoryCreateThing(unittest.TestCase):
    def setUp(self):
        self.sut = Repository(mockLoggerFactory)

    def testCreates(self):
        'ThingRepository.createThing() should add the created thing to the data'
        thing = {'uuid': 'uuid'}
        result = self.sut.createThing(thing)
        self.assertIs(thing, self.sut.data['uuid'])

    def testReturn(self):
        'ThingRepository.createThing() should return the created thing'
        thing = {'uuid': 'uuid'}
        result = self.sut.createThing(thing)
        self.assertIs(result, thing)


class RepositoryGetThing(unittest.TestCase):
    def setUp(self):
        self.sut = Repository(mockLoggerFactory)

    def testThingDoesNotExist(self):
        'ThingRepository.getThing() should return None if the thing does not exist'
        thing = self.sut.getThing('')
        self.assertIsNone(thing)

    def testThingDoesExists(self):
        'ThingRepository.getThing() should return the thing if the thing exists'
        thing = self.sut.getThing('001')
        self.assertIsInstance(thing, dict)


class RepositoryUpdateThing(unittest.TestCase):
    def setUp(self):
        self.sut = Repository(mockLoggerFactory)

    def testUpdates(self):
        'ThingRepository.updateThing() should update the thing in the data'
        thing = {'uuid': 'uuid'}
        result = self.sut.updateThing(thing)
        self.assertIs(thing, self.sut.data['uuid'])

    def testReturn(self):
        'ThingRepository.updateThing() should return the updated thing'
        thing = {'uuid': 'uuid'}
        result = self.sut.updateThing(thing)
        self.assertIs(result, thing)


class RepositoryDeleteThing(unittest.TestCase):
    def setUp(self):
        self.sut = Repository(mockLoggerFactory)

    def testDeletes(self):
        'ThingRepository.deleteThing() should remove thing from the data'
        self.sut.deleteThing('001')
        self.assertIsNone(self.sut.data.get('001'))

    def testReturn(self):
        'ThingRepository.deleteThing() should return None'
        result = self.sut.deleteThing('001')
        self.assertIsNone(result)


class RepositoryListThings(unittest.TestCase):
    def setUp(self):
        self.sut = Repository(mockLoggerFactory)

    def testWithOwner(self):
        'ThingRepository.listThings() should return all the things of the owner'
        owner = 'ORG001'
        result = self.sut.listThings(owner)
        self.assertIsInstance(result, list)
        subset = [thing for thing in self.sut.data.values() if thing['owner'] == owner]
        self.assertEqual(result, subset)

    def testWithoutOwner(self):
        'ThingRepository.listThings() should return all the things'
        result = self.sut.listThings(None)
        self.assertEqual(result, list(self.sut.data.values()))
