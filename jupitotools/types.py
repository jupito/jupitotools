"""Types."""

import dataclasses


class ConvertibleDataclass:
    """Data class with member functions for convenient conversion."""

    _astuple = dataclasses.astuple
    _asdict = dataclasses.asdict


class IterableDataclass:
    """Iterable data class."""

    def __iter__(self):
        return iter(dataclasses.astuple(self))


class SplitItemDataclass:
    """A data class that provides a way to format items using a separator."""

    _sep = '-'  # Item separator.

    @classmethod
    def parse(cls, s):
        """Parse a string of items separated by a separator."""
        fields = dataclasses.fields(cls)
        items = s.split(cls._sep)
        if len(items) > len(fields):
            raise ValueError(f'Too many items for {cls.__qualname__}: {s}')
        return cls(**{x.name: x.type(y) for x, y in zip(fields, items)})

    def __str__(self):
        """Format items separated by a separator."""
        items = (str(x) for x in dataclasses.astuple(self) if x is not None)
        return self._sep.join(items)
