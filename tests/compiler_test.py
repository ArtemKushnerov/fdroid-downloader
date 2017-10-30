import os
import re
import unittest
from os import path

import compiler
from conf import config
from modules import util
from modules.exceptions import AbsentApkException


class TestCompiler(unittest.TestCase):

    PACKAGE_NAME = 'anupam.acrylic'
    PACKAGE_PATH = 'C:/Workspace/fdroid-downloader/%s' % PACKAGE_NAME

    @classmethod
    def setUpClass(cls):
        util.setup_logging()
        os.chdir(cls.PACKAGE_PATH)
        os.system('git reset --hard HEAD')
        os.system('git clean -fxd')

    def test_write_json(self):
        compiler.save_to_json('foo', 'bar', 'baz')

        with open(path.join(config.results_dir, 'packages.json')) as packages_file:
            actual_json_content = packages_file.read()
        self.assertTrue(os.path.exists(os.path.join(config.results_dir, 'packages.json')))

        expected_json_content = """{
                                  "packages": [
                                    {
                                      "path": "foo",
                                      "name": "bar",
                                      "gradle_version": "baz"
                                    }
                                  ]
                                }"""

        edited_expected = re.sub(r'\s+', ' ', expected_json_content)
        edited_actual = re.sub(r'\s+', ' ', actual_json_content)

        self.assertEqual(edited_expected, edited_actual)

    def test_get_gradle(self):
        self.assertEqual(compiler.get_gradle_executable('1.1.1'), config.gradle1_executable)
        self.assertEqual(compiler.get_gradle_executable('2.0.2'), config.gradle2_executable)
        self.assertEqual(compiler.get_gradle_executable('3.1.2'), config.gradle3_executable)
        self.assertEqual(compiler.get_gradle_executable('4.3.9'), config.gradle4_executable)
        self.assertEqual(compiler.get_gradle_executable('5.8.7'), config.gradle4_executable)
        self.assertEqual(compiler.get_gradle_executable('6.4.1'), config.gradle4_executable)

    def test_move_apk_to_results_dir(self):
        apk_path = '{}/app/build/outputs/apk/app-debug.apk'.format(self.PACKAGE_PATH)
        apk_dir = os.path.dirname(apk_path)
        apk_name = os.path.basename(apk_path)
        if not os.path.exists(apk_path):
            os.makedirs(apk_dir, exist_ok=True)
            os.chdir(apk_dir)
            os.system('abc > {}'.format(apk_name))
            compiler.move_apk_to_results_dir(self.PACKAGE_NAME)
            os.chdir(config.root_dir)
        self.assertTrue(os.path.exists('{}/result/anupam.acrylic.apk'.format(config.root_dir)))

        with self.assertRaises(AbsentApkException):
            compiler.move_apk_to_results_dir(self.PACKAGE_NAME)

    def test_add_write_storage_permission(self):
        manifest_path = '{}/app/src/main/AndroidManifest.xml'.format(self.PACKAGE_PATH)
        compiler.change_manifest(self.PACKAGE_PATH)
        permission = '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />'
        instrumentation = '<instrumentation android:name="com.zhauniarovich.bbtester.EmmaInstrumentation" android:targetPackage="{}" />'.format(self.PACKAGE_NAME)

        with open(manifest_path) as manifest:
            file = manifest.read()
            self.assertTrue(permission in file)
            self.assertTrue(instrumentation in file)

    def test_add_instrumentation_class(self):
        os.system('echo %cd%')
        compiler.add_instrumentation_class(self.PACKAGE_PATH)
        self.assertTrue(os.path.exists('{}//app/src/main/java/com/zhauniarovich/bbtester'
                                       '/EmmaInstrumentation.java'.format(self.PACKAGE_PATH)))

    def test_add_properties_file(self):
        compiler.add_properties_file(self.PACKAGE_PATH, self.PACKAGE_NAME)
        agent_file = '{}/app/src/main/resources/jacoco-agent.properties'.format(self.PACKAGE_PATH, self.PACKAGE_NAME)
        self.assertTrue(os.path.exists(agent_file))
        with open(agent_file) as agent:
            self.assertTrue('destfile=/mnt/sdcard/{}/coverage.exec'.format(self.PACKAGE_NAME) == agent.read())

    def test_change_build_file(self):
        compiler.change_build_file(self.PACKAGE_PATH)
        app_gradle_path = '{}/app/build.gradle'.format(self.PACKAGE_PATH)

        with open('{}/resources/build_gradle_changes.txt'.format(config.root_dir)) as changes_file, open(app_gradle_path) as gradle_file:
            changes_file_content = changes_file.read()
            gradle_file_content = gradle_file.read()
        self.assertTrue(changes_file_content in gradle_file_content)

    def test_is_coverage_enabled(self):
        self.assertFalse(compiler.is_coverage_enabled('blabbla'))
        self.assertFalse(compiler.is_coverage_enabled(''))
        self.assertFalse(compiler.is_coverage_enabled('testCoverageEnabled=false'))
        self.assertFalse(compiler.is_coverage_enabled('testCoverageEnabled'))

        self.assertTrue(compiler.is_coverage_enabled('testCoverageEnabled=true'))
        self.assertTrue(compiler.is_coverage_enabled('testCoverageEnabled  =   true'))

    def test_has_coverage_parameter(self):
        self.assertFalse(compiler.has_coverage_parameter(''))
        self.assertFalse(compiler.has_coverage_parameter('blabbla'))
        self.assertTrue(compiler.has_coverage_parameter('testCoverageEnabled'))
        self.assertTrue(compiler.has_coverage_parameter('testCoverageEnabled=true'))
        self.assertTrue(compiler.has_coverage_parameter('testCoverageEnabled=false'))

    def test_get_gradle_with_enabled_coverage(self):
        gradle_contents = 'blabla testCoverageEnabled = false blabla'
        modified_gradle = compiler.get_gradle_with_enabled_coverage(gradle_contents)
        self.assertIsNone(re.search('testCoverageEnabled\s*= \s*false', modified_gradle))
        self.assertTrue('testCoverageEnabled=true' in modified_gradle)
