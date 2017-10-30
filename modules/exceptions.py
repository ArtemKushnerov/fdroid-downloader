class FdroidCompilerException(Exception):
    pass


class InvalidGradleVersionError(FdroidCompilerException):
    pass


class AbsentGradleVersionException(FdroidCompilerException):
    pass


class AbsentApkException(FdroidCompilerException):
    pass


class NoIncludedModulesFoundException(FdroidCompilerException):
    pass


class BuildException(FdroidCompilerException):
    pass



