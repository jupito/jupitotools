# experimentation, under construction


class lazy_property(object):
    '''Decorator: Enables the value of a property to be lazy-loaded.
    From Mercurial's util.propertycache

    Apply this decorator to a no-argument method of a class and you
    will be able to access the result as a lazy-loaded class property.
    The method becomes inaccessible, and the property isn't loaded
    until the first time it's called.  Repeated calls to the property
    don't re-run the function.

    This takes advantage of the override behavior of Descriptors -
    __get__ is only called if an attribute with the same name does
    not exist.  By not setting __set__ this is a non-data descriptor,
    and "If an instance's dictionary has an entry with the same name
    as a non-data descriptor, the dictionary entry takes precedence."
     - http://users.rcn.com/python/download/Descriptor.htm

    To trigger a re-computation, 'del' the property - the value, not
    this class, will be deleted, and the value will be restored upon
    the next attempt to access the property.
    '''
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, obj, typ=None):
        result = self.func(obj)
        setattr(obj, self.name, result)
        return result


def memoize(f):
    """Memoization decorator."""
    cache = {}

    def helper(*args, **kwargs):
        t = (tuple(args), tuple(sorted(kwargs.items())))
        if t not in cache:
            cache[t] = f(*args, **kwargs)
        return cache[t]
    return helper
