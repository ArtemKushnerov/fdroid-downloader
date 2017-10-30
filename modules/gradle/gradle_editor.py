import re

import logging

from conf import config


class GradleEditor:
    APPLY_PLUGIN_TEXT = "apply plugin: 'jacoco'\n"
    COVERAGE_SOURCE_DIR_TEXT = "\ndef coverageSourceDirs = [\n  '../app/src/main/java'\n]\n"
    JACOCO_VERSION_TEXT = '\njacoco{\n  toolVersion = "0.7.7.201606060606"\n}\n\n'
    GOOGLE_REPO = "maven { url 'https://maven.google.com'}"

    with open(config.resources_dir + '/jacoco_task.txt') as jacoco_task_file:
        JACOCO_TASK_TEXT = jacoco_task_file.read()

    def __init__(self, project=None, content=None):
        self.project = project
        if content is not None:
            self.content = content
        else:
            self.build_file_path = f'{project.app_path}/build.gradle'
            with open(self.build_file_path) as gradle_file:
                self.content = gradle_file.read()

    def edit_build_file(self):
        logging.debug(f'{self.project.name}: EDIT BUILD FILE')
        self.insert_apply_plugin()
        self.insert_coverage_source_dir_definition()
        self.insert_jacoco_version()
        self.insert_jacoco_task()
        self.enable_coverage()
        self.write_changes()

    def insert_apply_plugin(self):
        if self.APPLY_PLUGIN_TEXT not in self.content:
            self.insert_after_match('apply plugin:.*\n', self.APPLY_PLUGIN_TEXT)

    def insert_coverage_source_dir_definition(self):
        self.remove_old_cov_source_dir()
        self.insert_after_match(self.APPLY_PLUGIN_TEXT, self.COVERAGE_SOURCE_DIR_TEXT)

    def remove_old_cov_source_dir(self):
        self.content = re.sub(r"def\s*coverageSourceDirs\s*=\s*\[[^\[\]]*\]", '', self.content, flags=re.DOTALL)

    def insert_jacoco_version(self):
        self.remove_old_jacoco_version()
        self.insert_after_match("\ndef coverageSourceDirs = \[\n  '../app/src/main/java'\n\]\n",
                                self.JACOCO_VERSION_TEXT)

    def remove_old_jacoco_version(self):
        self.content = re.sub(r'jacoco\s*{[^{}]*}\n', '', self.content, flags=re.DOTALL)

    def insert_jacoco_task(self):
        self.remove_old_jacoco_task()
        self.insert_after_match(self.JACOCO_VERSION_TEXT, self.JACOCO_TASK_TEXT + '\n')

    def remove_old_jacoco_task(self):
        self.content = re.sub(r'task jacocoTestReport\s*\([a-zA-z: ]*\)\s*{((?!^}).)*}', '', self.content, flags=(re.DOTALL | re.MULTILINE))

    def insert_after_match(self, regex, text_to_insert):
        matches = re.finditer(regex, self.content)
        last_match_last_character_idx = None
        if matches:
            for match in matches:
                last_match = match
                last_match_last_character_idx = last_match.end()
        self.content = self.content[:last_match_last_character_idx] + text_to_insert + self.content[
                                                                                  last_match_last_character_idx:]

    def enable_coverage(self):
        if self.has_coverage_parameter():
            if not self.is_coverage_parameter_true():
                self.set_coverage_parameter_as_true()
        else:
            if self.has_debug_build_type():
                self.insert_coverage_enabled_to_debug_section()
            else:
                self.insert_debug_section_with_coverage_enabled()

    def has_coverage_parameter(self):
        return 'testCoverageEnabled' in self.content

    def is_coverage_parameter_true(self):
        match = re.search('testCoverageEnabled\s*=?\s*(true|false)', self.content)
        if match:
            enabled = match.group(1)
            return enabled == 'true'
        else:
            return False

    def set_coverage_parameter_as_true(self):
        return re.sub('testCoverageEnabled\s*=?\s*false', 'testCoverageEnabled=true', self.content)

    def has_debug_build_type(self):
        return re.search('buildTypes\s*{\s*debug', self.content) is not None

    def insert_coverage_enabled_to_debug_section(self):
        self.content = re.sub(r'(buildTypes\s*{debug\s*{(\s*))', r'\1testCoverageEnabled=true\2', self.content)

    def insert_debug_section_with_coverage_enabled(self):
        debug_section_part1 = "debug {"
        debug_section_part2 = "  testCoverageEnabled=true"
        debug_section_part3 = "}"
        self.content = re.sub(r'(buildTypes\s*{(\s*))', r'\1{}\2{}\2{}\2'.format(debug_section_part1,
                                                                                 debug_section_part2,
                                                                                 debug_section_part3), self.content)

    def write_changes(self):
        with open(self.build_file_path, 'w') as gradle_file:
            gradle_file.write(self.content)
