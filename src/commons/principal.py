from src.commons.nsp_error import NspError


def raiseForbiddenError(action):
    raise NspError(NspError.FORBIDDEN, 'Principal is not authorized to {0}'.format(action))


class Principal:

    ROLE_ADMIN = 'ROLE_ADMIN'

    def __init__(self, principal):
        self.__dict__ = principal

    def isAdmin(self):
        return self.ROLE_ADMIN in self.roles

    def checkAuthorization(self, requiredRoles, action):
        if len(self.roles.intersection(requiredRoles)) == 0:
            raiseForbiddenError(action)

    def checkVisibility(self, entity, entityName, errorCode):
        if not self.isAdmin() and entity.get('owner') != self.organizationId:
            raise NspError(errorCode, '{0} "{1}" not found'.format(entityName.capitalize(), entity['uuid']))

    def checkReadOnlyProperties(self, oldEntity, newEntity, readOnlyProperties, errorCode):
        if not self.isAdmin():
            readOnlyProperties = readOnlyProperties.copy()
            readOnlyProperties.append('owner')
        errors = []
        for property in readOnlyProperties:
            if not oldEntity[property] == newEntity[property]:
                errors.append('Cannot change read-only property {0} from {1} to {2}'.format(
                    property, repr(oldEntity[property]), repr(newEntity[property])
                ))
        if errors:
            raise NspError(errorCode, 'Cannot change read-only properties', errors)

    def getOwner(self, owner):
        if owner is None:
            return self.organizationId
        if self.isAdmin():
            return owner
        raiseForbiddenError('choose an owner')

    def getOwnerFilter(self, owner):
        if self.isAdmin():
            return owner
        if owner is not None:
            raiseForbiddenError('choose an owner filter')
        return self.organizationId
