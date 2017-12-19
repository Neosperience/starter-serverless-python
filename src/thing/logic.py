from datetime import datetime
import uuid

from src.commons.nsp_error import NspError


def Logic(repository):

    def checkCreate(principal, thing):
        pass

    def checkUpdate(principal, oldThing, newThing):
        principal.checkReadOnlyProperties(
            oldThing,
            newThing,
            ['uuid', 'created', 'lastModified'],
            NspError.THING_UNPROCESSABLE
        )

    def checkDelete(principal, thing):
        pass

    def getAndCheckThing(principal, uuid):
        thing = repository.getThing(uuid)
        if thing is None:
            raise NspError(NspError.THING_NOT_FOUND, 'Thing "{0}" not found'.format(uuid))
        else:
            principal.checkVisibility(thing, 'Thing', NspError.THING_NOT_FOUND)
            return thing

    class Service:
        def createThing(self, principal, thing):
            if thing.get('uuid') is not None:
                existing = repository.getThing(thing.uuid)
                if existing is not None:
                    raise NspError(NspError.THING_ALREADY_EXISTS, 'Thing "{0}" already exists'.format(uuid))
            else:
                thing['uuid'] = str(uuid.uuid4())
            thing['created'] = datetime.now()
            thing['lastModified'] = thing['created']
            checkCreate(principal, thing)
            return repository.createThing(thing)

        def getThing(self, principal, uuid):
            return getAndCheckThing(principal, uuid)

        def updateThing(self, principal, uuid, newThing):
            thing = getAndCheckThing(principal, uuid)
            checkUpdate(principal, thing, newThing)
            thing['lastModified'] = datetime.now()
            return repository.updateThing(newThing)

        def deleteThing(self, principal, uuid):
            thing = getAndCheckThing(principal, uuid)
            checkDelete(principal, thing)
            return repository.deleteThing(uuid)

        def listThings(self, principal, owner):
            return repository.listThings(owner)

    return Service()
