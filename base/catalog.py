from config import db, app
from datetime import datetime
from slugify import slugify
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

ROLE_USER = 0
ROLE_ADMIN = 1


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

