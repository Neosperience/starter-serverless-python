import dependency_injector.containers as containers
import dependency_injector.providers as providers

from src.commons.api_gateway import APIGateway

from src.thing.lambda_mapper import LambdaMapper as EntityLambdaMapper
from src.thing.authorizer import Authorizer as EntityAuthorizer
from src.thing.logic import Logic as EntityLogic
from src.thing.repository import Repository as EntityRepository


def Container():
    class Cont(containers.DeclarativeContainer):
        config = providers.Configuration('config/config.json')
        apiGatewayFactory = providers.DelegatedFactory(APIGateway)
        thingRepository = providers.Singleton(EntityRepository)
        thingLogic = providers.Singleton(EntityLogic, thingRepository)
        thingAuthorizer = providers.Singleton(EntityAuthorizer, thingLogic)
        thingLambdaMapper = providers.Singleton(EntityLambdaMapper, thingAuthorizer, apiGatewayFactory)

        def shutdown():
            pass

    return Cont
