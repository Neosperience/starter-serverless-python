import unittest
import datetime

from src.commons.nsp_error import NspError
from src.commons.http_error import HttpError


class HttpErrorSpec(unittest.TestCase):
    def test_status_codes(self):
        'All the expected status codes should be defined'
        self.assertEqual(HttpError.BAD_REQUEST, 400)
        self.assertEqual(HttpError.FORBIDDEN, 403)
        self.assertEqual(HttpError.INTERNAL_SERVER_ERROR, 500)
        self.assertEqual(HttpError.NOT_FOUND, 404)
        self.assertEqual(HttpError.UNAUTHORIZED, 401)
        self.assertEqual(HttpError.UNPROCESSABLE_ENTITY, 422)
        self.assertEqual(HttpError.UNSUPPORTED_MEDIA_TYPE, 415)

    def test_init1(self):
        'The instance should have the expected attributes [without causes and timestamp]'
        e = HttpError(HttpError.NOT_FOUND, 'message')
        self.assertEqual(e.statusCode, 404)
        self.assertEqual(e.message, 'message')
        self.assertEqual(e.causes, [])
        self.assertIsInstance(e.timestamp, datetime.datetime)

    def test_init2(self):
        'The instance should have the expected attributes [without timestamp]'
        e = HttpError(HttpError.NOT_FOUND, 'message', ['cause'])
        self.assertEqual(e.statusCode, 404)
        self.assertEqual(e.message, 'message')
        self.assertEqual(e.causes, ['cause'])
        self.assertIsInstance(e.timestamp, datetime.datetime)

    def test_init3(self):
        'The instance should have the expected attributes [without causes]'
        e = HttpError(HttpError.NOT_FOUND, 'message', timestamp='dummy')
        self.assertEqual(e.statusCode, 404)
        self.assertEqual(e.message, 'message')
        self.assertEqual(e.causes, [])
        self.assertEqual(e.timestamp, 'dummy')

    def test_init4(self):
        'The instance should have the expected attributes [with causes and timestamp]'
        e = HttpError(HttpError.NOT_FOUND, 'message', causes=['cause'], timestamp='dummy')
        self.assertEqual(e.statusCode, 404)
        self.assertEqual(e.message, 'message')
        self.assertEqual(e.causes, ['cause'])
        self.assertEqual(e.timestamp, 'dummy')

    def test_BAD_REQUEST(self):
        'The BAD_REQUEST instance should have the expected attributes'
        e = HttpError(HttpError.BAD_REQUEST, 'message')
        self.assertEqual(e.statusCode, 400)
        self.assertEqual(e.statusReason, 'Bad request')

    def test_FORBIDDEN(self):
        'The FORBIDDEN instance should have the expected attributes'
        e = HttpError(HttpError.FORBIDDEN, 'message')
        self.assertEqual(e.statusCode, 403)
        self.assertEqual(e.statusReason, 'Forbidden')

    def test_INTERNAL_SERVER_ERROR(self):
        'The INTERNAL_SERVER_ERROR instance should have the expected attributes'
        e = HttpError(HttpError.INTERNAL_SERVER_ERROR, 'message')
        self.assertEqual(e.statusCode, 500)
        self.assertEqual(e.statusReason, 'Internal server error')

    def test_NOT_FOUND(self):
        'The NOT_FOUND instance should have the expected attributes'
        e = HttpError(HttpError.NOT_FOUND, 'message')
        self.assertEqual(e.statusCode, 404)
        self.assertEqual(e.statusReason, 'Not found')

    def test_UNAUTHORIZED(self):
        'The UNAUTHORIZED instance should have the expected attributes'
        e = HttpError(HttpError.UNAUTHORIZED, 'message')
        self.assertEqual(e.statusCode, 401)
        self.assertEqual(e.statusReason, 'Unauthorized')

    def test_UNPROCESSABLE_ENTITY(self):
        'The UNPROCESSABLE_ENTITY instance should have the expected attributes'
        e = HttpError(HttpError.UNPROCESSABLE_ENTITY, 'message')
        self.assertEqual(e.statusCode, 422)
        self.assertEqual(e.statusReason, 'Unprocessable entity')

    def test_UNSUPPORTED_MEDIA_TYPE(self):
        'The UNSUPPORTED_MEDIA_TYPE instance should have the expected attributes'
        e = HttpError(HttpError.UNSUPPORTED_MEDIA_TYPE, 'message')
        self.assertEqual(e.statusCode, 415)
        self.assertEqual(e.statusReason, 'Unsupported media type')

    def test_wrapNspError(self):
        'It should wrap the NspError with the expected attributes'
        nspError = NspError(NspError.ENTITY_NOT_FOUND, 'message', ['causes'])
        e = HttpError.wrap(nspError)
        self.assertEqual(e.message, nspError.message)
        self.assertEqual(e.causes, nspError.causes)
        self.assertEqual(e.timestamp, nspError.timestamp)

    def test_wrap_ENTITY_NOT_FOUND(self):
        'It should wrap the ENTITY_NOT_FOUND NspError'
        e = HttpError.wrap(NspError(NspError.ENTITY_NOT_FOUND, 'message'))
        self.assertEqual(e.statusCode, 404)
        self.assertEqual(e.message, 'message')

    def test_wrap_FORBIDDEN(self):
        'It should wrap the FORBIDDEN NspError'
        e = HttpError.wrap(NspError(NspError.FORBIDDEN, 'message'))
        self.assertEqual(e.statusCode, 403)
        self.assertEqual(e.message, 'message')

    def test_wrapException(self):
        'It should wrap an Exception with the expected attributes'
        exception = None
        e = HttpError.wrap(exception)
        self.assertEqual(e.statusCode, HttpError.INTERNAL_SERVER_ERROR)
        self.assertEqual(e.message, repr(exception))
        self.assertEqual(e.causes, [])
        self.assertIsInstance(e.timestamp, datetime.datetime)
