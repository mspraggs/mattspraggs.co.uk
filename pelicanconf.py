#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Matt Spraggs'
SITENAME = 'Matt Spraggs'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
CATEGORY_FEED_RSS = 'feeds/{slug}.rss.xml'

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (
    ('linkedin.png', 'https://www.linkedin.com/in/matt-spraggs'),
    ('github.png', 'https://github.com/mspraggs/'),
    ('rss.png', f'{SITEURL}/feeds/matt-spraggs.rss.xml'),
)

SITEMAP = {
    'exclude': ['drafts/'],
}

DEFAULT_PAGINATION = 10
SUMMARY_MAX_LENGTH = 150

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = '.'

STRAPLINE = 'Software engineer. Ex-physicist. Funny surname.'

AUTHOR_SAVE_AS = ''

PLUGIN_PATHS = ['plugins']
PLUGINS = [
    'read_more_link',
    'sort_tags',
    'pelican.plugins.sitemap',
]

# "Read more" link configuration
SUMMARY_MAX_LENGTH = 150
READ_MORE_LINK_TEXT = '<span>Read more</span>'
READ_MORE_LINK_TEMPLATE = (
    '<a class="read-more" href="{{ url }}">{{ text }}</a>'
)
