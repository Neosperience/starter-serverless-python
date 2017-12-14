import dependency_injector.containers as containers
import dependency_injector.providers as providers

from src.commons.api_gateway import APIGateway

from src.entity.lambda_mapper import LambdaMapper as EntityLambdaMapper
from src.entity.authorizer import Authorizer as EntityAuthorizer
from src.entity.logic import Logic as EntityLogic
from src.entity.repository import Repository as EntityRepository


def Container():
    class Cont(containers.DeclarativeContainer):
        apiGatewayFactory = providers.DelegatedFactory(APIGateway)
        entityRepository = providers.Singleton(EntityRepository)
        entityLogic = providers.Singleton(EntityLogic, entityRepository)
        entityAuthorizer = providers.Singleton(EntityAuthorizer, entityLogic)
        entityLambdaMapper = providers.Singleton(EntityLambdaMapper, entityAuthorizer, apiGatewayFactory)

        def shutdown():
            pass

    return Cont
