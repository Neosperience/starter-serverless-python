import re
from datetime import datetime, timezone
import dateutil.parser

ISO_DATETIME_MATCHER = re.compile('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[-+]\d{2}:\d{2})$')


def transformDictionary(obj, select, convert):
    '''
    Recursively traverses a dictionary, selecting the nodes with select() and converting the selected nodes with
    convert()
    '''
    if isinstance(obj, dict):
        for (key, value) in obj.items():
            if (select(key, value)):
                obj[key] = convert(key, value)
            transformDictionary(value, select, convert)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            value = obj[i]
            if (select(i, value)):
                obj[i] = convert(i, value)
            transformDictionary(value, select, convert)


def normalizeDatetime(d):
    'Converts aware datetimes to naive utc'
    return d.astimezone(timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def datetime2json(d):
    'Convert datetimes to naive utc and then to json with millisecond precision and Z timezone'
    return normalizeDatetime(d).isoformat(timespec='milliseconds') + 'Z'


def json2datetime(s):
    'Parses json datetime strings to naive utc datetimes'
    return normalizeDatetime(dateutil.parser.parse(s))


def dumpdefault(obj):
    'Default handler for json.dump that converts datetimes to json datetime strings'
    if isinstance(obj, datetime):
        return datetime2json(obj)


def convertDatetimeValues(dct):
    'Given a dictionary, converts all the strings that match the json datetimeformat to naive utc datetimes'
    def select(key, value):
        return isinstance(value, str) and ISO_DATETIME_MATCHER.match(value)

    def convert(key, value):
        return json2datetime(value)

    transformDictionary(dct, select, convert)
