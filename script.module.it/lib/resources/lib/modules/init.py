# -*- coding: utf-8 -*-

'''
#:::::::::::::::::::::#
#:'######':'########':#
#::: ## :::::: ## ::::#
#:.. ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#::: ## :::::: ## ::::#
#: ###### :::: ## ::::#
#:::::::::::::::::::::#

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
'''

import urlparse, sys

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
name = params.get('name')
title = params.get('title')
year = params.get('year')
imdb = params.get('imdb')
tvdb = params.get('tvdb')
tmdb = params.get('tmdb')
season = params.get('season')
episode = params.get('episode')
tvshowtitle = params.get('tvshowtitle')
premiered = params.get('premiered')
url = params.get('url')
image = params.get('image')
meta = params.get('meta')
sub = params.get('sub')
select = params.get('select')
query = params.get('query')
source = params.get('source')
content = params.get('content')
rtype = params.get('rtype')
content_type = params.get('content_type')

windowedtrailer = params.get('windowedtrailer')
windowedtrailer = int(windowedtrailer) if windowedtrailer in ('0', '1') else 0
