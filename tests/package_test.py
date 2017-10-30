import unittest

from modules.entities import Package
from modules.exceptions import NoIncludedModulesFoundException


class TestPackage(unittest.TestCase):
    def test_get_app_dir(self):
        self.assertTrue(Package.get_app_dir("include ':app'"), 'app')
        self.assertTrue(Package.get_app_dir("include 'app'"), 'app')
        self.assertTrue(Package.get_app_dir("include 'app'"), 'app')
        self.assertTrue(Package.get_app_dir("include 'app', 'otherModule'"), 'app')
        self.assertTrue(Package.get_app_dir("include 'app',\ninclude 'otherModule'"), 'app')
        with self.assertRaises(NoIncludedModulesFoundException):
            Package.get_app_dir("")
            Package.get_app_dir("include app")
