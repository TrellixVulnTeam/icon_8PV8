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


import os
import sys

import xbmc
import xbmcgui
import xbmcplugin
from core import config, logger
from core.item import Item
from core.tmdb import Tmdb


def dialog_ok(heading, line1, line2="", line3=""):
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, line1, line2, line3)


def dialog_notification(heading, message, icon=0, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    try:
        l_icono = xbmcgui.NOTIFICATION_INFO, xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR
        dialog.notification(heading, message, l_icono[icon], time, sound)
    except:
        dialog_ok(heading, message)


def dialog_yesno(heading, line1, line2="", line3="", nolabel="No", yeslabel="Si", autoclose=""):
    dialog = xbmcgui.Dialog()
    if autoclose:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel, autoclose)
    else:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def dialog_select(heading, _list):
    return xbmcgui.Dialog().select(heading, _list)


def dialog_progress(heading, line1, line2=" ", line3=" "):
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, line1, line2, line3)
    return dialog


def dialog_progress_bg(heading, message=""):
    try:
        dialog = xbmcgui.DialogProgressBG()
        dialog.create(heading, message)
        return dialog
    except:
        return dialog_progress(heading, message)


def dialog_input(default="", heading="", hidden=False):
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def dialog_numeric(_type, heading, default=""):
    dialog = xbmcgui.Dialog()
    d = dialog.numeric(_type, heading, default)
    return d


def itemlist_refresh():
    xbmc.executebuiltin("Container.Refresh")


def itemlist_update(item):
    xbmc.executebuiltin("Container.Update(" + sys.argv[0] + "?" + item.tourl() + ")")


def render_items(itemlist, parent_item):
    """
    Función encargada de mostrar el itemlist en kodi, se pasa como parametros el itemlist y el item del que procede
    @type itemlist: list
    @param itemlist: lista de elementos a mostrar

    @type parent_item: item
    @param parent_item: elemento padre
    """
    # Si el itemlist no es un list salimos
    if not type(itemlist) == list:
        if config.get_platform() == "boxee":
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        return

    # Si no hay ningun item, mostramos un aviso
    if not len(itemlist):
        itemlist.append(Item(title="Non ci sono elementi da visualizzare"))

    # Recorremos el itemlist
    for item in itemlist:
        # logger.debug(item)
        # Si el item no contiene categoria, le ponemos la del item padre
        if item.category == "":
            item.category = parent_item.category

        # Si el item no contiene fanart, le ponemos el del item padre
        if item.fanart == "":
            item.fanart = parent_item.fanart

        # Formatear titulo
        if item.text_color:
            item.title = '[COLOR %s]%s[/COLOR]' % (item.text_color, item.title)
        if item.text_blod:
            item.title = '[B]%s[/B]' % item.title
        if item.text_italic:
            item.title = '[I]%s[/I]' % item.title

        # Añade headers a las imagenes si estan en un servidor con cloudflare
        from core import httptools
        item.thumbnail = httptools.get_url_headers(item.thumbnail)
        item.fanart = httptools.get_url_headers(item.fanart)

        # IconImage para folder y video
        if item.folder:
            icon_image = "DefaultFolder.png"
        else:
            icon_image = "DefaultVideo.png"

        # Creamos el listitem
        listitem = xbmcgui.ListItem(item.title, iconImage=icon_image, thumbnailImage=item.thumbnail)

        # Ponemos el fanart
        if item.fanart:
            listitem.setProperty('fanart_image', item.fanart)
        else:
            listitem.setProperty('fanart_image', os.path.join(config.get_runtime_path(), "fanart.jpg"))

        # TODO: ¿Se puede eliminar esta linea? yo no he visto que haga ningun efecto.
        xbmcplugin.setPluginFanart(int(sys.argv[1]), os.path.join(config.get_runtime_path(), "fanart.jpg"))

        # Añadimos los infoLabels
        set_infolabels(listitem, item)

        # Montamos el menu contextual
        context_commands = set_context_commands(item, parent_item)

        # Añadimos el item
        if config.get_platform() == "boxee":
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?%s' % (sys.argv[0], item.tourl()),
                                        listitem=listitem, isFolder=item.folder)
        else:
            listitem.addContextMenuItems(context_commands, replaceItems=True)

            if not item.totalItems:
                item.totalItems = 0
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?%s' % (sys.argv[0], item.tourl()),
                                        listitem=listitem, isFolder=item.folder,
                                        totalItems=item.totalItems)

    # Fijar los tipos de vistas...
    if config.get_setting("forceview") == True:
        # ...forzamos segun el viewcontent
        xbmcplugin.setContent(int(sys.argv[1]), parent_item.viewcontent)
        # logger.debug(parent_item)
    elif parent_item.channel not in ["channelselector", ""]:
        # ... o segun el canal
        xbmcplugin.setContent(int(sys.argv[1]), "movies")

    # Fijamos el "breadcrumb"
    xbmcplugin.setPluginCategory(handle=int(sys.argv[1]), category=parent_item.category.capitalize())

    # No ordenar items
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)

    # Cerramos el directorio
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    # Fijar la vista
    if config.get_setting("forceview") == True:
        viewmode_id = get_viewmode_id(parent_item)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % viewmode_id)


def get_viewmode_id(parent_item):
    # viewmode_json habria q guardarlo en un archivo y crear un metodo para q el user fije sus preferencias en:
    # user_files, user_movies, user_tvshows, user_season y user_episodes.
    viewmode_json = {'skin.confluence': {'default_files': 50,
                                         'default_movies': 515,
                                         'default_tvshows': 508,
                                         'default_seasons': 503,
                                         'default_episodes': 504,
                                         'view_list': 50,
                                         'view_thumbnails': 500,
                                         'view_movie_with_plot': 503},
                     'skin.estuary': {'default_files': 50,
                                      'default_movies': 54,
                                      'default_tvshows': 502,
                                      'default_seasons': 500,
                                      'default_episodes': 53,
                                      'view_list': 50,
                                      'view_thumbnails': 500,
                                      'view_movie_with_plot': 54}}

    # Si el parent_item tenia fijado un viewmode usamos esa vista...
    if parent_item.viewmode == 'movie':
        # Remplazamos el antiguo viewmode 'movie' por 'thumbnails'
        parent_item.viewmode = 'thumbnails'

    if parent_item.viewmode in ["list", "movie_with_plot", "thumbnails"]:
        view_name = "view_" + parent_item.viewmode

        '''elif isinstance(parent_item.viewmode, int):
            # only for debug
            viewName = parent_item.viewmode'''

    # ...sino ponemos la vista por defecto en funcion del viewcontent
    else:
        view_name = "default_" + parent_item.viewcontent

    skin_name = xbmc.getSkinDir()
    if skin_name not in viewmode_json:
        skin_name = 'skin.confluence'
    view_skin = viewmode_json[skin_name]
    return view_skin.get(view_name, 50)


def set_infolabels(listitem, item, player=False):
    """
    Metodo para pasar la informacion al listitem (ver tmdb.set_InfoLabels() )
    item.infoLabels es un dicionario con los pares de clave/valor descritos en:
    http://mirrors.xbmc.org/docs/python-docs/14.x-helix/xbmcgui.html#ListItem-setInfo
    @param listitem: objeto xbmcgui.ListItem
    @type listitem: xbmcgui.ListItem
    @param item: objeto Item que representa a una pelicula, serie o capitulo
    @type item: item
    """
    if item.infoLabels:
        if 'mediatype' not in item.infoLabels:
            item.infoLabels['mediatype'] = item.contentType
        listitem.setInfo("video", item.infoLabels)

    if player and not item.contentTitle:
        if item.fulltitle:
            listitem.setInfo("video", {"Title": item.fulltitle})
        else:
            listitem.setInfo("video", {"Title": item.title})

    elif not player:
        listitem.setInfo("video", {"Title": item.title})

    # Añadido para Kodi Krypton (v17)
    if config.get_platform(True)['num_version'] >= 17.0:
        listitem.setArt({"poster": item.thumbnail})


def set_context_commands(item, parent_item):
    """
    Función para generar los menus contextuales.
        1. Partiendo de los datos de item.context
             a. Metodo antiguo item.context tipo str separando las opciones por "|" (ejemplo: item.context = "1|2|3")
                (solo predefinidos)
            b. Metodo list: item.context es un list con las diferentes opciones del menu:
                - Predefinidos: Se cargara una opcion predefinida con un nombre.
                    item.context = ["1","2","3"]

                - dict(): Se cargara el item actual modificando los campos que se incluyan en el dict() en caso de
                    modificar los campos channel y action estos serán guardados en from_channel y from_action.
                    item.context = [{"title":"Nombre del menu", "action": "action del menu",
                                        "channel":"channel del menu"}, {...}]

        2. Añadiendo opciones segun criterios
            Se pueden añadir opciones al menu contextual a items que cumplan ciertas condiciones.


        3. Añadiendo opciones a todos los items
            Se pueden añadir opciones al menu contextual para todos los items

        4. Se pueden deshabilitar las opciones del menu contextual añadiendo un comando 'no_context' al item.context.
            Las opciones que Kodi, el skin u otro añadido añada al menu contextual no se pueden deshabilitar.

    @param item: elemento que contiene los menu contextuales
    @type item: item
    @param parent_item:
    @type parent_item: item
    """
    context_commands = []
    num_version_xbmc = config.get_platform(True)['num_version']

    # Creamos un list con las diferentes opciones incluidas en item.context
    if type(item.context) == str:
        context = item.context.split("|")
    elif type(item.context) == list:
        context = item.context
    else:
        context = []

    # Opciones segun item.context
    for command in context:
        # Predefinidos
        if type(command) == str:
            if command == "no_context":
                return []

        # Formato dict
        if type(command) == dict:
            # Los parametros del dict, se sobreescriben al nuevo context_item en caso de sobreescribir "action" y
            # "channel", los datos originales se guardan en "from_action" y "from_channel"
            if "action" in command:
                command["from_action"] = item.action
            if "channel" in command:
                command["from_channel"] = item.channel

            if "goto" in command:
                context_commands.append((command["title"], "XBMC.Container.Refresh (%s?%s)" %
                                         (sys.argv[0], item.clone(**command).tourl())))
            else:
                context_commands.append(
                    (command["title"], "XBMC.RunPlugin(%s?%s)" % (sys.argv[0], item.clone(**command).tourl())))

    # Opciones segun criterios, solo si el item no es un tag (etiqueta), ni es "Añadir a la biblioteca", etc...
    if item.action and item.action not in ["add_pelicula_to_library", "add_serie_to_library", "buscartrailer"]:
        # Mostrar informacion: si el item tiene plot suponemos q es una serie, temporada, capitulo o pelicula
        if item.infoLabels['plot'] and (num_version_xbmc < 17.0 or item.contentType == 'season'):
            context_commands.append(("Informazioni", "XBMC.Action(Info)"))

        # ExtendedInfo: Si esta instalado el addon y se cumplen una serie de condiciones
        if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)') \
                and config.get_setting("extended_info") == True:
            if item.contentType == "episode" and item.contentEpisodeNumber and item.contentSeason \
                    and (item.infoLabels['tmdb_id'] or item.contentSerieName):
                param = "tvshow_id =%s, tvshow=%s, season=%s, episode=%s" \
                        % (item.infoLabels['tmdb_id'], item.contentSerieName, item.contentSeason,
                           item.contentEpisodeNumber)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=extendedepisodeinfo,%s)" % param))

            elif item.contentType == "season" and item.contentSeason \
                    and (item.infoLabels['tmdb_id'] or item.contentSerieName):
                param = "tvshow_id =%s,tvshow=%s, season=%s" \
                        % (item.infoLabels['tmdb_id'], item.contentSerieName, item.contentSeason)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=seasoninfo,%s)" % param))

            elif item.contentType == "tvshow" and (item.infoLabels['tmdb_id'] or item.infoLabels['tvdb_id'] or
                                                   item.infoLabels['imdb_id'] or item.contentSerieName):
                param = "id =%s,tvdb_id=%s,imdb_id=%s,name=%s" \
                        % (item.infoLabels['tmdb_id'], item.infoLabels['tvdb_id'], item.infoLabels['imdb_id'],
                           item.contentSerieName)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=extendedtvinfo,%s)" % param))

            elif item.contentType == "movie" and (item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or
                                                  item.contentTitle):
                param = "id =%s,imdb_id=%s,name=%s" \
                        % (item.infoLabels['tmdb_id'], item.infoLabels['imdb_id'], item.contentTitle)
                context_commands.append(("ExtendedInfo",
                                         "XBMC.RunScript(script.extendedinfo,info=extendedinfo,%s)" % param))

        # InfoPlus
        if config.get_setting("infoplus") == True:
            if item.infoLabels['tmdb_id'] or item.infoLabels['imdb_id'] or item.infoLabels['tvdb_id'] or \
                    (item.contentTitle and item.infoLabels["year"]) or item.contentSerieName:
                context_commands.append(("InfoPlus", "XBMC.RunPlugin(%s?%s)" % (sys.argv[0], item.clone(
                    channel="infoplus", action="start", from_channel=item.channel).tourl())))

        # Ir al Menu Principal (channel.mainlist)
        if parent_item.channel not in ["novedades", "channelselector"] and item.action != "mainlist" \
                and parent_item.action != "mainlist":
            context_commands.append(("Vai a menù principale", "XBMC.Container.Refresh (%s?%s)" %
                                     (sys.argv[0], Item(channel=item.channel, action="mainlist").tourl())))

        # Añadir a Favoritos
        if num_version_xbmc < 17.0 and ((item.channel not in ["favoritos", "biblioteca", "ayuda", ""] or
                                         item.action in ["update_biblio"]) and not parent_item.channel == "favoritos"):
            context_commands.append((config.get_localized_string(30155), "XBMC.RunPlugin(%s?%s)" %
                                     (sys.argv[0], item.clone(channel="favoritos", action="addFavourite",
                                                              from_channel=item.channel,
                                                              from_action=item.action).tourl())))

        if item.channel != "biblioteca":
            # Añadir Serie a la biblioteca
            if item.action in ["episodios", "get_episodios"] and item.contentSerieName:
                context_commands.append(("Aggiungi serie a libreria", "XBMC.RunPlugin(%s?%s)" %
                                         (sys.argv[0], item.clone(action="add_serie_to_library",
                                                                  from_action=item.action).tourl())))
            # Añadir Pelicula a Biblioteca
            elif item.action in ["detail", "findvideos"] and item.contentType == 'movie' and item.contentTitle:
                context_commands.append(("Aggiungi film a libreria", "XBMC.RunPlugin(%s?%s)" %
                                         (sys.argv[0], item.clone(action="add_pelicula_to_library",
                                                                  from_action=item.action).tourl())))

        # Abrir configuración
        if parent_item.channel not in ["configuracion", "novedades", "buscador"]:
            context_commands.append(("Configurazione", "XBMC.Container.Update(%s?%s)" %
                                     (sys.argv[0], Item(channel="configuracion", action="mainlist").tourl())))

        # Buscar Trailer
        if item.action == "findvideos" or "buscar_trailer" in context:
            context_commands.append(("Cerca Trailer", "XBMC.RunPlugin(%s?%s)" % (sys.argv[0], item.clone(
                channel="trailertools", action="buscartrailer", contextual=True).tourl())))

    # Añadir SuperFavourites al menu contextual (1.0.53 o superior necesario)
    sf_file_path = xbmc.translatePath("special://home/addons/plugin.program.super.favourites/LaunchSFMenu.py")
    check_sf = os.path.exists(sf_file_path)
    if check_sf and xbmc.getCondVisibility('System.HasAddon("plugin.program.super.favourites")'):
        context_commands.append(("Super Favourites Menu",
                                 "XBMC.RunScript(special://home/addons/plugin.program.super.favourites/LaunchSFMenu.py)"))

    return sorted(context_commands, key=lambda comand: comand[0])


def is_playing():
    return xbmc.Player().isPlaying()


def play_video(item, strm=False):
    logger.info()
    # logger.debug(item.tostring('\n'))

    if item.channel == 'descargas':
        logger.info("Reproducir video local: %s [%s]" % (item.title, item.url))
        xlistitem = xbmcgui.ListItem(path=item.url, thumbnailImage=item.thumbnail)
        set_infolabels(xlistitem, item, True)
        xbmc.Player().play(item.url, xlistitem)
        return

    default_action = config.get_setting("default_action")
    logger.info("default_action=%s" % default_action)

    # Abre el diálogo de selección para ver las opciones disponibles
    opciones, video_urls, seleccion, salir = get_dialogo_opciones(item, default_action, strm)
    if salir:
        return

    # se obtienen la opción predeterminada de la configuración del addon
    seleccion = get_seleccion(default_action, opciones, seleccion, video_urls)
    if seleccion < 0:  # Cuadro cancelado
        return

    logger.info("seleccion=%d" % seleccion)
    logger.info("seleccion=%s" % opciones[seleccion])

    # se ejecuta la opcion disponible, jdwonloader, descarga, favoritos, añadir a la biblioteca... SI NO ES PLAY
    salir = set_opcion(item, seleccion, opciones, video_urls)
    if salir:
        return

    # obtenemos el video seleccionado
    mediaurl, view, mpd = get_video_seleccionado(item, seleccion, video_urls)
    if mediaurl == "":
        return

    # se obtiene la información del video.
    if not item.contentThumbnail:
        xlistitem = xbmcgui.ListItem(path=mediaurl, thumbnailImage=item.thumbnail)
    else:
        xlistitem = xbmcgui.ListItem(path=mediaurl, thumbnailImage=item.contentThumbnail)
    set_infolabels(xlistitem, item, True)

    # si se trata de un vídeo en formato mpd, se configura el listitem para reproducirlo
    # con el addon inpustreamaddon implementado en Kodi 17
    if mpd:
        xlistitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        xlistitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')

    # se lanza el reproductor
    set_player(item, xlistitem, mediaurl, view, strm)


def stop_video():
    xbmc.Player().stop()


def get_seleccion(default_action, opciones, seleccion, video_urls):
    # preguntar
    if default_action == 0:
        # "Elige una opción"
        seleccion = dialog_select(config.get_localized_string(30163), opciones)
    # Ver en calidad baja
    elif default_action == 1:
        seleccion = 0
    # Ver en alta calidad
    elif default_action == 2:
        seleccion = len(video_urls) - 1
    else:
        seleccion = 0
    return seleccion


def show_channel_settings(list_controls=None, dict_values=None, caption="", callback=None, item=None,
                          custom_button=None, channelpath=None):
    """
    Muestra un cuadro de configuracion personalizado para cada canal y guarda los datos al cerrarlo.

    Parametros: ver descripcion en xbmc_config_menu.SettingsWindow
    @param list_controls: lista de elementos a mostrar en la ventana.
    @type list_controls: list
    @param dict_values: valores que tienen la lista de elementos.
    @type dict_values: dict
    @param caption: titulo de la ventana
    @type caption: str
    @param callback: función que se llama tras cerrarse la ventana.
    @type callback: str
    @param item: item para el que se muestra la ventana de configuración.
    @type item: Item
    @param custom_button: botón personalizado, que se muestra junto a "OK" y "Cancelar".
    @type custom_button: dict

    @return: devuelve la ventana con los elementos
    @rtype: SettingsWindow
    """
    from xbmc_config_menu import SettingsWindow
    return SettingsWindow("ChannelSettings.xml", config.get_runtime_path()) \
        .start(list_controls=list_controls, dict_values=dict_values, title=caption, callback=callback, item=item,
               custom_button=custom_button, channelpath=channelpath)


def show_video_info(data, caption="", item=None, scraper=Tmdb):
    """
    Muestra una ventana con la info del vídeo. Opcionalmente se puede indicar el titulo de la ventana mendiante
    el argumento 'caption'.

    Si se pasa un item como argumento 'data' usa el scrapper Tmdb para buscar la info del vídeo
        En caso de peliculas:
            Coge el titulo de los siguientes campos (en este orden)
                  1. contentTitle (este tiene prioridad 1)
                  2. fulltitle (este tiene prioridad 2)
                  3. title (este tiene prioridad 3)
            El primero que contenga "algo" lo interpreta como el titulo (es importante asegurarse que el titulo este en
            su sitio)

        En caso de series:
            1. Busca la temporada y episodio en los campos contentSeason y contentEpisodeNumber
            2. Intenta Sacarlo del titulo del video (formato: 1x01)

            Aqui hay dos opciones posibles:
                  1. Tenemos Temporada y episodio
                    Muestra la información del capitulo concreto
                  2. NO Tenemos Temporada y episodio
                    En este caso muestra la informacion generica de la serie

    Si se pasa como argumento 'data' un  objeto InfoLabels(ver item.py) muestra en la ventana directamente
    la información pasada (sin usar el scrapper)
        Formato:
            En caso de peliculas:
                infoLabels({
                         "type"           : "movie",
                         "title"          : "Titulo de la pelicula",
                         "original_title" : "Titulo original de la pelicula",
                         "date"           : "Fecha de lanzamiento",
                         "language"       : "Idioma original de la pelicula",
                         "rating"         : "Puntuacion de la pelicula",
                         "votes"          : "Numero de votos",
                         "genres"         : "Generos de la pelicula",
                         "thumbnail"      : "Ruta para el thumbnail",
                         "fanart"         : "Ruta para el fanart",
                         "plot"           : "Sinopsis de la pelicula"
                      }
            En caso de series:
                infoLabels({
                         "type"           : "tv",
                         "title"          : "Titulo de la serie",
                         "episode_title"  : "Titulo del episodio",
                         "date"           : "Fecha de emision",
                         "language"       : "Idioma original de la serie",
                         "rating"         : "Puntuacion de la serie",
                         "votes"          : "Numero de votos",
                         "genres"         : "Generos de la serie",
                         "thumbnail"      : "Ruta para el thumbnail",
                         "fanart"         : "Ruta para el fanart",
                         "plot"           : "Sinopsis de la del episodio o de la serie",
                         "seasons"        : "Numero de Temporadas",
                         "season"         : "Temporada",
                         "episodes"       : "Numero de episodios de la temporada",
                         "episode"        : "Episodio"
                      }
    Si se pasa como argumento 'data' un listado de InfoLabels() con la estructura anterior, muestra los botones
    'Anterior' y 'Siguiente' para ir recorriendo la lista. Ademas muestra los botones 'Aceptar' y 'Cancelar' que
    llamaran a la funcion 'callback' del canal desde donde se realiza la llamada pasandole como parametros el elemento
    actual (InfoLabels()) o None respectivamente.

    @param data: información para obtener datos del scraper.
    @type data: item, InfoLabels, list(InfoLabels)
    @param caption: titulo de la ventana.
    @type caption: str
    @param item: elemento del que se va a mostrar la ventana de información
    @type item: Item
    @param scraper: scraper que tiene los datos de las peliculas o series a mostrar en la ventana.
    @type scraper: Scraper
    """

    from xbmc_info_window import InfoWindow
    return InfoWindow("InfoWindow.xml", config.get_runtime_path()).Start(data, caption=caption, item=item,
                                                                         scraper=scraper)


def show_recaptcha(key, referer):
    from recaptcha import Recaptcha
    return Recaptcha("Recaptcha.xml", config.get_runtime_path()).Start(key, referer)


def alert_no_disponible_server(server):
    # 'El vídeo ya no está en %s' , 'Prueba en otro servidor o en otro canal'
    dialog_ok(config.get_localized_string(30055), (config.get_localized_string(30057) % server),
              config.get_localized_string(30058))


def alert_unsopported_server():
    # 'Servidor no soportado o desconocido' , 'Prueba en otro servidor o en otro canal'
    dialog_ok(config.get_localized_string(30065), config.get_localized_string(30058))


def handle_wait(time_to_wait, title, text):
    logger.info("handle_wait(time_to_wait=%d)" % time_to_wait)
    espera = dialog_progress(' ' + title, "")

    secs = 0
    increment = int(100 / time_to_wait)

    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = ' Espera ' + secs_left + ' segundos para que comience el vídeo...'
        espera.update(percent, ' ' + text, remaining_display)
        xbmc.sleep(1000)
        if espera.iscanceled():
            cancelled = True
            break

    if cancelled:
        logger.info('Espera cancelada')
        return False
    else:
        logger.info('Espera finalizada')
        return True


def get_dialogo_opciones(item, default_action, strm):
    logger.info()
    # logger.debug(item.tostring('\n'))
    from core import servertools

    opciones = []
    error = False

    try:
        item.server = item.server.lower()
    except AttributeError:
        item.server = ""

    if item.server == "":
        item.server = "directo"

    # Si no es el modo normal, no muestra el diálogo porque cuelga XBMC
    muestra_dialogo = (config.get_setting("player_mode") == 0 and not strm)

    # Extrae las URL de los vídeos, y si no puedes verlo te dice el motivo
    # Permitir varias calidades para server "directo"
    if item.video_urls:
        video_urls, puedes, motivo = item.video_urls, True, ""
    else:
        video_urls, puedes, motivo = servertools.resolve_video_urls_for_playing(
            item.server, item.url, item.password, muestra_dialogo)

    seleccion = 0
    # Si puedes ver el vídeo, presenta las opciones
    if puedes:
        for video_url in video_urls:
            opciones.append(config.get_localized_string(30151) + " " + video_url[0])

        if item.server == "local":
            opciones.append(config.get_localized_string(30164))
        else:
            if item.isFavourite:
                # "Quitar de favoritos"
                opciones.append(config.get_localized_string(30154))
            else:
                # "Añadir a favoritos"
                opciones.append(config.get_localized_string(30155))

            if not strm and item.contentType == 'movie':
                # "Añadir a Biblioteca"
                opciones.append(config.get_localized_string(30161))

        if default_action == "3":
            seleccion = len(opciones) - 1

        # Busqueda de trailers en youtube
        if item.channel not in ["Trailer", "ecarteleratrailers"]:
            # "Buscar Trailer"
            opciones.append(config.get_localized_string(30162))

    # Si no puedes ver el vídeo te informa
    else:
        if item.server != "":
            if "<br/>" in motivo:
                dialog_ok("Non è possibile visualizzare questo video perché...", motivo.split("<br/>")[0],
                          motivo.split("<br/>")[1],
                          item.url)
            else:
                dialog_ok("Non è possibile visualizzare questo video perché...", motivo, item.url)
        else:
            dialog_ok("Non è possibile visualizzare questo video perché...", "Il server che lo ospita non è",
                      "ancora supportato da Stefanondemand", item.url)

        if item.channel == "favoritos":
            # "Quitar de favoritos"
            opciones.append(config.get_localized_string(30154))

        if len(opciones) == 0:
            error = True

    return opciones, video_urls, seleccion, error


def set_opcion(item, seleccion, opciones, video_urls):
    logger.info()
    # logger.debug(item.tostring('\n'))
    salir = False
    # No ha elegido nada, lo más probable porque haya dado al ESC
    # TODO revisar
    if seleccion == -1:
        # Para evitar el error "Uno o más elementos fallaron" al cancelar la selección desde fichero strm
        listitem = xbmcgui.ListItem(item.title, iconImage="DefaultVideo.png", thumbnailImage=item.thumbnail)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, listitem)

    # "Quitar de favoritos"
    elif opciones[seleccion] == config.get_localized_string(30154):
        from channels import favoritos
        favoritos.delFavourite(item)
        salir = True

    # "Añadir a favoritos":
    elif opciones[seleccion] == config.get_localized_string(30155):
        from channels import favoritos
        item.from_channel = "favoritos"
        favoritos.addFavourite(item)
        salir = True

    # "Añadir a Biblioteca":  # Library
    elif opciones[seleccion] == config.get_localized_string(30161):
        titulo = item.fulltitle
        if titulo == "":
            titulo = item.title

        new_item = item.clone(title=titulo, action="play_from_library", category="Cine",
                              fulltitle=item.fulltitle, channel=item.channel)

        from core import library
        library.add_pelicula_to_library(new_item)

        salir = True

    # "Buscar Trailer":
    elif opciones[seleccion] == config.get_localized_string(30162):
        config.set_setting("subtitulo", False)
        xbmc.executebuiltin("XBMC.RunPlugin(%s?%s)" %
                            (sys.argv[0], item.clone(channel="trailertools", action="buscartrailer",
                                                     contextual=True).tourl()))
        salir = True

    return salir


def get_video_seleccionado(item, seleccion, video_urls):
    logger.info()
    mediaurl = ""
    view = False
    wait_time = 0
    mpd = False

    # Ha elegido uno de los vídeos
    if seleccion < len(video_urls):
        mediaurl = video_urls[seleccion][1]
        if len(video_urls[seleccion]) > 4:
            wait_time = video_urls[seleccion][2]
            item.subtitle = video_urls[seleccion][3]
            mpd = True
        elif len(video_urls[seleccion]) > 3:
            wait_time = video_urls[seleccion][2]
            item.subtitle = video_urls[seleccion][3]
        elif len(video_urls[seleccion]) > 2:
            wait_time = video_urls[seleccion][2]
        view = True

    # Si no hay mediaurl es porque el vídeo no está :)
    logger.info("mediaurl=" + mediaurl)
    if mediaurl == "":
        if item.server == "unknown":
            alert_unsopported_server()
        else:
            alert_no_disponible_server(item.server)

    # Si hay un tiempo de espera (como en megaupload), lo impone ahora
    if wait_time > 0:
        continuar = handle_wait(wait_time, item.server, "Cargando vídeo...")
        if not continuar:
            mediaurl = ""

    return mediaurl, view, mpd


def set_player(item, xlistitem, mediaurl, view, strm):
    logger.info()
    logger.debug("item:\n" + item.tostring('\n'))

    # Si es un fichero strm no hace falta el play
    if strm:
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xlistitem)
        if item.subtitle != "":
            xbmc.sleep(2000)
            xbmc.Player().setSubtitles(item.subtitle)

    else:
        logger.info("player_mode=%s" % config.get_setting("player_mode"))
        logger.info("mediaurl=" + mediaurl)

        if config.get_setting("player_mode") == 0 or \
                (config.get_setting("player_mode") == 3 and mediaurl.startswith("rtmp")):
            # Añadimos el listitem a una lista de reproducción (playlist)
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            playlist.add(mediaurl, xlistitem)

            # Reproduce
            playersettings = config.get_setting('player_type')
            logger.info("playersettings=%s" % playersettings)

            if config.get_system_platform() == "xbox":
                player_type = xbmc.PLAYER_CORE_AUTO
                if playersettings == 0:
                    player_type = xbmc.PLAYER_CORE_AUTO
                    logger.debug("PLAYER_CORE_AUTO")
                elif playersettings == 1:
                    player_type = xbmc.PLAYER_CORE_MPLAYER
                    logger.debug("PLAYER_CORE_MPLAYER")
                elif playersettings == 2:
                    player_type = xbmc.PLAYER_CORE_DVDPLAYER
                    logger.debug("PLAYER_CORE_DVDPLAYER")

                xbmc_player = xbmc.Player(player_type)
            else:
                xbmc_player = xbmc.Player()

            xbmc_player.play(playlist, xlistitem)

        elif config.get_setting("player_mode") == 1:
            logger.info("mediaurl :" + mediaurl)
            logger.info("Tras setResolvedUrl")
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=mediaurl))

        elif config.get_setting("player_mode") == 2:
            xbmc.executebuiltin("PlayMedia(" + mediaurl + ")")

    # TODO MIRAR DE QUITAR VIEW
    if item.subtitle != "" and view:
        logger.info("Subtítulos externos: " + item.subtitle)
        xbmc.sleep(2000)
        xbmc.Player().setSubtitles(item.subtitle)

    # si es un archivo de la biblioteca enviar a marcar como visto
    if strm or item.strm_path:
        from platformcode import xbmc_library
        xbmc_library.mark_auto_as_watched(item)