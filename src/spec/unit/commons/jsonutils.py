import unittest
from datetime import datetime, timezone, timedelta
from src.commons.jsonutils import *

ISO_DATETIME_Z_REGEX = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$'


class JSONUtilsNormalizeDateTime(unittest.TestCase):
    def setUp(self):
        self.sut = normalizeDatetime

    def naiveTest(self):
        now = datetime.now()
        naive = self.sut(now)
        self.assertIs(naive, now)

    def awareTest(self, tz):
        aware = datetime.now(tz)
        naive = self.sut(aware)
        self.assertIsNone(naive.tzinfo)
        self.assertEqual(aware.astimezone(timezone.utc).replace(tzinfo=None), naive)

    def testNaive(self):
        'jsonutils.normalizeDatetime() should not convert a naive datetime'
        self.naiveTest()

    def testAwareURC(self):
        'jsonutils.normalizeDatetime() should convert an aware utc datetime to a naive utc datetime'
        self.awareTest(timezone.utc)

    def testAwareNonUTC(self):
        'jsonutils.normalizeDatetime() should convert an aware non utc datetime to a naive utc datetime'
        self.awareTest(timezone(timedelta(seconds=3600)))


class JSONUtilsDateTime2Json(unittest.TestCase):
    def setUp(self):
        self.sut = datetime2json

    def naiveTest(self):
        now = datetime.now()
        str = self.sut(now)
        self.assertRegex(str, ISO_DATETIME_Z_REGEX)
        parsed = dateutil.parser.parse(str)
        self.assertEqual(now.year, parsed.year)
        self.assertEqual(now.month, parsed.month)
        self.assertEqual(now.day, parsed.day)
        self.assertEqual(now.hour, parsed.hour)
        self.assertEqual(now.second, parsed.second)

    def awareTest(self, tz):
        aware = datetime.now(tz)
        str = self.sut(aware)
        self.assertRegex(str, ISO_DATETIME_Z_REGEX)
        parsed = dateutil.parser.parse(str).astimezone(tz)
        self.assertEqual(aware.year, parsed.year)
        self.assertEqual(aware.month, parsed.month)
        self.assertEqual(aware.day, parsed.day)
        self.assertEqual(aware.hour, parsed.hour)
        self.assertEqual(aware.second, parsed.second)

    def testNaive(self):
        'jsonutils.datetime2json() should convert a naive datetime'
        self.naiveTest()

    def testAwareUTC(self):
        'jsonutils.datetime2json() should convert an aware utc datetime'
        self.awareTest(timezone.utc)

    def testAwareNonUTC(self):
        'jsonutils.datetime2json() should convert an aware non utc datetime'
        self.awareTest(timezone(timedelta(seconds=3600)))


class JSONUtilsJson2DateTime(unittest.TestCase):
    def setUp(self):
        self.sut = json2datetime

    def doTest(self, dt, json):
        parsed = self.sut(json)
        self.assertEqual(parsed, dt)

    def testZ(self):
        'jsonutils.json2datetime() should convert a string with Z timezone offset'
        self.doTest(datetime(2013, 1, 31, 3, 45, 0, 123000), '2013-01-31T03:45:00.123Z')

    def testNonZ(self):
        'jsonutils.json2datetime() should convert a string with a numeric timezone offset'
        self.doTest(datetime(2013, 1, 31, 3, 45, 0, 123000), '2013-01-31T04:45:00.123+01:00')


class JSONUtilsDumpDefault(unittest.TestCase):
    def setUp(self):
        self.sut = dumpdefault

    def testDatetime(self):
        'jsonutils.dumpdefault() should convert a datetime to a string using datetime2json()'
        dt = datetime.now()
        obj = self.sut(dt)
        self.assertEqual(obj, datetime2json(dt))

    def testNonDatetime(self):
        'jsonutils.dumpdefault() should convert a non datetime to None'
        obj = self.sut('hello')
        self.assertIsNone(obj)


class JSONUtilsConvertDatetimeValues(unittest.TestCase):
    def setUp(self):
        self.sut = convertDatetimeValues

    def test(self):
        'jsonutils.convertDatetimeValues() should convert only the json datetime strings to datetimes'
        dict1 = {
            'a': 'hello',
            'b': '2013-01-31T03:45:00.123Z',
            'c': '2013-01-31T03:45:00.123Z ',
            'd': [1, False, None, 'hello', '2013-01-31T04:45:00.123+01:00', ['2013-01-31T05:45:00.123+02:00']],
            'e': {
                'a': {
                    'b': '2013-01-31T06:45:00.123+03:00',
                    'a': '2013-01-31 06:45:00.123+03:00'
                }
            }
        }
        dict2 = {
            'a': 'hello',
            'b': json2datetime(dict1['b']),
            'c': '2013-01-31T03:45:00.123Z ',
            'd': [1, False, None, 'hello', json2datetime(dict1['d'][4]), [json2datetime(dict1['d'][5][0])]],
            'e': {
                'a': {
                    'b': json2datetime(dict1['e']['a']['b']),
                    'a': '2013-01-31 06:45:00.123+03:00'
                }
            }
        }
        self.sut(dict1)
        self.assertEqual(dict1, dict2)
