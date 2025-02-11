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


import urllib2,urllib
import re
import mydecode

BASEURL='http://tvp1-online.blogspot.com/p/tvp-1-online-kanaly.html'
UA='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

def getUrl(url,data=None,header={}):
    if not header:
        header = {'User-Agent':UA}
    req = urllib2.Request(url,data,headers=header)
    try:
        response = urllib2.urlopen(req, timeout=15)
        link = response.read()
        response.close()
    except:
        link=''
    return link
    
def getChannels(addheader=False):
    content = getUrl(BASEURL)

    out=[]
    s_hex = re.compile('document.write\(unescape\(\'(.*?)\'\)').findall(content)
    if s_hex:
        data = urllib.unquote(s_hex[0])
        button=re.compile('<button class="button1" value="(.*?)"[^>]*/>(.*?)</button>').findall(data)
        for href,title in button:
            h = href
            t = title.strip()
            if h and t:
                out.append({'title':t,'tvid':t,'img':'','url':h,'group':'','urlepg':''})
    if addheader and len(out):
        t='[COLOR yellow]Updated: %s (cinema-tv)[/COLOR]' %time.strftime("%d/%m/%Y: %H:%M:%S")
        out.insert(0,{'title':t,'tvid':'','img':'','url':BASEURL,'group':'','urlepg':''})
    return out  

def getChannelVideo(url='http://sporty14.blogspot.com/p/tp1a.html'):
    #rtmp://50.7.115.2/stream/<playpath>2111L <swfUrl>http://p.jwpcdn.com/6/12/jwplayer.flash.swf <pageUrl>http://filterup.blogspot.com/p/tp2.html
    video=[]
    if 'blogspot' in url:
        content = getUrl(url)
        rtmp = re.compile('"(rtmp://.*?)"').findall(content)
        swfUrl='http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
        if rtmp:
            href = rtmp[0]+ ' swfUrl=%s pageUrl=%s live=1 timeout=10'%(swfUrl,url)
            video=[{'url':href}]
            
    return video     
     
def test():
    out=getChannels()
    for o in out:
        link = getChannelVideo(o.get('url'))
        print link
        