from src.commons.nsp_error import NspError


class Principal:

    ROLE_ADMIN = 'ROLE_ADMIN'

    def __init__(self, principal):
        self.__dict__ = principal

    def isAdmin(self):
        return self.ROLE_ADMIN in self.roles

    def checkAuthorization(self, requiredRoles, operation):
        if len(self.roles.intersection(requiredRoles)) == 0:
            raise NspError(NspError.FORBIDDEN, 'Principal is not authorized to {0}'.format(operation))

    def checkVisibility(self, entity, entityName, errorCode):
        if not self.isAdmin() and entity.get('owner') != self.organizationId:
            raise NspError(errorCode, '{0} "{1}" not found'.format(entityName.capitalize(), entity['uuid']))
