import unittest
from main import check_url_exists


class TestGetCsvUrl(unittest.TestCase):
    def test_empty_string(self):
        self.assertTrue(check_url_exists(''), 'Should return false')

    def test_null_string(self):
        self.assertTrue(check_url_exists(None), 'Should return false')

    def test_happy_path(self):
        self.assertTrue((check_url_exists('https://www.whatever.com'), 'Shout Return True'))


if __name__ == '__main__':
    unittest.main()
