from datetime import datetime

from src.commons.nsp_error import NspError


class HttpError(Exception):
    BAD_REQUEST = 400
    CONFLICT = 409
    FORBIDDEN = 403
    INTERNAL_SERVER_ERROR = 500
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    UNPROCESSABLE_ENTITY = 422
    UNSUPPORTED_MEDIA_TYPE = 415

    STATUS_REASONS = {
        BAD_REQUEST: 'Bad request',
        CONFLICT: 'Conflict',
        FORBIDDEN: 'Forbidden',
        INTERNAL_SERVER_ERROR: 'Internal server error',
        NOT_FOUND: 'Not found',
        UNAUTHORIZED: 'Unauthorized',
        UNPROCESSABLE_ENTITY: 'Unprocessable entity',
        UNSUPPORTED_MEDIA_TYPE: 'Unsupported media type'
    }

    ERROR_CODES_TO_STATUS_CODES = {}
    ERROR_CODES_TO_STATUS_CODES[NspError.THING_ALREADY_EXISTS] = CONFLICT
    ERROR_CODES_TO_STATUS_CODES[NspError.THING_NOT_FOUND] = NOT_FOUND
    ERROR_CODES_TO_STATUS_CODES[NspError.THING_UNPROCESSABLE] = UNPROCESSABLE_ENTITY
    ERROR_CODES_TO_STATUS_CODES[NspError.FORBIDDEN] = FORBIDDEN

    def wrap(cls, error):
        if isinstance(error, NspError):
            statusCode = cls.ERROR_CODES_TO_STATUS_CODES.get(error.code, cls.INTERNAL_SERVER_ERROR)
            httpError = HttpError(statusCode, error.message, error.causes, error.timestamp)
        else:
            httpError = HttpError(cls.INTERNAL_SERVER_ERROR, repr(error))
        return httpError
    wrap = classmethod(wrap)

    def __init__(self, statusCode, message, causes=[], timestamp=None):
        Exception.__init__(self, message)
        self.statusCode = statusCode
        self.statusReason = self.STATUS_REASONS[statusCode]
        self.message = message
        self.causes = causes
        self.timestamp = timestamp or datetime.now()
