import unittest
from unittest.mock import MagicMock

from src.commons.principal import Principal
from src.commons.nsp_error import NspError
from src.entity.lambda_mapper import LambdaMapper


class LambdaMapperGetEntity(unittest.TestCase):

    def setUp(self):
        self.authorizer = MagicMock()
        self.apiGateway = MagicMock()
        self.apiGatewayFactory = MagicMock(return_value=self.apiGateway)
        self.sut = LambdaMapper(self.authorizer, self.apiGatewayFactory)

    def test_ItCallsMethods(self):
        'EntityLambdaMapper.getEntity() should call the right methods with the right parameters'
        self.apiGateway.getAndValidatePrincipal.return_value = 'principal'
        self.apiGateway.getPathParameter.return_value = 'uuid'
        self.apiGateway.createResponse.return_value = None
        self.authorizer.getEntity.return_value = 'entity'

        self.sut.getEntity('event')

        self.apiGatewayFactory.assert_called_once_with('event')
        self.apiGateway.getAndValidatePrincipal.assert_called_once_with()
        self.apiGateway.getPathParameter.assert_called_once_with('uuid', required=True)
        self.authorizer.getEntity.assert_called_once_with('principal', 'uuid')
        self.apiGateway.createResponse.assert_called_once_with(body='entity')

    def test_ItReturnsResultResponseOnInvalidPrincipal(self):
        'EntityLambdaMapper.getEntity() should call apiGateway.createErrorResponse() if the principal is not valid'
        error = Exception('error')
        self.apiGateway.getAndValidatePrincipal.side_effect = error

        self.sut.getEntity('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def test_ItReturnsResultResponseOnInvalidUUIDParameter(self):
        'EntityLambdaMapper.getEntity() should call apiGateway.createErrorResponse() if the uuid parameter is not valid'
        error = Exception('error')
        self.apiGateway.getPathParameter.side_effect = error

        self.sut.getEntity('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)

    def test_ItReturnsResultResponseOnInvalidEntity(self):
        'EntityLambdaMapper.getEntity() should call apiGateway.createErrorResponse() if authorizer.getEntity() raises'
        error = Exception('error')
        self.authorizer.getEntity.side_effect = error

        self.sut.getEntity('event')
        self.apiGateway.createErrorResponse.assert_called_once_with(error)
