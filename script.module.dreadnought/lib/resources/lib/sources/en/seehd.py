# -*- coding: utf-8 -*-

'''
    resistance Scraper

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    resistance
'''


import re,urllib,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import directstream
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['seehd.club', 'seehd.unblckd.bet']
        self.base_link = 'http://seehd.club'
        self.movie_link = '/%s-%04d-watch-online/'
        self.tvshow_link = '/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.geturl(title)
            url = urlparse.urljoin(self.base_link, self.movie_link %(t, int(year)))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            t = cleantitle.geturl(tvshowtitle)
            url = urlparse.urljoin(self.base_link, self.tvshow_link %(t))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url += '-s%02de%02d-watch-online/' % (int(season), int(episode))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)
            if '<meta name="application-name" content="Unblocked">' in r: return sources
            r = client.parseDOM(r, 'div',attrs={'class':'entry-content'})[0]
            frames = []
            frames += client.parseDOM(r, 'iframe', ret='src')
            frames += client.parseDOM(r, 'a', ret='href')
            frames += client.parseDOM(r, 'source', ret='src')
            
            try:
                q = re.findall('<strong>Quality:</strong>([^<]+)', r)[0]
                if 'high' in q.lower(): quality = '720p'
                elif 'cam' in q.lower(): quality = 'CAM'
                else: quality = 'SD'
            except: quality = 'SD'
            
            for i in frames:
                try:
                    if 'facebook' in i or 'plus.google' in i: continue
                    url = i
                    if 'http://24hd.org' in url and url.lower().endswith(('.mp4','ts')):
                        sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': url,
                                    'info': '', 'direct': True, 'debridonly': False})

                    elif 'ok.ru' in url:
                        print url
                        host = 'vk'
                        url = directstream.odnoklassniki(url)
                        print url
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': True})

                    elif 'vk.com' in url:
                        host = 'vk'
                        url = directstream.vk(url)
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': True})

                    else:
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': False})
                        else:
                            valid, host = source_utils.is_host_valid(url, hostprDict)
                            if not valid: continue
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url,
                                        'info': '', 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url


