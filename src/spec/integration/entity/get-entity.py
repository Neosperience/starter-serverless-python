import json
import unittest

from src.entity.lambdas.get_entity import handler

ISO_DATETIME_Z_REGEX = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'


class GetEntityLambdaSpec(unittest.TestCase):
    def setUp(self):
        self.principal = {
            'organizationId': 'ORG001',
            'roles': ['ROLE_ENTITY_USER']
        }

    def test_401(self):
        'Should return a 401 response if there is no principal'
        uuid = 'dario'
        event = {
            'httpMethod': 'GET',
            'path': '/entity/{0}'.format(uuid),
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': None
                }
            },
            'pathParameters': {
                'uuid': uuid
            }
        }
        response = handler(event)
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 401)
        self.assertEqual(body['statusReason'], 'Unauthorized')
        self.assertEqual(body['message'], 'Missing principal')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/entity/dario')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test_400(self):
        'Should return a 400 response if there is no uuid'
        uuid = 'dario'
        event = {
            'httpMethod': 'GET',
            'path': '/entity/{0}'.format(uuid),
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': json.dumps(self.principal)
                }
            },
            'pathParameters': None
        }
        response = handler(event)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 400)
        self.assertEqual(body['statusReason'], 'Bad request')
        self.assertEqual(body['message'], 'Missing path parameter "uuid"')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/entity/dario')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test_403(self):
        'Should return a 403 response if the principal is not authorized'
        self.principal['roles'].clear()
        uuid = 'dario'
        event = {
            'httpMethod': 'GET',
            'path': '/entity/{0}'.format(uuid),
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': json.dumps(self.principal)
                }
            },
            'pathParameters': {
                'uuid': uuid
            }
        }
        response = handler(event)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 403)
        self.assertEqual(body['statusReason'], 'Forbidden')
        self.assertEqual(body['message'], 'Principal is not authorized to get entities')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/entity/dario')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test_404NotExists(self):
        'Should return a 404 response if the entity does not exist'
        uuid = 'unknown'
        event = {
            'httpMethod': 'GET',
            'path': '/entity/{0}'.format(uuid),
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': json.dumps(self.principal)
                }
            },
            'pathParameters': {
                'uuid': uuid
            }
        }
        response = handler(event)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 404)
        self.assertEqual(body['statusReason'], 'Not found')
        self.assertEqual(body['message'], 'Entity "unknown" not found')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/entity/unknown')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test_404NotOwned(self):
        'Should return a 404 response if the entity is not owned'
        self.principal['organizationId'] = 'ANOTHER'
        uuid = 'dario'
        event = {
            'httpMethod': 'GET',
            'path': '/entity/{0}'.format(uuid),
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': json.dumps(self.principal)
                }
            },
            'pathParameters': {
                'uuid': uuid
            }
        }
        response = handler(event)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 404)
        self.assertEqual(body['statusReason'], 'Not found')
        self.assertEqual(body['message'], 'Entity "dario" not found')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/entity/dario')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test_200(self):
        'Should return a 200 response with the requested entity'
        uuid = 'dario'
        event = {
            'httpMethod': 'GET',
            'path': '/entity/{0}'.format(uuid),
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': json.dumps(self.principal)
                }
            },
            'pathParameters': {
                'uuid': uuid
            }
        }
        response = handler(event)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['uuid'], uuid)
        self.assertEqual(body['owner'], self.principal['organizationId'])
        self.assertIsInstance(body['name'], str)
        self.assertRegex(body['created'], ISO_DATETIME_Z_REGEX)
