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

    def __init__(self, line, path):
        self.line = line
        self.path = path
        self.expr, *self.descs = [x.strip() for x in line.split(self.SEP)]
        self.desc = self.descs[0]

    # def tokens(self):
    #     return (x.strip() for x in self.line.split(self.SEP))

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

    @lru_cache()
    def match(self, date, today):
        """Does date match with event?"""
        # TODO
        # return True
        return abs(date.toordinal() - today.toordinal()) < 2


def yield_filepaths(paths, glob='*.milloin'):
    """Get file paths, explicitly given files or expanded directories."""
    for path in paths:
        if path.is_dir():
            yield from sorted(x for x in path.glob(glob) if x.is_file() and
                              x.suffix != '.disable')
        else:
            yield path


def print_dates(dates, today):
    for date in dates:
        marker = '*' if date == today else ' '
        print(f'{marker} {date}')


def print_events(events):
    for event in events:
        print(event)
        if any([event.time(), event.location()]):
            print('-', event.time(), event.location())


def date_marker(date, today):
    """Return a one-character date marker."""
    if date == today:
        return '*'
    if date == today.tomorrow():
        return '+'
    if date == today.tomorrow(-1):
        return '-'
    return ' '


def print_agenda(matches, today):
    """Print agenda."""
    for date, events in matches.items():
        marker = date_marker(date, today)
        datestr_normal = str(date)
        datestr_repeating = ' ' * len(datestr_normal)
        if not events:
            print(f'{marker} {datestr_normal} (no events)')
        for i, event in enumerate(events):
            datestr = datestr_normal if i == 0 else datestr_repeating
            eventstr = str(event)[:70]
            print(f'{marker} {datestr} {eventstr}')


@click.group()
def cli():
    pass


@cli.command()
@click.argument('paths', nargs=-1, type=Path, metavar='[PATH]...')
@click.option('-t', '--today', help='Date today.')
@click.option('-f', '--future', type=int, default=7,
              help='Number of future days to show (current day included).')
@click.option('-p', '--past', type=int, default=1,
              help='Number of past days to show.')
@click.option('--fmt', default='date_week', help='Output date format.')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
def agenda(paths, today, future, past, fmt, verbose):
    """Process a when(1)-style file."""
    if not paths:
        # ~/.config/milloin/*.milloin
        paths = [Path(click.get_app_dir('milloin'))]
    today = Date.fromisoformat(today) if today else Date.today()
    fmt = DEFAULT_FORMATS.get(fmt, fmt)

    # for each file:
    #     for each line:
    #         parse, create, collect entry
    # make date objects
    # for each date:
    #     for each entry:
    #         if expression evaluates true with date, show description

    dates = [today.tomorrow(x) for x in range(-past, future + 1)]
    paths = list(yield_filepaths(paths))
    events = [Event(y, x) for x in paths for y in valid_lines(x)]

    def collect_matches(date, events, today):
        # it = (x if x.match(date, today) else None for x in events)
        # yield from filter(None, it)
        def event_matches(event):
            return event.match(date, today)
        return filter(event_matches, events)
    matches = {x: list(collect_matches(x, events, today)) for x in dates}

    if verbose > 0:
        print(f'Today is {today}.')
        print(f'Filepaths: {", ".join(str(x) for x in paths)}.')
        print_dates(dates, today)
    if verbose > 1:
        print_events(events)
    print_agenda(matches, today)
