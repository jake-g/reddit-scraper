#!/usr/local/bin/python
from __future__ import unicode_literals, print_function

import argparse
import os
import re
import signal
import sys

import youtube_dl
from bs4 import BeautifulSoup

try:
    from urllib import quote_plus  # Python 2.X
except ImportError:
    from urllib.parse import quote_plus  # Python 3+
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# # hack for osx
# reload(sys)
# sys.setdefaultencoding('utf8')

# Defaults
VERBOSITY = 0
DEFAULT_PATH = './downloads/'


def download_playlist(playlist, opts):
    # must be txt file with link per line
    print('Downloading List...\n')
    with open(playlist) as f:
        urls = [urls.strip() for urls in f]
        count = len(urls)
        for i, url in enumerate(urls):
            print('\n(%d/%d)' % (i + 1, count))
            try:
                if '#' not in url:
                    download_track(str(url), opts)
            except:
                pass


def download_track(url, opts):
    class logger(object):
        def debug(self, msg):
            if VERBOSITY > 0:
                print(msg)
            pass

        def warning(self, msg):
            print(msg)

        def error(self, msg):
            print(msg)

    def callback(d):
        if d['status'] == 'finished':
            print('\x1b[1A[\033[92mSaving\033[00m] %s' % (d[u'filename']), end='')

    opts[u'logger'] = logger()
    opts[u'progress_hooks'] = [callback]
    print('[\033[91mFetching\033[00m] %s' % url)
    if 'soundcloud.com' in url:
        opts[u'postprocessors'][0][u'titleformat'] = "%(uploader)s - %(title)s"
    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])


def valid_url(url):
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


def process_search(query, opts):
    def _list_links(links):
        for idx, (title, _) in enumerate(links):
            yield '[{}] {}'.format(idx, title)

    def _extract_links(html):
        soup = BeautifulSoup(html, 'html.parser')
        pattern = re.compile(r'/watch\?v=')
        found = soup.find_all('a', 'yt-uix-tile-link', href=pattern)
        return [(x.text.encode('utf-8'), x.get('href')) for x in found]

    def _search_youtube(query):
        print('Searching...')
        response = urllib2.urlopen('https://www.youtube.com/results?search_query=' + query)
        return _extract_links(response.read())

    search = quote_plus(query)
    available = _search_youtube(search)
    if not available:
        print('No results found matching your query.')
        sys.exit()

    print("Search Results:")
    print('\n'.join(_list_links(available)))
    choice = ''  # pick choice
    while choice.strip() == '':
        choice = input('Pick one: ')
        print('')
        title, video_link = available[int(choice)]
        download_track('http://www.youtube.com/' + video_link, opts)


def _quit_handler(signum, frame):
    print('Terminating...')
    os._exit(0)


def _help_text():
    print('\nInput Query:\n' \
          ' URL (valid if url to youtube or soundcloud track/playlist/set)\n' \
          ' Link File (a path to a .txt containing valid URLs)\n' \
          ' Search (songname/lyrics/artist or other)\n')


def main(args):
    signal.signal(signal.SIGINT, _quit_handler)

    # Get Query
    opts['outtmpl'] = args.path + '%(title)s.%(ext)s'
    if args.link:  # input argument
        query = args.link
    else:  # ask for input
        _help_text()
        query = str(input('Query:\n> '))

    # Process Query
    if valid_url(query):  # track
        download_track(query, opts)
    elif '.txt' in query:  # playlist
        download_playlist(query, opts)
    else:
        process_search(query, opts)  # search


if __name__ == '__main__':
    opts = {  # Settings for youtube-dl
        'format': 'bestaudio/best',
        'forcejson': True,
        'outtmpl': './downloads/%(title)s.%(ext)s',
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'MetadataFromTitle',
                'titleformat': "%(artist)s - %(title)s"
            },
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0'
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False
            }
        ]
    }
    # TODO set id3 tags in smart way

    parser = argparse.ArgumentParser()
    parser.add_argument("--link", "-l", type=str, help="url to download")
    parser.add_argument("--path", "-p", default=DEFAULT_PATH, type=str, help="download path")
    args = parser.parse_args()

    main(args)
