"""Looking at when(1)."""

# http://www.lightandmatter.com/when/when.html
# /usr/bin/when

# import re
from functools import lru_cache
# from pathlib import Path

# from dateutil import parser

# import jupitotools.time
from jupitotools.time import Datetime, Timedelta


class Event:
    """Calendar event."""
    LOCATION_PREFIX = '@'

    def __init__(self, datetime, desc):
        """Initialize."""
        assert not any([datetime.second, datetime.microsecond]), datetime
        self.datetime = datetime
        self.desc = desc

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.datetime} , {self.desc})'

    def __str__(self):
        return f'{self.datetime} , {self.desc}'

    @classmethod
    def parse(cls, s):
        """Parse a string."""
        datetime, desc = (x.strip() for x in s.split(',', maxsplit=1))
        datetime = Datetime.fromisoformat(datetime)
        return cls(datetime, desc)

    @property
    def date(self):
        return self.datetime.date()

    @property
    def time(self):
        return self.datetime.time()

    def has_time(self):
        """Tells if it has time (not just date)."""
        return not self.datetime.timetuple() == self.date.timetuple()

    @property
    @lru_cache()
    def location(self):
        return self.desc.split(self.LOCATION_PREFIX, maxsplit=1)[1].strip()

    def check_sanity(self):
        if self.LOCATION_PREFIX in self.location:
            raise Warning('Location with sep char')


# Testing...
events = [
    Event.parse(' 1998-12-31 03:12, joo siis /25min @Hki @ Tku, Finland'),
    Event.parse(' 2014-03-12 , joo siis /25min @Hki @ Tku, Finland; joo '),
]
dts = [x.datetime for x in events]
ds = [x.date for x in events]
ts = [x.time for x in events]
e1, e2 = events
dt1, dt2 = dts
d1, d2 = ds
t1, t2 = ts
