import xml.etree.ElementTree as ET

import logging

from exceptions import ManifestEditingException, PackageNameNotProvidedException, PackagePathNotProvidedException


class Manifest:
    def __init__(self, package=None, package_name=None, manifest_path=None):
        if package_name:
            self.package_name = package_name
        elif package:
            self.package_name = package.name
        else:
            raise PackageNameNotProvidedException('Provide either package or package name')

        if manifest_path:
            self.manifest_path = manifest_path
        elif package:
            self.manifest_path = '{}/src/main/AndroidManifest.xml'.format(package.app_path)
        else:
            raise PackagePathNotProvidedException('Provide either package or manifest path')

        ET.register_namespace('android', "http://schemas.android.com/apk/res/android")
        self.tree = ET.parse(self.manifest_path)
        self.root = self.tree.getroot()

    def add_tag(self, tag):
        self.root.append(tag)

    def write(self):
        self.tree.write(self.manifest_path)

    def has(self, tag, namespaces):
        tag = self.root.find(tag, namespaces)
        logging.debug(str(tag))
        return tag is not None


class ManifestEditor:
    def __init__(self, manifest):
        self.manifest = manifest

    def edit_manifest(self):
        try:
            logging.info(f'{self.manifest.package_name}: EDIT MANIFEST')
            self.add_permission_tag()
            self.add_instrumentation_tag()
            self.manifest.write()

        except BaseException:
            raise ManifestEditingException(BaseException)

    def add_permission_tag(self):
        permission = ET.Element('uses-permission', {'android:name': 'android.permission.WRITE_EXTERNAL_STORAGE'})
        if not self.manifest.has('.//uses-permission[@android:name="android.permission.WRITE_EXTERNAL_STORAGE"]', {'android': "http://schemas.android.com/apk/res/android"}):
            self.manifest.add_tag(permission)

    def add_instrumentation_tag(self):
        instrumentation = ET.Element('instrumentation',
                                     {'android:name': 'com.zhauniarovich.bbtester.EmmaInstrumentation',
                                      'android:targetPackage': '{}'.format(self.manifest.package_name)})
        if not self.manifest.has('instrumentation', {'android': "http://schemas.android.com/apk/res/android"}):
            self.manifest.add_tag(instrumentation)
