import unittest
from datetime import datetime, timedelta
from main import check_url_exists, set_log_date


class TestGetCsvUrl(unittest.TestCase):
    def test_empty_string(self):
        self.assertFalse(check_url_exists(''), 'Should return false')

    def test_null_string(self):
        self.assertFalse(check_url_exists(None), 'Should return false')

    def test_happy_path(self):
        self.assertTrue((check_url_exists('https://www.whatever.com'), 'Shout Return True'))


class TestGetLogDate(unittest.TestCase):
    def test_empty_arg(self):
        yesterday = datetime.now() - timedelta(1)
        self.assertEqual(datetime.strftime(yesterday, '%Y-%m-%d'), set_log_date(None))

    def test_with_arg(self):
        date_arg = '2021-03-17'
        self.assertEqual(date_arg, set_log_date(date_arg))

    def test_empty_string(self):
        yesterday = datetime.now() - timedelta(1)
        self.assertEqual(datetime.strftime(yesterday, '%Y-%m-%d'), set_log_date(''), 'expected yesterday, got ' + set_log_date(''))

    def test_assertion_bad_format(self):
        with self.assertRaises(ValueError):
            set_log_date('2010/20/3')


if __name__ == '__main__':
    unittest.main()
