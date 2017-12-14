import unittest

from src.commons.principal import Principal
from src.commons.nsp_error import NspError


class PrincipalInit(unittest.TestCase):
    def test(self):
        'Principal.__init__() should assign the parameter to __dict__'
        dct = {'a': 'A'}
        principal = Principal(dct)
        self.assertEqual(principal.__dict__, dct)


class PrincipalIsAdmin(unittest.TestCase):
    def testFalse(self):
        'Principal.isAdmin() should return false'
        principal = Principal({'roles': {'a', 'b'}})
        self.assertFalse(principal.isAdmin())

    def testTrue(self):
        'Principal.isAdmin() should return true'
        principal = Principal({'roles': {'ROLE_ADMIN', 'a'}})
        self.assertTrue(principal.isAdmin())


class PrincipalCheckAuthorization(unittest.TestCase):
    def testReturns(self):
        'Principal.checkAuthorization() should return'
        principal = Principal({'roles': {'a'}})
        principal.checkAuthorization(['a'], 'operation')

    def testRaises(self):
        'Principal.checkAuthorization() should raise'
        principal = Principal({'roles': {'a'}})
        try:
            principal.checkAuthorization(['b'], 'operation')
            self.fail()
        except Exception as error:
            self.assertIsInstance(error, NspError)
            self.assertEqual(error.code, NspError.FORBIDDEN)
            self.assertEqual(error.message, 'Principal is not authorized to operation')


class PrincipalCheckVisibility(unittest.TestCase):
    def testReturnsForAdmin(self):
        'Principal.checkVisibility() should return if principal.isAdmin()'
        entity = {'uuid': 'uuid', 'owner': '001'}
        principal = Principal({'roles': {'ROLE_ADMIN'}})
        principal.checkVisibility(entity, 'entity', 'code')

    def testReturnsForOwner(self):
        'Principal.checkVisibility() should return if principal is owner'
        entity = {'uuid': 'uuid', 'owner': '001'}
        principal = Principal({'organizationId': '001', 'roles': {'ROLE_ENTITY_USER'}})
        principal.checkVisibility(entity, 'entity', 'code')

    def testRaisesForNotOwner(self):
        'Principal.checkVisibility() should raise if principal is not owner'
        entity = {'uuid': 'uuid', 'owner': '001'}
        principal = Principal({'organizationId': '002', 'roles': {'ROLE_ENTITY_USER'}})
        try:
            principal.checkVisibility(entity, 'entity', 'code')
            self.fail()
        except Exception as error:
            self.assertIsInstance(error, NspError)
            self.assertEqual(error.code, 'code')
            self.assertEqual(error.message, 'Entity "uuid" not found')
