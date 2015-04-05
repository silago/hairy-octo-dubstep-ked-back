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
from views.auth import check_access
from views.common import unquote_twice


class Page(Resource):
    def get(self,url):
        lang = (request.args.get('lang')) or 'ru'
        url = unquote_twice(url)
        result = {}
        #print(url)

        item = PageItem.query.filter(PageItem.url==url,).first()
        if item:
            result = item.__to_dict__(lang)
        return result
        #return result

    @check_access
    def put(self,url):
        lang = (request.args.get('lang')) or 'ru'
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
        lang = (request.args.get('lang')) or 'ru'
        print(lang)
        url = unquote_twice(url)
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except Exception:
            print("cannot load json data")

        item = PageItem.query.filter(PageItem.url==url).first()
        if not item:
            item = PageItem(url,json.dumps([]))
        if ('meta' in data['data']):
            item.meta = json.dumps(data['data']['meta'])
        if ('subitems' in data['data']):
            new_blocks =[i for i in item.blocks if i.lang!=lang] 
            new_blocks+=self.__create_blocks(data['data']['subitems'],None,lang)
            item.blocks = new_blocks
        db.session.add(item)
        db.session.commit()
        return self.get(url)

    @login_required
    def __create_blocks(self,data,parent_id = None,lang='ru'):
        result = []
        i = 0
        for block in data:
            i+=1
            if (not block or block['type'] == 'deleted'):
                continue
            if 'id' not in block:
                new_block = BlockItem(parent_id,block['type'],json.dumps(block['data']),lang)
            else:
                new_block = BlockItem.query.get(block['id'])
                new_block.data=json.dumps(block['data'])
            new_block.order = i
            db.session.add(new_block)
            db.session.commit()
            result.append(new_block)
            if 'subitems' in block:
                new_block.subitems = self.__create_blocks(block['subitems'],new_block.id,lang)
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
