def LambdaMapper(authorizer, apiGatewayFactory):

    class Service:
        def getEntity(self, event):
            apiGateway = apiGatewayFactory(event)
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                result = authorizer.getEntity(principal, uuid)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

    return Service()
