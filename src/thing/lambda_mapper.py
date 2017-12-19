import json


def LambdaMapper(authorizer, apiGatewayFactory):

    thingCreateSchema = json.load(open('resources/json-schemas/thing-create.json'))
    thingUpdateSchema = json.load(open('resources/json-schemas/thing-update.json'))

    class Service:
        def createThing(self, event):
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                thing = apiGateway.getAndValidateThing(thingCreateSchema, 'thing')
                result = authorizer.createThing(principal, thing)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def getThing(self, event):
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                result = authorizer.getThing(principal, uuid)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def updateThing(self, event):
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                thing = apiGateway.getAndValidateThing(thingUpdateSchema, 'thing')
                result = authorizer.updateThing(principal, uuid, thing)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def deleteThing(self, event):
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                result = authorizer.deleteThing(principal, uuid)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

        def listThings(self, event):
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                owner = apiGateway.getQueryParameter('owner')
                result = authorizer.listThings(principal, owner)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

    return Service()
