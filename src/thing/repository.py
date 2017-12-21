import logging
from datetime import datetime, timedelta


def Repository(loggerFactory):

    logger = loggerFactory(__name__)

    created = datetime(year=2103, month=1, day=31, hour=3, minute=45, second=1, microsecond=234000)
    lastModified = datetime(year=2108, month=1, day=1, hour=12, minute=12, second=12, microsecond=345000)
    data = {
        '001': {
            'uuid': '001',
            'owner': 'ORG001',
            'name': 'Thing1',
            'description': 'Thing 001',
            'created': created,
            'lastModified': lastModified
        },
        '002': {
            'uuid': '002',
            'owner': 'ORG002',
            'name': 'Thing2',
            'description': 'Thing 002',
            'created': created + timedelta(hours=1),
            'lastModified': lastModified + timedelta(hours=1)
        },
        '003': {
            'uuid': '003',
            'owner': 'ORG001',
            'name': 'Thing3',
            'description': 'Thing 003',
            'created': created + timedelta(hours=2),
            'lastModified': lastModified + timedelta(hours=2)
        },
    }

    class Service:
        def createThing(self, thing):
            logger.debug('createThing(): thing=%s', thing)
            data[thing['uuid']] = thing
            return thing

        def getThing(self, uuid):
            logger.debug('getThing(): uuid=%s', uuid)
            return data.get(uuid)

        def updateThing(self, thing):
            logger.debug('updateThing(): thing=%s', thing)
            data[thing['uuid']] = thing
            return thing

        def deleteThing(self, uuid):
            logger.debug('deleteThing(): uuid=%s', uuid)
            del data[uuid]

        def listThings(self, owner):
            logger.debug('listThings(): owner=%s', owner)
            return [thing for thing in data.values() if owner is None or thing['owner'] == owner]

    return Service()
