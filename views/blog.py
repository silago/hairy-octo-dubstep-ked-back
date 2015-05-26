import sys, os, io
from flask.ext.restful import Resource, Api
from flask import request, g, session, make_response
from base.blog import *
import json
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL, STATIC_FILES_SUB, ROOT_DIR
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.cors import CORS, cross_origin


class Blog(Resource):
    def get(self):
        coll = (request.args.get('categories')) or False
        if (coll):
            return {'data':[{'name':i.name,'url':i.url,'id':i.id,'visible':i.visible} for i in BlogCategory.query.all()]}
        else:
            return {'data':[i.__to_dict__() for i in BlogPageItem.query.limit(10).all()]}
    def post(self):
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except Exception:
            print("cannot load json data")
        cat_ids = [i["id"] for i in data["data"] if "id" in i]
        print(cat_ids)
        for d in BlogCategory.query.filter(~BlogCategory.id.in_((cat_ids))).all():
            d.query.delete()
        for i in data["data"]:
            cat = (BlogCategory.query.get(i["id"]) if "id" in i else BlogCategory(i["name"],i["url"])) or BlogCategory(i["name"],i["url"])
            cat.name=(i["name"])
            cat.url=(i["url"])
            cat.visible=i["visible"] if 'visible' in i else 1
            db.session.add(cat)
        db.session.commit()
        return self.get()

class BlogPageBlock(Resource):
    def get(self,page_name,alias):
       return BlogPageItem.query.filter(BlogPageItem.url==alias).first().__to_dict__()

# page name - it is category name
class BlogPages(Resource):
    def _walkThrowBlocks(self,arr):
        order = 0
        for i in arr:
            if i['type']=='deleted':
                arr.remove(i)
            elif 'subitems' in i:
                order = order+1
                i['order']=order
                i['subitems'] = self._walkThrowBlocks(i['subitems'])
        return arr


    def get(self,url):
       c = BlogCategory.query.filter(BlogCategory.url==url).first()
       offset = int(request.args.get('offset')) or 0 
       limit  = 1+offset 
       pages = c.pages[offset:limit] if c else []
       return {'url':url,'subitems':[ i.__to_dict__(True) for i in pages ]}
       #return {'name':page_name,'subitems':[ i.__to_dict__() for i in BlogCategory.query.filter(BlogCategory.name==page_name).first().pages]}
    
    def post(self,url):
        category = BlogCategory.query.filter(BlogCategory.url==url).first()
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except Exception:
            print("cannot load json data")
        data = data["data"]
        category_pages = []
        for page in data["subitems"]:
            page_item = BlogPageItem.query.get(page["id"]) if "id" in page else BlogPageItem("","","")
            page_item.category_id = page["category_id"]
            if 'url' in page: page_item.url = page['url']
            if 'subitems' in page: page_item.blocks  = self.__create_blocks(page['subitems'])
            pr = json.dumps( self._walkThrowBlocks(page['preview'])) if page['preview'] else '{}'
            page_item.preview = pr
            db.session.add(page_item)
            if (page_item.category_id==category.id):
                category_pages.append(page_item)
        category.pages = category_pages


        
        #item = PageItem.query.filter(PageItem.url==url).first()
        #if not item:
        #    item = PageItem(url,json.dumps([]))
        #if ('meta' in data['data']):
        #    item.meta = json.dumps(data['data']['meta'])
        #new_blocks = self.__create_blocks(data['data']['subitems'])
        #item.blocks = new_blocks
        db.session.add(category)
        BlogBlockItem.query.filter(BlogBlockItem.type=='deleted').delete()
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
                new_block = BlogBlockItem(parent_id,block['type'],json.dumps(block['data']))
            else:
                new_block = BlogBlockItem.query.get(block['id'])
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
