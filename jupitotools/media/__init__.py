"""Media targets."""

# file, dir, playlist, http, youtube, yle

# https://en.wikipedia.org/wiki/Uniform_Resource_Identifier

# from pathlib import Path, PurePath
# from functools import lru_cache
#
# import requests
#
#
# class MediaURI:
#     """Media URI."""
#
#     def __init__(self, uri):
#         self.uri = uri
#
#     def size(self):
#         raise NotImplementedError
#
#     def duration(self):
#         raise NotImplementedError
#
#     def guess(self):
#         """Guess type of URI."""
#         raise NotImplementedError
#
#
# class MediaURL(MediaURI):
#     """Media URL."""
#
#     def __init__(self, uri):
#         super().__init__(uri)
#
#     @property
#     @lru_cache(None)
#     def url_parsed(self):
#         return requests.utils.urlparse(self.url)
#
#     def filename(self):
#         return PurePath(PurePath(self.url_parsed.path).name)
#
#     def size(self):
#         raise NotImplementedError
#
#     def download(self):
#         return net.download(self.url, self.dst_path, tmp_path=self.tmp_path,
#                             progress=self.progress)
