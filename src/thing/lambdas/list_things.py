from src.container import Container


def handler(event, context=None, container=Container()):
    try:
        return container.thingLambdaMapper().listThings(event)
    finally:
        container.shutdown()
