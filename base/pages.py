
from config import db, app
from datetime import datetime
from config import slugify
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

ROLE_USER = 0
ROLE_ADMIN = 1

blocks = db.Table('page_blocks',
    db.Column('page_id',  db.Integer, db.ForeignKey('page_item.id')),
    db.Column('block_id', db.Integer, db.ForeignKey('block_item.id')),
    db.Column('place',    db.String())
)

class BlockItem(db.Model):
    id    = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('block_item.id'), nullable=True)
    type  = db.Column(db.String(255))
    data  = db.Column(db.String())
    order = db.Column(db.Integer, nullable=True)
    lang  = db.Column(db.Integer, nullable=True, default='ru')
    subitems = db.relationship('BlockItem',cascade="all,delete",remote_side=[parent_id],order_by="BlockItem.order")

    def __get_page__(self,item=False):
        if not item: item = self
        while item and not item.PageItem and item.parent_id: item=BlockItem.query.get(item.parent_id)
        if not item.PageItem:
            item.subitems=[]
            db.session.delete(item)
            return False
        return item.PageItem[0]

    def __get_children__(self):
        return [sub.__to_dict__() for sub in self.subitems]
    def __to_dict__(self):
        return dict({'id':self.id, 'parent_id':self.parent_id,'type':self.type,'data':json.loads(self.data),'subitems':self.__get_children__(),'order':self.order})

    def __init__(self, parent_id, type, data,lang):
        self.parent_id = parent_id
        self.lang = lang
        self.type = type
        self.data = data

    def __repr__(self):
        return "<block %r>" % self.id


class PageItem(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    url  = db.Column(db.String(), unique=True)
    meta = db.Column(db.String())
    blocks = db.relationship('BlockItem',secondary=blocks,backref=db.backref('PageItem'),order_by="BlockItem.order")

    def __to_dict__(self,lang='ru'):
        result = {}
        result['id'] =     self.id
        result['meta'] =   json.loads(self.meta)
        result['url'] =    self.url
        result['subitems'] = [i.__to_dict__() for i in self.blocks if i.lang == lang]
        return result

    def __init__(self,url,meta):
        self.url = url
        self.meta =  meta
