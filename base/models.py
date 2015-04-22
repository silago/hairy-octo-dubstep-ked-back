from config import db, app
from datetime import datetime
from config import slugify
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


