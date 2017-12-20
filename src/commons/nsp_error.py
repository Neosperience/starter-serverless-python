from datetime import datetime


class NspError(Exception):
    THING_NOT_FOUND = 'THING_NOT_FOUND'
    THING_ALREADY_EXISTS = 'THING_ALREADY_EXISTS'
    THING_UNPROCESSABLE = 'THING_UNPROCESSABLE'
    FORBIDDEN = 'FORBIDDEN'
    INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'

    def __init__(self, code, message, causes=[]):
        Exception.__init__(self, message)
        self.code = code
        self.message = message
        self.causes = causes
        self.timestamp = datetime.now()
