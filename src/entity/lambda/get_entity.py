from src.container import Container


def handler(event, context, container=Container()):
    try:
        return container.entityLambdaMapper().getEntity(event)
    finally:
        container.shutdown()
