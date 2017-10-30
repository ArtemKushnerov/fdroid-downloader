import json
import os

from conf import config


class JsonWriter:
    def __init__(self, packages):
        self.packages = packages

    def write_to_json(self):
        for package in self.packages:
            records = []
            record = {"path": package.path, "name": package.name, "gradle_version": package.gradle_version}
            records.append(record)
            document = {"packages": records}
            with open(os.path.join(config.results_dir, 'packages.json'), 'w') as packages_file:
                json.dump(document, packages_file, indent=2)
