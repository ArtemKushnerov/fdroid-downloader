import os
import shutil
from conf import config


class InstrumentationHandler:

    def __init__(self, package):
        self.package = package

    def add_instrumentation_class(self):
        instrumentation_package = '{}/src/main/java/com/zhauniarovich/bbtester'.format(self.package.app_path)
        os.makedirs(instrumentation_package, exist_ok=True)
        shutil.copyfile('{}/resources/EmmaInstrumentation.java'.format(config.root_dir),
                 '{}/EmmaInstrumentation.java'.format(instrumentation_package))

    def add_properties_file(self):
        jacoco_agent_properties_dir = '{}/src/main/resources/'.format(self.package.app_path)
        os.makedirs(jacoco_agent_properties_dir, exist_ok=True)
        with open('{}/jacoco-agent.properties'.format(jacoco_agent_properties_dir), 'w') as agent_file:
            agent_file.write('destfile=/mnt/sdcard/{}/coverage.exec'.format(self.package.name))
