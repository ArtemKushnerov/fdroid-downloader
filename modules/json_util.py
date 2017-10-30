import json
import os

import logging

from conf import config


class JsonWriter:
    def __init__(self, packages):
        self.packages = packages
        self.json_path = os.path.join(config.results_dir, 'packages.json')
        self.document = self.read()

    def save_to_json(self):
        logging.info('=============================================================================================================================================================')
        logging.info('SAVE TO JSON')
        for package in self.packages:
            record = {"path": package.path, "name": package.name, "gradle_version": package.gradle_version}
            self.document["packages"].append(record)
            logging.debug(self.document)
        self.write()

    def read(self):
        document = {"packages": []}
        if os.path.exists(self.json_path):
            with open(self.json_path) as packages_file:
                document = json.load(packages_file)
        return document

    def write(self):
        with open(self.json_path, 'w') as packages_file:
            json.dump(self.document, packages_file, indent=2)
