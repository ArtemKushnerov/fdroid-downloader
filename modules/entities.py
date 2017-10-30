import os

import re

import logging

import conf.config as config
from modules.exceptions import AbsentApkException


class Project:
    def __init__(self, name, app_dir=None):
        self.name = name
        self.path = os.path.join(config.repo_dir, name)
        self.gradle_version = ''
        if not app_dir:
            settings_gradle_path = os.path.join(self.path, 'settings.gradle')
            if os.path.exists(settings_gradle_path):
                with open(settings_gradle_path) as settings_gradle:
                    app_dir = self.get_app_dir(settings_gradle.read())
            else:
                app_dir = ''
        self.app_path = os.path.join(self.path, app_dir)

    def get_app_dir(self, settings_gradle_content):
        match = re.search(r"include ('|\")([^'\"]*)('|\")", settings_gradle_content)
        if match:
            app_dir = match.group(2)
            if app_dir.startswith(':'):
                app_dir = app_dir[1:]
        else:
            logging.warning(f'{self.name}: No included modules found in {self.path}/settings.gradle.')
            app_dir = ''
        return app_dir


class Apk:
    def __init__(self, project, instrumented):
        self.project = project
        self.instrumented = instrumented
        apk_dir = f'{project.app_path}/build/outputs/apk'
        for dir_path, _, file_names in os.walk(apk_dir):
            for file_name in file_names:
                logging.debug(file_name)
                if 'debug' in file_name and file_name.endswith('.apk'):
                    self.path = os.path.join(dir_path, file_name)
                    return
        raise AbsentApkException(f'Cannot find debug apk in the {project.app_path}/build/outputs/apk/')





