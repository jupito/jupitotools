"""Miscellaneous utility funcionality."""

import logging
import os
import platform
import shlex
import shutil
import subprocess
import sys
from functools import lru_cache
from itertools import chain
from pathlib import PurePath


class TagDict(dict):
    """Tag string as dict."""
    tag_sep = ','
    key_sep = '='

    @classmethod
    def fromstr(cls, s, default_value=None):
        """Parse tag string."""
        def get_key_value(tag):
            if cls.key_sep in tag:
                k, v = tag.split(cls.key_sep, 1)
            else:
                k, v = tag, default_value
            return cls.normalize_key(k), v
        return cls(get_key_value(x) for x in s.split(cls.tag_sep))

    def __str__(self):
        """Generate tag string."""
        def get_tag(k, v):
            if v is None:
                return str(k)
            return f'{k}{self.key_sep}{v}'
        return self.tag_sep.join((get_tag(k, v) for k, v in self.items()))

    @staticmethod
    def normalize_key(key, space='_'):
        """Normalize tag key."""
        return key.strip().lower().replace(' ', space).replace("'", '')

    # @staticmethod
    # def key_is_sane(key):
    #     """Is tag key behaving nicely?"""
    #     return len(key) and all(x.isalnum() or x in '_&/-:' for x in key)


def one(iterable, too_short=None, too_long=None):
    """Return the only item from iterable.

    Return the first item from *iterable*, which is expected to contain only
    that item. Raise an exception if *iterable* is empty or has more than one
    item. This funcion was taken from `more_itertools.one`.
    """
    it = iter(iterable)
    try:
        value = next(it)
    except StopIteration:
        raise too_short or ValueError('Too few items in iterable (expected 1)')
    try:
        next(it)
    except StopIteration:
        pass
    else:
        raise too_long or ValueError('Too many items in iterable (expected 1)')
    return value


def clamp(value, mn, mx):
    """Clamp value between minimun, maximum."""
    assert mn <= mx, (mn, mx)
    return max(min(value, mx), mn)


def int_or_float(x):
    """Return `x` as `int` if possible, or as `float` otherwise."""
    x = float(x)
    if x.is_integer():
        return int(x)
    return x


def asline(iterable, sep=' ', end='\n'):
    """Convert an iterable into a line."""
    return sep.join(str(x) for x in iterable) + end


def numbered_lines(iterable):
    """Return iterator of members as strings prefixed by line number."""
    return (f'{i}: {x}' for i, x in enumerate(iterable, start=1))


@lru_cache(maxsize=32)
def get_prefix(n, factor=1024, prefixes=None):
    """Get magnitude prefix for number."""
    if prefixes is None:
        prefixes = ('',) + tuple('kMGTPEZY')
    if abs(n) < factor or len(prefixes) == 1:
        return n, prefixes[0]
    return get_prefix(n / factor, factor=factor, prefixes=prefixes[1:])


def fmt_size(n, unit='B'):
    """Format file size (given as B) in human-readable way (k, M, G, ...)."""
    if n is None:
        return f'?{unit}'
    n, prefix = get_prefix(n)
    return f'{n:.0f}{prefix}{unit}'


def fmt_bitrate(bitrate):
    """Format human-readable bitrate, given as kb/s."""
    # return f'{bitrate}kb/s'
    return fmt_size(bitrate * 1024, unit='b/s')


def fmt_args(_cmd, *args, **kwargs):
    """Split first, then format. To easily have arguments with spaces."""
    return [x.format(**kwargs) for x in shlex.split(_cmd)] + [os.fspath(x) for
                                                              x in args]


def shlex_join(split_command):
    """Return a shell-escaped string from *split_command*.

    This is from Python 3.8:
    https://github.com/python/cpython/blob/3.8/Lib/shlex.py

    XXX: Obsolete with 3.8.
    """
    return ' '.join(shlex.quote(arg) for arg in split_command)


def esc_seq(n, s):
    """Escape sequence. Call sys.stdout.write() to apply."""
    return f'\033]{n};{s}\007'


def set_term_title(title):
    """Return control string for setting X terminal title."""
    return esc_seq(0, title)


def set_term_bg(color):
    """Return control string for setting X term bg color, eg 'rgb:ff/ee/ee'."""
    return esc_seq(11, color)


def ring_bell():
    """Bell character."""
    return '\a'


# pylint: disable=too-many-arguments
def notify_send(summary, body=None, urgency=None, expire_time=None,
                app_name=None, icons=None, categories=None, hints=None,
                fgcolor=None, bgcolor=None, progress=None):
    """Send notification.

    At least dunst supports fgcolor, bgcolor, progress.
    """
    def _hint(typ, name, value):
        assert typ in ['int', 'double', 'string', 'byte'], typ
        return ['-h', f'{typ}:{name}:{value}']

    args = ['notify-send', summary]
    if body is not None:
        args.append(body)
    if urgency is not None:
        assert urgency in ['low', 'normal', 'critical'], urgency
        args.extend(['-u', urgency])
    if expire_time is not None:
        args.extend(['-t', str(expire_time)])
    if app_name is not None:
        args.extend(['-a', app_name])
    if icons:
        args.extend(['-i', ','.join(icons)])
    if categories:
        args.extend(['-c', ','.join(categories)])
    if hints:
        args.extend(chain.from_iterable(_hint(*x) for x in hints))
    if fgcolor is not None:
        args.extend(_hint('string', 'fgcolor', fgcolor))
    if bgcolor is not None:
        args.extend(_hint('string', 'bgcolor', bgcolor))
    if progress is not None:
        assert 0 <= progress <= 100, progress
        args.extend(_hint('int', 'value', progress))
    logging.debug('Running: %s', args)
    subprocess.check_call(args)


def truncate(s, reserved=0, columns=None, ellipsis='…', minimum_length=2):
    """Truncate string to fit limit, if possible."""
    if columns is None:
        columns = shutil.get_terminal_size().columns
    space_left = max(columns - reserved, minimum_length)
    if space_left < len(s):
        s = s[:space_left]
        if ellipsis:
            s = s[:-len(ellipsis)] + ellipsis
    return s


def camel(s):
    """Convert string to CamelCase."""
    return ''.join(x[0].upper() + x[1:].lower() for x in s.split())


def get_loglevel(name):
    """Return the numeric correspondent of a logging level name."""
    try:
        return getattr(logging, name.upper())
    except AttributeError:
        raise ValueError(f'Invalid log level: {name}')


def get_progname():
    """Get program name."""
    return PurePath(sys.argv[0]).name


def get_hostname():
    """Try to return system hostname in a portable fashion."""
    name = platform.uname().node
    if not name:
        raise OSError(None, 'Could not determine hostname')
    return name


def peco(lines, initial=0, index=False, prg='peco'):
    """Use 'peco' to select items from list. Return selected lines, or None."""
    args = [prg, f'--initial-index={initial}']
    if index:
        lines = (f'{i} {x}' for i, x in enumerate(lines))
    d = dict(input='\n'.join(lines), stdout=subprocess.PIPE,
             universal_newlines=True)
    process = subprocess.run(args, **d)
    if process.stdout:
        # Filter tailing ''.
        output_lines = filter(None, process.stdout.split('\n'))
        if index:
            return [int(x.split(maxsplit=1)[0]) for x in output_lines]
        return output_lines
    return None
