import unittest
from unittest.mock import MagicMock
from src.commons.nsp_error import NspError
from src.thing.authorizer import Authorizer


class AuthorizerGetThing(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(self.logic)

    def test_ItCallsCheckAuthorization(self):
        'ThingAuthorizer.getThing() should call principal.checkAuthorization() and logic.getThing()'
        uuid = 'uuid'
        self.sut.getThing(self.principal, uuid)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'get things')
        self.logic.getThing.assert_called_once_with(self.principal, uuid)
