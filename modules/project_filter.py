import logging

from modules.entities import Project
from modules.gradle.gradle_project_detector import GradleProjectDetector
from conf import config


class ProjectFilter:

    def __init__(self, directories):
        self.directories = directories

    def get_gradle_projects(self):
        projects = []
        logging.info(f'OVERALL PROJECTS NUMBER: {len(self.directories)}')
        for directory in self.directories:
            directory_path = config.repo_dir + '\\' + directory
            if GradleProjectDetector(directory_path).is_gradle_project():
                projects.append(Project(directory))
        logging.info(f'OF THEM GRADLE: {len(projects)}')
        return projects
