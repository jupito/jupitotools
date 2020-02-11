"""Time and date related stuff."""

import datetime
import sys
from functools import lru_cache

import dateutil.easter
import dateutil.parser


class DateMixin:
    """Date mixin."""

    @classmethod
    def fromdatelike(cls, other):
        return cls(**_asdict(other, ['year', 'month', 'day']))

    @classmethod
    def parse(cls, s):
        """Parse date from string."""
        try:
            return cls.fromdatelike(dateutil.parser.isoparse(s))
        except ValueError:
            return cls.fromdatelike(dateutil.parser.parse(s))

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

    def posixday(self):
        """POSIX timestamp day."""
        return int(Datetime.fromdatelike(self).timestamp() / 60**2 / 24)

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

    @lru_cache
    def easter(self, year=None):
        """Return the date of (Western) Easter."""
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
