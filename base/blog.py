from config import db, app
from datetime import datetime
from slugify import slugify
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

ROLE_USER = 0
ROLE_ADMIN = 1



# blog models
blog_blocks = db.Table('blog_page_blocks',
    db.Column('page_id',  db.Integer, db.ForeignKey('blog_page_item.id')),
    db.Column('block_id', db.Integer, db.ForeignKey('blog_block_item.id')),
    db.Column('place',    db.String())
)

class BlogCategory(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    pages = db.relationship('BlogPageItem')
    visible = db.Column(db.Integer())
    def __get_children__(self):
        return BlogPageItem.query.filter(BlogPageItem.category_id==self.id).all()
    def __init__(self,name):
        self.visible = 1
        self.name = name

class BlogPageItem(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    url  = db.Column(db.String())
    meta = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'), nullable=True)
    blocks = db.relationship('BlogBlockItem',secondary=blog_blocks,backref=db.backref('BlogPageItem'),order_by="BlogBlockItem.order")

    def __to_dict__(self):
        category = self.category_id
        result = {}
        result['id'] =     self.id
        result['meta'] =   self.meta
        result['url'] =    self.url
        result['subitems'] = [i.__to_dict__() for i in self.blocks]
        result['category_id'] = self.category_id 
        result['category_name'] = BlogCategory.query.get(self.category_id).name if self.category_id else False
        return result

    def __init__(self,url,meta):
        if not url: url = '123213'
        if not meta: meta = ''
        self.url = url
        self.meta =  meta



class BlogBlockItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_block_item.id'), nullable=True)
    type = db.Column(db.String(255))
    data = db.Column(db.String())
    order = db.Column(db.Integer, nullable=True)
    subitems = db.relationship('BlogBlockItem',cascade="all,delete",remote_side=[parent_id],order_by="BlogBlockItem.order")

    def __get_page__(self,item=False):
        if not item: item = self
        while item and not item.BlogPageItem and item.parent_id: item=BlogBlockItem.query.get(item.parent_id)
        if not item.BlogPageItem:
            item.subitems=[]
            db.session.delete(item)
            return False
        return item.BlogPageItem[0]

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
