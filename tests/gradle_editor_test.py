import unittest

from conf import config
from modules import util
from modules.gradle.gradle_editor import GradleEditor


class TestGradleEditor(unittest.TestCase):
    def setUp(self):
        util.setup_logging()

    def test_has_debug_build_type(self):
        self.assertFalse(GradleEditor(content='').has_debug_build_type())
        self.assertFalse(GradleEditor(content='bla').has_debug_build_type())

        self.assertTrue(GradleEditor(content='buildTypes{debug{').has_debug_build_type())
        content = 'buildTypes{ ' \
                  'debug {' \
                  'blablabla}}'
        self.assertTrue(GradleEditor(content=content).has_debug_build_type())

    def test_insert_coverage_enabled_to_debug_section(self):
        GradleEditor(content='').insert_coverage_enabled_to_debug_section()

        handler = GradleEditor(content='buildTypes {debug{\n  hello')
        handler.insert_coverage_enabled_to_debug_section()
        self.assertTrue('buildTypes {debug{\n  testCoverageEnabled=true\n  hello' in handler.content,
                        'Modified content: {}'.format(handler.content))

    def test_insert_debug_with_coverage_enabled(self):
        content = ("buildTypes {\n"
                   "  release {\n"
                   "    blabla\n"
                   "  }\n"
                   "}")

        handler = GradleEditor(content=content)
        handler.insert_debug_section_with_coverage_enabled()
        expected_content = ("buildTypes {\n"
                            "  debug {\n"
                            "    testCoverageEnabled=true\n"
                            "  }\n"
                            "  release {\n"
                            "    blabla\n"
                            "  }\n"
                            "}")
        self.assertEqual(expected_content, handler.content)

    def test_insert_apply_plugin(self):
        editor = GradleEditor(content="apply plugin: 'pl'\nblabla")
        editor.insert_apply_plugin()
        self.assertEqual(editor.content, "apply plugin: 'pl'\napply plugin: 'jacoco'\nblabla")

    def test_insert_coverage_source_dir_definition(self):
        editor = GradleEditor(content="apply plugin: 'pl'\napply plugin: 'jacoco'\nblabla")
        editor.insert_coverage_source_dir_definition()
        coverage_source_dir = "\ndef coverageSourceDirs = [\n  '../app/src/main/java'\n]\n"
        expected_content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + coverage_source_dir + 'blabla'
        self.assertEqual(editor.content, expected_content)

    def test_insert_jacoco_version(self):
        coverage_source_dir = "\ndef coverageSourceDirs = [\n  '../app/src/main/java'\n]\n"
        content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + coverage_source_dir + 'blabla'

        editor = GradleEditor(content=content)
        editor.insert_jacoco_version()
        jacoco_plugin_text = '\njacoco{\n  toolVersion = "0.7.7.201606060606"\n}\n\n'
        expected_content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + coverage_source_dir + jacoco_plugin_text + 'blabla'
        print(repr(editor.content))
        print(repr(expected_content))
        self.assertEqual(editor.content, expected_content)

    def test_insert_jacoco_task(self):
        jacoco_plugin_text = '\njacoco{\n  toolVersion = "0.7.7.201606060606"\n}\n\n'
        coverage_source_dir = "\ndef coverageSourceDirs = [\n  '../app/src/main/java'\n]\n"

        content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + coverage_source_dir + jacoco_plugin_text + 'blabla'
        with open(config.resources_dir + '/jacoco_task.txt') as jacoco_task_file:
            jacoco_task_text = jacoco_task_file.read()

        editor = GradleEditor(content=content)
        editor.insert_jacoco_task()
        expected_content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + coverage_source_dir + jacoco_plugin_text \
                           + jacoco_task_text + '\n' + 'blabla'
        self.assertEqual(editor.content, expected_content)

    def test_remove_if_coverage_source_dir_already_present(self):
        coverage_source_dir = "def coverageSourceDirs = [\n  '../app/src/main/java'\n]\n"
        content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + coverage_source_dir + 'blabla'
        editor = GradleEditor(content=content)
        editor.remove_old_cov_source_dir()
        expected_content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n\nblabla"
        print(editor.content)
        self.assertEqual(editor.content, expected_content)

    def test_remove_old_jacoco_task(self):
        jacoco_task = 'task jacocoTestReport() {\nheya}\n'
        content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n" + jacoco_task + 'blabla'

        editor = GradleEditor(content=content)
        editor.remove_old_jacoco_task()
        expected_content = "apply plugin: 'pl'\napply plugin: 'jacoco'\n\nblabla"
        print(repr(editor.content))
        print(repr(expected_content))

        self.assertEqual(editor.content, expected_content)
