# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################


import re
from resources.lib.modules import cleantitle
from resources.lib.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['hdm.to']
        self.base_link = 'https://hdm.to'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = cleantitle.geturl(title)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            url = '%s/%s/' % (self.base_link, url)
            r = self.scraper.get(url).content
            match = re.compile('<iframe.+?src="(.+?)"').findall(r)
            for url in match:
                sources.append({'source': 'Openload.co', 'quality': '1080p', 'language': 'en',
                                'url': url, 'direct': False, 'debridonly': False})
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url