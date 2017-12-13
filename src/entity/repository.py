from datetime import datetime


def Repository():

    class Service:
        def getEntity(self, uuid):
            return {
                'uuid': uuid,
                'owner': 'ORG001',
                'name': 'Dario',
                'created': datetime.now()
            } if uuid == 'dario' else None

    return Service()
