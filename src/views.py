# -*- coding: utf-8 -*-

import os
import datetime
import itertools
import functools


from bottle import Bottle, request, redirect

from models import Tag, Post, session
from convert import Convert
from utils import jinja_view, key_verified

from paper.settings import DEBUG



app = Bottle()



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
@jinja_view('index.html')
def index():
    posts = session.query(Post).order_by(Post.create_at.desc())
    posts = group_posts(posts)
    return {'posts': posts}
    
    

@app.get('/tag/<tag>')
@jinja_view('index.html')
def filter_by_tag(tag):
    posts = session.query(Post).filter(Post.tags.any(Tag.name==tag)
                                    ).order_by(Post.create_at.desc())
    
    posts = group_posts(posts)
    return {'posts': posts}
    
    
    
@app.get('/blog/<title>')
@jinja_view('post.html')
def show_post(title):
    post = session.query(Post).filter(Post.title == title)
    if post.count() < 1:
        redirect('/')
        
    post = post.one()
    post.view_count += 1
    session.commit()
    
    return {'post': post}



@app.get('/about')
@jinja_view('about.html')
def about():
    return {}




def edit_post(session, post_obj, content, tags):
    #if not isinstance(tags, (list, tuple)):
    #    tags = [tags]
    #    
    #new_tags = tags
    #
    #old_tags = [t.name for t in post_obj.tags]
    #new_tags, old_tags = set(new_tags), set(old_tags)
    #
    #removed_tags = old_tags - new_tags
    #added_tags = new_tags - old_tags
    
    # TODO, tag changes
    
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
    print key
    
    if not key_verified(key):
        return 'Verify Failured, Key Error!\n'
    
    filename = request.forms.get('filename')
    content = request.forms.get('content')
    
    title, ext = os.path.splitext(filename)
    ext = ext.lstrip('.')
    
    tags_str, content = content.split('\n', 1)
    tags_str = tags_str.split(':')[-1]
    tags = [t.strip() for t in tags_str.split(',')]
    
    try:
        c = Convert(ext)
    except NotImplementedError:
        return 'This format not supported yet!\n'
    except Exception:
        return 'Error occurred!\n'
    
    html = c.convert(content)
    
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

