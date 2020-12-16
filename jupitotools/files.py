"""Paths, files, and such."""

# TODO: (?) https://github.com/jaraco/path.py

import errno
import logging
import os
import shutil
import sys
import tempfile
from collections.abc import MutableMapping
from contextlib import contextmanager
from pathlib import Path, PosixPath

# # Try to use newer version of pathlib, if available.
# try:
#     from pathlib2 import Path
# except ImportError:
#     from pathlib import Path


# https://www.freedesktop.org/wiki/CommonExtendedAttributes/
# https://www.lesbonscomptes.com/pages/extattrs.html
# http://blog.siphos.be/2013/06/using-extended-attributes-for-custom-information
class XAttr(MutableMapping):
    """Dict-like interface to extended attributes.

    Listing, reading, and writing is done immediately.
    """

    def __init__(self, path, follow_symlinks=True):
        """Init."""
        self.path = os.fspath(path)
        self.follow_symlinks = follow_symlinks

    def _wrapper(self, func, *args):
        """General wrapper with follow_symlinks and KeyError."""
        try:
            return func(self.path, *args, follow_symlinks=self.follow_symlinks)
        except OSError as e:
            # if e.errno == 61:
            if e.errno == errno.ENODATA:
                raise KeyError(*args)
            raise

    def _list(self):
        """Read and return attribute keys."""
        # XXX: Should this be renamed to "keys" even if it returns a list?
        return self._wrapper(os.listxattr)

    def __getitem__(self, key):
        return self._wrapper(os.getxattr, key)

    def __setitem__(self, key, value):
        self._wrapper(os.setxattr, key, value)

    def __delitem__(self, key):
        self._wrapper(os.removexattr, key)

    def __iter__(self):
        return iter(self._list())

    def __len__(self):
        return len(self._list())

    def __contains__(self, key):
        return key in self._list()

    def __repr__(self):
        # XXX: Make it work on py34.
        return '{0.__class__.__name__}({0.path!r})'.format(self)
        # return f'{self.__class__.__name__}({self.path!r})'

    def __str__(self):
        # XXX: Make it work on py34.
        return '{}{}'.format(self.path, self._list())
        # return f'{self.path}{self._list()}'


class XAttrStr(XAttr):
    """XAttr for strings. Automatically convert to and from bytes."""

    def __getitem__(self, key):
        return super().__getitem__(key).decode('utf-8')

    def __setitem__(self, key, value):
        super().__setitem__(key, value.encode('utf-8'))


class ExtPath(PosixPath):
    """PosixPath extended for convenience."""

    @classmethod
    def expand(cls, path):
        """Create and expand."""
        # TODO: Test.
        return cls(os.path.expandvars(os.path.expanduser(os.fspath(path))))

    @property
    def suffix_(self):
        """Greedy version of suffix."""
        return ''.join(self.suffixes)

    @property
    def stem_(self):
        """Stem for greedy suffix."""
        return self.name[:-len(self.suffix_)]

    def with_hometilde(self):
        """Replace leading user home directory with tilde."""
        path = self.expanduser()
        nparts = len(path.home().parts)
        if path.parts[:nparts] == path.home().parts:
            path = '~' / self.__class__(*path.parts[nparts:])
        return path

    def disk_usage(self):
        """Get disk usage."""
        return shutil.disk_usage(self)

    def ensure_parent(self):
        """Create parent directory if not already there."""
        self.parent.mkdir(parents=True, exist_ok=True)

    def trash(self):
        """Send to trash."""
        # pylint: disable=import-outside-toplevel
        from send2trash import send2trash
        logging.debug('Sending to trash: %s', self)
        send2trash(os.fspath(self))

    def trash_or_rm(self):
        """Send to trash if possible, otherwise remove."""
        try:
            self.trash()
        except ImportError:
            logging.debug('Removing: %s', self)
            try:
                self.unlink()
            except IsADirectoryError:
                self.rmdir()


# class GlobChain:
#     def __init__(self, path, pattern, index=0, sort=True):
#         self.path = path
#         self.pattern = pattern
#         self.index = index
#         self.sort = sort
#
#     def __iter__(self):
#         def numeral_index(it, s):
#             print(s, [(i, x) for i, x in enumerate(it)])
#             return next(i for i, x in enumerate(it) if str(x) == s)
#         it = self.path.glob(self.pattern)
#         if self.sort:
#             it = iter(sorted(it))
#         i = self.index
#         if isinstance(i, str):
#             i = numeral_index(it, i)
#             it = self.path.glob(self.pattern)
#             if self.sort:
#                 it = iter(sorted(it))
#         for _ in range(i):
#             next(it)
#         return it


@contextmanager
def temp_dir(**kwargs):
    """A temporary directory context that deletes it afterwards."""
    # TODO: Use tempfile.TemporaryDirectory() instead.
    tmpdir = tempfile.mkdtemp(**kwargs)
    try:
        yield Path(tmpdir)
    finally:
        try:
            shutil.rmtree(tmpdir)
        except FileNotFoundError:
            pass


@contextmanager
def tempfile_and_backup(path, mode, bakext='.bak', **kwargs):
    """Create a temporary file for writing, do backup, replace destination."""
    path = Path(path)
    if path.exists() and not path.is_file():
        raise IOError('Not a regular file: {}'.format(path))
        # raise IOError(f'Not a regular file: {path}')
    with tempfile.NamedTemporaryFile(mode=mode, delete=False, **kwargs) as fp:
        try:
            yield fp
            fp.close()
            if path.exists():
                shutil.copy2(os.fspath(path),
                             os.fspath(path.with_suffix(bakext)))
            shutil.move(fp.name, os.fspath(path))
        finally:
            fp.close()
            if os.path.exists(fp.name):
                os.remove(fp.name)


def ensure_dir(path):
    """Ensure existence of the file's parent directory."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def sanitize_line(line, commenter='#'):
    """Clean up input line."""
    return line.split(commenter, 1)[0].strip()


def valid_lines(*paths, sanitizer=sanitize_line):
    """Read and yield lines that are neither empty nor comments."""
    for path in paths:
        with Path(path).open() as fp:
            yield from filter(None, (sanitizer(x) for x in fp))


def copy_times(src, dst):
    """Copy atime and mtime from src to dst, following symlinks."""
    src = os.fspath(src)
    dst = os.fspath(dst)
    st = os.stat(src)
    try:
        os.utime(dst, ns=(st.st_atime_ns, st.st_mtime_ns))
    except (TypeError, AttributeError):
        os.utime(dst, (st.st_atime, st.st_mtime))  # Pre-3.3 has no nanosec.


def move(src, dst):
    """Move path."""
    # Note: pathlib cannot handle cross-device operations.
    return shutil.move(os.fspath(src), os.fspath(dst))


def rm_rf(path):
    """Recursively remove path, whatever it is, if it exists. Like rm -rf."""
    path = os.fspath(path)
    if os.path.exists(path):
        logging.debug('Removing: %s', format(path))
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def abbreviate_path(path):
    """Abbreviate path (replace with first letters of parts)."""
    return ''.join(x[0] for x in path.parts)


def cli_abbr_path():
    """Abbreviate given or current pathname."""
    strings = sys.argv[1:] or [os.getcwd()]
    path = ExtPath(*strings).with_hometilde()
    print(abbreviate_path(path))
