import os

import logging
from distutils.version import StrictVersion

import re

from conf import config
from modules.entities import Apk

from modules.exceptions import InvalidGradleVersionError, BuildException, BuildTimeOutException
import subprocess


class ApkAssembler:
    def __init__(self, project):
        self.gradle_version = project.gradle_version
        self.project = project
        if StrictVersion('1.0.0') <= StrictVersion(project.gradle_version) <= StrictVersion('1.1.3'):
            self.gradle_executable_path = config.gradle23_executable_path
        elif StrictVersion('1.2.0') <= StrictVersion(project.gradle_version) <= StrictVersion('1.3.1'):
            self.gradle_executable_path = config.gradle29_executable_path
        elif StrictVersion(project.gradle_version) == StrictVersion('1.5.0'):
            self.gradle_executable_path = config.gradle213_executable_path
        elif StrictVersion('2.0.0') <= StrictVersion(project.gradle_version) <= StrictVersion('2.1.2'):
            self.gradle_executable_path = config.gradle213_executable_path
        elif StrictVersion('2.1.3') <= StrictVersion(project.gradle_version) <= StrictVersion('2.2.3'):
            self.gradle_executable_path = config.gradle2141_executable_path
        elif StrictVersion('2.3.0') <= StrictVersion(project.gradle_version):
            self.gradle_executable_path = config.gradle33_executable_path
        else:
            raise InvalidGradleVersionError(f'Invalid version: {project.gradle_version}')

        with open(f'{project.path}/build.gradle') as build_file:
            file_read = build_file.read()
            match = re.findall('google\(\)', file_read)
            if match:
                self.gradle_executable_path = config.gradle4_executable_path

        logging.info(f'{project.name}: EXECUTABLE={self.gradle_executable_path}')

    def assemble_apk(self, is_instrumented=False):
        msg = f'ASSEMBLE'
        logging.debug(is_instrumented)
        if is_instrumented:
            msg += ' INSTRUMENTED'
        logging.info(f'{self.project.name}: {msg}')
        logging.debug(f'{self.project.name}: instrumented={is_instrumented}, extracted gradle version={self.gradle_version}, gradle_executable={self.gradle_executable_path}')

        os.chdir(self.project.path)
        try:
            subprocess.check_output(f'{self.gradle_executable_path} assembleDebug', shell=True, stderr=subprocess.STDOUT, timeout=20 * 60)
        except subprocess.CalledProcessError as e:
            out = e.output.decode('utf-8')
            raise BuildException(f'{self.project.name}: Failed to assemble apk, gradle_version={self.gradle_version}, gradle_executable={self.gradle_executable_path},'
                                 f'output=\n{out}')
        except subprocess.TimeoutExpired:
            raise BuildTimeOutException(f'BUILD TIMEOUT={config.timeout} EXCEEDED, INSTRUMENTED={is_instrumented}')

        os.chdir(config.root_dir)
        return Apk(self.project, is_instrumented)
