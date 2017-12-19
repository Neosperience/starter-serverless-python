from src.container import Container


def handler(event, context=None, container=Container()):
    try:
        return container.thingLambdaMapper().deleteThing(event)
    finally:
        container.shutdown()
