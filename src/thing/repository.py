from datetime import datetime


def Repository():

    now = datetime.now()
    data = {
        '001': {
            'uuid': '001',
            'owner': 'ORG001',
            'name': 'Thing1',
            'description': 'Thing 001',
            'created': now,
            'lastModified': now
        },
        '002': {
            'uuid': '002',
            'owner': 'ORG002',
            'name': 'Thing2',
            'description': 'Thing 002',
            'created': now,
            'lastModified': now
        },
        '003': {
            'uuid': '003',
            'owner': 'ORG001',
            'name': 'Thing2',
            'description': 'Thing 003',
            'created': now,
            'lastModified': now
        },
    }

    class Service:
        def createThing(self, thing):
            data[thing.uuid] = thing
            return thing

        def getThing(self, uuid):
            return data.get(uuid)

        def updateThing(self, uuid, thing):
            data[thing.uuid] = thing
            return thing

        def deleteThing(self, uuid):
            del data[uuid]

        def listThings(self, owner):
            return [thing for thing in data.values() if owner is None or thing.owner == owner]

    return Service()
