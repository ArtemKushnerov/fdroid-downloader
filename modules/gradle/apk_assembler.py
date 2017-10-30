import os

import logging
from distutils.version import LooseVersion

from conf import config
from modules.entities import Apk

from modules.exceptions import InvalidGradleVersionError, BuildException
import subprocess


class Gradle:
    def __init__(self, gradle_version):
        self.gradle_version = gradle_version
        if LooseVersion('1.0.0') <= LooseVersion(gradle_version) <= LooseVersion('1.1.3'):
            self.gradle_executable_path = config.gradle23_executable_path
        elif LooseVersion('1.2.0') <= LooseVersion(gradle_version) <= LooseVersion('1.3.1'):
            self.gradle_executable_path = config.gradle29_executable_path
        elif LooseVersion(gradle_version) == LooseVersion('1.5.0'):
            self.gradle_executable_path = config.gradle213_executable_path
        elif LooseVersion('2.0.0') <= LooseVersion(gradle_version) <= LooseVersion('2.1.2'):
            self.gradle_executable_path = config.gradle213_executable_path
        elif LooseVersion('2.1.3') <= LooseVersion(gradle_version) <= LooseVersion('2.2.3'):
            self.gradle_executable_path = config.gradle2141_executable_path
        elif LooseVersion('2.3.0') <= LooseVersion(gradle_version):
            self.gradle_executable_path = config.gradle33_executable_path
        else:
            raise InvalidGradleVersionError
        # gradle_version_first_char = gradle_version[0]
        # if gradle_version_first_char is '1':
        #     self.gradle_executable_path = config.gradle1_executable_path
        # elif gradle_version_first_char is '2':
        #     self.gradle_executable_path = config.gradle2_executable_path
        # # elif gradle_version_first_char is '3':
        # #     self.gradle_executable_path = config.gradle3_executable_path
        # elif gradle_version_first_char is '4' or gradle_version_first_char is '3' or int(gradle_version_first_char) > 4:
        #     self.gradle_executable_path = config.gradle4_executable_path
        # else:
        #     raise InvalidGradleVersionError


    def assemble_apk(self, package, is_instrumented=False):
        logging.info(f'{package.name}: start ASSEMBLING instrumented={is_instrumented}')
        logging.debug(f'{package.name}: instrumented={is_instrumented}, extracted gradle version={self.gradle_version}, gradle_executable={self.gradle_executable_path}')

        os.chdir(package.path)
        status, out = subprocess.getstatusoutput(f'{self.gradle_executable_path} assembleDebug')
        os.chdir(config.root_dir)
        if status != 0:
            raise BuildException(f'{package.name}: Problem during ASSEMBLING, extracted gradle version={self.gradle_version}, gradle_executable={self.gradle_executable_path},' 
                                 f'code={status}, output={out}')
        else:
            logging.info(f'{package.name}:done ASSEMBLING')
        return Apk(package, is_instrumented)
