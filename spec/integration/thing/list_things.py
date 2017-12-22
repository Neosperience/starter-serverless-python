import json
import unittest
import email.utils

from src.thing.lambdas.list_things import handler
from src.commons.jsonutils import json2datetime
from src.container import Container

ISO_DATETIME_Z_REGEX = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'


# TODO owner filter, non admin
class ListThingLambdaSpec(unittest.TestCase):
    def setUp(self):
        self.principal = {
            'organizationId': 'ORG001',
            'roles': ['ROLE_THING_USER']
        }
        self.container = Container()

    def test401(self):
        'Should return a 401 response if there is no principal'
        event = {
            'httpMethod': 'GET',
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
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/thing')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test403NotAuthorized(self):
        'Should return a 403 response if the principal is not authorized'
        self.principal['roles'].clear()
        event = {
            'httpMethod': 'GET',
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
            }
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 403)
        self.assertEqual(body['statusReason'], 'Forbidden')
        self.assertEqual(body['message'], 'Principal is not authorized to list things')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/thing')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test403NonAdminCannotSetOwnerFilter(self):
        'Should return a 403 response if the principal is not admin and the owner parameter is present'
        event = {
            'httpMethod': 'GET',
            'path': '/thing?owner=owner',
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
            'queryStringParameters': {
                'owner': 'owner'
            }
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(response['headers'], {'Access-Control-Allow-Origin': '*'})
        body = json.loads(response['body'])
        self.assertEqual(body['statusCode'], 403)
        self.assertEqual(body['statusReason'], 'Forbidden')
        self.assertEqual(body['message'], 'Principal is not authorized to choose an owner filter')
        self.assertEqual(body['causes'], [])
        self.assertEqual(body['method'], 'GET')
        self.assertEqual(body['resource'], 'http://localhost/thing?owner=owner')
        self.assertRegex(body['timestamp'], ISO_DATETIME_Z_REGEX)

    def test200Admin(self):
        'Should return a 200 response with the all the things'
        self.principal['roles'].append('ROLE_ADMIN')
        event = {
            'httpMethod': 'GET',
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
            }
        }
        response = handler(event, None, self.container)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers'], {
            'Access-Control-Allow-Origin': '*'
        })
        body = json.loads(response['body'])
        for thing in body:
            thing['created'] = json2datetime(thing['created'])
            thing['lastModified'] = json2datetime(thing['lastModified'])
        self.assertEqual(body, list(self.container.thingRepository().data.values()))
