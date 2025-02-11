# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# stefano 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of stefano 5.
#
# stefano 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# stefano 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with stefano 5.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Logger (kodi)
# --------------------------------------------------------------------------------

import inspect
import os

import xbmc
from core import config

loggeractive = (config.get_setting("debug") is True)


def log_enable(active):
    global loggeractive
    loggeractive = active


def encode_log(message=""):
    # Unicode to utf8
    if type(message) == unicode:
        message = message.encode("utf8")

    # All encodings to utf8
    elif type(message) == str:
        message = unicode(message, "utf8", errors="replace").encode("utf8")

    # Objects to string
    else:
        message = str(message)

    return message


def get_caller(message=None):
    module = inspect.getmodule(inspect.currentframe().f_back.f_back)

    # En boxee en ocasiones no detecta el modulo, de este modo lo hacemos manual
    if module is None:
        module = ".".join(os.path.splitext(inspect.currentframe().f_back.f_back.f_code.co_filename.split("Stefano")[1])[0].split(os.path.sep))[1:]
    else:
        module = module.__name__

    function = inspect.currentframe().f_back.f_back.f_code.co_name

    if module == "__main__":
        module = "Stefano"
    else:
        module = "Stefano." + module
    if message:
        if module not in message:
            if function == "<module>":
                return module + " " + message
            else:
                return module + " [" + function + "] " + message
        else:
            return message
    else:
        if function == "<module>":
            return module
        else:
            return module + "." + function


def info(texto=""):
    if loggeractive:
        xbmc.log(get_caller(encode_log(texto)), xbmc.LOGNOTICE)


def debug(texto=""):
    if loggeractive:
        texto = "    [" + get_caller() + "] " + encode_log(texto)

        xbmc.log("######## DEBUG #########", xbmc.LOGNOTICE)
        xbmc.log(texto, xbmc.LOGNOTICE)


def error(texto=""):
    texto = "    [" + get_caller() + "] " + encode_log(texto)

    xbmc.log("######## ERROR #########", xbmc.LOGERROR)
    xbmc.log(texto, xbmc.LOGERROR)
