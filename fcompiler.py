import os

import logging

import sys
import subprocess

from modules.environment_setuper import EnvironmentSetuper
from modules.json_util import JsonWriter
from modules.exceptions import FdroidCompilerException
from modules.gradle.gradle_editor import GradleEditor
from modules.instrumentation import InstrumentationHandler
from modules.gradle.apk_assembler import ApkAssembler
from modules.gradle.gradle_version_extractor import GradleVersionExtractor
from modules import util
from modules.manifest import ManifestEditor, Manifest
from conf import config
from modules.project_filter import ProjectFilter


def main():
    project_names = os.listdir(config.repo_dir)
    ignore_done_list = False
    done_list_path = os.path.join(config.results_dir, 'done_list.txt')
    with open(done_list_path, 'a+') as done_list_file:
        projects_to_process = set(project_names)
        counter = 0
        fail_counter = 0
        if not ignore_done_list:
            done_project_names = get_done_project_names(done_list_file)
            logging.info('================================================================================================================================================')
            logging.info(f'DONE LIST SIZE: {len(done_project_names)}')
            logging.debug(f'DONE LIST CONTENT: {done_project_names}')
            projects_to_process = projects_to_process - set(done_project_names)
            counter = len(done_project_names)
            fail_counter = get_fail_counter(done_list_file)

        gradle_projects = ProjectFilter(projects_to_process).get_gradle_projects()
        size = len(gradle_projects)
        for project in gradle_projects:
            counter += 1
            try:
                logging.info('================================================================================================================================================')
                logging.info(f'{project.name}: {counter} OF {size}, FAILS={fail_counter}')
                reset_project_state(project)
                EnvironmentSetuper(project).add_local_properties()

                project.gradle_version = GradleVersionExtractor(project).extract_gradle_version()
                assembler = ApkAssembler(project)

                gradle_editor = GradleEditor(project)

                apk = assembler.assemble_apk(is_instrumented=False)
                util.move_apk_to_results_dir(apk)

                manifest = Manifest(project)
                ManifestEditor(manifest).edit_manifest()

                InstrumentationHandler(project).add_instrumentation_files()

                gradle_editor.edit_build_file()

                instrumented_apk = assembler.assemble_apk(is_instrumented=True)
                util.move_apk_to_results_dir(instrumented_apk)

                logging.info(f'{project.name}: SUCCESS')
                done_list_file.write(f'{project.name}: SUCCESS\n')
                done_list_file.flush()
                JsonWriter(project).save_to_json()
            except KeyboardInterrupt:
                logging.info('Keyboard interrupt, revert changes to current project')
                reset_project_state(project)
                sys.exit()
            except (FdroidCompilerException, BaseException):
                logging.exception(f'{project.name}: FAIL')
                fail_counter += 1
                done_list_file.write(f'{project.name}: FAIL\n')
                done_list_file.flush()
    logging.info(f'{counter} gradle processed_projects of {size} processed_projects processed, {fail_counter} failed')


def get_fail_counter(done_list_file):
    done_list_file.seek(0)
    fail_counter = done_list_file.read().count('FAIL')
    return fail_counter


def get_done_project_names(done_list_file):
    done_list_file.seek(0)
    done_project_names = [line.split(': ')[0] for line in done_list_file.readlines()]
    return done_project_names


def reset_project_state(project):
    os.chdir(project.path)
    out = subprocess.check_output('git status', shell=True, stderr=subprocess.STDOUT)
    if 'nothing to commit, working tree clean' not in out.decode('utf-8'):
        logging.info(f'{project.name}: RESET PROJECT STATE')
        out = subprocess.check_output('git reset --hard HEAD && git clean -xfd', shell=True, stderr=subprocess.STDOUT)
        logging.debug(out.decode('utf-8'))


if __name__ == '__main__':
    util.setup_logging()
    main()
