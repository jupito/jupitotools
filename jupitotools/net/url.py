"""URL functionality."""

import sys
from itertools import chain

import click
import boltons.urlutils

_examples = '''
https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
https://suomenkuvalehti.fi/jutut/ulkomaat/salaliittoihmiset-touhottavat-adrenokromista-ja-vaittavat-sen-liittyvan-lasten-kiduttamiseen-totuus-aineesta-oli-iso-pettymys/?shared=1182821-d1082217-500&utm_medium=Social&utm_source=Facebook&fbclid=IwAR2fElPrreYVLEl8SVfUELNKANcNIBXs-mvEFRuMDw3vNborUcob71OAPwA#Echobox=1620987596
https://www.facebook.com/Philosophyhounds/posts/423494438973487?__cft__[0]=AZWL7nGrd311EODcgQ4pXmHIwjVu5WkxYvwa3pI5JBTIyw7cduCXHydP-wVyQEgUuAzQQDCHx9Bv_Wt7geNoiRsox9dzxfrfvsxjYHJir3c-V9CFt4Dqpx778BURzXQSDbB53zrQBUkGN7OgYvk3rUtWysi-YOe7Eg_aF-WGO7RxpQ&__tn__=%2CO%2CP-R
http://psyvault.net/viewtopic.php?f=8&t=476&sid=578a367c6b421ddbc6c4263c2e5d2a81&start=30
http://tajunta.net/blog/tuukka-virtaperko-ja-laadun-metafysiikka/#.X7BS5_r8K00
'''


def remove_tracking_chaff(url):
    """Remove some known tracking chaff."""
    queries = 'fbclid,shared,utm_medium,utm_source'.split(',')
    fragment_prefixes = ['Echobox=']
    for query in queries:
        if query in url.qp:
            del url.qp[query]
    if any(url.fragment.startswith(x) for x in fragment_prefixes):
        url.fragment = ''


@click.command()
@click.option('-n', '--normalize', is_flag=True, help='Normalize')
@click.option('-f', '--full_quote', is_flag=True, help='Full quote')
@click.option('-T', '--remove_tracking', is_flag=True,
              help='Remove some known tracking chaff')
# @click.option('-f', '--future', type=int, default=7,
def cli_scan_urls(normalize, full_quote, remove_tracking):
    """Scan input stream for URLs."""
    urls = chain(*(boltons.urlutils.find_all_links(x) for x in sys.stdin))
    for url in urls:
        if normalize:
            url.normalize()
        if remove_tracking:
            remove_tracking_chaff(url)
        text = url.to_text(full_quote=full_quote)
        print(text)
