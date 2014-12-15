from flask.ext.restful import Resource, Api
from flask import request, g
from base.models import *
import json
from config import db
from urllib.parse import unquote
import base64
import hashlib
from flask.ext.login import login_user, logout_user, current_user, login_required


def unquote_twice(st):
    return unquote(unquote(st))

class User(Resource):
    def get(self):
        print("$")
        print(request.cookies)
        print("$")
        if 'user' in g and g.user.is_authenticated():
            return g.user
        else:
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
            g.user = user
            token  = g.user.generate_auth_token()
            print("we are loggined")
            return {'username':user.username,'role_id':user.role_id,'token':token}
        else: return 0

class Page(Resource):
    def get(self,url):
        url = unquote_twice(url)
        result = {}
        #print(url)

        item = PageItem.query.filter(PageItem.url==url).first()
        if item:
            result['id'] = item.id
            result['meta'] = item.meta
            result['url'] = item.url
            result['subitems'] = [i.__to_dict__() for i in item.blocks]
        return result
        #return result

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

    def __create_blocks(self,data,parent_id = None):
        result = []
        i = 0
        for block in data:
            i+=1
            if block['type'] == 'deleted':
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
