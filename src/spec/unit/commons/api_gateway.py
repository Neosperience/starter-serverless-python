import json
import unittest
from unittest.mock import MagicMock

from src.commons.nsp_error import NspError
from src.commons.http_error import HttpError
from src.commons.principal import Principal
import src.commons.jsonutils as jsonutils
from src.commons.api_gateway import APIGateway
from src.spec.helper import mockLoggerFactory


class APIGatewayGetHttpMethod(unittest.TestCase):
    def testMissing(self):
        'APIGateway.getHttpMethod() should return `UNKNOWN_METHOD` if no method is found in the event'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        httpMethod = sut.getHttpMethod()
        self.assertEqual(httpMethod, 'UNKNOWN_METHOD')

    def testFound(self):
        'APIGateway.getHttpMethod() should return the method found in the event'
        event = {'httpMethod': 'method'}
        sut = APIGateway(mockLoggerFactory, event)
        httpMethod = sut.getHttpMethod()
        self.assertEqual(httpMethod, 'method')


class APIGatewayGetHttpResource(unittest.TestCase):
    def testStandardHttps(self):
        'APIGateway.getHttpResource() should return a standard port https resource'
        event = {
            'headers': {
                'X-Forwarded-Port': '443',
                'X-Forwarded-Proto': 'https',
                'Host': 'localhost'
            },
            'path': '/path'
        }
        sut = APIGateway(mockLoggerFactory, event)
        httpResource = sut.getHttpResource()
        self.assertEqual(httpResource, 'https://localhost/path')

    def testNonStandardHttps(self):
        'APIGateway.getHttpResource() should return a standard port https resource'
        event = {
            'headers': {
                'X-Forwarded-Port': '8443',
                'X-Forwarded-Proto': 'https',
                'Host': 'localhost'
            },
            'path': '/path'
        }
        sut = APIGateway(mockLoggerFactory, event)
        httpResource = sut.getHttpResource()
        self.assertEqual(httpResource, 'https://localhost:8443/path')

    def testStandardHttp(self):
        'APIGateway.getHttpResource() should return a standard port http resource'
        event = {
            'headers': {
                'X-Forwarded-Port': '80',
                'X-Forwarded-Proto': 'http',
                'Host': 'localhost'
            },
            'path': '/path'
        }
        sut = APIGateway(mockLoggerFactory, event)
        httpResource = sut.getHttpResource()
        self.assertEqual(httpResource, 'http://localhost/path')

    def testNonStandardHttp(self):
        'APIGateway.getHttpResource() should return a standard port http resource'
        event = {
            'headers': {
                'X-Forwarded-Port': '8080',
                'X-Forwarded-Proto': 'http',
                'Host': 'localhost'
            },
            'path': '/path'
        }
        sut = APIGateway(mockLoggerFactory, event)
        httpResource = sut.getHttpResource()
        self.assertEqual(httpResource, 'http://localhost:8080/path')

    def testContextPath(self):
        'APIGateway.getHttpResource() should insert a context path if the host is an API Gateway API'
        event = {
            'headers': {
                'X-Forwarded-Port': '443',
                'X-Forwarded-Proto': 'https',
                'Host': '12345678.execute-api.eu-west-1.amazonaws.com'
            },
            'path': '/path',
            'requestContext': {
                'stage': 'stage'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        httpResource = sut.getHttpResource()
        self.assertEqual(httpResource, 'https://12345678.execute-api.eu-west-1.amazonaws.com/stage/path')

    def testMissingElemenst(self):
        'APIGateway.getHttpResource() should return a default value for needed elements are missing'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        httpResource = sut.getHttpResource()
        self.assertEqual(httpResource, 'UNKNOWN_PROTOCOL://UNKNOWN_HOST:UNKNOWN_PORT/UNKNOWN_PATH')


class APIGatewayGetAndValidatePrincipal(unittest.TestCase):
    def testMissing(self):
        'APIGateway.getAndValidatePrincipal() should raise a 401 HttpError if principalId is missing'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidatePrincipal()
        self.assertEqual(cm.exception.statusCode, 401)
        self.assertEqual(cm.exception.message, 'Missing principal')

    def testMalformedJSON(self):
        'APIGateway.getAndValidatePrincipal() should raise a 401 HttpError if principalId is not a JSON string'
        event = {
            'requestContext': {
                'authorizer': {
                    'principalId': 'hello'
                }
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidatePrincipal()
        self.assertEqual(cm.exception.statusCode, 401)
        self.assertEqual(cm.exception.message, 'Malformed principal JSON')
        self.assertIsInstance(cm.exception.causes, list)
        self.assertGreater(len(cm.exception.causes), 0)
        for i in range(len(cm.exception.causes)):
            with self.subTest(i=i):
                self.assertIsInstance(cm.exception.causes[i], str)

    def testInvalidJSON(self):
        'APIGateway.getAndValidatePrincipal() should raise a 401 HttpError if principalId is not a valid JSON'
        event = {
            'requestContext': {
                'authorizer': {
                    'principalId': '{}'
                }
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidatePrincipal()
        self.assertEqual(cm.exception.statusCode, 401)
        self.assertEqual(cm.exception.message, 'Invalid principal')
        self.assertIsInstance(cm.exception.causes, list)
        self.assertGreater(len(cm.exception.causes), 0)
        for i in range(len(cm.exception.causes)):
            with self.subTest(i=i):
                self.assertIsInstance(cm.exception.causes[i], str)

    def testOK(self):
        'APIGateway.getAndValidatePrincipal() should return the principal as a Principal instance'
        p = {'organizationId': 'id', 'roles': []}
        event = {
            'requestContext': {
                'authorizer': {
                    'principalId': json.dumps(p)
                }
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        principal = sut.getAndValidatePrincipal()
        # Non si possono confrontare i Principal se non si scrive il loro operatore, e per i test non ne vale la pena
        self.assertIsInstance(principal, Principal)
        self.assertEqual(principal.organizationId, p['organizationId'])
        self.assertEqual(principal.roles, set(p['roles']))


class APIGatewayGetPathParameter(unittest.TestCase):
    def testMissingRequired(self):
        'APIGateway.getPathParameter() should raise a 400 HttpError if the parameter is missing and required'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        with self.assertRaises(HttpError) as cm:
            sut.getPathParameter('p', True)
        self.assertEqual(cm.exception.statusCode, 400)
        self.assertEqual(cm.exception.statusReason, 'Bad request')
        self.assertEqual(cm.exception.message, 'Missing path parameter "p"')

    def testMissingNotRequired(self):
        'APIGateway.getPathParameter() should return None if the parameter is missing and not required'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        param = sut.getPathParameter('p', False)
        self.assertIsNone(param)

    def testValidateMissing(self):
        'APIGateway.getPathParameter() should call the validator if passed [with missing param]'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        validator = MagicMock()
        sut.getPathParameter('p', False, validator)
        validator.assert_called_once_with(None)

    def testValidateFound(self):
        'APIGateway.getPathParameter() should call the validator if passed [with found param]'
        event = {
            'pathParameters': {
                'p': 'param'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        validator = MagicMock()
        sut.getPathParameter('p', False, validator)
        validator.assert_called_once_with('param')

    def testReturn(self):
        'APIGateway.getPathParameter() should return the parameter'
        event = {
            'pathParameters': {
                'p': 'param'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        param = sut.getPathParameter('p', False)
        self.assertEqual(param, 'param')


class APIGatewayGetQueryStringParameter(unittest.TestCase):
    def testMissingRequired(self):
        'APIGateway.getQueryStringParameter() should raise a 400 HttpError if the parameter is missing and required'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        with self.assertRaises(HttpError) as cm:
            sut.getQueryStringParameter('p', True)
        self.assertEqual(cm.exception.statusCode, 400)
        self.assertEqual(cm.exception.statusReason, 'Bad request')
        self.assertEqual(cm.exception.message, 'Missing query string parameter "p"')

    def testMissingNotRequired(self):
        'APIGateway.getQueryStringParameter() should return None if the parameter is missing and not required'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        param = sut.getQueryStringParameter('p', False)
        self.assertIsNone(param)

    def testValidateMissing(self):
        'APIGateway.getQueryStringParameter() should call the validator if passed [with missing param]'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        validator = MagicMock()
        sut.getQueryStringParameter('p', False, validator)
        validator.assert_called_once_with(None)

    def testValidateFound(self):
        'APIGateway.getQueryStringParameter() should call the validator if passed [with found param]'
        event = {
            'queryStringParameters': {
                'p': 'param'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        validator = MagicMock()
        sut.getQueryStringParameter('p', False, validator)
        validator.assert_called_once_with('param')

    def testReturn(self):
        'APIGateway.getQueryStringParameter() should return the parameter'
        event = {
            'queryStringParameters': {
                'p': 'param'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        param = sut.getQueryStringParameter('p', False)
        self.assertEqual(param, 'param')


class APIGatewayGetHeader(unittest.TestCase):
    def testMissingRequired(self):
        'APIGateway.getHeader() should raise a 400 HttpError if the header is missing and required'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        with self.assertRaises(HttpError) as cm:
            sut.getHeader('h', True)
        self.assertEqual(cm.exception.statusCode, 400)
        self.assertEqual(cm.exception.statusReason, 'Bad request')
        self.assertEqual(cm.exception.message, 'Missing header "h"')

    def testMissingNotRequired(self):
        'APIGateway.getHeader() should return None if the header is missing and not required'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        param = sut.getHeader('h', False)
        self.assertIsNone(param)

    def testValidateMissing(self):
        'APIGateway.getHeader() should call the validator if passed [with missing header]'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        validator = MagicMock()
        sut.getHeader('h', False, validator)
        validator.assert_called_once_with(None)

    def testValidateFound(self):
        'APIGateway.getHeader() should call the validator if passed [with found header]'
        event = {
            'headers': {
                'h': 'param'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        validator = MagicMock()
        sut.getHeader('h', False, validator)
        validator.assert_called_once_with('param')

    def testReturn(self):
        'APIGateway.getHeader() should return the header'
        event = {
            'headers': {
                'h': 'header'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        header = sut.getHeader('h', False)
        self.assertEqual(header, 'header')


class APIGatewayCreateLocationHeader(unittest.TestCase):
    def test(self):
        'APIGateway.createLocationHeader() should return getHttpResource() with the parameter appended'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        sut.getHttpResource = MagicMock(return_value='http-resource')
        uuid = 'uuid'
        location = sut.createLocationHeader(uuid)
        self.assertEqual(location, {'Location': 'http-resource/uuid'})


class APIGatewayCreateResponse(unittest.TestCase):
    def testWithoutParameters(self):
        '''APIGateway.createResponse() should create a response with statusCode 200, the Access-Control-Allow-Origin
        header and a body with an empty JSON if called without parameters'''
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        response = sut.createResponse()
        self.assertEqual(response, {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': '{}'})

    def testWithAllParameters(self):
        '''APIGateway.createResponse() should create a response with the passed statusCode, the
        Access-Control-Allow-Origin header added to the passed headers and the conversiont to json
        of the passed body as body'''
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        body = {'this': {'is': {'the': 'body'}}}
        response = sut.createResponse(123, {'h': 'header'}, body)
        self.assertEqual(response, {
            'statusCode': 123,
            'headers': {'Access-Control-Allow-Origin': '*', 'h': 'header'},
            'body': json.dumps(body, default=jsonutils.dumpdefault)
        })


class APIGatewayCreateErrorResponse(unittest.TestCase):

    def testWithHttpError(self):
        '''APIGateway.createErrorResponse() should create a response with the statusCode of the passed HttpError, the
        Access-Control-Allow-Origin header and the conversion to json of the __dict__ of the passed HttpError as
        body'''
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        error = HttpError(HttpError.NOT_FOUND, 'message')
        response = sut.createErrorResponse(error)
        self.assertEqual(response, {
            'statusCode': error.statusCode,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(error.__dict__, default=jsonutils.dumpdefault)
        })

    def testWithNspError(self):
        '''APIGateway.createErrorResponse() should wrap the passed NspError in an HttpError and then create an error
        response with it'''
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        error = NspError(NspError.THING_NOT_FOUND, 'message')
        httpError = HttpError.wrap(error)
        httpError.method = sut.getHttpMethod()
        httpError.resource = sut.getHttpResource()
        response = sut.createErrorResponse(error)
        self.assertEqual(response, {
            'statusCode': httpError.statusCode,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(httpError.__dict__, default=jsonutils.dumpdefault)
        })

    def testWithException(self):
        '''APIGateway.createErrorResponse() should wrap the passed Exception in an HttpError and the create an error
        response with it'''
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        error = KeyError('unknown')
        httpError = HttpError.wrap(error)
        httpError.method = sut.getHttpMethod()
        httpError.resource = sut.getHttpResource()
        response = sut.createErrorResponse(error)
        self.assertEqual(response['statusCode'], httpError.statusCode)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['message'], httpError.message)
        self.assertEqual(body['method'], httpError.method)
        self.assertEqual(body['resource'], httpError.resource)
        self.assertIsInstance(body['causes'], list)
        self.assertIs(len(body['causes']), 1)
        print(httpError.message)


class APIGatewayGetAndValidateEntity(unittest.TestCase):
    def testNotJSON(self):
        'APIGateway.getAndValidateEntity() should raise a 415 HttpError if Content-Type is not `application/json`'
        event = {
            'headers': {
                'Content-Type': 'application/xml'
            }
        }
        sut = APIGateway(mockLoggerFactory, event)
        schema = {}
        name = 'entity'
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidateEntity(schema, name)
        self.assertEqual(cm.exception.statusCode, 415)
        self.assertEqual(cm.exception.message, 'Expected application/json Content-Type')

    def testMissing(self):
        'APIGateway.getAndValidateEntity() should raise a 400 HttpError if body is missing'
        event = {}
        sut = APIGateway(mockLoggerFactory, event)
        schema = {}
        name = 'entity'
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidateEntity(schema, name)
        self.assertEqual(cm.exception.statusCode, 400)
        self.assertEqual(cm.exception.message, 'Missing entity')

    def testMalformedJSON(self):
        'APIGateway.getAndValidateEntity() should raise a 400 HttpError if body is not a JSON string'
        event = {
            'body': 'hello'
        }
        sut = APIGateway(mockLoggerFactory, event)
        schema = {}
        name = 'entity'
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidateEntity(schema, name)
        self.assertEqual(cm.exception.statusCode, 400)
        self.assertEqual(cm.exception.message, 'Malformed entity JSON')
        self.assertIsInstance(cm.exception.causes, list)
        self.assertGreater(len(cm.exception.causes), 0)
        for i in range(len(cm.exception.causes)):
            with self.subTest(i=i):
                self.assertIsInstance(cm.exception.causes[i], str)

    def testInvalidJSON(self):
        'APIGateway.getAndValidateEntity() should raise a 422 HttpError if body is not a valid JSON'
        event = {
            'body': '[1]'
        }
        sut = APIGateway(mockLoggerFactory, event)
        schema = {'type': 'object'}
        name = 'entity'
        with self.assertRaises(HttpError) as cm:
            sut.getAndValidateEntity(schema, name)
        self.assertEqual(cm.exception.statusCode, 422)
        self.assertEqual(cm.exception.message, 'Invalid entity')
        self.assertIsInstance(cm.exception.causes, list)
        self.assertGreater(len(cm.exception.causes), 0)
        for i in range(len(cm.exception.causes)):
            with self.subTest(i=i):
                self.assertIsInstance(cm.exception.causes[i], str)

    def testOK(self):
        'APIGateway.getAndValidateEntity() should return the parsed entity as a dictionary with the datetimes converted'
        e = {
            'name': 'entity',
            'created': '2013-01-31T03:45:00.000Z'
        }
        expected = e.copy()
        expected['created'] = jsonutils.json2datetime(e['created'])
        event = {
            'body': json.dumps(e, default=jsonutils.dumpdefault)
        }
        sut = APIGateway(mockLoggerFactory, event)
        schema = {'type': 'object'}
        name = 'entity'
        entity = sut.getAndValidateEntity(schema, name)
        self.assertEqual(entity, expected)
