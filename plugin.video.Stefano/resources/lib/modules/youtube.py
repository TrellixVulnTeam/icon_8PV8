# ------------------------------------------------------------
# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Stefano Thegroove 360
# Copyright 2018 https://stefanoaddon.info
#
# Distribuito sotto i termini di GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------- -----------
# Questo file fa parte di Stefano Thegroove 360.
#
# Stefano Thegroove 360 ​​è un software gratuito: puoi ridistribuirlo e / o modificarlo
# è sotto i termini della GNU General Public License come pubblicata da
# la Free Software Foundation, o la versione 3 della licenza, o
# (a tua scelta) qualsiasi versione successiva.
#
# Stefano Thegroove 360 ​​è distribuito nella speranza che possa essere utile,
# ma SENZA ALCUNA GARANZIA; senza nemmeno la garanzia implicita di
# COMMERCIABILITÀ o IDONEITÀ PER UN PARTICOLARE SCOPO. Vedere il
# GNU General Public License per maggiori dettagli.
#
# Dovresti aver ricevuto una copia della GNU General Public License
# insieme a Stefano Thegroove 360. In caso contrario, vedi <http://www.gnu.org/licenses/>.
# ------------------------------------------------- -----------
# Client for Stefano Thegroove 360
#------------------------------------------------------------


import re,json

from resources.lib.modules import client
from resources.lib.modules import workers


class youtube(object):
    def __init__(self, key=''):
        self.list = [] ; self.data = []
        self.base_link = 'http://www.youtube.com'
        self.key_link = '&key=%s' % key
        self.playlists_link = 'https://www.googleapis.com/youtube/v3/playlists?part=snippet&maxResults=50&channelId=%s'
        self.playlist_link = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=%s'
        self.videos_link = 'https://www.googleapis.com/youtube/v3/search?part=snippet&order=date&maxResults=50&channelId=%s'
        self.content_link = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=%s'
        self.play_link = 'plugin://plugin.video.youtube/play/?video_id=%s'


    def playlists(self, url):
        url = self.playlists_link % url + self.key_link
        return self.play_list(url)


    def playlist(self, url, pagination=False):
        cid = url.split('&')[0]
        url = self.playlist_link % url + self.key_link
        return self.video_list(cid, url, pagination)


    def videos(self, url, pagination=False):
        cid = url.split('&')[0]
        url = self.videos_link % url + self.key_link
        return self.video_list(cid, url, pagination)


    def play_list(self, url):
        try:
            result = client.request(url)
            result = json.loads(result)
            items = result['items']
        except:
            pass

        for i in range(1, 5):
            try:
                if not 'nextPageToken' in result: raise Exception()
                next = url + '&pageToken=' + result['nextPageToken']
                result = client.request(next)
                result = json.loads(result)
                items += result['items']
            except:
                pass

        for item in items:
            try:
                title = item['snippet']['title']
                title = title.encode('utf-8')

                url = item['id']
                url = url.encode('utf-8')

                image = item['snippet']['thumbnails']['high']['url']
                if '/default.jpg' in image: raise Exception()
                image = image.encode('utf-8')

                self.list.append({'title': title, 'url': url, 'image': image})
            except:
                pass

        return self.list


    def video_list(self, cid, url, pagination):
        try:
            result = client.request(url)
            result = json.loads(result)
            items = result['items']
        except:
            pass

        for i in range(1, 5):
            try:
                if pagination == True: raise Exception()
                if not 'nextPageToken' in result: raise Exception()
                page = url + '&pageToken=' + result['nextPageToken']
                result = client.request(page)
                result = json.loads(result)
                items += result['items']
            except:
                pass

        try:
            if pagination == False: raise Exception()
            next = cid + '&pageToken=' + result['nextPageToken']
        except:
            next = ''

        for item in items: 
            try:
                title = item['snippet']['title']
                title = title.encode('utf-8')

                try: url = item['snippet']['resourceId']['videoId']
                except: url = item['id']['videoId']
                url = url.encode('utf-8')

                image = item['snippet']['thumbnails']['high']['url']
                if '/default.jpg' in image: raise Exception()
                image = image.encode('utf-8')

                append = {'title': title, 'url': url, 'image': image}
                if not next == '': append['next'] = next
                self.list.append(append)
            except:
                pass

        try:
            u = [range(0, len(self.list))[i:i+50] for i in range(len(range(0, len(self.list))))[::50]]
            u = [','.join([self.list[x]['url'] for x in i]) for i in u]
            u = [self.content_link % i + self.key_link for i in u]

            threads = []
            for i in range(0, len(u)):
                threads.append(workers.Thread(self.thread, u[i], i))
                self.data.append('')
            [i.start() for i in threads]
            [i.join() for i in threads]

            items = []
            for i in self.data: items += json.loads(i)['items']
        except:
            pass

        for item in range(0, len(self.list)):
            try:
                vid = self.list[item]['url']

                self.list[item]['url'] = self.play_link % vid

                d = [(i['id'], i['contentDetails']) for i in items]
                d = [i for i in d if i[0] == vid]
                d = d[0][1]['duration']

                duration = 0
                try: duration += 60 * 60 * int(re.findall('(\d*)H', d)[0])
                except: pass
                try: duration += 60 * int(re.findall('(\d*)M', d)[0])
                except: pass
                try: duration += int(re.findall('(\d*)S', d)[0])
                except: pass
                duration = str(duration)

                self.list[item]['duration'] = duration
            except:
                pass

        return self.list


    def thread(self, url, i):
        try:
            result = client.request(url)
            self.data[i] = result
        except:
            return