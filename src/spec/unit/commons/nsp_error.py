import unittest
import datetime

from src.commons.nsp_error import NspError


class NspErrorSpec(unittest.TestCase):
    def test_codes(self):
        'All the expected codes should be defined'
        self.assertEqual(NspError.FORBIDDEN, 'FORBIDDEN')
        self.assertEqual(NspError.THING_NOT_FOUND, 'THING_NOT_FOUND')
        self.assertEqual(NspError.THING_UNPROCESSABLE, 'THING_UNPROCESSABLE')

    def test_initWithoutCauses(self):
        'The instance should have the expected attributes [without causes]'
        e = NspError('code', 'message')
        self.assertEqual(e.code, 'code')
        self.assertEqual(e.message, 'message')
        self.assertEqual(e.causes, [])
        self.assertIsInstance(e.timestamp, datetime.datetime)

    def test_initWithCauses(self):
        'The instance should have the expected attributes [with causes]'
        e = NspError('code', 'message', ['cause1'])
        self.assertEqual(e.code, 'code')
        self.assertEqual(e.message, 'message')
        self.assertEqual(e.causes, ['cause1'])
        self.assertIsInstance(e.timestamp, datetime.datetime)
