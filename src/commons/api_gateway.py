import json
import re
import email.utils

import jsonschema
import dateutil.parser

import src.commons.jsonutils as jsonutils
from src.commons.http_error import HttpError
from src.commons.principal import Principal

__all__ = ['APIGateway']

API_GATEWAY_URL_MATCHER = re.compile('\\.execute-api\\..*\\.amazonaws\\.com$')
APPLICATION_JSON_MATCHER = re.compile('^application/json')
PRINCIPAL_SCHEMA_FILE_NAME = 'resources/json-schemas/principal.json'

with open(PRINCIPAL_SCHEMA_FILE_NAME) as infile:
    principalSchema = json.load(infile)


# TODO gestire list
def getAtPath(obj, path, default):
    if isinstance(path, str):
        path = path.split('.')
    for step in path:
        if not isinstance(obj, dict):
            obj = None
            break
        obj = obj.get(step)
        if obj is None:
            break
    return obj if obj is not None else default


def createResponse(statusCode, headers, body):
    myHeaders = {'Access-Control-Allow-Origin': '*'}
    myHeaders.update(headers)
    response = {
        'statusCode': statusCode,
        'headers': myHeaders,
        'body': json.dumps(body, default=jsonutils.dumpdefault)
    }
    return response


def parseJSON(string, name, errorFactory):
    try:
        return json.loads(string)
    except Exception as parsingError:
        error = errorFactory()
        error.causes = [str(parsingError)]
        raise error


def validateJSON(instance, schema, errorFactory):
    # jsonschema.Draft4Validator.check_schema(schema) (throws SchemaError) per validare lo schema, perché purtroppo
    # scegliendo esplicitamente il validator si dà per scontato che lo schema sia corretto...
    validator = jsonschema.Draft4Validator(schema, format_checker=jsonschema.FormatChecker())
    if not validator.is_valid(instance):
        error = errorFactory()
        error.causes = [e.message for e in validator.iter_errors(instance)]
        raise error


def getAndValidateJSON(string, name, schema, missingErrorFactory, malformedErrorFactory, invalidErrorFactory):
    if string is None:
        raise missingErrorFactory()
    obj = parseJSON(string, name, malformedErrorFactory)
    validateJSON(obj, schema, invalidErrorFactory)
    jsonutils.convertDatetimeValues(obj)
    return obj


class APIGateway:

    def __init__(self, loggerFactory, event):
        self.event = event
        self.logger = loggerFactory(__name__)

    def eventGet(self, path, default=None):
        return getAtPath(self.event, path, default)

    def getHttpMethod(self):
        return self.eventGet('httpMethod', 'UNKNOWN_METHOD')

    def getHttpResource(self):
        protocol = self.eventGet('headers.X-Forwarded-Proto', 'UNKNOWN_PROTOCOL')
        port = self.eventGet('headers.X-Forwarded-Port', 'UNKNOWN_PORT')
        if protocol == 'http' and port == '80' or protocol == 'https' and port == '443':
            port = ''
        else:
            port = ':' + port
        host = self.eventGet('headers.Host', 'UNKNOWN_HOST')
        contextPath = ''
        # add stage as context path when calling API directly:
        if API_GATEWAY_URL_MATCHER.search(host):
            contextPath = '/' + self.eventGet('requestContext.stage', 'UNKNOWN_STAGE')
        path = self.eventGet('path', '/UNKNOWN_PATH')
        return '{protocol}://{host}{port}{contextPath}{path}'.format(
            protocol=protocol, host=host, port=port, contextPath=contextPath, path=path
        )

    def getAndValidatePrincipal(self):
        principal = getAndValidateJSON(
            self.eventGet('requestContext.authorizer.principalId'),
            'principal',
            principalSchema,
            lambda: HttpError(HttpError.UNAUTHORIZED, 'Missing principal'),
            lambda: HttpError(HttpError.UNAUTHORIZED, 'Malformed principal JSON'),
            lambda: HttpError(HttpError.UNAUTHORIZED, 'Invalid principal')
        )
        principal['roles'] = set(principal['roles'])
        return Principal(principal)

    def getPathParameter(self, name, required, validator=None):
        param = self.eventGet('pathParameters.{0}'.format(name))
        if required and not param:
            raise HttpError(HttpError.BAD_REQUEST, 'Missing path parameter "{0}"'.format(name))
        if (validator):
            validator(param)
        return param

    def getQueryStringParameter(self, name, required, validator=None):
        param = self.eventGet('queryStringParameters.{0}'.format(name))
        if required and not param:
            raise HttpError(HttpError.BAD_REQUEST, 'Missing query string parameter "{0}"'.format(name))
        if (validator):
            validator(param)
        return param

    def getHeader(self, name, required, validator=None):
        header = self.eventGet('headers.{0}'.format(name))
        if required and not header:
            raise HttpError(HttpError.BAD_REQUEST, 'Missing header "{0}"'.format(name))
        if (validator):
            validator(header)
        return header

    def getAndValidateEntity(self, schema, name):
        contentType = self.eventGet('headers.Content-Type')
        if contentType and not APPLICATION_JSON_MATCHER.match(contentType):
            raise HttpError(HttpError.UNSUPPORTED_MEDIA_TYPE, 'Expected application/json Content-Type')
        entity = getAndValidateJSON(
            self.eventGet('body'),
            name,
            schema,
            lambda: HttpError(HttpError.BAD_REQUEST, 'Missing entity'),
            lambda: HttpError(HttpError.BAD_REQUEST, 'Malformed entity JSON'),
            lambda: HttpError(HttpError.UNPROCESSABLE_ENTITY, 'Invalid {0}'.format(name))
        )
        return entity

    def wasModifiedSince(self, entity):
        ifModifiedSince = self.eventGet('headers.If-Modified-Since')
        if ifModifiedSince is None:
            return True
        try:
            ifModifiedSince = int(dateutil.parser.parse(ifModifiedSince).timestamp())
            lastModified = int(entity['lastModified'].timestamp())
            return lastModified > ifModifiedSince
        except Exception as e:
            raise HttpError(
                HttpError.BAD_REQUEST,
                'Invalid If-Modified-Since header: "{0}"'.format(ifModifiedSince),
                repr(e)
            )

    def createLastModifiedHeader(self, entity):
        return {
            'Last-Modified': email.utils.formatdate(
                timeval=entity['lastModified'].timestamp(),
                localtime=False,
                usegmt=True
            )
        }

    def createLocationHeader(self, uuid):
        return {'Location': self.getHttpResource() + '/' + uuid}

    def createErrorResponse(self, error):
        if not isinstance(error, HttpError):
            error = HttpError.wrap(error)
        error.method = self.getHttpMethod()
        error.resource = self.getHttpResource()
        return createResponse(error.statusCode, {}, error.__dict__)

    def createResponse(self, statusCode=200, headers={}, body={}):
        return createResponse(statusCode, headers, body)
