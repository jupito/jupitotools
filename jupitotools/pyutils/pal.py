#!/bin/python3

"""Palette test.
Usage: pal.py < /usr/share/X11/rgb.txt.
Outputs RGB, hex, term hex, term dec, fg test, bg test, bg test RGB mode, name.
"""

# TODO: Use NamedColor dataclass. :)

# https://github.com/welbornprod/colr
# https://gist.github.com/XVilka/8346728
# https://lists.suckless.org/dev/1307/16688.html
# https://github.com/martanne/dvtm/issues/10

import sys
from typing import Tuple
import dataclasses
from dataclasses import dataclass

import colr
from colr import Colr


@dataclass(order=True, frozen=True)
class Color:
    r: int
    g: int
    b: int

    asdict = dataclasses.asdict
    astuple = dataclasses.astuple
    replace = dataclasses.astuple

    @property
    def rgb(self) -> Tuple[int]:
        return tuple([self.r, self.g, self.b])

    @property
    def hex(self) -> str:
        return colr.rgb2hex(*self.rgb)


@dataclass(order=True, frozen=True)
class NamedColor(Color):
    name: str


def sanitize_line(line, commenter='!'):
    """Clean up input line."""
    return line.split(commenter, 1)[0].strip()


def valid_lines(path):
    """Read and yield lines that are neither empty nor comments."""
    with sys.stdin as fp:
        yield from filter(None, (sanitize_line(x) for x in fp))


def main(sep='  '):
    """Palette test main function."""
    for line in valid_lines(None):
        r, g, b, name = line.split(maxsplit=3)
        r, g, b = (int(x) for x in [r, g, b])

        h = colr.rgb2hex(r, g, b)
        th = colr.rgb2termhex(r, g, b)
        t = colr.rgb2term(r, g, b)

        d = dict(r=r, g=g, b=b, name=name, h=h, th=th, t=t)
        d['testfg'] = Colr().hex(h, 'test', rgb_mode=False)
        d['testbg'] = Colr().b_hex(h, 'test    ', rgb_mode=False)
        d['testbg_rgb'] = Colr().b_hex(h, '    ', rgb_mode=True)

        fmt = sep.join(['{r:3} {g:3} {b:3}',
                        '0x{h}',
                        '0x{th}',
                        '{t:>3s}',
                        '{testfg}{testbg}{testbg_rgb}',
                        '{name}'])
        print(fmt.format(**d))


if __name__ == '__main__':
    main()
