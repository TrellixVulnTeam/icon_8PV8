# -*- coding: utf-8 -*-

"""
    Venom Add-on
"""

import os, sys, urllib, urlparse, re
import xbmc, xbmcaddon, xbmcplugin, xbmcvfs, xbmcgui

integer = 1000

addon = xbmcaddon.Addon
AddonID = xbmcaddon.Addon().getAddonInfo('id')
addonInfo = xbmcaddon.Addon().getAddonInfo
addonName = addonInfo('name')
addonVersion = addonInfo('version')

lang = xbmcaddon.Addon().getLocalizedString
lang2 = xbmc.getLocalizedString

setting = xbmcaddon.Addon().getSetting
setSetting = xbmcaddon.Addon().setSetting

item = xbmcgui.ListItem
listControl = xbmcgui.ControlList
labelControl = xbmcgui.ControlLabel
XBFONT_LEFT = 0x00000000
XBFONT_RIGHT = 0x00000001
XBFONT_CENTER_X = 0x00000002
XBFONT_CENTER_Y = 0x00000004
XBFONT_TRUNCATED = 0x00000008
window = xbmcgui.Window(10000)
windowDialog = xbmcgui.WindowDialog()
dialog = xbmcgui.Dialog()
progressDialog = xbmcgui.DialogProgress()
progressDialogBG = xbmcgui.DialogProgressBG()
getCurrentDialogId = xbmcgui.getCurrentWindowDialogId()
button = xbmcgui.ControlButton
image = xbmcgui.ControlImage

addItem = xbmcplugin.addDirectoryItem
directory = xbmcplugin.endOfDirectory
content = xbmcplugin.setContent
property = xbmcplugin.setProperty
resolve = xbmcplugin.setResolvedUrl

infoLabel = xbmc.getInfoLabel
condVisibility = xbmc.getCondVisibility
keyboard = xbmc.Keyboard
execute = xbmc.executebuiltin
skin = xbmc.getSkinDir()

player = xbmc.Player()
player2 = xbmc.Player
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

jsonrpc = xbmc.executeJSONRPC
skinPath = xbmc.translatePath('special://skin/')

# addonPath = xbmc.translatePath(addonInfo('path'))

try:
    addonPath = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8')
except:
    addonPath = xbmcaddon.Addon().getAddonInfo('path')

menus_path = os.path.join(addonPath, 'resources', 'lib', 'menus')
# images_path = os.path.join(menus_path, 'images')

SETTINGS_PATH = xbmc.translatePath(os.path.join(addonInfo('path'), 'resources', 'settings.xml'))

try:
    dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
except:
    dataPath = xbmc.translatePath(addonInfo('profile'))

settingsFile = os.path.join(dataPath, 'settings.xml')
viewsFile = os.path.join(dataPath, 'views.db')
bookmarksFile = os.path.join(dataPath, 'bookmarks.db')
providercacheFile = os.path.join(dataPath, 'providers.db')
metacacheFile = os.path.join(dataPath, 'metadata.db')
searchFile = os.path.join(dataPath, 'search.db')
libcacheFile = os.path.join(dataPath, 'library.db')
cacheFile = os.path.join(dataPath, 'cache.db')  # Used by trakt.py
# traktSyncFile = os.path.join(dataPath, 'traktSync.db') # Used by trakt.py

openFile = xbmcvfs.File
makeFile = xbmcvfs.mkdir
deleteFile = xbmcvfs.delete
listDir = xbmcvfs.listdir
deleteDir = xbmcvfs.rmdir
transPath = xbmc.translatePath
existsPath =  xbmcvfs.exists

key = "RgUkXp2s5v8x/A?D(G+KbPeShVmYq3t6"
iv = "p2s5v8y/B?E(H+Mb"


# def lang(language_id):
    # text = getLangString(language_id)
    # text = text.encode('utf-8', 'replace')
    # text = display_string(text)
    # return text


# def display_string(object):
    # if type(object) is str or type(object) is unicode:
        # return deaccentString(object)
    # if type(object) is int:
        # return '%s' % object
    # if type(object) is bytes:
        # object = ''.join(chr(x) for x in object)
        # return object


# def deaccentString(text):
    # text = u'%s' % text
    # text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    # return text


def sleep(time):  # Modified `sleep` command that honors a user exit request
    while time > 0 and not xbmc.abortRequested:
        xbmc.sleep(min(100, time))
        time = time - 100


def getKodiVersion():
    return xbmc.getInfoLabel("System.BuildVersion").split(".")[0]


def getCurrentViewId():
    win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return str(win.getFocusId())


def get_plugin_url(queries):
    try:
        query = urllib.urlencode(queries)
    except UnicodeEncodeError:
        for k in queries:
            if isinstance(queries[k], unicode):
                queries[k] = queries[k].encode('utf-8')
        query = urllib.urlencode(queries)
    addon_id = sys.argv[0]
    if not addon_id: addon_id = addonId()
    return addon_id + '?' + query


def version():
    num = ''
    try:
        version = addon('xbmc.addon').getAddonInfo('version')
    except:
        version = '999'
    for i in version:
        if i.isdigit():
            num += i
        else:
            break
    return int(num)


def addonId():
    return addonInfo('id')


def addonName():
    return addonInfo('name')


def addonPath(addon):
    try:
        addonID = xbmcaddon.Addon(addon)
    except:
        addonID = None

    if addonID is None:
        return ''
    else:
        return xbmc.translatePath(addonID.getAddonInfo('path').decode('utf-8'))


def addonVersion(addon):
    return xbmcaddon.Addon(addon).getAddonInfo('version')


def artPath():
    theme = appearance()
    return os.path.join(xbmcaddon.Addon('plugin.video.venom').getAddonInfo('path'), 'resources', 'artwork', theme)
#    if theme in ['-', '']: return
#    elif condVisibility('System.HasAddon(script.venom.artwork)'):
#        return os.path.join(xbmcaddon.Addon('script.venom.artwork').getAddonInfo('path'), 'resources', 'media', theme)


def appearance():
    appearance = setting('appearance.1').lower()
    return appearance


def artwork():
    if condVisibility('System.HasAddon(script.venom.artwork)'):
        execute('RunPlugin(plugin://script.venom.artwork)')


def addonIcon():
    theme = appearance()
    art = artPath()
    if not (art is None and theme in ['-', '']):
        return os.path.join(art, 'icon.png')
    return addonInfo('icon')


def addonThumb():
    theme = appearance()
    art = artPath()
    if not (art is None and theme in ['-', '']):
        return os.path.join(art, 'poster.png')
    elif theme == '-':
        return 'DefaultFolder.png'
    return addonInfo('icon')


def addonPoster():
    theme = appearance()
    art = artPath()
    if not (art is None and theme in ['-', '']):
        return os.path.join(art, 'poster.png')
    return 'DefaultVideo.png'


def addonBanner():
    theme = appearance()
    art = artPath()
    if not (art is None and theme in ['-', '']):
        return os.path.join(art, 'banner.png')
    return 'DefaultVideo.png'


def addonFanart():
    theme = appearance()
    art = artPath()
    if not (art is None and theme in ['-', '']):
        return os.path.join(art, 'fanart.jpg')
    return addonInfo('fanart')


def addonNext():
    theme = appearance()
    art = artPath()
    if not (art is None and theme in ['-', '']):
        return os.path.join(art, 'next.png')
    return 'DefaultVideo.png'


def metaFile():
    # rid this fucking thing already!!
    #    if condVisibility('System.HasAddon(script.venom.metadata)'):
    #        return os.path.join(xbmcaddon.Addon('script.venom.metadata').getAddonInfo('path'), 'resources', 'data', 'meta.db')
    return os.path.join(dataPath, 'metadata.db')


def metadataClean(metadata):
    # Filter out non-existing/custom keys.
    # Otherise there are tons of errors in Kodi 18 log.
    if metadata is None:
        return metadata
    allowed = ['genre', 'country', 'year', 'episode', 'season', 'sortepisode', 'sortseason', 'episodeguide', 'showlink',
               'top250', 'setid', 'tracknumber', 'rating', 'userrating', 'watched', 'playcount', 'overlay', 'cast',
               'castandrole', 'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle',
               'duration', 'studio', 'tagline', 'writer', 'tvshowtitle', 'premiered', 'status', 'set', 'setoverview',
               'tag', 'imdbnumber', 'code', 'aired', 'credits', 'lastplayed', 'album', 'artist', 'votes', 'path',
               'trailer', 'dateadded', 'mediatype', 'dbid']
    return {k: v for k, v in metadata.iteritems() if k in allowed}



####################################################
# --- Dialogs
####################################################
def infoDialog(message, heading=addonInfo('name'), icon='', time=3000, sound=False):
    if icon == '':
        icon = addonIcon()
    elif icon == 'INFO':
        icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING':
        icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR':
        icon = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, message, icon, time, sound=sound)


def notification(title=None, message=None, icon=None, time=3000, sound=False):
    if title == 'default' or title == None:
        title = addonName()

    if isinstance(title, (int, long)):
        heading = lang(title).encode('utf-8')
    else:
        heading = str(title)

    if isinstance(message, (int, long)):
        body = lang(message).encode('utf-8')
    else:
        body = str(message)

    if icon is None or 'icon' or 'default':
        icon = addonIcon()

    elif icon == 'INFO':
        icon = xbmcgui.NOTIFICATION_INFO

    elif icon == 'WARNING':
        icon = xbmcgui.NOTIFICATION_WARNING

    elif icon == 'ERROR':
        icon = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, body, icon, time, sound=sound)


def yesnoDialog(line1, line2, line3, heading=addonInfo('name'), nolabel='', yeslabel=''):
    return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def selectDialog(list, heading=addonInfo('name')):
    return dialog.select(heading, list)


def okDialog(title=None, message=None):
    if title == 'default' or title == None:
        title = addonName()

    if isinstance(title, (int, long)):
        heading = lang(title).encode('utf-8')
    else:
        heading = str(title)

    if isinstance(message, (int, long)):
        body = lang(message).encode('utf-8')
    else:
        body = str(message)

    return dialog.ok(heading, body)


def context(items = None, labels = None):
    if items:
        labels = [i[0] for i in items]
        choice = xbmcgui.Dialog().contextmenu(labels)

        if choice >= 0:
            return items[choice][1]()
        else:
            return False

    else:
        return xbmcgui.Dialog().contextmenu(labels)


def busy():
    if int(getKodiVersion()) >= 18:
        return execute('ActivateWindow(busydialognocancel)')
    else:
        return execute('ActivateWindow(busydialog)')


def idle():
    if int(getKodiVersion()) >= 18:
        return execute('Dialog.Close(busydialognocancel)')
    else:
        return execute('Dialog.Close(busydialog)')


def hide():
    if int(getKodiVersion()) >= 18:
        return execute('Dialog.Close(busydialognocancel)')
    else:
        return execute('Dialog.Close(busydialog)')


def closeAll():
    return execute('Dialog.Close(all,true)')


def visible():
    if int(getKodiVersion()) >= 18 and xbmc.getCondVisibility('Window.IsActive(busydialognocancel)') == 1:
        return True
    return xbmc.getCondVisibility('Window.IsActive(busydialog)') == 1
########################



def refresh():
    return execute('Container.Refresh')


def queueItem():
    return execute('Action(Queue)')


def openSettings(query=None, id=addonInfo('id')):
    try:
        idle()
        execute('Addon.OpenSettings(%s)' % id)

        if query is None:
            raise Exception()

        c, f = query.split('.')

        if int(getKodiVersion()) >= 18:
            execute('SetFocus(%i)' % (int(c) - 100))
            execute('SetFocus(%i)' % (int(f) - 80))
        else:
            execute('SetFocus(%i)' % (int(c) + 100))
            execute('SetFocus(%i)' % (int(f) + 200))
    except:
        import traceback
        traceback.print_exc()
        return


def apiLanguage(ret_name=None):
    langDict = {'Bulgarian': 'bg', 'Chinese': 'zh', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl',
                'English': 'en', 'Finnish': 'fi', 'French': 'fr', 'German': 'de', 'Greek': 'el', 'Hebrew': 'he',
                'Hungarian': 'hu', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko', 'Norwegian': 'no', 'Polish': 'pl',
                'Portuguese': 'pt', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Slovak': 'sk',
                'Slovenian': 'sl', 'Spanish': 'es', 'Swedish': 'sv', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk'}
    trakt = ['bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it', 'ja', 'ko', 'nl', 'no', 'pl',
             'pt', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'th', 'tr', 'uk', 'zh']
    tvdb = ['en', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'fr', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt',
            'zh', 'cs', 'sl', 'hr', 'ko']
    youtube = ['gv', 'gu', 'gd', 'ga', 'gn', 'gl', 'ty', 'tw', 'tt', 'tr', 'ts', 'tn', 'to', 'tl', 'tk', 'th', 'ti',
               'tg', 'te', 'ta', 'de', 'da', 'dz', 'dv', 'qu', 'zh', 'za', 'zu', 'wa', 'wo', 'jv', 'ja', 'ch', 'co',
               'ca', 'ce', 'cy', 'cs', 'cr', 'cv', 'cu', 'ps', 'pt', 'pa', 'pi', 'pl', 'mg', 'ml', 'mn', 'mi', 'mh',
               'mk', 'mt', 'ms', 'mr', 'my', 've', 'vi', 'is', 'iu', 'it', 'vo', 'ii', 'ik', 'io', 'ia', 'ie', 'id',
               'ig', 'fr', 'fy', 'fa', 'ff', 'fi', 'fj', 'fo', 'ss', 'sr', 'sq', 'sw', 'sv', 'su', 'st', 'sk', 'si',
               'so', 'sn', 'sm', 'sl', 'sc', 'sa', 'sg', 'se', 'sd', 'lg', 'lb', 'la', 'ln', 'lo', 'li', 'lv', 'lt',
               'lu', 'yi', 'yo', 'el', 'eo', 'en', 'ee', 'eu', 'et', 'es', 'ru', 'rw', 'rm', 'rn', 'ro', 'be', 'bg',
               'ba', 'bm', 'bn', 'bo', 'bh', 'bi', 'br', 'bs', 'om', 'oj', 'oc', 'os', 'or', 'xh', 'hz', 'hy', 'hr',
               'ht', 'hu', 'hi', 'ho', 'ha', 'he', 'uz', 'ur', 'uk', 'ug', 'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an',
               'as', 'ar', 'av', 'ay', 'az', 'nl', 'nn', 'no', 'na', 'nb', 'nd', 'ne', 'ng', 'ny', 'nr', 'nv', 'ka',
               'kg', 'kk', 'kj', 'ki', 'ko', 'kn', 'km', 'kl', 'ks', 'kr', 'kw', 'kv', 'ku', 'ky']
    name = None
    name = setting('api.language')

    if not name:
        name = 'AUTO'

    if name[-1].isupper():
        try:
            name = xbmc.getLanguage(xbmc.ENGLISH_NAME).split(' ')[0]
        except: pass

    try:
        name = langDict[name]
    except:
        name = 'en'

    lang = {'trakt': name} if name in trakt else {'trakt': 'en'}
    lang['tvdb'] = name if name in tvdb else 'en'
    lang['youtube'] = name if name in youtube else 'en'

    if ret_name:
        lang['trakt'] = [i[0] for i in langDict.iteritems() if i[1] == lang['trakt']][0]
        lang['tvdb'] = [i[0] for i in langDict.iteritems() if i[1] == lang['tvdb']][0]
        lang['youtube'] = [i[0] for i in langDict.iteritems() if i[1] == lang['youtube']][0]
    return lang


def cdnImport(uri, name):
    import imp
    from resources.lib.modules import client
    path = os.path.join(dataPath, 'py' + name)
    path = path.decode('utf-8')
    deleteDir(os.path.join(path, ''), force=True)
    makeFile(dataPath);
    makeFile(path)
    r = client.request(uri)
    p = os.path.join(path, name + '.py')
    f = openFile(p, 'w');
    f.write(r);
    f.close()
    m = imp.load_source(name, p)
    deleteDir(os.path.join(path, ''), force=True)
    return m


###---start adding TMDb to params
def autoTraktSubscription(tvshowtitle, year, imdb, tvdb):
    from resources.lib.modules import libtools
    libtools.libtvshows().add(tvshowtitle, year, imdb, tvdb)


def getSettingDefault(id):
    try:
        settings = open(SETTINGS_PATH, 'r')
        value = ' '.join(settings.readlines())
        value.strip('\n')
        settings.close()
        value = re.findall(r'id=\"%s\".*?default=\"(.*?)\"' % (id), value)[0]
        return value
    except:
        return None
