from config import db, app
from datetime import datetime
from slugify import slugify
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

ROLE_USER = 0
ROLE_ADMIN = 1


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
    address = db.Column(db.String())
    city_id = db.Column(db.ForeignKey('city_item.id'),nullable=True)
    #position_x = db.Column(db.Float(), nullable=True)
    #position_y = db.Column(db.Float(), nullable=True)
    position   = db.Column(db.String())
    def __init__(self,name,position,city_id,address=""):
        self.name = name
        self.position = json.dumps(position)
        self.city_id = city_id
        self.address = address
    def __to_dict__(self):
        return dict({'id':self.id,'name':self.name,'position':json.loads(self.position),'city_id':self.city_id,'address':self.address})
