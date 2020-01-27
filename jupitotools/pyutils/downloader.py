"""Downloading utility."""

import datetime
import json
import sys
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path, PurePath
from pprint import pprint

import requests

import net
from misc import fmt_args, fmt_bitrate, fmt_size, numbered_lines, one

TIMEOUT = 10


class Downloader:
    """File downloader."""

    def __init__(self, url, dst_path=None, tmp_path=None, progress=True):
        self.url = url
        self.dst_path = dst_path or Path.cwd()
        self.tmp_path = tmp_path or Path(tempfile.gettempdir())
        self.progress = progress

    @property
    @lru_cache(None)
    def url_parsed(self):
        return requests.utils.urlparse(self.url)

    def filename(self):
        return PurePath(PurePath(self.url_parsed.path).name)

    def size(self):
        raise NotImplementedError

    def download(self):
        return net.download(self.url, self.dst_path, tmp_path=self.tmp_path,
                            progress=self.progress)


class HTTPDownloader(Downloader):
    """HTTP downloader."""

    @lru_cache(None)
    def get_headers(self):
        with requests.get(self.url, stream=True) as r:
            return r.headers

    def size(self):
        return int(self.get_headers()['Content-Length'])


# https://areena.yle.fi/1-3430910
class YleDownloader(Downloader):
    """Media downloader that uses yle-dl externally."""

    def __init__(self, *args, **kwargs):
        """Initialize yle-dl downloader with URL."""
        super().__init__(*args, **kwargs)
        cmd = kwargs.get('cmd', 'yle-dl')
        sublang = kwargs.get('sublang', 'none')
        self._data = dict(url=self.url, cmd=cmd, sublang=sublang)

    @property
    def _popenargs(self):
        return dict(stdout=subprocess.PIPE, cwd=self.tmp_path, text=True)

    @property
    def _runargs(self):
        return dict(self._popenargs, check=True)

    @lru_cache(None)
    def get_url(self):
        """Get media content URL."""
        args = fmt_args('{cmd} --showurl {url}', **self._data)
        completed = subprocess.run(args, timeout=TIMEOUT, **self._runargs)
        return completed.stdout.strip()

    @lru_cache(None)
    def get_metadata(self):
        """Get media metadata."""
        args = fmt_args('{cmd} --showmetadata {url}', **self._data)
        completed = subprocess.run(args, timeout=TIMEOUT, **self._runargs)
        return one(json.loads(completed.stdout))

    def publish_time(self):
        """Publish timestamp."""
        s = self.get_metadata()['publish_timestamp']
        return datetime.datetime.fromisoformat(s)

    def filename(self):
        """Get suggested media content filename."""
        return PurePath(self.get_metadata()['filename'])

    def title(self):
        """Get media title."""
        return self.get_metadata()['title']

    def webpage(self):
        """Get media web page URL."""
        return self.get_metadata()['webpage']

    def duration(self):
        """Duration in secons."""
        n = self.get_metadata()['duration_seconds']
        return datetime.timedelta(seconds=n)

    def bitrate(self):
        """Maximum bitrate in kb/s."""
        return max(x['bitrate'] for x in self.get_metadata()['flavors'])

    def size(self):
        """Maximum downloadable size in B."""
        return self.duration().total_seconds() * self.bitrate() / 8 * 1024

    def subtitle_languages(self):
        """Get subtitle languages."""
        return sorted(set(x['language'] for x in
                          self.get_metadata()['embedded_subtitles']))

    def mediatypes(self):
        """Get media types."""
        return sorted(set(x['media_type'] for x in
                          self.get_metadata()['flavors']))

    def mediatype(self):
        """Get media type, assuming there's only one."""
        return one(self.mediatypes())

    @lru_cache(None)
    def playlist(self):
        """Get media content playlist: listed in URL, or URL itself."""
        r = requests.head(self.get_url())
        if r.headers['Content-Type'] == 'application/x-mpegurl':
            r = requests.get(self.get_url())
            return [x.strip() for x in r.text.splitlines()]
        return [self.get_url()]

    def playlist_urls(self):
        """Get media content playlist without comment lines."""
        return [x for x in self.playlist() if not x.startswith('#')]

    def download(self):
        """Download media."""
        args = fmt_args('{cmd} --sublang {sublang} {url}', **self._data)
        completed = subprocess.run(args, timeout=None, **self._runargs)
        return completed.stdout

    def download_subtitles(self):
        """Download subtitles."""
        args = fmt_args('{cmd} --subtitlesonly --sublang {sublang} {url}',
                        **self._data)
        completed = subprocess.run(args, timeout=None, **self._runargs)
        return completed.stdout


def downloader(url):
    """Get a suitable class for url."""
    parsed = requests.utils.urlparse(url)
    if parsed.scheme in ['http', 'https']:
        if parsed.netloc in ['areena.yle.fi']:
            return YleDownloader(url)
        return HTTPDownloader(url)
    return Downloader(url)


def showinfo(url, verbosity=0):
    """Show info."""
    print(url)
    dl = downloader(url)
    print(dl.webpage())
    print(dl.title())
    print(dl.filename())
    print(dl.publish_time(), dl.mediatype(), dl.duration(),
          fmt_bitrate(dl.bitrate()), fmt_size(dl.size()),
          dl.subtitle_languages(), sep=', ')
    if verbosity:
        pprint(dl.get_metadata())
    if verbosity > 1:
        print(fmt_size(downloader(dl.get_url()).size()), dl.get_url())
    if verbosity > 2:
        print(*(f'{fmt_size(downloader(x).size())}: {x}' for x in
                dl.playlist_urls()), sep='\n')


def main():
    """Main."""
    verbosity = 0
    for arg in sys.argv[1:]:
        if arg == '-v':
            verbosity += 1
        else:
            showinfo(arg, verbosity=verbosity)


if __name__ == '__main__':
    main()
