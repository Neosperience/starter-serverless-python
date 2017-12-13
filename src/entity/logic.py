from src.commons.nsp_error import NspError


def Logic(repository):

    class Service:
        def getEntity(self, principal, uuid):
            entity = repository.getEntity(uuid)
            if entity is None:
                raise NspError(NspError.ENTITY_NOT_FOUND, 'Entity "{0}" not found'.format(uuid))
            else:
                principal.checkVisibility(entity, 'Entity', NspError.ENTITY_NOT_FOUND)
                return entity

    return Service()
