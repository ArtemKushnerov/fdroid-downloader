import unittest

import shutil

from modules.entities import Package
from conf import config
from modules.gradle.gradle_editor import GradleEditor


class TestGradleEditor(unittest.TestCase):

    def setUp(self):
        gradle_path = '{}/{}/resources/build.gradle'.format(config.root_dir, 'tests')
        copy_gradle_path = '{}/{}/resources/build.gradle_copy'.format(config.root_dir, 'tests')

        shutil.copyfile(copy_gradle_path, gradle_path)
        shutil.rmtree(copy_gradle_path, ignore_errors=True)

    def test_edit_build_file(self):
        package = Package('name')
        package.app_path = '{}/{}/resources/'.format(config.root_dir, 'tests')
        editor = GradleEditor(package)
        editor.edit_build_file()
        with open(f'{config.root_dir}/tests/resources/expected_build_file.gradle') as expected_file:
            self.assertEqual(editor.content, expected_file.read())
