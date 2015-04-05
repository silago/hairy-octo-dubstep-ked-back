import sys, os, io
from time import sleep
import re
from flask.ext.restful import Resource, Api
from sqlalchemy.sql import func
from flask import request, g, session, make_response
from base.models import *
from base.blog import *
from base.catalog import *
from base.map import *
from base.pages import *
import json
#from urllib3 import PoolManager
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL, STATIC_FILES_SUB, ROOT_DIR
from urllib.parse import unquote
import requests
#from xml.etree import ElementTree
from lxml import etree #import ElementTree
import base64
import hashlib
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.cors import CORS, cross_origin
from werkzeug import secure_filename
from time import time
import csv
from sqlalchemy.sql.expression import or_

def check_access(fn):
    def wrapped(obj,*args,  **kwargs):
        role_id = current_user.role_id or 0

        if (role_id==2): return fn(obj,**kwargs)
        obj_name = obj.__class__.__name__
        fun_name = fn.__name__

        rules = {}
        rules[role_id] = Rights.get(Rights,role_id)
        if (obj_name in rules[role_id] and fun_name in rules[role_id][obj_name]):
            return fn(obj,**kwargs)
            return fn(obj)
        else:
            return {'error':'you have no power here'}
        return fn(obj,**kwargs)

    return wrapped

class Auth(Resource):
    def get(self):
        if current_user.is_authenticated():
            return current_user.__to_dict__()
        else:
            return dict()

    def delete(self):
        logout_user()
        return dict()

    def post(self):
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except:
            print("cannot load json data")
        data = data['data']
        username = data['username']
        password = base64.b64decode(data['password'])
        password = hashlib.md5(password).hexdigest()
        user = UserItem.query.filter(UserItem.username==username,UserItem.password==password).first()
        if user:
            is_logged = login_user(user)
            return {'username':user.username,'role_id':user.role_id}
        else: return {}

class User(Resource):
    @login_required
    def accessable(self):
        return {'error':'you have no access here'}

    def get(self):
        users = UserItem.query.all()
        return {'data':[u.__to_dict__() for u in users]} or dict()

    @check_access
    def post(self):
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
            uid = data['id']
        except:
            print("cannot load json data")
        item = UserItem.query.get(uid)
        item.role_id = data['role_id']
        item.username = data['username']
        if ('password' in data and data['password']): item.password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        db.session.add(item)
        db.session.commit()
        return self.get()


    @check_access
    def put(self):
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except:
            print("cannot load json data")

        password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        item = UserItem(data['username'],password,data['role_id'])
        db.session.add(item)
        db.session.commit()
        return self.get()


class Rights(Resource):
    def get(self,group_id):
        # получить текущие разрещения групп
        group = GroupItem.query.get(group_id)
        views = ViewItem.query.all()
        result = {}
        for _v in views: result[_v.name] = []
        for _g in group.rights:
            result[_g.name]+=[_g.method]
        return result
        pass

    def post(self,group_id):
        data = request.data.decode('utf-8')
        data = json.loads(data)
        data = data['data']
        group = GroupItem.query.get(group_id)
        a = [v for k,v in data.items()]
        _r = []
        for k,v in data.items():
            _r = _r+ [ViewItem.query.filter(ViewItem.name==k,ViewItem.method==m).first() or ViewItem(k,m) for m in v]
        group.rights = _r
        db.session.add(group)
        db.session.commit()
        return self.get(group_id)

