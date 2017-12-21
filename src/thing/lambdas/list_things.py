from src.container import Container


def handler(event, context, container=None):
    try:
        container = container or Container()
        return container.thingLambdaMapper().listThings(event)
    finally:
        if container:
            container.shutdown()
