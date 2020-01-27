#!/usr/bin/python3

"""Time and date related stuff."""

import datetime
import sys
from pathlib import Path

import click

from .files import valid_lines


class DateMixin:
    """Date mixin."""

    @classmethod
    def fromdatelike(cls, other):
        return cls(**_asdict(other, ['year', 'month', 'day']))

    def isoweek(self):
        """Return the ISO 8601 week number."""
        return self.isocalendar()[1]

    def isodate(self):
        """Return the ISO 8601 date without time."""
        return self.isoformat()[:10]

    def isoweekyear(self):
        """Return the ISO 8601 week-based year (i.e. year starts on Monday)."""
        return int(self.strftime('%G'))

    def yearday(self):
        """Return the day of the year."""
        return int(self.strftime('%j'))

    def tomorrow(self, days=1):
        """Shift by days."""
        # Just modifying the `day` variable fails when months change.
        o = self.fromordinal(self.toordinal() + days)
        return self.replace(year=o.year, month=o.month, day=o.day)

    def this_monday(self):
        """Return this week's monday."""
        return self + datetime.timedelta(days=-self.weekday())

    def next_monday(self):
        """Return next week's monday."""
        return self + datetime.timedelta(days=-self.weekday(), weeks=1)

    def easter(self, year=None):
        """Return the date of easter."""
        import dateutil.easter
        if year is None:
            year = self.year
        return dateutil.easter.easter(year)


class TimeMixin:
    """Time mixin."""

    @classmethod
    def fromtimelike(cls, other):
        return cls(**_asdict(other, ['hour', 'minute', 'second', 'microsecond',
                                     'tzinfo']))

    def fmt_cute_hours(self):
        """Format 'cute', i.e. quarter of day as a letter, plus hour offset."""
        letters = "nmde"  # Night, morning, day, evening.
        quarter, offset = divmod(self.hour, 6)
        return f'{letters[quarter]}{offset}'


class Date(datetime.date, DateMixin):
    """Extended date class."""


class Time(datetime.time, TimeMixin):
    """Extended time class."""


class Datetime(datetime.datetime, DateMixin, TimeMixin):
    """Extended datetime class."""

    @classmethod
    def fromdatetimelike(cls, other):
        return cls(**_asdict(other, ['year', 'month', 'day', 'hour', 'minute',
                                     'second', 'microsecond', 'tzinfo']))

    def date_only(self):
        """Prune time fields, leave date fields."""
        return self.fromordinal(self.toordinal())


class Timedelta(datetime.timedelta):
    """Extended timedelta class."""

    @classmethod
    def from_timedelta(cls, other):
        """Copy from another timedelta object."""
        return cls(seconds=other.total_seconds())

    def floatdays(self):
        """Return timedelta days as float."""
        return self.total_seconds() / 60**2 / 24

    def fmt_duration(self):
        """Format as duration like 'h:mm'."""
        hours, secs = divmod(self.total_seconds(), 60**2)
        # mins = round(secs / 60)
        hours, mins = int(hours), int(secs / 60)
        return f'{hours}:{mins:02}'


class JWhen:
    """Evaluate `when(1)`-style strings.

    See `set_today()` for supported keys in `self.d`. Strings beginning with a
    `@` are taken as plain date values.

    From `when(1)` manual (http://www.lightandmatter.com/when/when.html):
        w - day of the week
        m - month
        d - day of the month
        y - year
        j - modified Julian day number
        a - 1 for the first 7 days of the month, 2 for the next 7, etc.
        b - 1 for the last 7 days of the month, 2 for the previous 7, etc.
        c - on Monday or Friday, equals the day of the month of the nearest
            weekend day; otherwise -1
        e - days until this year's (Western) Easter
        z - day of the year (1 on New Year's day)
    """
    def __init__(self, today=None):
        self.set_today(today)

    # @staticmethod
    # def get_today(now=None):
    #     """Get the 'now' date."""
    #     if now is None or now == 'local':
    #         now = Datetime.now()
    #     if now == 'utc':
    #         now = Datetime.utcnow()
    #     try:
    #         now = Datetime.fromisoformat(now)
    #     except TypeError:
    #         pass
    #     return now.date_only()

    @staticmethod
    def a(date):
        """1 for the first 7 days of the month, 2 for the next 7, etc."""
        return (date.day - 1) // 7 + 1

    @staticmethod
    def b(date):
        """1 for the last 7 days of the month, 2 for the previous 7, etc."""
        # TODO: Does this work in december (month + 1)?
        dist = (date.replace(month=date.month + 1, day=1) - date).days
        return (dist - 1) // 7 + 1

    @staticmethod
    def posixday(date):
        """POSIX timestamp day."""
        return int(Datetime.fromdatelike(date).timestamp() / 60**2 / 24)

    def set_today(self, today=None):
        """Set the 'today' date."""
        if today is None:
            today = Date.today()
        self.today = today
        self.d = dict(
            res=None,  # Result of the previous expression evaluation.
            y=today.year,
            m=today.month,
            d=today.day,
            i=today.isodate(),  # NB: It's a string, must be quoted.
            wd=today.isoweekday(),
            wa=today.strftime('%a'),
            wk=today.isoweek(),
            wy=today.isoweekyear(),
            yd=today.yearday(),
            a=self.a(today),
            b=self.b(today),
            gd=today.toordinal(),  # Gregorian day. Jan 1 of year 1 is day 1.
            pd=self.posixday(self.today),
            )
        return self

    def eval(self, s):
        """Evaluate expression."""
        # pylint: disable=eval-used
        if s[0] == '@':
            # date = self.today.fromisoformat(s[1:])
            # res = self.today.toordinal() == date.toordinal()
            res = self.today == self.today.fromisoformat(s[1:])
        elif s[0] == '*':
            _, m, d = s.split()
            res = self.today == self.today.replace(month=int(m), day=int(d))
        else:
            res = eval(s, dict(__builtins__=None), self.d)
        self.d['datespec'] = s
        self.d['res'] = res
        return res


def _asdict(obj, keys):
    return {k: getattr(obj, k) for k in keys}


def timedelta_floatdays(td):
    """Return timedelta days as float."""
    # TODO: Remove.
    # return td.total_seconds() / 60 / 60 / 24
    return Timedelta(td).floatdays()


def fmt_duration(td):
    """Format media duration, represented by a timedelta."""
    # TODO: Remove.
    # td = datetime.timedelta(seconds=td.seconds)  # Drop microseconds.
    # return str(td)
    if td is None:
        return '?:?'
    # hours, secs = divmod(td.total_seconds(), 60**2)
    # mins = round(secs / 60)
    # return f'{int(hours)}:{mins:02}'
    # return Timedelta(td).fmt_duration()
    return Timedelta.from_timedelta(td).fmt_duration()


def cli_monday():
    """Print this week's monday."""
    fmt = '%Y-%m-%d'
    if len(sys.argv) > 1:
        fmt = sys.argv[1]
    print(Datetime.today().this_monday().strftime(fmt))


def cli_cute_hours():
    """Print cutely formatted hours."""
    print(Datetime.today().fmt_cute_hours())


def jwhen_filepaths(paths, glob='*.jwhen'):
    """Get file paths, explicitly given files or expanded directories."""
    for path in paths:
        if path.is_dir():
            yield from sorted(x for x in path.glob(glob) if x.is_file())
        else:
            yield path


def jwhen_relative_date(difference):
    # d = {-1: 'yesterday', 0: 'today', 1: 'tomorrow'}
    d = {-1: 'yestr', 0: 'today', 1: 'tomrw'}
    return d.get(difference, f'{difference:+d}d')


def jwhen_parse_line(line):
    datespec, desc = (x.strip() for x in line.split(';', 1))
    return datespec, desc


def jwhen_do_file(jwhen, path):
    """Process a jwhen file."""
    for line in valid_lines(path):
        try:
            datespec, desc = jwhen_parse_line(line)
        except ValueError as e:
            print(e)
            print(line)
        else:
            res = jwhen.eval(datespec)
            yield res, desc, jwhen.d


def jwhen_output(res, desc, d, formatted, relative, verbose):
    """Output a jwhen result."""
    desc = desc.format(**d)
    if res:
        if verbose:
            print(f'{formatted} {relative:>5}  {desc} [{d["datespec"]}]')
        else:
            print(f'{formatted} {relative:>5}  {desc}')
    elif verbose > 1:
        print(f'# {d["datespec"]}; {desc}')


@click.command()
@click.argument('paths', nargs=-1, type=Path, metavar='[PATH]...')
@click.option('-t', '--today', help='Date today.')
@click.option('-f', '--future', type=int, default=7,
              help='Number of future days to show (current day included).')
@click.option('-p', '--past', type=int, default=1,
              help='Number of past days to show.')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
def cli_jwhen(paths, today, future, past, verbose):
    """Process a when(1)-style file."""
    if today:
        today = Date.fromisoformat(today)
    if not paths:
        paths = [Path(click.get_app_dir('jwhen'))]
    jwhen = JWhen(today=today)
    begin = jwhen.today
    for i in range(-past, future):
        jwhen.set_today(begin.tomorrow(i))
        formatted = jwhen.today.strftime('%V-%a')
        relative = jwhen_relative_date(i)
        for path in jwhen_filepaths(paths):
            for res, desc, d in jwhen_do_file(jwhen, path):
                jwhen_output(res, desc, d, formatted, relative, verbose)
