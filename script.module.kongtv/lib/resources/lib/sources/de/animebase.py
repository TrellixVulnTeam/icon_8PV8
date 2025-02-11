# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 11-23-2018 by JewBMX in Scrubs.

import re,urllib,urlparse
from resources.lib.modules import cleantitle,client,tvmaze,source_utils,dom_parser,cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['anime-base.net']
        self.base_link = 'http://anime-base.net'
        self.search_link = '/suche_ajax.php'
        self.scraper = cfscrape.create_scraper()


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = None
            for title in [tvshowtitle, localtvshowtitle, tvmaze.tvMaze().showLookup('thetvdb', tvdb).get('name')] + source_utils.aliases_to_array(aliases):
                if url: break
                url = self.__search(title)
            return urllib.urlencode({'url': url}) if url else None
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            episode = tvmaze.tvMaze().episodeAbsoluteNumber(tvdb, int(season), int(episode))
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            data.update({'episode': episode})
            return urllib.urlencode(data)
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = data.get('url')
            episode = int(data.get('episode', 1))
            r = self.scraper.get(urlparse.urljoin(self.base_link, url)).content
            r = {'': dom_parser.parse_dom(r, 'div', attrs={'id': 'gerdub'}), 'subbed': dom_parser.parse_dom(r, 'div', attrs={'id': 'gersub'})}
            for info, data in r.iteritems():
                data = dom_parser.parse_dom(data, 'tr')
                data = [dom_parser.parse_dom(i, 'a', req='href') for i in data if dom_parser.parse_dom(i, 'a', attrs={'id': str(episode)})]
                data = [(link.attrs['href'], dom_parser.parse_dom(link.content, 'img', req='src')) for i in data for link in i]
                data = [(i[0], i[1][0].attrs['src']) for i in data if i[1]]
                data = [(i[0], re.findall('/(\w+)\.\w+', i[1])) for i in data]
                data = [(i[0], i[1][0]) for i in data if i[1]]
                for link, hoster in data:
                    valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                    if not valid: continue
                    sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            if not url.startswith('http'): url = urlparse.urljoin(self.base_link, url)
            if self.base_link in url:
                r = self.scraper.get(url).content
                r = dom_parser.parse_dom(r, 'meta', req='content')[0]
                r = r.attrs['content']
                r = re.findall('''url\s*=\s*([^'"]+)''', r, re.I)
                if r:
                    url = r[0]
            return url
        except:
            return


    def __search(self, title):
        try:
            t = cleantitle.get(title)
            r = self.scraper.get(urlparse.urljoin(self.base_link, self.search_link), post={'suchbegriff': title}).content
            r = dom_parser.parse_dom(r, 'a', attrs={'class': 'ausgabe_1'}, req='href')
            r = [(i.attrs['href'], i.content) for i in r]
            r = [i[0] for i in r if cleantitle.get(i[1]) == t][0]
            return source_utils.strip_domain(r)
        except:
            return

