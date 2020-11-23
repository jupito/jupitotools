"""Contacts."""

# Reading contacts from Baikal db:
# echo .dump | sqlite3 db.sqlite >> db.sqlite_dump.txt
# grep -i 'insert into cards' db.sqlite_dump.txt >> cards_dump.txt

# https://en.wikipedia.org/wiki/Telephone_number
# https://en.wikipedia.org/wiki/Telephone_numbering_plan

import re
import sys
# from pathlib import Path

import click
import vobject


def vcard_from_string(s):
    """..."""
    regexp = r'BEGIN:VCARD.*END:VCARD'
    match = re.search(regexp, s, flags=re.I)
    if match is None:
        # raise ValueError('No vcard found', s)
        return None
    s = match.group(0).replace('\\r\\n', '\n')
    card = vobject.readOne(s)
    return card


def compact_values(lst):
    """..."""
    assert all(x.validate() for x in lst), lst
    # params_lst = [tuple(x.params.values()) for x in lst]
    # assert all(len(x) == 1 for x in params_lst), [lst, params_lst]
    # params = sorted(set(tuple(sorted(x[0])) for x in params_lst))
    # return params

    def trim_str(s):
        return str(s).strip().replace('  ', ' ')

    try:
        values = ', '.join(set(trim_str(x.value) for x in lst))
    except TypeError as e:
        print(e, lst)
        raise
    return values


def compact_vcard(card):
    """Compact representation."""
    d = card.contents
    discard_keys = 'version', 'uid', 'rev', 'photo'
    keys = list(d.keys())
    for key in keys:
        if key in d:
            if key in discard_keys:
                del d[key]
            else:
                d[key] = compact_values(d.pop(key))
    if 'n' in d and 'fn' in d and d['n'] == d['fn']:
        del d['fn']
    return '; '.join(f'{k}={v}' for k, v in d.items())


@click.command()
def cli_read_vcards_from_dump():
    """..."""
    it = (vcard_from_string(x) for x in sys.stdin)
    cards = list(filter(None, it))
    print(len(cards))
    cards[0].prettyPrint()
    cards[-1].prettyPrint()
    for i, card in enumerate(cards):
        print(f'{i}: {compact_vcard(card)}')
