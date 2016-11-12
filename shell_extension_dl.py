#! /usr/bin/env python3

import sys
import urllib
from urllib.request import urlopen
import codecs
import json
import shutil


GNOME_URL = 'https://extensions.gnome.org'
INFO = '/extension-info/?pk='
VERSION = '&shell_version='


class InvalidUrlError(Exception):
    pass


def main(url):
    parsed = urllib.parse.urlparse(url)

    try:
        ext, extension = parsed.path.split('/')[1:3]
        int(extension)
    except ValueError:
        raise InvalidUrlError
    if parsed.netloc != 'extensions.gnome.org' or ext != 'extension':
        raise InvalidUrlError

    reader = codecs.getreader('utf-8')

    try:
        with urlopen(GNOME_URL + INFO + extension) as response:
            versions = json.load(reader(response))
    except urllib.error.HTTPError:
        raise InvalidUrlError

    vlist = list(versions['shell_version_map'].keys())
    vlist.sort(key=lambda s: [int(u) for u in s.split('.')])
    selected = GNOME_URL + INFO + extension + VERSION + vlist[-1]

    with urlopen(selected) as response:
        dl_url = GNOME_URL + json.load(reader(response))['download_url']
    with urlopen(dl_url) as response, \
         open(versions['uuid'] + '.zip', 'wb') as dl_file:
        shutil.copyfileobj(response, dl_file)


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except InvalidUrlError:
        sys.exit('invalid url')
    except IndexError:
        sys.exit('please specify an url')
