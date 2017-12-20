import logging
import logging.config

import dependency_injector.containers as containers
import dependency_injector.providers as providers

from src.commons.api_gateway import APIGateway

from src.commons.config import loadConfig
from src.thing.lambda_mapper import LambdaMapper as ThingLambdaMapper
from src.thing.authorizer import Authorizer as ThingAuthorizer
from src.thing.logic import Logic as ThingLogic
from src.thing.repository import Repository as ThingRepository


def Container():
    class Cont(containers.DeclarativeContainer):
        config = providers.Configuration('config')
        loggerFactory = providers.DelegatedFactory(logging.getLogger)
        apiGatewayFactory = providers.DelegatedFactory(APIGateway, loggerFactory)
        thingRepository = providers.Singleton(ThingRepository, loggerFactory)
        thingLogic = providers.Singleton(ThingLogic, loggerFactory, thingRepository)
        thingAuthorizer = providers.Singleton(ThingAuthorizer, loggerFactory, thingLogic)
        thingLambdaMapper = providers.Singleton(ThingLambdaMapper, loggerFactory, apiGatewayFactory, thingAuthorizer)

        def shutdown():
            pass

    configDict = loadConfig()
    Cont.config.update(configDict)
    logging.config.dictConfig(Cont.config.logging())
    return Cont
