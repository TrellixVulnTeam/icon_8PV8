# -*- coding: utf-8 -*-
"""
    sources.py ---
    Copyright (C) 2017, Jen

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

 Update :2019-3-11
 Version 2.0 Jen
    Updated to include torrent and magnet links in xml

<title>[/COLOR]</title>
<link>
<sublink>magnet:?xt=urn:btih:9CA50DA836B52A6BCB06AAA91BB2478FD96F5DD0&dn=A+Beautiful+Mind+%282001%29+1080p+BrRip+x264+-+YIFY</sublink>
</link>
<thumbnail></thumbnail>
<fanart></fanart>
</item>


"""
import random

import universalscrapers,logging
import requests
import xbmcaddon
import xbmcgui
import xbmc,urllib
import koding
from koding import route
import sys
import xbmcplugin

import resolveurl

from resources.lib.util.xml import JenItem, JenList
from resources.lib.util.messages import get_link_message, get_searching_message
from resources.lib.util.info import get_info
from resources.lib.player import JenPlayer
from resources.lib.plugin import run_hook
from language import get_string as _

ADDON = xbmcaddon.Addon()
DIALOG = xbmcgui.Dialog()


class Sources(object):
    """interface to NaN scraper library and helper functions"""

    def __init__(self):
        """initialise class"""
        pass

    @staticmethod
    def get_sources(
        title,
        year,
        imdb,
        tvdb,
        season,
        episode,
        tvshowtitle,
        premiered,
        timeout=30,
        preset="search",
        dialog=None,
        exclude=None,
        scraper_title=False,
        listitem=None,
        output_function=koding.Play_Video,
        skip_selector=False,
        player=None,
        icon=' ',
        fanart=' ',
                    
    ):
        """
        scrapes for video sources using NaN scraper library
        Args:
            title: movie or episode title
            year: year movie/episode came out
            imdb: imdb identifier
            tvdb:  tvdb identifier
            season: season number
            episode: episode number
            tvshowtitle: title of tv show
            premiered: year tv show premiered
            timeout: timeout for scraping link
            preset: preferred quality of stream
            dialog: dialog to use for displaying messages
            exclude: list of scrapers to exclude
            scraper_title: extra movie/tv show title to search first.
                           required if scrapers use an alternate spelling
        Returns:
            Boolean indicating playback success
        """
        
        year = str(year)
        content = "movie" if tvshowtitle is None else "episode"
        allow_debrid = ADDON.getSetting("allow_debrid") == "true"
        if  ADDON.getSetting("jen_sources")=='1':
            if content == "movie":
                original_title=title
                episode='%20'
                season='%20'
            else:
                original_title=tvshowtitle
            logging.warning('movie info')
            logging.warning(content)
            logging.warning(original_title)
            logging.warning(year)
            logging.warning(imdb)
            logging.warning(tvshowtitle)
            
            
            try:
                xbmc.executebuiltin(('Container.update("plugin://plugin.video.destinyds/?data=%s&dates=EMPTY&description=%s-NEXTUP-&eng_name=%s&episode=%s&fanart=%s&heb_name=%s&iconimage=%s&id=%s&isr=%s&mode2=4&name=%s&original_title=%s&season=%s&show_original_year=%s&tmdbid=EMPTY&url=%s&fast_link=%s&url=www",return)'%(str(year),urllib.quote_plus(' '),original_title,episode,urllib.quote_plus(fanart),original_title,urllib.quote_plus(icon),imdb,' ',original_title,original_title,season,str(year),urllib.quote_plus(''),urllib.quote_plus(''))).replace('EMPTY','%20'))
                            
                #play(name,fast_link,iconimage,image,description,data,season,episode,original_title,name,heb_name,show_original_year,eng_name,isr,original_title,id,windows_play=True,auto_fast=False,nextup=True)
                
                logging.warning('PLAY NEXTUP FULLSCREEN')
                xbmc.executebuiltin( "XBMC.Action(Fullscreen)" )
                return '0'
            except Exception as e:
                logging.warning(e)
        if ADDON.getSetting("use_link_dialog") == "true" and not skip_selector:
            # use link selector
            if content == "movie":
                scraper = universalscrapers.scrape_movie_with_dialog
                link, rest = scraper(
                    title,
                    year,
                    imdb,
                    timeout=timeout,
                    exclude=exclude,
                    extended=True,
                    sort_function=Sources.sort_function,
                    enable_debrid=allow_debrid,
                )
            elif content == "episode":
                scraper = universalscrapers.scrape_episode_with_dialog
                link, rest = scraper(
                    tvshowtitle,
                    year,
                    premiered,
                    season,
                    episode,
                    imdb,
                    tvdb,
                    timeout=timeout,
                    exclude=exclude,
                    extended=True,
                    sort_function=Sources.sort_function,
                    enable_debrid=allow_debrid,
                )
            else:
                return

            if type(link) == dict and "path" in link:
                link = link["path"]
            if link is None:
                return False
            url = link["url"]
            if ADDON.getSetting("link_fallthrough") == "true":
                played = False
                index = 0
                links = []
                for item in rest:
                    if type(item) == dict and "path" in item:
                        links.extend(item["path"][1])
                    else:
                        links.extend(item[1])
                index = links.index(link)
                links = links[index + 1 :]
                num_results = len(rest) + 1
                while not played:
                    try:
                        if dialog is not None and dialog.iscanceled():
                            return False
                        if dialog is not None:
                            index = index + 1
                            percent = int((index * 100) / num_results)
                            line = "%s - %s (%s)" % (
                                link["scraper"],
                                link["source"],
                                link["quality"],
                            )
                            dialog.update(percent, line)
                    except:
                        pass
                    try:
                        resolved_link = universalscrapers.resolve(
                            link["scraper"], link["url"]
                        )
                        played = output_function(
                            resolved_link,
                            showbusy=False,
                            ignore_dp=True,
                            item=listitem,
                            player=player,
                            resolver=resolveurl,
                        )
                        link = links[0]
                        links = links[1:]
                    except:
                        return False
                return played
            else:
                resolved_link = universalscrapers.resolve(link["scraper"], link["url"])
                return output_function(
                    resolved_link,
                    showbusy=False,
                    ignore_dp=True,
                    item=listitem,
                    player=player,
                    resolver=resolveurl,
                )
        else:
            if content == "movie":
                title = title
                scraper = universalscrapers.scrape_movie
                links_scraper = scraper(
                    title,
                    year,
                    imdb,
                    timeout=timeout,
                    exclude=exclude,
                    enable_debrid=allow_debrid,
                )

            elif content == "episode":
                if scraper_title:
                    tvshowtitle = title
                tvshowtitle = tvshowtitle
                scraper = universalscrapers.scrape_episode
                links_scraper = scraper(
                    tvshowtitle,
                    year,
                    premiered,
                    season,
                    episode,
                    imdb,
                    tvdb,
                    timeout=timeout,
                    exclude=exclude,
                    enable_debrid=allow_debrid,
                )
            else:
                return

        sd_links = []
        non_direct_links = []
        non_direct_sd_links = []
        num_scrapers = len(universalscrapers.relevant_scrapers())
        index = 0
        try:
            for scraper_links in links_scraper():
                if dialog is not None and dialog.iscanceled():
                    return
                if dialog is not None:
                    index = index + 1
                    percent = int((index * 100) / num_scrapers)
                    dialog.update(percent)
                if scraper_links is not None:
                    random.shuffle(scraper_links)
                    for scraper_link in scraper_links:
                        if dialog is not None and dialog.iscanceled():
                            return False

                        if Sources().__check_skip_pairing(scraper_link):
                            continue

                        quality = Sources.__determine_quality(scraper_link["quality"])
                        preset = preset.lower()
                        if preset == "searchsd":
                            if quality == "HD":
                                continue
                        elif preset == "search":
                            if quality == "SD":
                                sd_links.append(scraper_link)

                        if scraper_link["direct"]:
                            resolved_link = universalscrapers.resolve(scraper_link["scraper"], scraper_link["url"])
                            result = output_function(
                                resolved_link,
                                showbusy=False,
                                ignore_dp=True,
                                item=listitem,
                                player=player,
                                resolver=resolveurl,
                            )
                            if result:
                                return result
                        else:
                            non_direct_links.append(scraper_link)

            for scraper_link in non_direct_links:
                if dialog is not None and dialog.iscanceled():
                    return False
                resolved_link = universalscrapers.resolve(scraper_link["scraper"], scraper_link["url"])
                result = output_function(
                    resolved_link,
                    showbusy=False,
                    ignore_dp=True,
                    item=listitem,
                    player=player,
                    resolver=resolveurl,
                )
                if result:
                    return result

            for scraper_link in sd_links:
                if dialog is not None and dialog.iscanceled():
                    return

                if scraper_link["direct"]:
                    resolved_link = universalscrapers.resolve(scraper_link["scraper"], scraper_link["url"])
                    result = output_function(
                        resolved_link,
                        showbusy=False,
                        ignore_dp=True,
                        item=listitem,
                        player=player,
                        resolver=resolveurl,
                    )
                    if result:
                        return result
                else:
                    non_direct_sd_links.append(scraper_link)

            for scraper_link in non_direct_sd_links:
                if dialog is not None and dialog.iscanceled():
                    return
                resolved_link = universalscrapers.resolve(scraper_link["scraper"], scraper_link["url"])
                result = output_function(
                    resolved_link,
                    showbusy=False,
                    ignore_dp=True,
                    item=listitem,
                    player=player,
                    resolver=resolveurl,
                )
                if result:
                    return result

            return False
        except:
            return False

    @staticmethod
    def get_music_sources(
        title,
        artist,
        timeout=30,
        preset="search",
        dialog=None,
        exclude=None,
        listitem=None,
        output_function=koding.Play_Video,
        skip_selector=False,
        player=None,
    ):
        """
        scrapes for music sources using NaN scraper library
        Args:
            title: song title
            artist: song artist
            timeout: timeout for scraping link
            preset: preferred quality of stream
            dialog: dialog to use for displaying messages
            exclude: list of scrapers to exclude
        Returns:
            Boolean indicating playback success
        """
        title = title
        allow_debrid = ADDON.getSetting("allow_debrid") == "true"
        if ADDON.getSetting("use_link_dialog") == "true" and not skip_selector:
            link, rest = universalscrapers.scrape_song_with_dialog(
                title,
                artist,
                timeout=timeout,
                exclude=exclude,
                enable_debrid=allow_debrid,
                extended=True,
            )
            if type(link) == dict and "path" in link:
                link = link["path"]
            if link is None:
                return False
            url = link["url"]
            if ADDON.getSetting("link_fallthrough") == "true":
                played = False
                index = 0
                links = []
                for item in rest:
                    if type(item) == dict and "path" in item:
                        links.extend(item["path"][1])
                    else:
                        links.extend(item[1])
                index = links.index(link)
                links = links[index + 1 :]
                num_results = len(rest) + 1
                while not played:
                    try:
                        if dialog is not None and dialog.iscanceled():
                            return
                        if dialog is not None:
                            index = index + 1
                            percent = int((index * 100) / num_results)
                            line = "%s - %s (%s)" % (
                                link["scraper"],
                                link["source"],
                                link["quality"],
                            )
                            dialog.update(percent, line)
                    except:
                        pass
                    try:
                        played = output_function(
                            url,
                            showbusy=False,
                            ignore_dp=True,
                            item=listitem,
                            player=player,
                            resolver=resolveurl,
                        )
                        link = links[0]
                        links = links[1:]
                    except:
                        return False
                return played
            else:
                return output_function(
                    url,
                    showbusy=False,
                    ignore_dp=True,
                    item=listitem,
                    player=player,
                    resolver=resolveurl,
                )
        links_scraper = universalscrapers.scrape_song(
            title, artist, timeout=timeout, exclude=exclude, enable_debrid=allow_debrid
        )

        sd_links = []
        num_scrapers = len(universalscrapers.relevant_scrapers())
        index = 0
        try:
            for scraper_links in links_scraper():
                if dialog is not None and dialog.iscanceled():
                    return
                if dialog is not None:
                    index = index + 1
                    percent = int((index * 100) / num_scrapers)
                    dialog.update(percent)
                if scraper_links is not None:
                    random.shuffle(scraper_links)
                    for scraper_link in scraper_links:
                        if dialog is not None and dialog.iscanceled():
                            return

                        if Sources().__check_skip_pairing(scraper_link):
                            continue

                        quality = Sources.__determine_quality(scraper_link["quality"])
                        preset = preset.lower()
                        if preset == "searchsd":
                            if quality == "HD":
                                continue
                        elif preset == "search":
                            if quality == "SD":
                                sd_links.append(scraper_link)

                        result = output_function(
                            scraper_link["url"],
                            showbusy=False,
                            ignore_dp=True,
                            item=listitem,
                            player=player,
                            resolver=resolveurl,
                        )
                        if result:
                            return result

            for scraper_link in sd_links:
                if dialog is not None and dialog.iscanceled():
                    return
                result = output_function(
                    scraper_link["url"],
                    showbusy=False,
                    ignore_dp=True,
                    item=listitem,
                    player=player,
                    resolver=resolveurl,
                )
                if result:
                    return result
        except:
            pass
        return False

    @staticmethod
    def youtube_resolve(url):
        """
        transform youtube url to link to youtube add-on
        Args:
            url: youtube url
        Returns:
            playable url
        """
        try:
            youtube_id = url.split("?v=")[-1].split("/")[-1].split("?")[0].split("&")[0]
            result = requests.head("http://www.youtube.com/watch?v=%s" % youtube_id)
            if result:
                return "plugin://plugin.video.youtube/play/?video_id=%s" % (youtube_id)
        except:
            return

    @staticmethod
    def sort_function(item):
        """
        transform items quality into a string that's sort-able
        Args:
            item: scraper link
        Returns:
            sortable quality string
        """
        if "quality" in item[1][0]:
            quality = item[1][0]["quality"]
        else:
            quality = item[1][0]["path"]["quality"]

        if "path" in item[1][0]:
            if "debridonly" in item[1][0]["path"]:
                q = "A"
        elif "debridonly" in item[1][0]:
            q = "A"
        else:
            q = "B"

        if q == "A":
            if quality.startswith("4K"):
                quality = "Aa"
            elif quality.startswith("1080"):
                quality = "Ab"
            elif quality.startswith("720"):
                quality = "Ac"
            elif quality.startswith("560"):
                quality = "Ad"
            elif quality == "DVD":
                quality = "Ae"
            elif quality == "HD":
                quality = "Af"
            elif quality.startswith("480"):
                quality = "Ba"
            elif quality.startswith("360"):
                quality = "Bb"
            elif quality.startswith("SD"):
                quality = "Bc"
            else:
                quality = "CZ"

        elif quality.startswith("4K"):
            quality = "HDa"
        elif quality.startswith("1080"):
            quality = "HDb"
        elif quality.startswith("720"):
            quality = "HDc"
        elif quality.startswith("560"):
            quality = "HDd"
        elif quality == "DVD":
            quality = "HDe"
        elif quality == "HD":
            quality = "HDf"
        elif quality.startswith("480"):
            quality = "SDa"
        elif quality.startswith("360"):
            quality = "SDb"
        elif quality.startswith("SD"):
            quality = "SDc"
        else:
            quality = "Z"
        return quality

    @staticmethod
    def __determine_quality(quality_string):
        try:
            quality = int(quality_string)
            if quality > 576:
                return "HD"
            else:
                return "SD"
        except ValueError:
            if quality_string not in ["SD", "CAM", "SCR"]:
                return "HD"
            else:
                return "SD"

    @staticmethod
    def __check_skip_pairing(scraper_link):
        if (
            not ADDON.getSetting("allow_openload") == "true"
            and "openload" in scraper_link["url"]
        ):
            return True
        if (
            not ADDON.getSetting("allow_the_video_me") == "true"
            and "thevideo.me" in scraper_link["url"]
        ):
            return True
        if (
            not ADDON.getSetting("allow_the_vidup_me") == "true"
            and "vidup.me" in scraper_link["url"]
        ):
            return True
        return False


def choose_quality(link, name=None, selected_link=None):
    """
    choose quality for scraping

    Keyword Arguments:
    link -- Jenitem link with sublinks
    name -- Name to display in dialog (default None)
    """
    import re

    if name is None:
        name = xbmc.getInfoLabel("listitem.label")
    if link.startswith("http") or link.startswith("plugin"):
        sublinks = [link]
    else:
        jen_link = JenItem(link)
        sublinks = jen_link.getAll("sublink")
        if not sublinks:
            sublinks = [jen_link]
    links = []
    message = get_link_message()
    if selected_link is None:
        default_link = ADDON.getSetting("default_link")
    else:
        default_link = selected_link
    link_dialog = ADDON.getSetting("use_link_dialog") == "true"
    direct_links = False
    for sublink in sublinks:
        if link_dialog and "search" in sublink:
            continue
        if "searchsd" in sublink:
            if default_link == "SD":
                return sublink
            label = "SD"
            if message["SD"] != "":
                label += " (%s)" % message["SD"]
            new_item = (label, sublink)
        elif "search" in sublink:
            if default_link == "HD":
                return sublink
            label = "HD"
            if message["HD"] != "":
                label += " (%s)" % message["HD"]
            new_item = (label, sublink)
        else:
            direct_links = True
            match = re.findall("(.*?)\((.*?)\)", sublink)
            if match:
                new_item = ("%s" % match[0][1], match[0][0])
            else:
                new_item = ("Link %s" % (int(sublinks.index(sublink)) + 1), sublink)
        links.append(new_item)
    if link_dialog and (not direct_links or len(sublinks) > 1):
        links.append(("Search", "search"))

    if len(links) == 1:
        url = links[0][1]
        return url

    select = xbmcgui.Dialog().select(name, [i[0] for i in links])
    if select == -1:
        return False
    else:
        url = links[select][1]
    return url
def regex_from_to(text, from_string, to_string, excluding=True):
    import re
    if excluding:
	   try: r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text, re.DOTALL).group(1)
	   except: r = ''
    else:
       try: r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text, re.DOTALL).group(1)
       except: r = ''
    return r
def regex_get_all(text, start_with, end_with):
    import re
    r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
    return r
def sort_function(item):
        """
        transform items quality into a string that's sort-able
        Args:
            item: scraper link
        Returns:
            sortable quality string
        """
        if "quality" in item[1][0]:
            quality = item[1][0]["quality"]
        else:
            quality = item[1][0]["path"]["quality"]

        if "path" in item[1][0]:
            if "debridonly" in item[1][0]["path"]:
                q = "A"
        elif "debridonly" in item[1][0]:
            q = "A"
        else:
            q = "B"

        if q == "A":
            if quality.startswith("4K"):
                quality = "Aa"
            elif quality.startswith("1080"):
                quality = "Ab"
            elif quality.startswith("720"):
                quality = "Ac"
            elif quality.startswith("560"):
                quality = "Ad"
            elif quality == "DVD":
                quality = "Ae"
            elif quality == "HD":
                quality = "Af"
            elif quality.startswith("480"):
                quality = "Ba"
            elif quality.startswith("360"):
                quality = "Bb"
            elif quality.startswith("SD"):
                quality = "Bc"
            else:
                quality = "CZ"

        elif quality.startswith("4K"):
            quality = "HDa"
        elif quality.startswith("1080"):
            quality = "HDb"
        elif quality.startswith("720"):
            quality = "HDc"
        elif quality.startswith("560"):
            quality = "HDd"
        elif quality == "DVD":
            quality = "HDe"
        elif quality == "HD":
            quality = "HDf"
        elif quality.startswith("480"):
            quality = "SDa"
        elif quality.startswith("360"):
            quality = "SDb"
        elif quality.startswith("SD"):
            quality = "SDc"
        else:
            quality = "Z"
        return quality
def GetSublinks(url,title,year,imdb):
   try:
        rd_sources=ADDON.getSetting("rdsource")
        allow_debrid = rd_sources == "true" 
        List=[]; ListU=[]; c=0
        all_videos = regex_get_all(url, 'sublink:', '#')
        
        for a in all_videos:
            logging.warning(a)
            if 'LISTSOURCE:' in a:
                logging.warning('In List')
                vurl = regex_from_to(a, 'LISTSOURCE:', '::')
                linename = regex_from_to(a, 'LISTNAME:', '::')
                logging.warning(vurl)
            else:
                vurl = a.replace('sublink:','').replace('#','')
                linename = title
            if len(vurl) > 10:
                c=c+1; List.append(linename); ListU.append(vurl)
      
        if c==1:
                return ListU[0]
               
            
        else:
             if len(List)==0:
                import universalscrapers
                title=title.replace('.',' ')
      
                scraper = universalscrapers.scrape_movie_with_dialog
                link, rest = scraper(
                    title,
                    year,
                    imdb,
                    timeout=30,
                    exclude=None,
                    extended=True,
                    sort_function=sort_function,
                    enable_debrid=allow_debrid,
                )
        
                if type(link) == dict and "path" in link:
                    link = link["path"]
                if link is None:
                    return False
                url = link["url"]
                if 'http' not in url and 'magnet' not in url:
                    url='http:'+url
       
                return url
             else:
                 dialog=xbmcgui.Dialog()
                 rNo=dialog.select('[COLORorange]Select A Source[/COLOR]', List)
                 if rNo>=0:
                     rName=title
                     rURL=str(ListU[rNo])
                     return rURL
   except Exception as e:
    logging.warning(e)
@route(mode="get_sources", args=["url"])
def get_sources(item):
    """
    get video_link and try to play it
    Keyword Arguments:
    item -- JenItem to try playing
    """
    logging.warning('Settings')
    logging.warning(ADDON.getSetting("jen_sources"))
    
    result = run_hook("get_sources", item)
    if result:
        return
    if item.startswith("<plugin>") :
        # link to plugin
       
        link = JenItem(item)["link"]
       
        sublinks = JenItem(link).getAll("sublink")
      
        if sublinks:
            if len(sublinks) > 1:
                link = choose_quality(link)
            else:
                link = sublinks[0]
        link = link.replace("&amp;", "&")
        xbmc.executebuiltin("Container.update(" + link + ")")
        return
    item = JenItem(item)
   
    link = item["link"]
    if not link or link.replace("\t", "") == "":
        return
        
    meta = JenItem(item["meta"])
    title = meta["title"]
    year = meta.get("year", "").split("-")[0].strip()
    imdb = meta.get("imdb", "")
    tvdb = meta.get("tvdb", "")
    season = meta.get("season", "")
    episode = meta.get("episode", "")
    tvshowtitle = meta.get("tvshowtitle", None)
    premiered = meta.get("premiered", "")
    try:
        premiered = premiered.split("-")[0].strip()
    except:
        if len(premiered) == 4:
            pass
        elif not premiered:
            pass
        else:
            koding.dolog("wrong premiered format")
    busy_dialog = xbmcgui.DialogProgress()
    dialog = xbmcgui.Dialog()
    icon = ADDON.getAddonInfo("icon")
    logging.warning('Start3:')
    
    if 'sublink' in item["link"] and '/sublink' not in item["link"]:
        logging.warning('Start3:1')
        logging.warning('new Sublink:'+item["link"])
        preset=GetSublinks(item["link"],title,year,imdb)
        logging.warning('preset:'+preset)
        message=''
        
    else:
        
        logging.warning('Start3:2')
        logging.warning('old Sublink:')
        preset = choose_quality(link)
        message = get_searching_message(preset)
    jen_pl=False
    if "search" not in preset:
        jen_pl=True
    elif ADDON.getSetting("jen_sources")=='0':
        jen_pl=True
    if jen_pl:
        jenplayer = JenPlayer(resume=False)
        try:
            spec = {"identifier": imdb, "season": season or "0", "episode": episode or "0"}
            match = koding.Get_From_Table("watched", spec)
            if match:
                match = match[0]
                
                if match["currentTime"] and not match["currentTime"] == "0":
                    if dialog.yesno(
                        ADDON.getAddonInfo("name"),
                        _("Previous playback detected"),
                        yeslabel=_("Resume"),
                        nolabel=_("Restart"),
                    ):
                        jenplayer = JenPlayer(resume=True)
        except:
            pass
    logging.warning('Start:')
    if "search" not in preset:
        jenplayer.setItem(item)
    elif ADDON.getSetting("jen_sources")=='0':
        jenplayer.setItem(item)
    
    
    busy_dialog.create(xbmcaddon.Addon().getAddonInfo("name"), _("Processing Link"))
    played = False
    infolabels = {}
    
    if preset:

        preset = preset.replace("&amp;", "&")
        busy_dialog.update(0, message)
        listitem = None
        fetch_meta = ADDON.getSetting("metadata") == "true"
        listitem = xbmcgui.ListItem(
            path=link,
            iconImage=item.get("thumbnail", icon),
            thumbnailImage=item.get("thumbnail", icon),
        )
        infolabels = {}
        if fetch_meta and imdb != "0":  # only try valid items with imdb
            try:
                info, created = get_info([item.item_string])
                if info and type(info) == dict:
                    infolabels = info
            except:
                pass
        else:
            infolabels["title"] = title
            infolabels["name"] = title
        if "plotoutline" not in infolabels:
            infolabels["plotoutline"] = infolabels.get("plot", "")
        if item.get("content", "") == "song":
            listitem.setInfo(
                type="Music",
                infoLabels={
                    "title": meta.get("title", ""),
                    "artist": meta.get("artist", ""),
                },
            )
        else:
            listitem.setInfo(type="video", infoLabels=infolabels)
            listitem.setLabel(item.get("title", item.get("name", "")))

        if "search" in preset:
            exclude_scrapers_content = item.get("exclude_scrapers", "")
            if exclude_scrapers_content:
                exclude_scrapers = exclude_scrapers_content.split(";")
            else:
                exclude_scrapers = None
            # nanscraper link

            if ADDON.getSetting("jen_sources")=='0':
                player_jen=jenplayer
            else:
                player_jen=None
            if item.get("content", "") == "song":
                artist = item.get("artist", "")
                played = Sources.get_music_sources(
                    title,
                    artist,
                    preset=preset,
                    dialog=busy_dialog,
                    exclude=exclude_scrapers,
                    listitem=listitem,
                    player=player_jen,
                )
            else:
                played = Sources.get_sources(
                    title,
                    year,
                    imdb,
                    tvdb,
                    season,
                    episode,
                    tvshowtitle,
                    premiered,
                    preset=preset,
                    dialog=busy_dialog,
                    listitem=listitem,
                    exclude=exclude_scrapers,
                    player=player_jen,
                    icon=item.get("thumbnail", icon),
                    fanart=item.get("fanart", icon),
                    
                )
        elif preset.startswith("http") or preset.startswith("plugin") or preset.endswith('.torrent') or preset.startswith('magnet'):
            # direct link
            
            if "/playlist" in preset and "youtube" in preset:
                busy_dialog.close()
                xbmc.executebuiltin("Container.update(" + preset + ")")
                return
            elif "plugin://plugin.video.youtube/play/?video_id=" in preset:
                xbmc.executebuiltin("PlayMedia(%s)" % preset)
                played = True
            elif item["content"] == "image":
                busy_dialog.close()
                xbmc.executebuiltin("ShowPicture(%s)" % preset)
                played = True
            else:
                played = koding.Play_Video(
                    preset,
                    showbusy=False,
                    ignore_dp=True,
                    item=listitem,
                    player=jenplayer,
                    resolver=resolveurl,
                )      
                
        else:
            # who knows
            busy_dialog.close()
            koding.dolog("unknown link type: " + repr(preset))
            raise Exception()
    busy_dialog.close()
    #if played:
    #    jenplayer.keep_alive()


@route(mode="queue", args=["url"])
def queue_source(item, depth=0):
    """
    queue item
    Keyword Arguments:
    item -- JenItem to try playing
    """
    from resources.lib.util.url import get_addon_url

    jen_item = JenItem(item)
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    if "<item>" in str(jen_item):
        play = False
        if xbmcaddon.Addon().getSetting("autostart_queue") == "true":
            if playlist.size() == 0:
                play = True
        playlist.add(
            get_addon_url("get_sources", str(item)),
            xbmcgui.ListItem(
                jen_item["title"], iconImage=jen_item.get("thumbnail", "")
            ),
        )
        if play:
            play_queue()
    else:
        link = jen_item.get("url", jen_item.get("link", ""))
        jenlist = JenList(link).get_raw_list()
        for list_item in jenlist:
            queue_source(str(list_item), depth + 1)
    if depth == 0:
        xbmcgui.Dialog().notification(
            ADDON.getAddonInfo("name"),
            _("Finished Queueing").encode("utf-8"),
            ADDON.getAddonInfo("icon"),
        )
        xbmc.executebuiltin("Container.Refresh")


@route(mode="clear_queue")
def clear_queue():
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
    xbmcgui.Dialog().notification(
        ADDON.getAddonInfo("name"),
        _("Queue cleared").encode("utf-8"),
        ADDON.getAddonInfo("icon"),
    )
    xbmc.executebuiltin("Container.Refresh")


@route(mode="play_queue")
def play_queue():
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    if playlist.size() > 0:
        item = playlist[0]
        xbmc.Player().play(playlist, item)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
    else:
        xbmcgui.Dialog().notification(
            ADDON.getAddonInfo("name"),
            _("Queue is empty").encode("utf-8"),
            ADDON.getAddonInfo("icon"),
        )
