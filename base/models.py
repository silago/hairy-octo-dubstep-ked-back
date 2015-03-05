from config import db, app
from datetime import datetime
from slugify import slugify
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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


#0 - нет доступа, 1-чтение (read), 2->read/wrtie
rights = db.Table('group_rights',
    db.Column('group_id',  db.Integer, db.ForeignKey('group_item.id')),
    db.Column('view_id', db.Integer, db.ForeignKey('view_item.id')),
)


similar = db.Table('groups_similar',
    db.Column('group_id',  db.Integer, db.ForeignKey('group_catalog_item.id')),
    db.Column('similar_group_id', db.Integer, db.ForeignKey('group_catalog_item.id')),
)

#class RightsGroupsItem(db.Model):
#    group_id = db.Column(db.ForeignKey('group_item.id')),
#    view_name = db.Column(db.ForeignKey('view_item.name')),
#    access_level = db.Column(db.Integer())


#"base image","thumbnail","small image","SKU","Цвет","Материал верха","Подкладка","analpa_razmer","Стелька","Сегмент","Сезон","год","Марка","Тип","status (активность)"

class ItemRating(db.Model):
    __tablename__="item_rating"
    id = db.Column(db.ForeignKey("side_catalog_item.sku"),primary_key=True)
    voters = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    def update_rating(self,rating):
        self.voters+=1
        self.rating+=rating
        return self.rating/float(self.voters)
        #self.rating = (self.rating*self.voters
    def get_rating(self):
        return self.rating/float(self.voters)

    def __init__(self,id,rating):
        self.id = id
        self.rating = 5
        self.voters = 0;

class GroupCatalogItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    info = db.Column(db.String(255))
    alias = db.Column(db.String(255))
    items = db.relationship('CatalogItem',backref='group')
    similar = db.relationship('GroupCatalogItem',secondary=similar,primaryjoin=id==similar.c.group_id, secondaryjoin=id==similar.c.similar_group_id)
    def __get_similar(self):
        return [[s.__to_dict__() for s in i.items] for i in self.similar]

    def __get_children__(self):
        return [i.__to_dict__() for i in CatalogItem.query.filter(CatalogItem.group_catalog_id==self.id).all()]

    def __init__(self,info):
        self.alias = ''    
        self.info = info
    def __to_dict__(self):
        return {'id':self.id,'info':self.info,'alias':self.alias,'items':self.__get_children__(),'similar':self.__get_similar()}

class SideCatalogGroup(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    parent_id = db.Column(db.Integer(),nullable=True)
    name =      db.Column(db.String(),nullable=True) 
    active  =   db.Column(db.Integer())
    description = db.Column(db.String(),nullable=True)
    after_menu  = db.Column(db.String(),nullable=True)
    
    def __init__(self,id,parent_id,name):
        self.active = 1
        self.id, self.parent_id,self.name = id,parent_id,name

class SideCatalogAttributes(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    entity_type_id = db.Column(db.Integer())
    attribute_code = db.Column(db.String())
    frontend_label = db.Column(db.String())

class SideCatalogProperties(db.Model):
    value_id = db.Column(db.Integer(),primary_key=True)
    option_id = db.Column(db.Integer())
    value = db.Column(db.String())
    attribute_id = db.Column(db.Integer())
    attribute_code = db.Column(db.String())

class SideCatalogItemImage(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    item_id = db.Column(db.ForeignKey('side_catalog_item.id'))
    url     = db.Column(db.String())
    def __init__(self,item_id,url):
        self.item_id,self.url = item_id,url

class SideCatalogItem(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    sku = db.Column(db.String())
    data = db.Column(db.String())
    images = db.relationship('SideCatalogItemImage')
    rating = db.relationship('ItemRating',primaryjoin=sku==ItemRating.id, uselist=False)
    def __init__(self,id,sku,data):
        self.id,self.sku,self.data = id,sku,data
    def __to_dict__(self):
        return {'id':self.id,'sku':self.sku,'data':json.loads(self.data),'images':[i.url for i in self.images]}

class CatalogItem(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    base_image     =db.Column(db.String(255))
    sku            =db.Column(db.String(255))
    color          =db.Column(db.String(255))
    material_top   =db.Column(db.String(255))
    lining         =db.Column(db.String(255))
    analpa_size    =db.Column(db.String(255))
    insole         =db.Column(db.String(255))
    segment        =db.Column(db.String(255))
    season         =db.Column(db.String(255))
    mark           =db.Column(db.String(255))
    item_type      =db.Column(db.String(255))
    created_time   =db.Column(db.DateTime()) 
    group_catalog_id = db.Column(db.ForeignKey('group_catalog_item.id'),nullable=True)
    coll_status    =db.Column(db.Integer,nullable=True,default=0)
    #image_1 =db.Column(db.String(255))
    image_2 =db.Column(db.String(255))
    image_3 =db.Column(db.String(255))
    #rating = db.relationship('ItemRating',primaryjoin=sku==ItemRating.id, uselist=False)

    def __init__(self,date,season,dic):
        self.created_time = date #datetime.now()
        self.season       = season
        for k,v in dic.items():
            attr = self.__get_csv_association(k)
            if (attr):
                setattr(self,attr,v )
    
    def __to_dict__(self):
        result = {k:str(v) for k,v in  vars(self).items() if k[0]!='_'}
        #result['rating'] = self.rating.get_rating() if self.rating else 5
        return result
            
        #return { k:getattr(self,k) for k,v in vars(self).items()}

    def __get_csv_association(self,key):
        csv_keys = {
                "image_1":"base_image",
                "image_2":"image_2",
                "image_3":"image_3",
                "SKU":"sku",
                "Артикул (SKU)":"sku",
                "Цвет":"color",
                "Материал верха":"material_top",
                "Материал подкладки":"lining",
                "Подкладка":"lining",
                "analpa_razmer":"analpa_size",
                "Размер":"analpa_size",
                "Стелька":"insole",
                "Сегмент":"segment",
                "Сезон":"season",
                "год":"year",
                "Марка":"mark",
                "Тип":"item_type",
                "Тип обуви":"item_type",
                "status":"status"
                }
        if (key in csv_keys):
            return csv_keys[key]
        else:
            return None

class ViewItem(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    method = db.Column(db.String(255))
    def __init__(self,name,method):
        self.name = name
        self.method = method


class GroupItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255),unique=True)
    rights= db.relationship('ViewItem',secondary=rights)

class UserItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    role_id  = db.Column(db.Integer)
    #role_id = db.Column(db.ForeignKey('group_item.id'),nullable=True)
    session_key = db.Column(db.String, unique=True)
    def __init__(self,username,password,role_id):
        self.username = username
        self.password = password
        self.role_id = role_id

    def __to_dict__(self):
      return {'id':self.id, 'username':self.username,'role_id':self.role_id}
    def is_anonymous(self):
      if self.id: return False
      else: return True
    def is_authenticated(self):
      return True

    def is_active(self):
        return True
    def get_id(self):
        return self.id
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'id':self.id}).decode('utf-8')
    # 1 = admin, 2 = moderator


class CategoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(255), unique=True)
    parent_id = db.Column(db.ForeignKey('category_item.id'),nullable=True)
    name  = db.Column(db.String(255))

class ArtikulItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(255))
    data  = db.Column(db.String())
    category_id = db.Column(db.ForeignKey('category_item.id'))


blocks = db.Table('page_blocks',
    db.Column('page_id',  db.Integer, db.ForeignKey('page_item.id')),
    db.Column('block_id', db.Integer, db.ForeignKey('block_item.id')),
    db.Column('place',    db.String())
)


class CityItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    position   = db.Column(db.String())
    def __init__(self,name,position):
        self.name = name
        self.position = json.dumps(position)
    def __to_dict__(self):
        return dict({'id':self.id,'name':self.name,'position':json.loads(self.position)})

class MapItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city_id = db.Column(db.ForeignKey('city_item.id'),nullable=True)
    #position_x = db.Column(db.Float(), nullable=True)
    #position_y = db.Column(db.Float(), nullable=True)
    position   = db.Column(db.String())
    def __init__(self,name,position,city_id):
        self.name = name
        self.position = json.dumps(position)
        self.city_id = city_id
    def __to_dict__(self):
        return dict({'id':self.id,'name':self.name,'position':json.loads(self.position),'city_id':self.city_id})


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

class BlockItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('block_item.id'), nullable=True)
    type = db.Column(db.String(255))
    data = db.Column(db.String())
    order = db.Column(db.Integer, nullable=True)
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

    def __init__(self, parent_id, type, data):
        self.parent_id = parent_id
        self.type = type
        self.data = data

    def __repr__(self):
        return "<block %r>" % self.id


class PageItem(db.Model):
    id   = db.Column(db.Integer, primary_key = True)
    url  = db.Column(db.String(), unique=True)
    meta = db.Column(db.String())
    blocks = db.relationship('BlockItem',secondary=blocks,backref=db.backref('PageItem'),order_by="BlockItem.order")

    def __to_dict__(self):
        result = {}
        result['id'] =     self.id
        result['meta'] =   json.loads(self.meta)
        result['url'] =    self.url
        result['subitems'] = [i.__to_dict__() for i in self.blocks]
        return result

    def __init__(self,url,meta):
        self.url = url
        self.meta =  meta


class SubscribedUsers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String())
    birthday = db.Column(db.String())
    city = db.Column(db.String())
    gender = db.Column(db.String())
    def __to_dict__(self):
        return dict({'email':self.email,'birthday':self.birthday,'city':self.city,'gender':self.gender})
    def __init__(self,email,birthday,city,gender):
        self.email,self.birthday,self.city,self.gender = email,birthday,city,gender
    #block_id = db.Column(db.Integer, db.ForeignKey('block_item.id'),nullable=True)

#class PageBlock(db.Model):
#    id = db.Column(db.Integer,primary_key = True)
#    page_id = db.Column(db.ForeignKey('page_item.id'))
#    block_id = db.Column(db.ForeignKey('block_item.id'))
#    place    = db.Column(db.String())
#    blocks = db.relationship('BlockItem')


