# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # # -*- coding: UTF-8 -*-
'''
    A Resource for SelflessLive.

    Updated and refactored by someone.
    Originally created by others.
'''

 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Selfless Live
# Addon id: plugin.video.selfless
# Addon Provider: Kodi Ghost

import time
import cProfile
import StringIO
import pstats
import json
import xbmc
from resources.lib.modules import control
from xbmc import LOGDEBUG, LOGERROR, LOGFATAL, LOGINFO, LOGNONE, LOGNOTICE, LOGSEVERE, LOGWARNING  # @UnusedImport

name = control.addonInfo('name')


def log(msg, level=LOGDEBUG):
    req_level = level
    # override message level to force logging when addon logging turned on
    if control.setting('addon_debug') == 'true' and level == LOGDEBUG:
        level = LOGNOTICE

    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('[%s] %s' % (name, msg), level)

    except Exception as e:
        try:
            xbmc.log('Logging Failure: %s' % (e), level)
        except:
            pass  # just give up


class Profiler(object):
    def __init__(self, file_path, sort_by='time', builtins=False):
        self._profiler = cProfile.Profile(builtins=builtins)
        self.file_path = file_path
        self.sort_by = sort_by

    def profile(self, f):
        def method_profile_on(*args, **kwargs):
            try:
                self._profiler.enable()
                result = self._profiler.runcall(f, *args, **kwargs)
                self._profiler.disable()
                return result
            except Exception as e:
                log('Profiler Error: %s' % (e), LOGWARNING)
                return f(*args, **kwargs)

        def method_profile_off(*args, **kwargs):
            return f(*args, **kwargs)

        if _is_debugging():
            return method_profile_on
        else:
            return method_profile_off

    def __del__(self):
        self.dump_stats()

    def dump_stats(self):
        if self._profiler is not None:
            s = StringIO.StringIO()
            params = (self.sort_by,) if isinstance(self.sort_by, basestring) else self.sort_by
            ps = pstats.Stats(self._profiler, stream=s).sort_stats(*params)
            ps.print_stats()
            if self.file_path is not None:
                with open(self.file_path, 'w') as f:
                    f.write(s.getvalue())


def trace(method):
    def method_trace_on(*args, **kwargs):
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        log('{name!r} time: {time:2.4f}s args: |{args!r}| kwargs: |{kwargs!r}|'.format(name=method.__name__, time=end - start, args=args, kwargs=kwargs), LOGDEBUG)
        return result

    def method_trace_off(*args, **kwargs):
        return method(*args, **kwargs)

    if _is_debugging():
        return method_trace_on
    else:
        return method_trace_off


def _is_debugging():
    command = {'jsonrpc': '2.0', 'id': 1, 'method': 'Settings.getSettings', 'params': {'filter': {'section': 'system', 'category': 'logging'}}}
    js_data = execute_jsonrpc(command)
    for item in js_data.get('result', {}).get('settings', {}):
        if item['id'] == 'debug.showloginfo':
            return item['value']

    return False


def execute_jsonrpc(command):
    if not isinstance(command, basestring):
        command = json.dumps(command)
    response = control.jsonrpc(command)
    return json.loads(response)
