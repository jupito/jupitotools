"""A `when(1)`-style simple calendar tool."""

# https://docs.python.org/3/library/functions.html#eval
# https://docs.python.org/3/library/ast.html#ast.literal_eval
# https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
# http://newville.github.io/asteval/
# https://en.wikipedia.org/wiki/ISO_8601

from functools import lru_cache
from pathlib import Path
import re

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
        try:
            y, m, d = parse_date_string(self.expr)
            parsed = Date(y or today.year, m or today.month, d or today.day)
            return date == parsed
        except ValueError as e:
            print(e)
        # # TODO: For testing.
        # return abs(date.toordinal() - today.toordinal()) < 2


def parse_date_string(s):
    """Attempt to parse the expression as a simple date string."""
    # Empty or zero is a wildcard.
    y = r'(\d\d\d\d)'
    m = r'(\d\d)'
    d = m
    # wk = r'W' + d
    # wd = r'(\d)'
    # yd = r'(\d\d\d)'

    date_ymd = '-'.join([y, m, d])
    # date_ym = '-'.join([y, m])
    # date_ywd = '-'.join([y, wk, wd])
    # date_yw = '-'.join([y, wk])
    # date_yd = '-'.join([y, yd])

    match = re.match(date_ymd, s)
    if match is None:
        raise ValueError('No valid date string found', s)
    return [int(x) for x in match.groups()]


def yield_filepaths(paths, glob='*.milloin'):
    """Get file paths, explicitly given files or expanded directories."""
    for path in paths:
        if path.is_dir():
            yield from sorted(x for x in path.glob(glob) if x.is_file() and
                              x.suffix != '.disable')
        else:
            yield path


def get_matches(dates, events, today):
    """Get matches."""
    def collect_matches(date):
        def is_match(event):
            return event.match(date, today)
        return filter(is_match, events)
    return {x: list(collect_matches(x)) for x in dates}


def date_marker(date, today):
    """Return a one-character date marker."""
    if date == today:
        return '*'
    if date == today.tomorrow():
        return '+'
    if date == today.tomorrow(-1):
        return '-'
    return ' '


@click.group()
@click.option('-P', '--path', type=Path, help='Input path')
@click.option('-t', '--today', help='Date today.')
@click.option('-f', '--future', type=int, default=7,
              help='Number of future days to show (current day included).')
@click.option('-p', '--past', type=int, default=1,
              help='Number of past days to show.')
@click.option('--fmt', default='date_week', help='Output date format.')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
@click.pass_context
def cli(ctx, path, today, future, past, fmt, verbose):
    """A when(1)-style calendar application."""
    ctx.ensure_object(dict)
    paths = [path]
    if not paths:
        # ~/.config/milloin/*.milloin
        paths = [Path(click.get_app_dir('milloin'))]
    paths = list(yield_filepaths(paths))
    today = Date.fromisoformat(today) if today else Date.today()
    dates = [today.tomorrow(x) for x in range(-past, future + 1)]
    events = [Event(y, x) for x in paths for y in valid_lines(x)]
    ctx.obj['paths'] = paths
    ctx.obj['today'] = today
    ctx.obj['dates'] = dates
    ctx.obj['events'] = events
    ctx.obj['fmt'] = DEFAULT_FORMATS.get(fmt, fmt)
    if verbose > 0:
        print(f'Today is {today}.')
        print(f'Filepaths: {", ".join(str(x) for x in paths)}.')


@cli.command('agenda')
@click.pass_context
def cli_agenda(ctx):
    """Print agenda."""
    today = ctx.obj['today']

    matches = get_matches(ctx.obj['dates'], ctx.obj['events'], today)
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


@cli.command('dates')
@click.pass_context
def cli_list_dates(ctx):
    """List dates."""
    for date in ctx.obj['dates']:
        marker = date_marker(date, ctx.obj['today'])
        print(f'{marker} {date}')


@cli.command('all')
@click.pass_context
def cli_list_all_events(ctx):
    """List all events."""
    for event in ctx.obj['events']:
        print(event)
        if any([event.time(), event.location()]):
            print('-', event.time(), event.location())
