import logging

from src.commons.nsp_error import NspError


def Authorizer(loggerFactory, logic):

    logger = loggerFactory(__name__)

    class Service:
        def createThing(self, principal, thing):
            logger.debug('createThing(): principal=%s, thing=%s', principal, thing)
            principal.checkAuthorization({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'create things')
            thing['owner'] = principal.getOwner(thing.get('owner'))
            return logic.createThing(principal, thing)

        def getThing(self, principal, uuid):
            logger.debug('getThing(): principal=%s, uuid=%s', principal, uuid)
            principal.checkAuthorization({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'get things')
            return logic.getThing(principal, uuid)

        def updateThing(self, principal, uuid, thing):
            logger.debug('updateThing(): principal=%s, uuid=%s, thing=%s', principal, uuid, thing)
            principal.checkAuthorization({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'update things')
            return logic.updateThing(principal, uuid, thing)

        def deleteThing(self, principal, uuid):
            logger.debug('deleteThing(): principal=%s, uuid=%s', principal, uuid)
            principal.checkAuthorization({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'delete things')
            return logic.deleteThing(principal, uuid)

        def listThings(self, principal, owner):
            logger.debug('listThings(): principal=%s, owner=%s', principal, owner)
            principal.checkAuthorization({'ROLE_ADMIN', 'ROLE_THING_USER'}, 'list things')
            owner = principal.getOwnerFilter(owner)
            return logic.listThings(principal, owner)

    return Service()
