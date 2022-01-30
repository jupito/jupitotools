"""Yle media files."""

# Examples:
# https://areena.yle.fi/1-3430910
# https://areena.yle.fi/1-50258660
# https://areena.yle.fi/1-50564137
# --showurl
# --showtitle
# --showepisodepage
# --showmetadata

import datetime
import json
import sys
import subprocess
# import tempfile
from functools import lru_cache
from pathlib import PurePath
import pprint

import requests
from tabulate import tabulate

from ..misc import fmt_args, fmt_bitrate, fmt_size, one


class YleMedia:
    """Media downloader that uses yle-dl externally."""

    def __init__(self, url, cmd='yle-dl', sublang='none'):
        """Initialize with URL."""
        self.url = self._normalize_url(url)
        self.cmd = cmd
        self.sublang = sublang

    @staticmethod
    def _normalize_url(url):
        """Normalize URL."""
        # TODO
        return url.strip()

    @staticmethod
    def _run(args):
        """Run subprocess."""
        return subprocess.run(args, stdout=subprocess.PIPE, text=True,
                              check=True)

    @lru_cache(None)
    def get_url(self):
        """Get media content URL."""
        args = fmt_args('{cmd} --showurl {url}', cmd=self.cmd, url=self.url)
        proc = self._run(args)
        return proc.stdout.strip()

    @lru_cache(None)
    def metadata(self):
        """Get media metadata."""
        args = fmt_args('{cmd} --showmetadata {url}', cmd=self.cmd,
                        url=self.url)
        proc = self._run(args)
        return one(json.loads(proc.stdout))

    def publish_time(self):
        """Publish time."""
        s = self.metadata()['publish_timestamp']
        return datetime.datetime.fromisoformat(s)

    def expire_time(self):
        """Expiration time."""
        s = self.metadata().get('expiration_timestamp')
        if s is None:
            return None
        return datetime.datetime.fromisoformat(s)

    def filename(self):
        """Get suggested media content filename."""
        return PurePath(self.metadata()['filename'])

    def title(self):
        """Get media title."""
        return self.metadata()['title']

    def webpage(self):
        """Get media web page URL."""
        return self.metadata()['webpage']

    def duration(self):
        """Duration in secons."""
        n = self.metadata()['duration_seconds']
        return datetime.timedelta(seconds=n)

    def bitrate(self):
        """Maximum bitrate in kb/s."""
        return max(x['bitrate'] for x in self.metadata()['flavors'])

    def size(self):
        """Maximum downloadable size in B."""
        return self.duration().total_seconds() * self.bitrate() / 8 * 1024

    def subtitle_languages(self):
        """Get subtitle languages."""
        return sorted(set(x['language'] for x in
                          self.metadata()['embedded_subtitles']))

    def mediatypes(self):
        """Get media types."""
        return sorted(set(x['media_type'] for x in
                          self.metadata()['flavors']))

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
        args = fmt_args('{cmd} --sublang {sublang} {url}', cmd=self.cmd,
                        sublang=self.sublang, url=self.url)
        proc = self._run(args)
        return proc.stdout

    def download_subtitles(self):
        """Download subtitles."""
        args = fmt_args('{cmd} --subtitlesonly --sublang {sublang} {url}',
                        cmd=self.cmd, sublang=self.sublang, url=self.url)
        proc = self._run(args)
        return proc.stdout

    def summary(self):
        """Get summary text."""
        raise NotImplementedError

    def is_rerun(self):
        """Try to guess whether program is a rerun."""
        return "uusinta" in self.summary().tolower()


def showinfo(url, verbosity=0):
    """Show info."""
    media = YleMedia(url)
    d = dict(
        url=url,
        webpage=media.webpage(),
        title=media.title(),
        filename=media.filename(),
        published=media.publish_time(),
        expires=media.expire_time(),
        mediatype=media.mediatype(),
        duration=media.duration(),
        bitrate=fmt_bitrate(media.bitrate()),
        size=fmt_size(media.size()),
        subtitles=media.subtitle_languages(),
        )
    print(tabulate(d.items(), tablefmt='plain', missingval='--'))
    if verbosity:
        pprint.pp(media.metadata())
    # if verbosity > 1:
    #     print(fmt_size(downloader(media.get_url()).size()), media.get_url())
    # if verbosity > 2:
    #     print(*(f'{fmt_size(downloader(x).size())}: {x}' for x in
    #             media.playlist_urls()), sep='\n')


def cli_ylemedia():
    """..."""
    verbosity = 0
    for arg in sys.argv[1:]:
        if arg == '-v':
            verbosity += 1
        else:
            showinfo(arg, verbosity=verbosity)
