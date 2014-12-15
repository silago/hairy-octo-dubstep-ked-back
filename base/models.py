from config import db, app
from datetime import datetime
from slugify import slugify
import json

ROLE_USER = 0
ROLE_ADMIN = 1




#class MenuItem(db.Model):
#    id = db.Column(db.Integer, primary_key = True)
#    parent_id = db.Column(db.Integer,db.ForeignKey('menu_item.id'), nullable=True)
#    title = db.Column(db.String(255))
#    url = db.Column(db.String(255))
#    #subitems = db.relationship('MenuItem',backref='parent',lazy='select')
#    subitems = db.relationship('MenuItem', cascade="all,delete", remote_side=[parent_id])
#
#    def __to_dict__(self):
#        return dict({'id':self.id, 'parent_id':self.parent_id,'title':self.title,'url':self.url,'subitems':[sub.__to_dict__() for sub in self.subitems]})
#
#    def __init__(self,parent_id,title,url):
#        self.parent_id = parent_id
#        self.title   = title
#        self.url   = url
#
#    def __repr__(self):
#        return '<MenuItem %r>' % self.title



blocks = db.Table('page_blocks',
    db.Column('page_id',  db.Integer, db.ForeignKey('page_item.id')),
    db.Column('block_id', db.Integer, db.ForeignKey('block_item.id')),
    db.Column('place',    db.String())
)

class BlockItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('block_item.id'), nullable=True)
    type = db.Column(db.String(255))
    data = db.Column(db.String())
    order = db.Column(db.Integer, nullable=True)
    subitems = db.relationship('BlockItem',cascade="all,delete",remote_side=[parent_id])

    def __get_children__(self):
        return [sub.__to_dict__() for sub in self.subitems]
    def __to_dict__(self):
        return dict({'id':self.id, 'parent_id':self.parent_id,'type':self.type,'data':json.loads(self.data),'subitems':self.__get_children__(),'order':self.order})

    def __init__(self, parent_id, type, data):
        self.parent_id = parent_id
        self.type = type
        self.data = data

    def __repr__(self):
        return "<block %r>" % self.id

class UserItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    role_id  = db.Column(db.Integer)
    session_key = db.Column(db.String, unique=True)
    def is_active(self):
        return True
    def get_id(self):
        return self.id
    # 1 = admin, 2 = moderator

class PageItem(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    url  = db.Column(db.String(), unique=True)
    meta = db.Column(db.String())
    blocks = db.relationship('BlockItem',secondary=blocks)

    def __init__(self,url,meta):
        self.url = url
        self.meta =  meta
    #block_id = db.Column(db.Integer, db.ForeignKey('block_item.id'),nullable=True)

#class PageBlock(db.Model):
#    id = db.Column(db.Integer,primary_key = True)
#    page_id = db.Column(db.ForeignKey('page_item.id'))
#    block_id = db.Column(db.ForeignKey('block_item.id'))
#    place    = db.Column(db.String())
#    blocks = db.relationship('BlockItem')


