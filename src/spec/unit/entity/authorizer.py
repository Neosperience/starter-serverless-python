import unittest
from unittest.mock import MagicMock
from src.commons.nsp_error import NspError
from src.entity.authorizer import Authorizer


class AuthorizerGetEntity(unittest.TestCase):
    def setUp(self):
        self.logic = MagicMock()
        self.principal = MagicMock()
        self.sut = Authorizer(self.logic)

    def test_ItCallsCheckAuthorization(self):
        'EntityAuthorizer.getEntity() should call principal.checkAuthorization() and logic.getEntity()'
        uuid = 'uuid'
        self.sut.getEntity(self.principal, uuid)
        self.principal.checkAuthorization.assert_called_once_with({'ROLE_ADMIN', 'ROLE_ENTITY_USER'}, 'get entities')
        self.logic.getEntity.assert_called_once_with(self.principal, uuid)
