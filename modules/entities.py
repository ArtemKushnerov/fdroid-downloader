import os

import re

import conf.config as config
from modules.exceptions import NoIncludedModulesFoundException


class Package:
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(config.repo_dir, name)
        self.gradle_version = ''
        with open(os.path.join(self.path, 'settings.gradle')) as settings_gradle:
            app_dir = self.get_app_dir(settings_gradle.read())
        self.app_path = os.path.join(self.path, app_dir)

    @staticmethod
    def get_app_dir(settings_gradle_content):
        match = re.search("include '(.*)'", settings_gradle_content)
        if match:
            app_dir = match.group(1)
            if app_dir.startswith(':'):
                app_dir = app_dir[1:]
        else:
            raise NoIncludedModulesFoundException
        return app_dir


class Apk:
    def __init__(self, package, instrumented):
        self.package = package
        self.instrumented = instrumented
        self.path = '{}/build/outputs/apk/app-debug.apk'.format(package.app_path)
