# -*- coding: utf-8 -*-

import os
import datetime
import itertools
import functools


from bottle import Bottle, request, redirect, response
from sqlalchemy.orm import subqueryload

from pygments.lexers import ClassNotFound

from models import Tag, Post
from convert import Convert
from utils import jinja_view, key_verified, session_context, forbid

from paper.settings import DEBUG


app = Bottle()



def no_cache(func):
    @functools.wraps(func)
    def deco(*args, **kwargs):
        response.set_header('Cache-Control', 'no-cache')
        return func(*args, **kwargs)
    return deco
    



format_time = lambda t, f: datetime.datetime.strftime(t, f)
get_year = functools.partial(format_time, f='%Y')
get_month = functools.partial(format_time, f='%B')


def group_posts(items):
    """group items with year and month"""
    
    def _year(items):
        return itertools.groupby(items, lambda a: get_year(a.create_at))
    
    def _month(items):
        return itertools.groupby(items, lambda a: get_month(a.create_at))
    
    groupby_year = _year(items)
    groupby_year_month = ((year, _month(items)) for year, items in groupby_year)
    return groupby_year_month
    


@app.get('/')
@no_cache
@jinja_view('index.html')
def index():
    with session_context() as session:
        posts = session.query(Post).order_by(Post.create_at.desc()).limit(2)
        
    return {'posts': posts, 'index': True}
    
    
    
    
    
@app.get('/archive')
@no_cache
@jinja_view('archive.html')
def archive():
    with session_context() as session:
        posts = session.query(Post).order_by(Post.create_at.desc())
        
    posts = group_posts(posts)
    return {'posts': posts}
    
    
    

@app.get('/tag/<tag>')
@no_cache
@jinja_view('archive.html')
def filter_by_tag(tag):
    with session_context() as session:
        posts = session.query(Post).filter(Post.tags.any(Tag.name==tag)
                                        ).order_by(Post.create_at.desc())
    
    posts = group_posts(posts)
    return {'posts': posts}
    
    
    
@app.get('/blog/<title>')
@forbid(referer='http://disqus.com')
@jinja_view('post.html')
def show_post(title):
    with session_context() as session:
        post = session.query(Post).options(
            subqueryload(Post.tags)
        ).filter(Post.title == title)
        
        if post.count() < 1:
            redirect('/')
            
        post = post.one()
        post.view_count += 1
        session.commit()
    
    return {'post': post, 'title': post.title}



@app.get('/about')
@jinja_view('about.html')
def about():
    return {'title': 'about'}




def edit_post(session, post_obj, content, tags):
    if not isinstance(tags, (list, tuple)):
        tags = [tags]
        
    new_tags = tags
    
    old_tags = [t.name for t in post_obj.tags]
    new_tags, old_tags = set(new_tags), set(old_tags)
    
    removed_tags = old_tags - new_tags
    added_tags = new_tags - old_tags
    
    def _get_tag_obj(name):
        obj = session.query(Tag).filter(Tag.name == name)
        if obj.count() == 0:
            return None
        return obj.one()
    
    for t in removed_tags:
        t_obj = _get_tag_obj(t)
        post_obj.tags.remove( t_obj )
        # if this tag's count == 1, then delete this tag
        if t_obj.posts_count < 2:
            session.delete(t_obj)
        
    for t in added_tags:
        t_obj = _get_tag_obj(t)
        if t_obj is None:
            # new tag
            t_obj = Tag(t)
        else:
            # increase exists tag's posts_count
            t_obj.posts_count += 1
        post_obj.tags.append( t_obj )
    
    post_obj.content = content
    
    



def store_new_post(session, title, content, tags):
    p = Post(title, content)
    
    if not isinstance(tags, (list, tuple)):
        tags = [tags]
        
    def _get_tag_obj(tag):
        t = session.query(Tag).filter(Tag.name == tag)
        if t.count() > 0:
            # this tag already exists, increase `posts_count`
            t = t.one()
            t.posts_count += 1
        else:
            # new tag
            t = Tag(tag)
            
        return t
    
    tags = filter(lambda t: '#' not in t, tags)
    p.tags = [_get_tag_obj(t) for t in tags]
    session.add(p)



@app.post('/blog/new')
def new_post():
    key = request.forms.get('key')
    
    if not key_verified(key):
        return 'Verify Failured, Key Error!\n'
    
    filename = request.forms.get('filename')
    content = request.forms.get('content')
    
    filename = os.path.basename(filename)
    title, ext = os.path.splitext(filename)
    ext = ext.lstrip('.')
    
    try:
        tags_str, content = content.split('\n', 1)
        tags_str = tags_str.split(':')[-1]
        tags = [t.strip() for t in tags_str.split(',')]
    except:
        return 'Invalid content!\n'
    
    try:
        c = Convert(ext)
    except NotImplementedError:
        return 'This format not supported yet!\n'
    except Exception:
        return 'Error occurred!\n'
    
    try:
        html = c.convert(content)
    except ClassNotFound, e:
        return 'ClassNotFound, %s\n' % str(e)
    
    with session_context() as session:
        p = session.query(Post).filter(Post.title == title)
        if p.count() > 0:
            # update
            edit_post(session, p.one(), html, tags)
        else:
            # new blog
            store_new_post(session, title, html, tags)
            
        session.commit()
    
    return 'Done\n'


if DEBUG:
    from bottle import static_file
    PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    @app.get('/static/<filepath:path>')
    def static_files(filepath):
        return static_file(filepath, root=PROJECT_PATH + '/static')

