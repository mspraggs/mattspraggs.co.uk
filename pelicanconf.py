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
    ('facebook.png', 'https://www.facebook.com/matthew.spraggs'),
    ('twitter.png', 'https://twitter.com/Orentago'),
    ('linkedin.png', 'https://www.linkedin.com/in/matthew-spraggs-990725a2'),
    ('github.png', 'https://github.com/mspraggs/'),
    ('rss.png', f'{SITEURL}/feeds/matt-spraggs.rss.xml'),
)

DEFAULT_PAGINATION = 10
SUMMARY_MAX_LENGTH = 150

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = '.'

STRAPLINE = 'Software engineer. Ex-physicist. Funny surname.'

AUTHOR_SAVE_AS = ''