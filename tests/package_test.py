import unittest

from modules.entities import Project
from modules.exceptions import NoIncludedModulesFoundException


class TestPackage(unittest.TestCase):
    def test_get_app_dir(self):
        self.assertTrue(Project.get_app_dir("include ':app'"), 'app')
        self.assertTrue(Project.get_app_dir("include 'app'"), 'app')
        self.assertTrue(Project.get_app_dir("include 'app'"), 'app')
        self.assertTrue(Project.get_app_dir("include 'app', 'otherModule'"), 'app')
        self.assertTrue(Project.get_app_dir("include 'app',\ninclude 'otherModule'"), 'app')
        with self.assertRaises(NoIncludedModulesFoundException):
            Project.get_app_dir("")
            Project.get_app_dir("include app")
