from datetime import datetime


class NspError(Exception):
    ENTITY_NOT_FOUND = 'ENTITY_NOT_FOUND'
    FORBIDDEN = 'FORBIDDEN'

    def __init__(self, code, message, causes=[]):
        Exception.__init__(self, message)
        self.code = code
        self.message = message
        self.causes = causes
        self.timestamp = datetime.now()
