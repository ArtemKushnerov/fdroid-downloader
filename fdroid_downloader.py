import json
import os
import urllib.request
import logging.config

import shutil

import subprocess

import sys
import yaml
from bs4 import BeautifulSoup


DESTINATION_FOLDER = 'd:\\fdroid\\'
SUCCESS = 0


def setup_logging():
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))


def get_html_source(url):
    response = urllib.request.urlopen(url)
    return response.read().decode('utf-8')


def get_sources_link(name):
    app_url = 'https://f-droid.org/packages/{}/'.format(name)
    html = get_html_source(app_url)
    soup = BeautifulSoup(html, 'html.parser')
    source_code_tag = soup('body')[0].find('b', text='Source Code')
    link_to_the_sources_tag = source_code_tag.next_sibling.next_sibling
    return link_to_the_sources_tag.get("href")


def already_downloaded(package_folder):
    return os.path.exists(os.path.join(DESTINATION_FOLDER, package_folder))


if __name__ == '__main__':
    setup_logging()

    with open('index.json', encoding='utf8') as index_file:
        parsed_json = json.load(index_file)
    packages = parsed_json['docs']
    package_number = len(packages)
    logging.info('Downloading {} apps source from the f-droid.org...'.format(package_number))
    counter = 0
    for package in packages.values():
        counter += 1
        package_name = package['packageName']
        app_name = package['name']
        if already_downloaded(package_name):
            logging.info('{} is already downloaded, skipping.'.format(package_name))
            continue
        try:
            sources_link = get_sources_link(package_name)
            logging.info('Downloading {} of {}. App: {}, packageName:{},'.format(counter, package_number, app_name, package_name))
            logging.info('Link to the repo: {}'.format(sources_link))
            if 'git' in sources_link:
                status, out = subprocess.getstatusoutput('git clone {} {}'.format(sources_link, os.path.join(DESTINATION_FOLDER, package_name)))
                if status == SUCCESS:
                    logging.info(out)
                    logging.info('Done')
                else:
                    logging.error('Error while cloning git repo. Status {}'.format(status))
                    logging.error(out)
            else:
                logging.info('The repo is not git. Skipping.')
        except KeyboardInterrupt:
            logging.info('Keyboard interrupt, removing last package folder in case of incomplete cloning')
            shutil.rmtree(os.path.join(DESTINATION_FOLDER, package_name))
            sys.exit()
        except Exception:
            logging.exception('Exception for package {}'.format(package_name))
