"""A `when(1)`-style simple calendar tool."""

# https://docs.python.org/3/library/functions.html#eval
# https://docs.python.org/3/library/ast.html#ast.literal_eval
# https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
# http://newville.github.io/asteval/

from functools import lru_cache
from pathlib import Path
# import re

import click

from .files import valid_lines
from .time import Date

# From when(1) manual (http://www.lightandmatter.com/when/when.html):
#     w - day of the week
#     m - month
#     d - day of the month
#     y - year
#     j - modified Julian day number
#     a - 1 for the first 7 days of the month, 2 for the next 7, etc.
#     b - 1 for the last 7 days of the month, 2 for the previous 7, etc.
#     c - on Monday or Friday, equals the day of the month of the nearest
#         weekend day; otherwise -1
#     e - days until this year's (Western) Easter
#     z - day of the year (1 on New Year's day)

DEFAULT_FORMATS = dict(
    date_week='%m-%d %V~%u',
    date_week_yearday='%m-%d %V~%u~%j',
    date_weekname='%m-%d %V~%a',
    )


class Event:
    """Calendar event."""
    SEP = ';'

    def __init__(self, path, line):
        self.path = path
        self.expr, *self.descs = [x.strip() for x in line.split(self.SEP)]
        self.desc = self.descs[0]

    def __str__(self):
        return f'{self.path}: {self.expr}; {self.desc}'

    @lru_cache()
    def time(self):
        """Return event time, or None."""
        tokens = self.desc.split(maxsplit=1)
        if tokens and '/' in tokens[0]:
            return tokens[0]
        return None

    @lru_cache()
    def location(self):
        """Return event location, or None."""
        tokens = self.desc.split('@', 1)
        if len(tokens) > 1:
            return tokens[1]
        return None


def yield_filepaths(paths, glob='*.milloin'):
    """Get file paths, explicitly given files or expanded directories."""
    # ~/.config/jwhen/test1.milloin
    for path in paths:
        if path.is_dir():
            # Descend to subdirectories maximum one level.
            yield from sorted(x for x in path.glob(glob) if x.is_file() and
                              x.suffix != '.disable')
        else:
            yield path


@click.command()
@click.argument('paths', nargs=-1, type=Path, metavar='[PATH]...')
@click.option('-t', '--today', help='Date today.')
@click.option('-f', '--future', type=int, default=7,
              help='Number of future days to show (current day included).')
@click.option('-p', '--past', type=int, default=1,
              help='Number of past days to show.')
@click.option('--fmt', default='date_week', help='Output date format.')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
def cli_milloin(paths, today, future, past, fmt, verbose):
    """Process a when(1)-style file."""
    if not paths:
        # ~/.config/milloin/*.milloin
        paths = [Path(click.get_app_dir('milloin'))]
    today = Date.fromisoformat(today) if today else Date.today()
    fmt = DEFAULT_FORMATS.get(fmt, fmt)
    # jwhen = JWhen(today=today)
    # begin = jwhen.today
    # for i in range(-past, future):
    #     jwhen.set_today(begin.tomorrow(i))
    #     formatted = jwhen.today.strftime(fmt)
    #     relative = relative_date(i)
    #     for path in filepaths(paths):
    #         for res, desc, d in do_file(jwhen, path):
    #             output(res, desc, d, formatted, relative, verbose)

    # for each file:
    #     for each line:
    #         parse, create, collect entry
    # make date objects
    # for each date:
    #     for each entry:
    #         if expression evaluates true with date, show description

    dates = [today.tomorrow(x) for x in range(-past, future + 1)]
    print(f'Today is {today}.')
    paths = list(yield_filepaths(paths))
    print(f'Filepaths: {", ".join(str(x) for x in paths)}.')
    events = [Event(x, y) for x in paths for y in valid_lines(x)]

    for date in dates:
        if verbose > 0:
            marker = '*' if date == today else ' '
            print(f'{marker} {date}')
    #     for event in events:
    #         if event.is_match(date):
    #             if verbose > 1:
    #                 print(event.desc)
    for event in events:
        print(event)
        if any([event.time(), event.location()]):
            print('-', event.time(), event.location())
