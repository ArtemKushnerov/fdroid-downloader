import os


class GradleProjectDetector:
    def __init__(self, project_path):
        self.project_path = project_path

    def is_gradle_project(self):
        build_gradle_path = os.path.join(self.project_path, 'build.gradle')
        return os.path.exists(build_gradle_path)
