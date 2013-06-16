# -*- coding: utf-8 -*-

import os
import datetime
from contextlib import contextmanager
from functools import wraps

from bottle import request
from jinja2 import Environment, FileSystemLoader
import PyRSS2Gen

from models import Tag, Post, session, now

from paper.settings import (BLOG_TITLE,
                            STATIC_FILE_VERSION,
                            GITHUB_LINK,
                            DOMAIN,
                            )

if not DOMAIN.endswith('/'):
    DOMAIN = "%s/" % DOMAIN


__all__ = ['jinja_view', 'key_verified', 'session_context']

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(CURRENT_PATH)
STATIC_PATH = os.path.join(PROJECT_PATH, 'static')
TEMPLATES_PATH = os.path.join(PROJECT_PATH, 'templates')
KEY_PATH = os.path.join(CURRENT_PATH, '_key')

env = Environment(loader = FileSystemLoader(TEMPLATES_PATH))

def format_date(value, f="%b %d, %Y"):
    return datetime.datetime.strftime(value, f)

env.filters['format_date'] = format_date



@contextmanager
def session_context():
    try:
        yield session
    except Exception:
        raise
    finally:
        session.close()



def blog_context():
    data = {
        'blog_title': BLOG_TITLE,
        'title': BLOG_TITLE,
        'ver': STATIC_FILE_VERSION,
        'github_link': GITHUB_LINK
    }
    
    # TODO cache the tags
    with session_context() as session:
        data['tags'] = session.query(Tag).order_by(Tag.name.asc())
    
    return data
    


def jinja_view(tpl, **kwargs):
    _kwargs = kwargs
    
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            data = blog_context()
            data.update(_kwargs)
            data.update(result)
            
            template = env.get_template(tpl)
            return template.render(**data)
        return wrapper
    return deco


def forbid(**kwargs):
    lower_key_kwargs = {}
    for k, v in kwargs.items():
        lower_key_kwargs[k.lower()] = v
        
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'referer' in lower_key_kwargs:
                if request.get_header('Referer', '').startswith(
                    lower_key_kwargs['referer']):
                    return ''
            return func(*args, **kwargs)
        return wrapper
    return deco
        


        

def key_verified(key):
    with open(KEY_PATH, 'r') as f:
        data = f.read()
        
    data = data.strip('\n')
    key = key.strip('\n')
    return key == data




def make_rss():
    with session_context() as session:
        posts = session.query(Post).order_by(Post.create_at.desc())
    def _make_item(p):
        return PyRSS2Gen.RSSItem(
            title = p.title,
            link = '%sblog/%s' % (DOMAIN, p.title),
            description = p.content[:200],
            pubDate = p.create_at
        )
    items = [_make_item(p) for p in posts]

    rss = PyRSS2Gen.RSS2(
        title = BLOG_TITLE,
        link = DOMAIN + 'atom.rss',
        lastBuildDate = now(),
        description = "The blog feeds of %s" % BLOG_TITLE,
        items = items
    )
    with open(os.path.join(STATIC_PATH, 'atom.rss'), 'w') as f:
        rss.write_xml(f)
