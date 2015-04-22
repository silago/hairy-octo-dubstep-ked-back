from config import db, app
from datetime import datetime
from config import slugify
import json, re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

ROLE_USER = 0
ROLE_ADMIN = 1

#class SideItemRating(db.Model):
#    __tablename__="item_rating"
#    id = db.Column(db.ForeignKey("catalog_item.sku"),primary_key=True)
#    voters = db.Column(db.Integer)
#    rating = db.Column(db.Integer)
#    def update_rating(self,rating):
#        self.voters+=1
#        self.rating+=rating
#        return self.rating/float(self.voters)
#        #self.rating = (self.rating*self.voters
#    def get_rating(self):
#        return self.rating/float(self.voters)
#
#    def __init__(self,id,rating):
#        self.id = id
#        self.rating = 5
#        self.voters = 0;

class SideCatalogData(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name            = db.Column(db.String())
    value            = db.Column(db.String())

class SideCatalogItemType(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    parent_id       = db.Column(db.ForeignKey('side_catalog_item_segment.id'))
    slug            = db.Column(db.String())
    name            = db.Column(db.String())
    display_name    = db.Column(db.String())
    data            = db.Column(db.String())
    items           = db.relationship('SideCatalogItem')
    def __first_item__(self):
        try:
            return SideCatalogItem.query.filter(SideCatalogItem.parent_id==self.id).first().__to_dict__()
        except:
            print(self.id)
            return {}
            

    def __to_dict__(self):
        return {'id':self.id,'parent_id':self.parent_id,'slug':self.slug,'name':self.name,'display_name':self.display_name,'data':('{}' if not self.data else json.loads(self.data)),'item_example':self.__first_item__()}

    def __init__(self,parent_id,name):
        self.parent_id = parent_id
        self.name = name
        self.display_name = name
        self.slug = slugify(name)

class SideCatalogItemSegment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    parent_id       = db.Column(db.ForeignKey('side_catalog_item_segment.id'),nullable=True)
    slug            = db.Column(db.String())
    name            = db.Column(db.String())
    data            = db.Column(db.String())
    #types           = db.relationship('CatalogItemType')
    types = db.relationship('SideCatalogItemType',primaryjoin=id==SideCatalogItemType.parent_id)
    def __to_dict__(self):
        return {'id':self.id,'parent_id':self.parent_id,'slug':self.slug,'name':self.name}

    def __init__(self,name):
        self.name = name
        self.slug = slugify(name)



class SideCatalogItem(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    sku       = db.Column(db.String(255))
    parent_id = db.Column(db.ForeignKey('side_catalog_item_type.id'),nullable=True)
    data      = db.Column(db.String(255))
    status    = db.Column(db.Integer,nullable=True,default=0)
    
    def __init__(self,parent_id,sku,status,data):
        self.parent_id = parent_id
        self.sku = sku
        self.status = status
        self.data = data
    
    def __to_dict__(self):
        return {'id':self.id,'sku':self.sku,'parent_id':self.parent_id,'data':('{}' if not self.data else json.loads(self.data))}

    def __get_csv_association(self,key):
        pass

#class CategoryItem(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    alias = db.Column(db.String(255), unique=True)
#    parent_id = db.Column(db.ForeignKey('category_item.id'),nullable=True)
#    name  = db.Column(db.String(255))
#
#class ArtikulItem(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    alias = db.Column(db.String(255))
#    data  = db.Column(db.String())
#    category_id = db.Column(db.ForeignKey('category_item.id'))

