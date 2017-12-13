import re
from datetime import datetime, timezone
import dateutil.parser

ISO_DATETIME_MATCHER = re.compile('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[-+]\d{2}:\d{2})$')


def normalizeDatetime(d):
    return d.astimezone(timezone.utc).replace(tzinfo=None)


def datetime2json(d):
    return normalizeDatetime(d).isoformat(timespec='milliseconds') + 'Z'


def json2datetime(s):
    return normalizeDatetime(dateutil.parser.parse(s))


def dumpdefault(obj):
    if isinstance(obj, datetime):
        return datetime2json(obj)


def assignToTree(node, filter, convert):
    if isinstance(node, dict):
        for (key, value) in node.items():
            if (filter(key, value)):
                node[key] = convert(key, value)
            assignToTree(value, filter, convert)
    elif isinstance(node, list):
        for i in range(len(node)):
            value = node[i]
            if (filter(i, value)):
                node[i] = convert(i, value)
            assignToTree(value, filter, convert)


def convertDatetimeValues(dct):
    def filter(key, value):
        return isinstance(value, str) and ISO_DATETIME_MATCHER.match(value)

    def convert(key, value):
        return json2datetime(value)

    assignToTree(dct, filter, convert)
