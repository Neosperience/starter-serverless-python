from src.container import Container


def oldHandler(event, context=None, container=Container()):
    try:
        return container.thingLambdaMapper().listThings(event)
    finally:
        container.shutdown()


def handler(event, context, container=None):
    try:
        container = Container()
        return container.thingLambdaMapper().listThings(event)
    finally:
        if container:
            container.shutdown()
