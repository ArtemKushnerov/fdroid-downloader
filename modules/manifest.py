import xml.etree.ElementTree as ET


class Manifest:
    def __init__(self, package=None, manifest_path=None):
        self.package = package
        if manifest_path:
            self.manifest_path = manifest_path
        else:
            self.manifest_path = '{}/src/main/AndroidManifest.xml'.format(package.app_path)
        self.tree = ET.parse(self.manifest_path)
        self.root = self.tree.getroot()

    def add_tag(self, tag):
        self.root.append(tag)

    def write(self):
        self.tree.write(self.manifest_path)


class ManifestEditor:
    def __init__(self, manifest):
        self.manifest = manifest

    def edit_manifest(self):
        self.add_permission_tag()
        self.add_instrumentation_tag()
        self.manifest.write()

    def add_permission_tag(self):
        permission = ET.Element('uses-permission', {'ns0:name': 'android.permission.WRITE_EXTERNAL_STORAGE'})
        self.manifest.add_tag(permission)

    def add_instrumentation_tag(self):
        instrumentation = ET.Element('instrumentation',
                                     {'ns0:name': 'com.zhauniarovich.bbtester.EmmaInstrumentation',
                                      'ns0:targetPackage': '{}'.format(self.manifest.package.name)})
        self.manifest.add_tag(instrumentation)
