import unittest

import shutil

import re

from modules.entities import Package
from conf import config
from modules.gradle.gradle_editor import GradleEditor


class TestGradleEditor(unittest.TestCase):

    # def setUp(self):
    #     gradle_path = '{}/{}/resources/build.gradle'.format(config.root_dir, 'tests')
    #     copy_gradle_path = '{}/{}/resources/build.gradle_copy'.format(config.root_dir, 'tests')
    #
    #     shutil.copyfile(copy_gradle_path, gradle_path)
    #     shutil.rmtree(copy_gradle_path, ignore_errors=True)

    def test_edit_build_file(self):
        package = Package('name', app_dir='test')
        package.app_path = f'{config.root_dir}/tests/resources/'
        editor = GradleEditor(package)
        editor.edit_build_file()
        with open(f'{config.root_dir}/tests/resources/expected_build.gradle') as expected_file:
            self.assertEqual(re.sub(r'\n*', '\n', editor.content), re.sub(r'\n*', '\n', expected_file.read()))
