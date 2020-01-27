"""Download."""


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
