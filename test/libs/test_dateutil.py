import unittest, datetime
from libs.dateutil import parse_date


class TestDateParser(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("2010-05-10", "%Y-%m-%d"), datetime.datetime(2010, 5, 10))
        self.assertEqual(parse_date("2010-05-10", "%Y-%d-%m"), datetime.datetime(2010, 10, 5))

        err = parse_date("2010-20-05", "%Y-%m-%d")
        self.assertIsInstance(err, ValueError)
        self.assertEqual(str(err), "Invalid datetime value: 2010-20-05 (%Y-%m-%d)")

        err = parse_date("2010-05-20 10:00:00", "%Y-%m-%d")
        self.assertIsInstance(err, ValueError)
        self.assertEqual(str(err), "Invalid datetime value: 2010-05-20 10:00:00 (%Y-%m-%d)")

        err = parse_date("2010-05-20", "%Y-%m-%d %H:%M:%S")
        self.assertIsInstance(err, ValueError)
        self.assertEqual(str(err), "Invalid datetime value: 2010-05-20 (%Y-%m-%d %H:%M:%S)")
