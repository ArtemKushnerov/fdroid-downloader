from conf import config


class EnvironmentSetuper:

    def __init__(self, project):
        self.package = project

    # noinspection PyMethodMayBeStatic
    def add_local_properties(self):
        sdk_dir = f'sdk.dir={config.sdk_dir}'
        sdk_location = f'sdk-location={config.sdk_dir}'
        ndk_dir = f'ndk-dir={config.ndk_dir}'
        with open(f'{self.package.path}/local.properties', 'w') as prop_file:
            prop_file.writelines([sdk_dir + '\n', sdk_location + '\n', ndk_dir])
