import os

import logging

import shutil

from json_util import JsonWriter
from modules.entities import Package
from modules.exceptions import FdroidCompilerException
from modules.gradle.gradle_editor import GradleEditor
from modules.instrumentation import InstrumentationHandler
from modules.gradle.apk_assembler import ApkAssembler
from modules.gradle.gradle_project_detector import GradleProjectDetector
from modules.gradle.gradle_version_extractor import GradleVersionExtractor
from modules import util
from modules.manifest import ManifestEditor, Manifest
from conf import config


def main():

    package_names = os.listdir(config.repo_dir)

    with open('done_list.txt', 'a+') as done_list:
        done_list.seek(0)
        done_list_lines = done_list.readlines()
        skip_package_names = [line.split(': ')[0] for line in done_list_lines]
        logging.info('================================================================================================================================================')
        logging.info(f'DONE LIST: {skip_package_names}')
        packages = []
        counter = len(done_list_lines)
        done_list.seek(0)
        fail = done_list.read().count('FAIL')
        size = len(package_names)
        for name in set(package_names) - set(skip_package_names):
            package_path = config.repo_dir + '\\' + name
            if GradleProjectDetector(package_path).is_gradle_project():
                counter += 1
                try:
                    logging.info('================================================================================================================================================')
                    logging.info(f'{name}: {counter} OF {size}, FAILS={fail}')
                    package = Package(name)

                    add_local_properties(package)

                    package.gradle_version = GradleVersionExtractor(package).extract_gradle_version()
                    assembler = ApkAssembler(package)

                    gradle_editor = GradleEditor(package)

                    apk = assembler.assemble_apk(is_instrumented=False)
                    util.move_apk_to_results_dir(apk)

                    manifest = Manifest(package)
                    ManifestEditor(manifest).edit_manifest()

                    InstrumentationHandler(package).add_instrumentation_files()

                    gradle_editor.edit_build_file()

                    instrumented_apk = assembler.assemble_apk(is_instrumented=True)
                    util.move_apk_to_results_dir(instrumented_apk)

                    packages.append(package)
                    logging.info(f'{name}: SUCCESS')
                    done_list.write(f'{name}: SUCCESS\n')
                    done_list.flush()
                except (FdroidCompilerException, BaseException):
                    logging.exception(f'{name}: FAIL')
                    fail += 1
                    done_list.write(f'{name}: FAIL\n')
                    done_list.flush()
    JsonWriter(packages).write_to_json()
    logging.info(f'{counter} gradle projects of {size} packages processed, {fail} failed')


def add_local_properties(package):
    sdk_dir = f'sdk.dir={config.sdk_dir}'
    sdk_location = f'sdk-location={config.sdk_dir}'
    ndk_dir = f'ndk-dir={config.ndk_dir}'
    with open(f'{package.path}/local.properties', 'w') as prop_file:
        prop_file.writelines([sdk_dir + '\n', sdk_location + '\n', ndk_dir])

if __name__ == '__main__':
    util.setup_logging()
    main()
