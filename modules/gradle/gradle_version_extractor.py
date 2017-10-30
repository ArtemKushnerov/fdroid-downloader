import os

import logging

import re

from modules.exceptions import AbsentGradleVersionException
from conf import config


class GradleVersionExtractor:
    def __init__(self, package):
        self.package = package

    def extract_gradle_version(self):
        build_gradle_path = os.path.join(self.package.path, 'build.gradle')
        with open(build_gradle_path, encoding='utf8') as build_gradle_file:
            gradle_dependency = re.search("com.android.tools.build:gradle:(\d.\d.\d)", build_gradle_file.read())
            if gradle_dependency:
                version = gradle_dependency.group(1)
                logging.info('Package {} have gradle version {}'.format(self.package.name, version))
                return version
            else:
                raise AbsentGradleVersionException
