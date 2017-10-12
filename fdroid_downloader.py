import json
import urllib.request

from bs4 import BeautifulSoup


def get_html_source(url):
    response = urllib.request.urlopen(url)
    return response.read().decode('utf-8')

index_file = open("index.json", encoding="utf8")

parsed_json = json.load(index_file)
package_name = parsed_json["docs"]["0"]["packageName"]
app_url = 'https://f-droid.org/packages/{}/'.format(package_name)

html = get_html_source(app_url)

soup = BeautifulSoup(html, 'html.parser')

source_code_tag = soup('body')[0].find('b', text='Source Code')
link_to_the_sources_tag = source_code_tag.next_sibling.next_sibling

link_to_the_sources = link_to_the_sources_tag.get("href")


print(link_to_the_sources)

os.system('git --quiet decode --no-src --no-debug-info --force --keep-broken-res -o {0} '
          '{1}'.format(apk.path_on_disk_decompiled, apk.path_on_disk))

