import json
import unittest
import email.utils

from src.commons.jsonutils import dumpdefault
from src.thing.lambdas.update_thing import handler
from src.commons.jsonutils import json2datetime
from src.container import Container

ISO_DATETIME_Z_REGEX = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'


# TODO completare
class UpdateThingLambdaSpec(unittest.TestCase):
    def setUp(self):
        self.principal = {
            'organizationId': 'ORG001',
            'roles': ['ROLE_THING_USER']
        }
        self.container = Container()

    def test401(self):
        'Should return a 401 response if there is no principal'
        uuid = 'dario'
        event = {
            'httpMethod': 'PUT',
            'path': '/thing/{0}'.format(uuid),
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
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 401)
        self.assertEqual(body['statusReason'], 'Unauthorized')
        self.assertEqual(body['message'], 'Missing principal')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'PUT')
        self.assertEqual(body['resource'], 'http://localhost/thing/dario')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test400(self):
        'Should return a 400 response if there is no uuid'
        uuid = 'dario'
        event = {
            'httpMethod': 'PUT',
            'path': '/thing/{0}'.format(uuid),
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
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 400)
        self.assertEqual(body['statusReason'], 'Bad request')
        self.assertEqual(body['message'], 'Missing path parameter "uuid"')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'PUT')
        self.assertEqual(body['resource'], 'http://localhost/thing/dario')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test403(self):
        'Should return a 403 response if the principal is not authorized'
        self.principal['roles'].clear()
        uuid = '001'
        thing = self.container.thingRepository().data[uuid].copy()
        event = {
            'httpMethod': 'PUT',
            'path': '/thing/{0}'.format(uuid),
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
            },
            'body': json.dumps(thing, default=dumpdefault)
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 403)
        self.assertEqual(body['statusReason'], 'Forbidden')
        self.assertEqual(body['message'], 'Principal is not authorized to update things')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'PUT')
        self.assertEqual(body['resource'], 'http://localhost/thing/{0}'.format(uuid))
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test404NotExists(self):
        'Should return a 404 response if the thing does not exist'
        uuid = 'unknown'
        thing = self.container.thingRepository().data['001'].copy()
        event = {
            'httpMethod': 'PUT',
            'path': '/thing/{0}'.format(uuid),
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
            },
            'body': json.dumps(thing, default=dumpdefault)
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 404)
        self.assertEqual(body['statusReason'], 'Not found')
        self.assertEqual(body['message'], 'Thing "unknown" not found')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'PUT')
        self.assertEqual(body['resource'], 'http://localhost/thing/unknown')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test404NotOwned(self):
        'Should return a 404 response if the thing is not owned'
        self.principal['organizationId'] = 'ANOTHER'
        uuid = '001'
        thing = self.container.thingRepository().data['001'].copy()
        event = {
            'httpMethod': 'PUT',
            'path': '/thing/{0}'.format(uuid),
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
            },
            'body': json.dumps(thing, default=dumpdefault)
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 404)
        self.assertEqual(body['statusReason'], 'Not found')
        self.assertEqual(body['message'], 'Thing "{0}" not found'.format(uuid))
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'PUT')
        self.assertEqual(body['resource'], 'http://localhost/thing/{0}'.format(uuid))
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    # def test200(self):
    #     'Should return a 200 response with the updated thing'
    #     uuid = '001'
    #     event = {
    #         'httpMethod': 'PUT',
    #         'path': '/thing/{0}'.format(uuid),
    #         'headers': {
    #             'Host': 'localhost',
    #             'X-Forwarded-Proto': 'http',
    #             'X-Forwarded-Port': '80'
    #         },
    #         'requestContext': {
    #             'authorizer': {
    #                 'principalId': json.dumps(self.principal)
    #             }
    #         },
    #         'pathParameters': {
    #             'uuid': uuid
    #         }
    #     }
    #     response = handler(event, None, self.container)
    #     self.assertEqual(response['statusCode'], 200)
    #     body = json.loads(response['body'])
    #     self.assertEqual(response['headers'], {
    #         'Access-Control-Allow-Origin': '*',
    #         'Last-Modified': email.utils.formatdate(
    #             timeval=json2datetime(body['lastModified']).timestamp(),
    #             localtime=False,
    #             usegmt=True
    #         )
    #     })
    #     self.assertEqual(body['uuid'], uuid)
    #     self.assertEqual(body['owner'], self.principal['organizationId'])
    #     self.assertIsInstance(body['name'], str)
    #     self.assertRegex(body['created'], ISO_DATETIME_Z_REGEX)
