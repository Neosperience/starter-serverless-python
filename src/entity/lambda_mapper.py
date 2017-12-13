from src.commons.api_gateway import APIGateway
import traceback


def LambdaMapper(authorizer):

    class Service:
        def getEntity(self, event):
            apiGateway = APIGateway(event)  # temp, si deve iniettare la factory
            try:
                principal = apiGateway.getAndValidatePrincipal()
                uuid = apiGateway.getPathParameter('uuid', required=True)
                result = authorizer.getEntity(principal, uuid)
                return apiGateway.createResponse(body=result)
            except Exception as error:
                return apiGateway.createErrorResponse(error)

    return Service()
