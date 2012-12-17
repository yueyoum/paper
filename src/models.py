# -*- coding: utf-8 -*-

import datetime


from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy.dialects.mysql import (
            INTEGER, DATETIME, VARCHAR, TEXT
        )


from paper.settings import DEBUG, MYSQL, TIME_DELTA

MYSQL_HOST = MYSQL['HOST']
MYSQL_PORT = MYSQL['PORT']
MYSQL_TABLE = MYSQL['TABLE']
MYSQL_USER = MYSQL['USER']
MYSQL_PASSWORD = MYSQL['PASSWORD']

__all__ = ['get_session', 'Tag', 'Post']


engine = create_engine(
    'mysql://%s:%s@%s:%d/%s?charset=utf8' % (
        MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_TABLE
    ),
    echo = DEBUG
)


def get_session():
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session()


Base = declarative_base()





class ModelSettings(type):
    """as metaclass, adding table settings and methods"""
    
    def __new__(cls, name, parent, class_dict):
        __tablename__ = name.lower()
        __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        }
        
        if '__tablename__' not in class_dict:
            class_dict['__tablename__'] = __tablename__
        if '__table_args__' not in class_dict:
            class_dict['__table_args__'] = __table_args__
            
            
        @classmethod
        def exists(cls, session, **kwargs):
            if not kwargs:
                raise Exception("Need kwargs")
            
            conditions = kwargs.items()
            # TODO: support multi-conditions
            name, value = conditions[0]
            print name, value
            query = session.query(getattr(cls, name)).filter(
                getattr(cls, name) == value)
            return query.count() > 0
        
        class_dict['exists'] = exists
            
        return type(name, parent, class_dict)
    



post_tags = Table('post_tags', Base.metadata,
    Column('post_id', INTEGER, ForeignKey('post.id')),
    Column('tag_id', INTEGER, ForeignKey('tag.id'))
)


class Tag(Base):
    __metaclass__ = ModelSettings
    
    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(20), unique=True)
    posts_count = Column(INTEGER, nullable=False)
    
    def __init__(self, name):
        self.name = name.lower()
        self.posts_count = 1
        
    def __repr__(self):
        name = self.name
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        return '<Tag (%s)>' % self.name




class Post(Base):
    __metaclass__ = ModelSettings
    
    id = Column(INTEGER, primary_key=True)
    title = Column(VARCHAR(60), nullable=False, unique=True)
    content = Column(TEXT, nullable=False)
    view_count = Column(INTEGER, nullable=False)

    create_at = Column(DATETIME, nullable=False)
    update_at = Column(DATETIME)
    
    tags = relationship('Tag', secondary=post_tags, backref='posts')
    
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.view_count = 0

    def __repr__(self):
        title = self.title
        if isinstance(title, unicode):
            title = title.encode('utf-8')
        return '<Blog (%s)>' % title





def set_post_create_time(mapper, connections, instance):
    now = datetime.datetime.now()
    if TIME_DELTA > 0:
        _now = now + datetime.timedelta(hours=TIME_DELTA)
    elif TIME_DELTA < 0:
        _now = now - datetime.timedelta(hours=abs(TIME_DELTA))
    else:
        _now = now
    
    instance.create_at = _now
    instance.update_at = instance.create_at


event.listen(Post, 'before_insert', set_post_create_time)


def sync():
    Base.metadata.create_all(engine)
