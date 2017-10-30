import unittest

import shutil

from conf import config
from modules.entities import Package

from modules.manifest import ManifestEditor, Manifest


class TestManifestEditor(unittest.TestCase):

    def setUp(self):
        manifest_path = '{}/{}/resources/AndroidManifest.xml'.format(config.root_dir, 'tests')
        copy_manifest_path = '{}/{}/resources/AndroidManifest.xml_copy'.format(config.root_dir, 'tests')

        shutil.copyfile(copy_manifest_path, manifest_path)
        shutil.rmtree(copy_manifest_path, ignore_errors=True)

    def test_add_permission_tag(self):
        manifest_path = '{}/{}/resources/AndroidManifest.xml'.format(config.root_dir, 'tests')
        manifest = Manifest(manifest_path=manifest_path)
        editor = ManifestEditor(manifest)
        editor.add_permission_tag()
        manifest.write()

        permission = '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />'

        with open(manifest_path) as manifest:
            file = manifest.read()
            self.assertTrue(permission in file)

    def test_add_instrumentation_tag(self):
        manifest_path = '{}/{}/resources/AndroidManifest.xml'.format(config.root_dir, 'tests')
        manifest = Manifest(manifest_path=manifest_path, package=Package('test.package'))
        editor = ManifestEditor(manifest)
        editor.add_instrumentation_tag()
        manifest.write()

        instrumentation = '<instrumentation android:name="com.zhauniarovich.bbtester.EmmaInstrumentation" android:targetPackage="test.package" />'.format()

        with open(manifest_path) as manifest:
            file = manifest.read()
            self.assertTrue(instrumentation in file)

