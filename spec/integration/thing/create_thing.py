import json
import unittest
import email.utils

from src.commons.jsonutils import dumpdefault
from src.thing.lambdas.create_thing import handler
from src.commons.jsonutils import json2datetime
from src.container import Container

ISO_DATETIME_Z_REGEX = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'


# TODO completare
class CreateThingLambdaSpec(unittest.TestCase):
    def setUp(self):
        self.principal = {
            'organizationId': 'ORG001',
            'roles': ['ROLE_THING_USER']
        }
        self.container = Container()

    def test401(self):
        'Should return a 401 response if there is no principal'
        event = {
            'httpMethod': 'POST',
            'path': '/thing',
            'headers': {
                'Host': 'localhost',
                'X-Forwarded-Proto': 'http',
                'X-Forwarded-Port': '80'
            },
            'requestContext': {
                'authorizer': {
                    'principalId': None
                }
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
        self.assertEqual(body['method'], 'POST')
        self.assertEqual(body['resource'], 'http://localhost/thing')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test403(self):
        'Should return a 403 response if the principal is not authorized'
        self.principal['roles'].clear()
        thing = {
            'name': 'a name',
            'description': 'a description'
        }
        event = {
            'httpMethod': 'POST',
            'path': '/thing',
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
            'body': json.dumps(thing, default=dumpdefault)
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 403)
        self.assertEqual(body['statusReason'], 'Forbidden')
        self.assertEqual(body['message'], 'Principal is not authorized to create things')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'POST')
        self.assertEqual(body['resource'], 'http://localhost/thing')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    # def test201(self):
    #     'Should return a 201 response with the created thing'
    #     uuid = '001'
    #     event = {
    #         'httpMethod': 'POST',
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
