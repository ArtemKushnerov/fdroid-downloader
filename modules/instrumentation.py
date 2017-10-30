import os
import shutil

import logging

from conf import config


# noinspection PyMethodMayBeStatic
class InstrumentationHandler:
    def __init__(self, package):
        self.package = package

    def add_instrumentation_files(self):
        logging.info(f'{self.package.name}: INSTRUMENT')
        self.add_instrumentation_class()
        self.add_properties_file()

    def add_instrumentation_class(self):
        instrumentation_package = f'{self.package.app_path}/src/main/java/com/zhauniarovich/bbtester'
        os.makedirs(instrumentation_package, exist_ok=True)
        shutil.copyfile(f'{config.root_dir}/resources/EmmaInstrumentation.java',
                        f'{instrumentation_package}/EmmaInstrumentation.java')

    def add_properties_file(self):
        jacoco_agent_properties_dir = f'{self.package.app_path}/src/main/resources/'
        os.makedirs(jacoco_agent_properties_dir, exist_ok=True)
        with open(f'{jacoco_agent_properties_dir}/jacoco-agent.properties', 'w') as agent_file:
            agent_file.write(f'destfile=/mnt/sdcard/{self.package.name}/coverage.exec')
