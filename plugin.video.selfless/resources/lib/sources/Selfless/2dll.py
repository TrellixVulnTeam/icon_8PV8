# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # # -*- coding: UTF-8 -*-
'''
    A scraper for SelflessLive.

    Updated and refactored by someone.
    Originally created by others.
'''

 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Selfless Live
# Addon id: plugin.video.selfless
# Addon Provider: Kodi Ghost


import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['2dll.unblocked.gdn']
        self.base_link = 'https://2ddl.unblocked.gdn/'
        self.search_link = '/search/%s/feed/rss2/'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            posts = client.parseDOM(r, 'item')

            hostDict = hostprDict + hostDict

            items = []

            for post in posts:
                try:
                    t = client.parseDOM(post, 'title')[0]

                    c = client.parseDOM(post, 'content.+?')[0]

                    u = re.findall('<singlelink>(.+?)(?:<download>|$)', c.replace('\n', ''))[0]
                    u = client.parseDOM(u, 'a', ret='href')

                    s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', c)
                    s = s[0] if s else '0'

                    items += [(t, i, s) for i in u]

                except:
                    pass

            for item in items:
                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)

                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()

                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()

                    if not y == hdlr: raise Exception()

                    quality, info = source_utils.get_release_quality(name, item[1])

                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', item[2])[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        pass

                    info = ' | '.join(info)

                    url = item[1]
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
                except:
                    pass

            check = [i for i in sources if not i['quality'] == 'CAM']
            if check: sources = check

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


