import json
import logging


def LambdaMapper(loggerFactory, apiGatewayFactory, authorizer):

    with open('resources/json-schemas/thing-create.json') as infile:
        thingCreateSchema = json.load(infile)
    with open('resources/json-schemas/thing-update.json') as infile:
        thingUpdateSchema = json.load(infile)
    logger = loggerFactory(__name__)

    class Service:
        def createThing(self, event):
            logger.debug('createThing(): event=%s', event)
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                thing = apiGateway.getAndValidateEntity(thingCreateSchema, 'thing')
                result = authorizer.createThing(principal, thing)
                return apiGateway.createResponse(
                    statusCode=201,
                    headers=apiGateway.createLocationHeader(result['uuid']),
                    body=result
                )
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def getThing(self, event):
            logger.debug('getThing(): event=%s', event)
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                result = authorizer.getThing(principal, uuid)
                if apiGateway.wasModifiedSince(result):
                    return apiGateway.createResponse(
                        body=result,
                        headers=apiGateway.createLastModifiedHeader(result)
                    )
                else:
                    return apiGateway.createResponse(statusCode=304)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def updateThing(self, event):
            logger.debug('updateThing(): event=%s', event)
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                thing = apiGateway.getAndValidateEntity(thingUpdateSchema, 'thing')
                result = authorizer.updateThing(principal, uuid, thing)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def deleteThing(self, event):
            logger.debug('deleteThing(): event=%s', event)
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                result = authorizer.deleteThing(principal, uuid)
                return apiGateway.createResponse(statusCode=204, body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def listThings(self, event):
            logger.debug('listThings(): event=%s', event)
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                owner = apiGateway.getQueryStringParameter('owner', required=False)
                result = authorizer.listThings(principal, owner)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

    return Service()
