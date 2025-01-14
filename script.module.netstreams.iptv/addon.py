# -*- coding: utf-8 -*-
#
# Copyright (C) 2016,2017 RACC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from xbmcgui import ListItem
from routing import Plugin

import time
import os
import warnings
import traceback

import requests
import requests_cache
import json
from datetime import timedelta
from base64 import urlsafe_b64encode
from binascii import a2b_hex
from hashlib import md5
try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar
try:
    from urllib.parse import quote as orig_quote
    from urllib.parse import unquote as orig_unquote
except ImportError:
    from urllib import quote as orig_quote
    from urllib import unquote as orig_unquote

warnings.filterwarnings("ignore")

addon = xbmcaddon.Addon()
plugin = Plugin()
plugin.name = addon.getAddonInfo('name')

USER_DATA_DIR = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

COOKIE_FILE = os.path.join(USER_DATA_DIR, 'lwp_cookies.dat')
CACHE_FILE = os.path.join(USER_DATA_DIR, 'cache')
expire_after = timedelta(hours=2)

user_agent = 'Mozilla/5.0 (Linux; Android 5.1.1; AFTT Build/LVY48F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.132 Mobile Safari/537.36'
auth_url = a2b_hex('68747470733a2f2f6170692e6d6f6264726f2e73782f7574696c732f61757468')
lb_url = a2b_hex('68747470733a2f2f6170692e6d6f6264726f2e73782f7574696c732f6c6f616462616c616e636572')
list_url = a2b_hex('68747470733a2f2f6170692e6d6f6264726f2e73782f73747265616d626f742f76342f73686f77')
app_signature = str(0x3b72c95d)     # 0x20b5d5bb 0xedecbf54 0x0c50a4f9

s = requests_cache.CachedSession(CACHE_FILE, allowable_methods='POST',
                                 expire_after=expire_after, old_data_on_error=True,
                                 ignored_parameters=['token'])
s.headers.update({'User-Agent': user_agent})
s.cookies = LWPCookieJar(filename=COOKIE_FILE)
if os.path.isfile(COOKIE_FILE):
    s.cookies.load(ignore_discard=True, ignore_expires=True)

auth_token_time = int(addon.getSetting('auth_token_time') or '0')
auth_token = addon.getSetting('auth_token')

current_time = int(time.time())
if current_time - auth_token_time > 7200:
    with s.cache_disabled():
        r = s.post(auth_url, data={'signature': app_signature}, timeout=10)

    if r.content.strip():
        auth_token = r.json().get('token')
        addon.setSetting('auth_token_time', str(current_time))
        addon.setSetting('auth_token', auth_token)


def quote(s, safe=''):
    return orig_quote(s.encode('utf-8'), safe.encode('utf-8'))


def unquote(s):
    return orig_unquote(s).decode('utf-8')


@plugin.route('/')
def root():
    categories = ["Channels", "News", "Shows", "Movies", "Sports", "Music"]
    list_items = []
    for c in categories:
        li = ListItem(c)
        url = plugin.url_for(list_channels, cat=c)
        list_items.append((url, li, True))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/list_channels/<cat>')
def list_channels(cat=None):
    data = {'data': cat, 'parental': 'no', 'languages': 'all', 'alphabetical': 'no', 'token': auth_token}
    r = s.post(list_url, data=data, timeout=10)

    list_items = []
    for ch in r.json():
        if 'relayer' in ch:
            channel = json.loads(ch.get('relayer'))
            if not channel.get('protocol') == 'rtmfp':
                image = "{0}|User-Agent={1}".format(ch.get('img'), quote(user_agent))
                li = ListItem(ch.get('name'))
                li.setProperty("IsPlayable", "true")
                li.setInfo(type='Video', infoLabels={'Title': ch.get('name'), 'mediatype': 'video', 'PlayCount': 0})
                li.setArt({'thumb': image, 'icon': image})
                # kodi 16/17
                try:
                    li.setContentLookup(False)
                except AttributeError:
                    # kodi 14/15
                    pass
                url = plugin.url_for(play_id, cat=cat, _id=ch.get('_id'))
                list_items.append((url, li, False))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/play_id/<cat>/<_id>')
def play_id(cat, _id):
    channel = None
    data = {'data': cat, 'parental': 'no', 'languages': 'all', 'alphabetical': 'no', 'token': auth_token}

    r = s.post(list_url, data=data, timeout=10)

    for ch in r.json():
        if 'relayer' in ch:
            if _id == ch.get('_id'):
                channel = json.loads(ch.get('relayer'))
                if not channel.get('protocol') == 'rtmfp':
                    label = ch.get('name')
                    image = "{0}|User-Agent={1}".format(ch.get('img'), quote(user_agent))
                    break

    if channel:
        data = {'referer': a2b_hex('6d6f6264726f2e6d65'), 'token': auth_token}
        try:
            with s.cache_disabled():
                # r = s.post(lb_url, data=data, timeout=10)
                r = s.get(lb_url, timeout=10)

            lb_info = r.json()
        except Exception:
            lb_info = {}

        time_stamp = str(int(lb_info.get('epoch', time.time())) + int(channel.get('expiration_time', '20400')))
        to_hash = '{password}{time_stamp}/{dir}/{playpath}'.format(time_stamp=time_stamp, **channel)
        out_hash = urlsafe_b64encode(md5(to_hash).digest()).rstrip('=')

        headers = ['Referer={0}'.format(quote(lb_info.get('referer', a2b_hex('6d6f6264726f2e6d65')))),
                   'User-Agent={0}'.format(quote(user_agent)),
                   'Cookie={0}'.format(quote(lb_info.get('cookie', 'token=null'))),
                   a2b_hex('582d5265717565737465642d576974683d322e302e3538253230467265656d69756d')]

        url = "{0}://{1}/{2}/{3}/{4}/{5}".format(channel.get('protocol', 'http'),
                                                 lb_info.get('server', channel.get('server')),
                                                 channel.get('app', 'live'),
                                                 out_hash, time_stamp,
                                                 channel.get('playpath').replace(channel.get('replace'), ''))

        media_url = '{url}|{headers}'.format(url=url, headers='&'.join(headers))

        if addon.getSetting('livestreamer') == 'true':
            serverPath = os.path.join(xbmc.translatePath(addon.getAddonInfo('path')), 'livestreamerXBMCLocalProxy.py')
            runs = 0
            while not runs > 10:
                try:
                    requests.get('http://127.0.0.1:19001/version')
                    break
                except Exception:
                    xbmc.executebuiltin('RunScript(' + serverPath + ')')
                    runs += 1
                    xbmc.sleep(600)

            livestreamer_url = 'http://127.0.0.1:19001/livestreamer/' + urlsafe_b64encode('hls://' + media_url)
            li = ListItem(label, path=livestreamer_url)
            li.setArt({'thumb': image, 'icon': image})
            li.setMimeType('video/x-mpegts')
        else:
            li = ListItem(label, path=media_url)
            li.setArt({'thumb': image, 'icon': image})
            li.setMimeType('application/vnd.apple.mpegurl')

        # kodi 18
        try:
            li.setContentLookup(False)
        except AttributeError:
            # kodi 14/15
            pass

        xbmcplugin.setResolvedUrl(plugin.handle, True, li)


if __name__ == '__main__':
    try:
        plugin.run()
        s.cookies.save(ignore_discard=True, ignore_expires=True)
        s.close()
    except requests.exceptions.RequestException:
        dialog = xbmcgui.Dialog()
        dialog.notification(plugin.name, "Web Request Exception", xbmcgui.NOTIFICATION_ERROR)
        traceback.print_exc()
