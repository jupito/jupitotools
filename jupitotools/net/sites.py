"""..."""


# o https://www.antikvariaatti.net/haku?q.type=&q.category=&q.seller=&q.language=&q=keskiy%C3%B6n+mato&sort=newest

# o https://www.antikka.net/haku.asp?tekija=&nimi=keskiy%F6n+mato&tryhma=0&sarja=0&myyja=0&kieli=kaikki&aika=&sort=tekija-ao&stype=full&Submit=%A0Hae%A0

# o https://www.antikvaari.fi/haku.asp?pikahaku=0&stype=full&haku=keskiy%F6n+mato&kieli=kaikki&Submit=Hae

# t https://www.kirjaverkko.fi/haku?bookName=keskiy%C3%B6n%20mato&order=added&min=1&max=9999
#   https://www.kirjaverkko.fi/haku?bookName=keskiy%C3%B6n%20mato
# a https://www.kirjaverkko.fi/haku?order=added&min=1&max=9999&author=albert%20kivinen
#   https://www.kirjaverkko.fi/haku?author=albert%20kivinen


import dataclasses
import urllib.parse
import webbrowser


@dataclasses.dataclass(repr=True, order=True, unsafe_hash=True, frozen=True)
class UrlComponents:
    scheme: str = 'https'
    netloc: str = ''
    path: str = ''
    query: dict = dict
    fragment: str = ''

    def components(self):
        """Components."""
        q = urllib.parse.quote_plus
        # kwargs = dict(doseq=False, quote_via=q)
        query = urllib.parse.urlencode(self.query)
        return ([q(x) for x in [self.scheme, self.netloc, self.path]] +
                [query, q(self.fragment)])

    def unsplit(self):
        return urllib.parse.urlunsplit(self.components())


class UsedBooksSites:
    def __init__(self, author='', title='', other=''):
        self.author = author
        self.title = title
        self.other = other

    @property
    def omni(self):
        return ' '.join(filter(None, [self.author, self.title, self.other]))

    def site_antikvariaatti_net(self):
        return UrlComponents(netloc='www.antikvariaatti.net',
                             path='haku',
                             query=dict(q=self.omni))

# o https://www.antikka.net/haku.asp?tekija=&nimi=keskiy%F6n+mato&tryhma=0&sarja=0&myyja=0&kieli=kaikki&aika=&sort=tekija-ao&stype=full&Submit=%A0Hae%A0
    def site_antikka_net(self):
        return UrlComponents(netloc='www.antikka.net',
                             path='haku.asp',
                             query=dict(tekija=self.author, nimi=self.title))

# o https://www.antikvaari.fi/haku.asp?pikahaku=0&stype=full&haku=keskiy%F6n+mato&kieli=kaikki&Submit=Hae
    def site_antikvaari_fi(self):
        return UrlComponents(netloc='www.antikvaari.fi',
                             path='haku.asp',
                             query=dict(haku=self.omni))

    def urls(self):
        return (x().unsplit() for x in [self.site_antikvariaatti_net,
                                        self.site_antikka_net,
                                        self.site_antikvaari_fi])

    def open(self):
        for x in self.urls():
            webbrowser.open(x)



# sites = UsedBooksSites(title='keskiyön mato')
# sites = UsedBooksSites(title='keskiyö')
sites = UsedBooksSites(title='muumi 6')
list(sites.urls())
