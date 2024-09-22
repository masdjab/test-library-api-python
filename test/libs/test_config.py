import unittest, os
from unittest.mock import patch, mock_open
from libs.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_yaml = """
APP_PORT:   2000
DB_URL:     somedburl
"""
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configy.yml")

    def test_get_config_values(self):
        with patch("builtins.open", mock_open(read_data=self.config_yaml)) as mock_file:
            config = Config(self.config_file)
            self.assertEqual(config.app_port, 2000)
            self.assertEqual(config.db_url, "somedburl")

            os.environ["APP_PORT"] = "2100"
            os.environ["DB_URL"] = "urlfromenv"
            config = Config(self.config_file)
            self.assertEqual(config.app_port, 2100)
            self.assertEqual(config.db_url, "urlfromenv")
        mock_file.assert_called_with(self.config_file)
