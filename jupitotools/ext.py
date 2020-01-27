"""Utility functions for external libraries."""


import json
import ucl
import zict


def zict_str(z):
    """Strings <-> bytes filter for `zict` mappings."""
    # First do: z = zict.File('/tmp/zict_dir')
    return zict.Func(str.encode, bytes.decode, z)


def zict_json(z):
    """JSON <-> str filter."""
    return zict.Func(json.dumps, json.loads, z)


def zict_ucl(z):
    """UCL <-> dict filter."""
    return zict.Func(ucl.dump, ucl.load, z)
