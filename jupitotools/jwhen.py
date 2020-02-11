"""A `when(1)`-style simple calendar tool."""

from pathlib import Path

import click

from .files import valid_lines
from .time import Date, Datetime

HELP = """
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

DEFAULT_FORMATS = dict(
    date_week='%m-%d %V~%u',
    date_week_yearday='%m-%d %V~%u~%j',
    date_weekname='%m-%d %V~%a',
    )

# ~/.config/jwhen/test.jwhen


class JWhen:
    """Evaluate `when(1)`-style strings.

    See `set_today()` for supported keys in `self.d`. Strings beginning with a
    `@` are taken as plain date values.
    """
    def __init__(self, today=None):
        self.exp = None  # Previous expression.
        self.res = None  # Result of the previous expression evaluation.
        self.set_today(today)

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

    def set_today(self, today=None):
        """Set the 'today' date."""
        if today is None:
            today = Date.today()
        self.today = today
        return self

    def __getitem__(self, key):
        try:
            return getattr(self, '_key_' + key)()
        except AttributeError:
            return self._getitem_fallback(key)

    def _key_y(self): return self.today.year
    def _key_m(self): return self.today.month
    def _key_d(self): return self.today.day
    def _key_md(self): return self.today.month, self.today.day

    # NB: It's a string, must be quoted.
    def _key_i(self): return self.today.isodate()
    def _key_wd(self): return self.today.isoweekday()
    def _key_wa(self): return self.today.strftime('%a')

    def _key_wk(self): return self.today.isoweek()
    def _key_wy(self): return self.today.isoweekyear()
    def _key_yd(self): return self.today.yearday()

    def _key_a(self): return self.a(self.today)
    def _key_b(self): return self.b(self.today)

    # Gregorian day. Jan 1 of year 1 is day 1.
    def _key_gd(self): return self.today.toordinal()
    def _key_pd(self): return self.today.posixday()
    def _key_workday(self): return self.today.isoweekday() < 6
    def _key_until_easter(self): return (self.today.easter() - self.today).days

    def _key_wk_of(self):
        def is_week_of(month, day):
            other = self.today.replace(month=int(month), day=int(day))
            return self.today.isoweek() == other.isoweek()
        return is_week_of

    def _getitem_fallback(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        if key.capitalize() in 'Mon Tue Wed Thu Fri Sat Sun'.split():
            return key.capitalize()
        return None

    def eval(self, s):
        """Evaluate expression."""
        # pylint: disable=eval-used
        if s[0] == '=':
            res = self.today.fromisoformat(s[1:])
        elif s[0] == '*':
            _, m, d = s.split()
            res = self.today.replace(month=int(m), day=int(d))
        else:
            res = eval(s, dict(__builtins__=None), self)
            # try:
            #     res = eval(s, dict(__builtins__=None), self)
            # except SyntaxError:
            #     res = self.today.parse(s)
        self.exp = s
        self.res = res
        # if isinstance(res, (tuple, list)):
        #     m, d = [int(x) for x in res]
        #     res = self.today.replace(month=m, day=d)
        if isinstance(res, str):
            res = self.today.parse(res)
        if isinstance(res, type(self.today)):
            res = self.today == res
        return res


def filepaths(paths, glob='*.jwhen'):
    """Get file paths, explicitly given files or expanded directories."""
    for path in paths:
        if path.is_dir():
            yield from sorted(x for x in path.glob(glob) if x.is_file())
        else:
            yield path


def relative_date(difference):
    # d = {-1: 'yesterday', 0: 'today', 1: 'tomorrow'}
    d = {-1: 'yestr', 0: 'today', 1: 'tomrw'}
    return d.get(difference, f'{difference:+d}d')


def parse_line(line):
    exp, desc = (x.strip() for x in line.split(';', 1))
    return exp, desc


def do_file(jwhen, path):
    """Process a jwhen file."""
    for line in valid_lines(path):
        try:
            exp, desc = parse_line(line)
        except ValueError as e:
            print(e)
            print(line)
        else:
            res = jwhen.eval(exp)
            yield res, desc, jwhen


def output(res, desc, d, formatted, relative, verbose):
    """Output a jwhen result."""
    desc = desc.format_map(d)
    if res:
        if verbose:
            print(f'{formatted} {relative:>5}  {desc} [{d["exp"]}]')
        else:
            print(f'{formatted} {relative:>5}  {desc}')
    elif verbose > 1:
        print(f'# {d["exp"]}; {desc}')


@click.command()
@click.argument('paths', nargs=-1, type=Path, metavar='[PATH]...')
@click.option('-t', '--today', help='Date today.')
@click.option('-f', '--future', type=int, default=14,
              help='Number of future days to show (current day included).')
@click.option('-p', '--past', type=int, default=1,
              help='Number of past days to show.')
@click.option('--fmt', default='date_week', help='Output date format.')
@click.option('-v', '--verbose', count=True, help='Increase verbosity.')
def cli_jwhen(paths, today, future, past, fmt, verbose):
    """Process a when(1)-style file."""
    if today:
        today = Date.fromisoformat(today)
    if not paths:
        paths = [Path(click.get_app_dir('jwhen'))]  # ~/.config/jwhen/*.jwhen
    fmt = DEFAULT_FORMATS.get(fmt, fmt)
    jwhen = JWhen(today=today)
    begin = jwhen.today
    for i in range(-past, future):
        jwhen.set_today(begin.tomorrow(i))
        formatted = jwhen.today.strftime(fmt)
        relative = relative_date(i)
        for path in filepaths(paths):
            for res, desc, d in do_file(jwhen, path):
                output(res, desc, d, formatted, relative, verbose)
