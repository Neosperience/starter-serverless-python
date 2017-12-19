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
        with self.assertRaises(NspError) as cm:
            principal.checkAuthorization(['b'], 'operation')
        self.assertEqual(cm.exception.code, NspError.FORBIDDEN)
        self.assertEqual(cm.exception.message, 'Principal is not authorized to operation')


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
        with self.assertRaises(NspError) as cm:
            principal.checkVisibility(entity, 'entity', 'code')
        self.assertEqual(cm.exception.code, 'code')
        self.assertEqual(cm.exception.message, 'Entity "uuid" not found')


class PrincipalCheckReadOnlyProperties(unittest.TestCase):
    def testRaisesForAdmin(self):
        'Principal.checkReadOnlyProperties() should raise if principal is admin'
        oldEntity = {'uuid': 'uuid1', 'owner': 'owner1', 'name': 'name1', 'created': 'created1'}
        newEntity = {'uuid': 'uuid2', 'owner': 'owner2', 'name': 'name2', 'created': 'created1'}
        principal = Principal({'roles': {'ROLE_ADMIN'}})
        with self.assertRaises(NspError) as cm:
            principal.checkReadOnlyProperties(oldEntity, newEntity, ['uuid', 'created'], 'code')
        self.assertEqual(cm.exception.code, 'code')
        self.assertEqual(cm.exception.message, 'Cannot change read-only properties')
        self.assertEqual(cm.exception.causes, [
            'Cannot change read-only property: uuid'
        ])

    def testRaisesForNonAdmin(self):
        'Principal.checkReadOnlyProperties() should raise if principal is not admin'
        oldEntity = {'uuid': 'uuid1', 'owner': 'owner1', 'name': 'name1', 'created': 'created1'}
        newEntity = {'uuid': 'uuid2', 'owner': 'owner2', 'name': 'name2', 'created': 'created1'}
        principal = Principal({'roles': {'ROLE_THING_USER'}})
        with self.assertRaises(NspError) as cm:
            principal.checkReadOnlyProperties(oldEntity, newEntity, ['uuid', 'created'], 'code')
        self.assertEqual(cm.exception.code, 'code')
        self.assertEqual(cm.exception.message, 'Cannot change read-only properties')
        self.assertEqual(cm.exception.causes, [
            'Cannot change read-only property: uuid',
            'Cannot change read-only property: owner'
        ])

    def testReturns(self):
        'Principal.checkReadOnlyProperties() should return'
        oldEntity = {'uuid': 'uuid1', 'owner': 'owner1', 'name': 'name1', 'created': 'created1'}
        newEntity = {'uuid': 'uuid1', 'owner': 'owner1', 'name': 'name2', 'created': 'created1'}
        principal = Principal({'roles': {'ROLE_THING_USER'}})
        principal.checkReadOnlyProperties(oldEntity, newEntity, ['uuid', 'created'], 'code')
