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

import requests
import sys
from resources.lib.modules import cleantitle
from bs4 import BeautifulSoup

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domain = 'beetv.to/'
        self.base_link = 'http://beetv.to/'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle
        except:
            print("Unexpected error in Beetv Script:", sys.exc_info()[0])
            return url
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            url = {'tvshowtitle': url, 'season': season, 'episode': episode}
            return url
        except:
            print("Unexpected error in Beetv Script: episode", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            with requests.Session() as s:
                episode_link = "http://beetv.to/" + cleantitle.geturl(url['tvshowtitle']) + "-s" + url['season'] + "-e" + url[
                    'episode']
                p = s.get(episode_link)
                soup = BeautifulSoup(p.text, 'html.parser')
                iframes = soup.findAll('iframe')
                for i in iframes:
                    if 'thevideo' in i.get('src'):
                        sources.append(
                            {'source': "thevideo.me", 'quality': 'SD', 'language': "en", 'url': i['src'], 'info': '',
                             'direct': False, 'debridonly': False})
                    if 'openload' in i['src']:
                        sources.append(
                            {'source': "openload.co", 'quality': 'SD', 'language': "en", 'url': i['src'], 'info': '',
                             'direct': False, 'debridonly': False})
                    if 'vshare' in i['src']:
                        sources.append(
                            {'source': "vshare.eu", 'quality': 'SD', 'language': "en", 'url': i['src'], 'info': '',
                             'direct': False, 'debridonly': False})
            return sources
        except:
            print("Unexpected error in Beetv Script: source", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def resolve(self, url):
            return url

#url = source.tvshow(source(), '', '', 'Vikings','','' '','2016')
#url = source.episode(source(),url,'', '', '', '', '5', '1')
#sources = source.sources(source(),url,'','')