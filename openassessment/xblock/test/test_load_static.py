"""
Test load static class
"""

from unittest.mock import patch
from django.test import TestCase, override_settings
from openassessment.xblock.load_static import LoadStatic, urljoin


class TestLoadStatic(TestCase):
    """Test load static class"""
    default_base_url = '/static/dist/'

    def setUp(self):
        LoadStatic._manifest = {}   # pylint: disable=protected-access
        LoadStatic._is_loaded = False   # pylint: disable=protected-access
        LoadStatic._base_url = ''   # pylint: disable=protected-access
        return super().setUp()

    def test_urljoin(self):
        expected_result_1 = 'path_1/path_2'
        expected_result_2 = 'path_1/path_2/'
        expected_result_3 = '/path_1/path_2'
        expected_result_4 = '/path_1/path_2/'

        self.assertEqual(expected_result_1, urljoin('path_1', 'path_2'))
        self.assertEqual(expected_result_1, urljoin('path_1/', 'path_2'))
        self.assertEqual(expected_result_1, urljoin('path_1', '/path_2'))
        self.assertEqual(expected_result_1, urljoin('path_1/', '/path_2'))

        self.assertEqual(expected_result_2, urljoin('path_1', 'path_2/'))
        self.assertEqual(expected_result_2, urljoin('path_1/', 'path_2/'))
        self.assertEqual(expected_result_2, urljoin('path_1', '/path_2/'))
        self.assertEqual(expected_result_2, urljoin('path_1/', '/path_2/'))

        self.assertEqual(expected_result_3, urljoin('/path_1', 'path_2'))
        self.assertEqual(expected_result_3, urljoin('/path_1/', 'path_2'))
        self.assertEqual(expected_result_3, urljoin('/path_1', '/path_2'))
        self.assertEqual(expected_result_3, urljoin('/path_1/', '/path_2'))

        self.assertEqual(expected_result_4, urljoin('/path_1', 'path_2/'))
        self.assertEqual(expected_result_4, urljoin('/path_1/', 'path_2/'))
        self.assertEqual(expected_result_4, urljoin('/path_1', '/path_2/'))
        self.assertEqual(expected_result_4, urljoin('/path_1/', '/path_2/'))

    def test_get_url_default(self):
        key_url = 'some_url.js'
        self.assertEqual(LoadStatic.get_url(key_url),
                         urljoin(self.default_base_url, key_url))

    def test_get_url_absolute_base_url(self):
        # Given my base_url is an absolute URL and is overridden (as in hot-reload
        # local dev setup)
        key_url = 'some_url.js'
        absolute_base_url = 'foo://bar'
        loaded_key_url = '/some_url.hashchunk.js'

        # When I get a static URL
        with patch('json.loads') as jsondata:
            jsondata.return_value = {
                'base_url': absolute_base_url,
                'some_url.js': loaded_key_url,
            }
            # Then I use the base URL instead of default LMS URL
            self.assertEqual(LoadStatic.get_url(key_url), urljoin(
                absolute_base_url, loaded_key_url))

    @patch('xblock.utils.resources.ResourceLoader.load_unicode')
    def test_get_url_file_not_found(self, load_unicode):
        key_url = 'some_url.js'
        load_unicode.side_effect = IOError()
        self.assertEqual(LoadStatic.get_url(key_url), urljoin(
            self.default_base_url, 'some_url.js'))

    @override_settings(LMS_ROOT_URL='localhost/')
    @patch('xblock.utils.resources.ResourceLoader.load_unicode')
    def test_get_url_file_not_found_with_root_url(self, load_unicode):
        key_url = 'some_url.js'
        load_unicode.side_effect = IOError()
        self.assertEqual(LoadStatic.get_url(key_url), urljoin(
            'localhost/', self.default_base_url, 'some_url.js'))

    @patch('xblock.utils.resources.ResourceLoader.load_unicode')
    def test_get_url_with_manifest(self, load_unicode):
        load_unicode.return_value = None
        key_url = 'some_url.js'
        with patch('json.loads') as jsondata:
            jsondata.return_value = {
                'some_url.js': 'some_url.hashchunk.js'
            }
            self.assertEqual(LoadStatic.get_url(key_url), urljoin(
                self.default_base_url, 'some_url.hashchunk.js'))

    @override_settings(LMS_ROOT_URL='localhost/')
    @patch('xblock.utils.resources.ResourceLoader.load_unicode')
    def test_get_url_with_manifest_and_root_url(self, load_unicode):
        load_unicode.return_value = None
        key_url = 'some_url.js'
        with patch('json.loads') as jsondata:
            jsondata.return_value = {
                'some_url.js': 'some_url.hashchunk.js'
            }
            self.assertEqual(LoadStatic.get_url(key_url), urljoin(
                'localhost/', self.default_base_url, 'some_url.hashchunk.js'))
