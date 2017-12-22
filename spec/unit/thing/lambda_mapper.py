import json
import unittest
from unittest.mock import MagicMock

from src.commons.principal import Principal
from src.commons.nsp_error import NspError
from src.thing.lambda_mapper import LambdaMapper
from spec.helper import mockLoggerFactory

with open('resources/json-schemas/thing-create.json') as infile:
    thingCreateSchema = json.load(infile)
with open('resources/json-schemas/thing-update.json') as infile:
    thingUpdateSchema = json.load(infile)


class LambdaMapperCreateThing(unittest.TestCase):

    def setUp(self):
        self.authorizer = MagicMock()
        self.apiGateway = MagicMock()
        self.apiGatewayFactory = MagicMock(return_value=self.apiGateway)
        self.sut = LambdaMapper(mockLoggerFactory, self.apiGatewayFactory, self.authorizer)

    def testItCallsMethods(self):
        'ThingLambdaMapper.createThing() should call the right methods with the right parameters'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getAndValidateEntity.return_value = {'uuid': 'uuid'}

        self.sut.createThing('event')

        self.apiGatewayFactory.assert_called_once_with('event')
        self.apiGateway.getAndValidatePrincipal.assert_called_once_with()
        self.apiGateway.getAndValidateEntity.assert_called_once_with(thingCreateSchema, 'thing')
        self.authorizer.createThing.assert_called_once_with('principal', {'uuid': 'uuid'})

    def testItReturnsErrorResponseOnInvalidPrincipal(self):
        'ThingLambdaMapper.createThing() should call apiGateway.createErrorResponse() if the principal is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidatePrincipal.side_effect = error

        self.sut.createThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnInvalidThing(self):
        'ThingLambdaMapper.createThing() should call apiGateway.createErrorResponse() if the thing is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidateEntity.side_effect = error

        self.sut.createThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnLogicError(self):
        '''
        ThingLambdaMapper.createThing() should call apiGateway.createErrorResponse() if authorizer.createThing() raises
        '''
        error = Exception('error')
        self.authorizer.createThing.side_effect = error

        self.sut.createThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsResultResponse(self):
        'ThingLambdaMapper.getThing() should return 201 with the thing and the Location header'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getAndValidateEntity.return_value = {'uuid': 'uuid'}
        self.authorizer.createThing.return_value = {'uuid': 'uuid1'}
        self.apiGateway.createLocationHeader.return_value = 'location-header'
        self.apiGateway.createResponse.return_value = None

        self.sut.createThing('event')

        self.apiGateway.createResponse.assert_called_once_with(
            statusCode=201,
            body={'uuid': 'uuid1'},
            headers='location-header'
        )


class LambdaMapperGetThing(unittest.TestCase):

    def setUp(self):
        self.authorizer = MagicMock()
        self.apiGateway = MagicMock()
        self.apiGatewayFactory = MagicMock(return_value=self.apiGateway)
        self.sut = LambdaMapper(mockLoggerFactory, self.apiGatewayFactory, self.authorizer)

    def testItCallsMethods(self):
        'ThingLambdaMapper.getThing() should call the right methods with the right parameters'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'
        self.authorizer.getThing.return_value = 'thing'

        self.sut.getThing('event')
        self.apiGatewayFactory.assert_called_once_with('event')
        self.apiGateway.getAndValidatePrincipal.assert_called_once_with()
        self.apiGateway.getPathParameter.assert_called_once_with('uuid', required=True)
        self.authorizer.getThing.assert_called_once_with('principal', 'uuid')
        self.apiGateway.createLastModifiedHeader.assert_called_once_with('thing')

    def testItReturnsErrorResponseOnInvalidPrincipal(self):
        'ThingLambdaMapper.getThing() should call apiGateway.createErrorResponse() if the principal is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidatePrincipal.side_effect = error

        self.sut.getThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnInvalidUUIDParameter(self):
        'ThingLambdaMapper.getThing() should call apiGateway.createErrorResponse() if the uuid parameter is not valid'
        error = Exception('error')
        self.apiGateway.getPathParameter.side_effect = error

        self.sut.getThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnLogicError(self):
        'ThingLambdaMapper.getThing() should call apiGateway.createErrorResponse() if authorizer.getThing() raises'
        error = Exception('error')
        self.authorizer.getThing.side_effect = error

        self.sut.getThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsResultResponseIfModified(self):
        'ThingLambdaMapper.getThing() should return 200 with the thing if it was modified'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'
        self.apiGateway.wasModifiedSince.return_value = True
        self.apiGateway.createLastModifiedHeader.return_value = 'last-modified-header'
        self.apiGateway.createResponse.return_value = None
        self.authorizer.getThing.return_value = 'thing'

        self.sut.getThing('event')
        self.apiGateway.createResponse.assert_called_once_with(
            body='thing',
            headers='last-modified-header'
        )

    def testItReturnsResultResponseIfNotModified(self):
        'ThingLambdaMapper.getThing() should return 304 if it was not modified'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'
        self.apiGateway.wasModifiedSince.return_value = False
        self.apiGateway.createResponse.return_value = None
        self.authorizer.getThing.return_value = 'thing'

        self.sut.getThing('event')
        self.apiGateway.createResponse.assert_called_once_with(statusCode=304)


class LambdaMapperUpdateThing(unittest.TestCase):

    def setUp(self):
        self.authorizer = MagicMock()
        self.apiGateway = MagicMock()
        self.apiGatewayFactory = MagicMock(return_value=self.apiGateway)
        self.sut = LambdaMapper(mockLoggerFactory, self.apiGatewayFactory, self.authorizer)

    def testItCallsMethods(self):
        'ThingLambdaMapper.updateThing() should call the right methods with the right parameters'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'
        self.apiGateway.getAndValidateEntity.return_value = {'uuid': 'uuid'}

        self.sut.updateThing('event')
        self.apiGatewayFactory.assert_called_once_with('event')
        self.apiGateway.getAndValidatePrincipal.assert_called_once_with()
        self.apiGateway.getAndValidateEntity.assert_called_once_with(thingUpdateSchema, 'thing')
        self.authorizer.updateThing.assert_called_once_with('principal', 'uuid', {'uuid': 'uuid'})

    def testItReturnsErrorResponseOnInvalidPrincipal(self):
        'ThingLambdaMapper.updateThing() should call apiGateway.createErrorResponse() if the principal is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidatePrincipal.side_effect = error

        self.sut.updateThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnInvalidThing(self):
        'ThingLambdaMapper.updateThing() should call apiGateway.createErrorResponse() if the thing is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidateEntity.side_effect = error

        self.sut.updateThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnLogicError(self):
        '''
        ThingLambdaMapper.updateThing() should call apiGateway.createErrorResponse() if authorizer.createThing() raises
        '''
        error = Exception('error')
        self.authorizer.updateThing.side_effect = error

        self.sut.updateThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsResultResponse(self):
        'ThingLambdaMapper.updateThing() should return 200 with the thing and the Last-Modified header'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getAndValidateEntity.return_value = {'uuid': 'uuid'}
        self.authorizer.updateThing.return_value = {'uuid': 'uuid1'}
        self.apiGateway.createResponse.return_value = None

        self.sut.updateThing('event')
        self.apiGateway.createResponse.assert_called_once_with(
            body={'uuid': 'uuid1'},
        )


class LambdaMapperDeleteThing(unittest.TestCase):

    def setUp(self):
        self.authorizer = MagicMock()
        self.apiGateway = MagicMock()
        self.apiGatewayFactory = MagicMock(return_value=self.apiGateway)
        self.sut = LambdaMapper(mockLoggerFactory, self.apiGatewayFactory, self.authorizer)

    def testItCallsMethods(self):
        'ThingLambdaMapper.deleteThing() should call the right methods with the right parameters'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'

        self.sut.deleteThing('event')
        self.apiGatewayFactory.assert_called_once_with('event')
        self.apiGateway.getAndValidatePrincipal.assert_called_once_with()
        self.apiGateway.getPathParameter.assert_called_once_with('uuid', required=True)
        self.authorizer.deleteThing.assert_called_once_with('principal', 'uuid')

    def testItReturnsErrorResponseOnInvalidPrincipal(self):
        'ThingLambdaMapper.deleteThing() should call apiGateway.createErrorResponse() if the principal is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidatePrincipal.side_effect = error

        self.sut.deleteThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnInvalidUUIDParameter(self):
        '''
        ThingLambdaMapper.deleteThing() should call apiGateway.createErrorResponse() if the uuid parameter is not valid
        '''
        error = Exception('error')
        self.apiGateway.getPathParameter.side_effect = error

        self.sut.deleteThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnLogicError(self):
        '''
        ThingLambdaMapper.deleteThing() should call apiGateway.createErrorResponse() if authorizer.deleteThing() raises
        '''
        error = Exception('error')
        self.authorizer.deleteThing.side_effect = error

        self.sut.deleteThing('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsResultResponse(self):
        'ThingLambdaMapper.deleteThing() should return 204 with an empty body'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'
        self.apiGateway.createResponse.return_value = None
        self.authorizer.deleteThing.return_value = 'thing'

        self.sut.deleteThing('event')
        self.apiGateway.createResponse.assert_called_once_with(statusCode=204)


class LambdaMapperListThings(unittest.TestCase):

    def setUp(self):
        self.authorizer = MagicMock()
        self.apiGateway = MagicMock()
        self.apiGatewayFactory = MagicMock(return_value=self.apiGateway)
        self.sut = LambdaMapper(mockLoggerFactory, self.apiGatewayFactory, self.authorizer)

    def testItCallsMethods(self):
        'ThingLambdaMapper.listThings() should call the right methods with the right parameters'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getQueryStringParameter.return_value = 'owner'

        self.sut.listThings('event')
        self.apiGatewayFactory.assert_called_once_with('event')
        self.apiGateway.getAndValidatePrincipal.assert_called_once_with()
        self.apiGateway.getQueryStringParameter.assert_called_once_with('owner', required=False)
        self.authorizer.listThings.assert_called_once_with('principal', 'owner')

    def testItReturnsErrorResponseOnInvalidPrincipal(self):
        'ThingLambdaMapper.listThings() should call apiGateway.createErrorResponse() if the principal is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidatePrincipal.side_effect = error

        self.sut.listThings('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsErrorResponseOnLogicError(self):
        '''
        ThingLambdaMapper.listThings() should call apiGateway.createErrorResponse() if authorizer.listThings() raises
        '''
        error = Exception('error')
        self.authorizer.listThings.side_effect = error

        self.sut.listThings('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def testItReturnsResultResponse(self):
        'ThingLambdaMapper.listThings() should return 200 with the result of authorizer.listThings()'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getQueryStringParameter.return_value = 'owner'
        self.apiGateway.createResponse.return_value = None
        self.authorizer.listThings.return_value = 'things'

        self.sut.listThings('event')
        self.apiGateway.createResponse.assert_called_once_with(body='things')
