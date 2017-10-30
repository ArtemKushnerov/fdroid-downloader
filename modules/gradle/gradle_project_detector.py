import os


class GradleProjectDetector:
    def __init__(self, package_path):
        self.package_path = package_path

    def is_gradle_project(self):
        build_gradle_path = os.path.join(self.package_path, 'build.gradle')
        return os.path.exists(build_gradle_path)
