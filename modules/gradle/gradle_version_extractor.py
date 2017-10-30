import os

import logging

import re

from modules.exceptions import AbsentGradleVersionException


class GradleVersionExtractor:

    GRADLE_DEPENDENCY_REGEX = re.compile('com.android.tools.build:gradle:(.\..\..)')

    def __init__(self, package):
        self.package = package

    #todo in fact this is  build tool version, not gradle, rename
    def extract_gradle_version(self):
        logging.info(f'{self.package.name}: EXTRACT VERSION')
        build_gradle_path = os.path.join(self.package.path, 'build.gradle')
        with open(build_gradle_path, encoding='utf8') as build_gradle_file:
            root_gradle_contents = build_gradle_file.read()
        gradle_dependency = self.GRADLE_DEPENDENCY_REGEX.search(root_gradle_contents)
        if not gradle_dependency:
            app_build_gradle_path = os.path.join(self.package.app_path, 'build.gradle')
            with open(app_build_gradle_path, encoding='utf8') as app_build_gradle_path_file:
                app_gradle_contents = app_build_gradle_path_file.read()
            gradle_dependency = self.GRADLE_DEPENDENCY_REGEX.search(app_gradle_contents)
            if not gradle_dependency:
                raise AbsentGradleVersionException(self.package.name)

        version = gradle_dependency.group(1)
        version = self.cut_plus_notation(version)
        logging.info(f'{self.package.name}: VERSION={version}')
        return version

    @staticmethod
    def cut_plus_notation(version):
        if version.endswith('+'):
            version = version[:-2]
        return version
