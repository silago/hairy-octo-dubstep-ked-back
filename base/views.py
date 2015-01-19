import sys, os
from flask.ext.restful import Resource, Api
from flask import request, g, session
from base.models import *
import json
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL
from urllib.parse import unquote
import base64
import hashlib
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.cors import CORS, cross_origin
from werkzeug import secure_filename
from time import time
import csv



def check_access(fn):
    def wrapped(obj,*args,  **kwargs):
        role_id = current_user.role_id or 0

        if (role_id==2): return fn(obj,**kwargs)
        obj_name = obj.__class__.__name__
        fun_name = fn.__name__

        rules = {}
        rules[role_id] = Rights.get(Rights,role_id)
        print(rules)
        if (obj_name in rules[role_id] and fun_name in rules[role_id][obj_name]):
            return fn(obj,**kwargs)
            return fn(obj)
        else:
            return {'error':'you have no power here'}
        return fn(obj,**kwargs)

    return wrapped

def unquote_twice(st):
    return unquote(unquote(st))


class Catalog(Resource):
    def get(self):
        #data = [i.__to_dict__() for i in CatalogItem.query.get()]
        data = [ i.__to_dict__() for i in CatalogItem.query.all() ]
        return {'data':data}
        
    def post(self):
        file = False
        try:
            file = request.files["Files"]
        except:
            pass
        if file:
            current_date = datetime.now()
            f = file.read().decode('utf-8').split("\n")

            columns = [ i[0] for i in csv.reader(f[0],delimiter=',',quotechar='"') if len(i) == 1]
            CatalogItem.query.delete()
            del(f[0])
            for row in csv.reader(f,delimiter=',',quotechar='"'):
                data =  { columns[k]:v   for k,v in enumerate(row)  }
                db.session.add(CatalogItem(current_date, data))
            db.session.commit()
            return self.get()
            #        if (len(row)==1):
            #            #fields[columns[i]] = 
            #            try:
            #                print(columns[i])
            #            except:
            #                print(">>")
            #                print(row[0])
            #                print(i)
            #                print("<<")
            #            i+=1
            #return []
                #db.session.add(CatalogItem(obj["name"],current_item,obj["position"]))
            #filename = str(time())+secure_filename(file.filename)
            #file.save(os.path.join(STATIC_FILES_DIR,filename))
        

        return self.get()

class City(Resource):
    def get(self):
        items = CityItem.query.all()
        return {'data':[i.__to_dict__() for i in items]} or dict()

    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        CityItem.query.delete()
        for obj in data["data"]:
            db.session.add(CityItem(obj["name"],obj["position"]))
        db.session.commit()
        return self.get()


class Map(Resource):
    def get(self):
        items = MapItem.query.all()
        return {'data':[i.__to_dict__() for i in items]} or dict()

    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        MapItem.query.delete()
        for obj in data["data"]:
            db.session.add(MapItem(obj["name"],obj["position"]))
        db.session.commit()
        return self.get()


    def put(self):
        data = request.data.decode('utf-8')
        print(data)
        #try:
        #    data = json.loads(data)
        #except:
        #    print("cannot load json data")
        #password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        #item = UserItem(data['username'],password,data['role_id'])
        #db.session.add(item)
        #db.session.commit()
        #return self.get()
        return {}

class Files(Resource):
    def get(self):
        return {'data':[STATIC_FILES_URL+i for i in os.listdir(STATIC_FILES_DIR)]}

    #@login_required
    def post(self):
        file = request.files["Files"]
        if file:
            filename = str(time())+secure_filename(file.filename)
            file.save(os.path.join(STATIC_FILES_DIR,filename))
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

class Search(Resource):
    def post(self):
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except:
            print("cannot load json data")
        q = '%'+data['data']+'%'
        q = q.encode('raw_unicode_escape').decode('utf-8')

        result = []
        search_result = BlockItem.query.filter(BlockItem.data.like(q)).all()

        for  r in search_result :
            _p = r.__get_page__()
            if (_p): result+= [_p.__to_dict__()]
            #print(r.__get_page__())
        return {'data':result}


class Page(Resource):
    def get(self,url):
        url = unquote_twice(url)
        result = {}
        #print(url)

        item = PageItem.query.filter(PageItem.url==url).first()
        if item:
            result = item.__to_dict__()
        return result
        #return result

    @check_access
    def put(self,url):
        url = unquote_twice(url)
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except:
            print("cannot load json data")
        item = PageItem.query.filter(PageItem.url==url).first() or PageItem(url,json.dumps(data['data']['meta']))
        db.session.add(item)
        db.session.commit()
        return self.get(url)


    @check_access
    def post(self,url):
        url = unquote_twice(url)
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except Exception:
            print("cannot load json data")

        item = PageItem.query.filter(PageItem.url==url).first()
        if not item:
            item = PageItem(url,json.dumps([]))

        new_blocks = self.__create_blocks(data['data'])
        item.blocks = new_blocks
        db.session.add(item)
        db.session.commit()
        return self.get(url)

    @login_required
    def __create_blocks(self,data,parent_id = None):
        result = []
        i = 0
        for block in data:
            i+=1
            if (not block or block['type'] == 'deleted'):
                continue
            if 'id' not in block:
                new_block = BlockItem(parent_id,block['type'],json.dumps(block['data']))
            else:
                new_block = BlockItem.query.get(block['id'])
                new_block.data=json.dumps(block['data'])
            new_block.order = i
            db.session.add(new_block)
            db.session.commit()
            result.append(new_block)
            if 'subitems' in block:
                new_block.subitems = self.__create_blocks(block['subitems'],new_block.id)
            db.session.add(new_block)
            db.session.commit()

        return result

    def __append_blocks(self,items,page_id):
        pass


class Block(Resource):
    def get(self,alias):
        pass
        item = BlockItem.query.filter(BlockItem.alias==alias)
        if not item: return dict()
        else: return item.__to_dict__()
        #if not result: result=dict()
        #else: result = result.__to_dict__()
        #return result

    def update_items(self,data,parent_id=None):
        pass
        #BlockItem.query.filter(~BlockItem.id.in_([i['id'] for i in data if 'id' in i]),BlockItem.parent_id==parent_id).delete(False)
        #for menu_item in data:
        #    if 'id' in menu_item:
        #        db_item = BlockItem.query.get(menu_item['id'])
        #        db_item.title = menu_item['title']
        #        db_item.url = menu_item['url']
        #        db.session.commit()
        #    else:
        #        db_item = BlockItem(parent_id,menu_item['title'],menu_item['url'])
        #        db.session.add(db_item)
        #        db.session.commit()
        #    if 'subitems' in menu_item: self.update_items(menu_item['subitems'],db_item.id)
        #return self.get()


    def post(self,item_id=None):
        pass
        #data = request.data.decode('utf-8')
        #try:
        #    data = json.loads(data)
        #except Exception:
        #    print("cannot load json data")
        #return self.update_items(data,item_id)
        ##print(data)
        #    #item_to_save = [title,url]
        #    #subitems = [{title:sub.title, url:sub.url, parent_id:item_to_save.id, subitems:sub.sub} for sub in menu_item.subitems]
        #    #self.post(subitems)

    def put(self):
        print((request.data))
        #data = json.load(request.data)
        return {}
