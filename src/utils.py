# -*- coding: utf-8 -*-

import os
import datetime
from contextlib import contextmanager
from functools import wraps

from bottle import request
from jinja2 import Environment, FileSystemLoader

from models import Tag, get_session

from paper.settings import (BLOG_TITLE,
                            STATIC_FILE_VERSION,
                            GITHUB_LINK,
                            DOUBAN_BOOK_LINK,
                            )


__all__ = ['jinja_view', 'key_verified',]

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(CURRENT_PATH)
TEMPLATES_PATH = os.path.join(PROJECT_PATH, 'templates')
KEY_PATH = os.path.join(CURRENT_PATH, '_key')

env = Environment(loader = FileSystemLoader(TEMPLATES_PATH))

def format_date(value, f="%b %d, %Y"):
    return datetime.datetime.strftime(value, f)

env.filters['format_date'] = format_date



@contextmanager
def session_context():
    s = get_session()
    try:
        yield s
    except Exception:
        raise
    finally:
        s.close()



def blog_context():
    data = {
        'blog_title': BLOG_TITLE,
        'title': BLOG_TITLE,
        'douban_book_link': DOUBAN_BOOK_LINK,
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
