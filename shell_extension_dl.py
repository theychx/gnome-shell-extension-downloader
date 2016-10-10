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
    name = versions['name']

    print ('"%s" available for these versions of gnome-shell:' % name)

    count = 0
    for vers in vlist:
        count += 1
        print ('%s : %s' % (count, vers))

    if len(vlist) > 1:
        while True:
            try:
                choose = int(input('Choose [1-%s]: ' % count).strip())
                if choose < 1 or choose > count:
                    raise ValueError
            except ValueError:
                print ('invalid choice')
            else:
                break
    else:
        choose = 1

    choice = vlist[choose - 1]
    selected = GNOME_URL + INFO + extension + VERSION + choice

    with urlopen(selected) as response:
        dl_url = GNOME_URL + json.load(reader(response))['download_url']
    with urlopen(dl_url) as response, \
         open(versions['uuid'] + '.zip', 'wb') as dl_file:
        shutil.copyfileobj(response, dl_file)

    print ('"%s" for "%s" downloaded OK' % (name, choice))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            main(sys.argv[1])
        except InvalidUrlError:
            sys.exit('invalid url')
    else:
        sys.exit('please specify an url')
