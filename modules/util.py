import os

import shutil

from modules.exceptions import AbsentApkException
import logging.config
import yaml
import conf.config as config


def move_apk_to_results_dir(apk):
    logging.debug(apk.instrumented)
    msg = 'MOVE'
    if apk.instrumented:
        msg += ' INSTRUMENTED'
    logging.info(f'{apk.project.name}: {msg}')
    if not os.path.exists(apk.path):
        raise AbsentApkException
    apk_name = apk.project.name
    if apk.instrumented:
        apk_name += '_instrumented'
    shutil.move(apk.path, '{}/{}.apk'.format(config.results_dir, apk_name))


def setup_logging():
    with open('{}\conf\logging.yaml'.format(config.root_dir)) as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))
