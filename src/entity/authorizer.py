def Authorizer(logic):

    class Service:
        def getEntity(self, principal, uuid):
            principal.checkAuthorization({'ROLE_ADMIN', 'ROLE_ENTITY_USER'}, 'get entities')
            return logic.getEntity(principal, uuid)

    return Service()
