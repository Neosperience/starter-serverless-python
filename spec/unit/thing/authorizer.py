import unittest
from unittest.mock import MagicMock
from src.commons.nsp_error import NspError
from src.thing.authorizer import Authorizer
from spec.helper import mockLoggerFactory


class AuthorizerCreateThing(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(mockLoggerFactory, self.logic)

    def testItCallsTheExpectedMethods(self):
        '''
        ThingAuthorizer.createThing() should call principal.checkAuthorization(), principal.getOwner() and
        logic.createThing()
        '''
        thing = {'owner': 'org'}
        self.sut.createThing(self.principal, thing)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'create things')
        self.principal.getOwner.assert_called_once_with('org')
        self.logic.createThing.assert_called_once_with(self.principal, thing)

    def testItReturnsTheExpectedValue(self):
        'ThingAuthorizer.createThing() should return the value of logic.createThing()'
        thing = 'thing'
        self.logic.createThing.return_value = thing
        value = self.sut.createThing(self.principal, {})
        self.assertIs(value, thing)


class AuthorizerGetThing(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(mockLoggerFactory, self.logic)

    def testItCallsTheExpectedMethods(self):
        'ThingAuthorizer.getThing() should call principal.checkAuthorization() and logic.getThing()'
        uuid = 'uuid'
        self.sut.getThing(self.principal, uuid)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'get things')
        self.logic.getThing.assert_called_once_with(self.principal, uuid)

    def testItReturnsTheExpectedValue(self):
        'ThingAuthorizer.getThing() should return the value of logic.getThing()'
        thing = 'thing'
        self.logic.getThing.return_value = thing
        value = self.sut.getThing(self.principal, '')
        self.assertIs(value, thing)


class AuthorizerUpdateThing(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(mockLoggerFactory, self.logic)

    def testItCallsTheExpectedMethods(self):
        'ThingAuthorizer.updateThing() should call principal.checkAuthorization() and logic.updateThing()'
        uuid = 'uuid'
        thing = 'thing'
        self.sut.updateThing(self.principal, uuid, thing)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'update things')
        self.logic.updateThing.assert_called_once_with(self.principal, uuid, thing)

    def testItReturnsTheExpectedValue(self):
        'ThingAuthorizer.updateThing() should return the value of logic.updateThing()'
        thing = 'thing'
        self.logic.updateThing.return_value = thing
        value = self.sut.updateThing(self.principal, 'uuid', 'obj')
        self.assertIs(value, thing)


class AuthorizerDeleteThing(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(mockLoggerFactory, self.logic)

    def testItCallsTheExpectedMethods(self):
        'ThingAuthorizer.deleteThing() should call principal.checkAuthorization() and logic.deleteThing()'
        uuid = 'uuid'
        self.sut.deleteThing(self.principal, uuid)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'delete things')
        self.logic.deleteThing.assert_called_once_with(self.principal, uuid)

    def testItReturnsTheExpectedValue(self):
        'ThingAuthorizer.deleteThing() should return the value of logic.deleteThing()'
        thing = 'thing'
        self.logic.deleteThing.return_value = thing
        value = self.sut.deleteThing(self.principal, '')
        self.assertIs(value, thing)


class AuthorizerListThings(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(mockLoggerFactory, self.logic)

    def testItCallsTheExpectedMethods(self):
        '''
        ThingAuthorizer.listThings() should call principal.checkAuthorization(), principal.getOwnerFilter() and
        logic.listThings()
        '''
        owner1 = 'owner1'
        owner2 = 'owner2'
        self.principal.getOwnerFilter.return_value = owner2
        self.sut.listThings(self.principal, owner1)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'list things')
        self.principal.getOwnerFilter.assert_called_once_with(owner1)
        self.logic.listThings.assert_called_once_with(self.principal, owner2)

    def testItReturnsTheExpectedValue(self):
        'ThingAuthorizer.listThings() should return the value of logic.listThings()'
        things = 'things'
        self.logic.listThings.return_value = things
        value = self.sut.listThings(self.principal, '')
        self.assertIs(value, things)
