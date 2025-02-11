# -*- coding: UTF-8 -*-
'''
    rlsbb scraper for Exodus forks.
    Dec 2 2018 - Cleaned and Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re,traceback,urllib,urlparse,json

from tikiscrapers.modules import cleantitle
from tikiscrapers.modules import client
from tikiscrapers.modules import control
from tikiscrapers.modules import debrid
from tikiscrapers.modules import log_utils
from tikiscrapers.modules import source_utils
from tikiscrapers.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rlsbb.to']
        self.base_link = 'http://rlsbb.to'
        self.search_base_link = 'http://search.rlsbb.to'
        self.search_cookie = 'serach_mode=rlsbb'
        self.search_link = '/lib/search526049.php?phrase=%s&pindex=1&content=true'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
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
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            scraper = cfscrape.create_scraper()

            if url == None: return sources

            if debrid.status() == False: raise Exception()

            data = urlparse.parse_qs(url)         
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])        
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            premDate = ''
            
            query = '%s S%02dE%02d' % (
            data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
            data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

            query = query.replace("&", "and")
            query = query.replace("  ", " ")
            query = query.replace(" ", "-")
            
            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            url = "http://rlsbb.to/" + query                                
            if 'tvshowtitle' not in data: url = url + "-1080p"               

            r = scraper.get(url).content                                         
            
            if r == None and 'tvshowtitle' in data:
                season = re.search('S(.*?)E', hdlr)
                season = season.group(1)
                query = title
                query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)
                query = query + "-S" + season
                query = query.replace("&", "and")
                query = query.replace("  ", " ")
                query = query.replace(" ", "-")
                url = "http://rlsbb.to/" + query
                r = scraper.get(url).content

            
            for loopCount in range(0,2):
                if loopCount == 1 or (r == None and 'tvshowtitle' in data):                     
                    
                    
                    premDate = re.sub('[ \.]','-',data['premiered'])                            
                    query = re.sub('[\\\\:;*?"<>|/\-\']', '', data['tvshowtitle'])              
                    query = query.replace("&", " and ").replace("  ", " ").replace(" ", "-")    
                    query = query + "-" + premDate                      
                    
                    url = "http://rlsbb.to/" + query            
                    url = url.replace('The-Late-Show-with-Stephen-Colbert','Stephen-Colbert')   
                    

                    r = scraper.get(url).content
                    
                posts = client.parseDOM(r, "div", attrs={"class": "content"})   
                hostDict = hostprDict + hostDict                                
                items = []
                for post in posts:
                    try:
                        u = client.parseDOM(post, 'a', ret='href')             
                        for i in u:                                            
                            try:
                                name = str(i)
                                if hdlr in name.upper(): items.append(name)
                                elif len(premDate) > 0 and premDate in name.replace(".","-"): items.append(name)      
                                
                            except:
                                pass
                    except:
                        pass
                        
                if len(items) > 0: break

            seen_urls = set()

            for item in items:
                try:
                    url = str(item)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    if url in seen_urls: continue
                    seen_urls.add(url)

                    host = url.replace("\\", "")
                    host2 = host.strip('"')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host2.strip().lower()).netloc)[0]

                    if not host in hostDict: raise Exception()
                    if any(x in host2 for x in ['.rar', '.zip', '.iso']): continue

                    quality, info = source_utils.get_release_quality(host2)

                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', con)[0]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except BaseException:
                        pass

                    info = ' | '.join(info)
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': host2, 'info': info, 'direct': False, 'debridonly': False})
                    
                except:
                    pass
            check = [i for i in sources if not i['quality'] == 'CAM']
            if check: sources = check
            sources = source_utils.limit_results(sources)
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('RLSBB - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url