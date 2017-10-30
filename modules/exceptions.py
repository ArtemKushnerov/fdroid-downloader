class FdroidCompilerException(Exception):
    pass


class InvalidGradleVersionError(FdroidCompilerException):
    pass


class AbsentGradleVersionException(FdroidCompilerException):

    def __init__(self, package_name):
        self.package_name = package_name

    def __str__(self):
        return f'Gradle version is not found for package {self.package_name}'


class AbsentApkException(FdroidCompilerException):
    pass


class NoIncludedModulesFoundException(FdroidCompilerException):
    pass


class BuildException(FdroidCompilerException):
    pass


class ManifestEditingException(FdroidCompilerException):
    pass


class ProjectNameNotProvidedException(FdroidCompilerException):
    pass


class ProjectPathNotProvidedException(FdroidCompilerException):
    pass


class NoSettingsGradleException(FdroidCompilerException):
    pass


class BuildTimeOutException(FdroidCompilerException):
    pass


