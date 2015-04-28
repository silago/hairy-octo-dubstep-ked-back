import sys, os, io
from time import sleep
import re
from flask.ext.restful import Resource, Api
from sqlalchemy.sql import func
from flask import request, g, session, make_response
from base.models import *
#from base.blog import *
from base.catalog import *
from base.map import *
#from base.pages import *
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
from views.common import unquote_twice


class CatalogItemData(Resource):
    def get(self,segment_slug,type_slug,sku):
        sku  = unquote_twice(sku)
        #active_collection = CatalogItemCollections.query.filter(CatalogItemCollections.active==1).first()
        #segment = CatalogItemSegment.query.filter(CatalogItemSegment.collection_id==active_collection.id,CatalogItemSegment.slug==segment_slug).first()
        #stype = CatalogItemType.query.filter(
        #        CatalogItemType.parent_id==segment.id,
        #        CatalogItemType.slug==type_slug).first()
        result = CatalogItem.query.filter(CatalogItem.sku==sku).first().__to_dict__()
        rating = ItemRating.query.filter(ItemRating.id==result['sku']).first()
        rating = rating.get_rating() if rating else 3
        #result = [ i.__to_dict__() for i in stype.items ]
        result['rating'] = rating
        return result 

class CatalogItems(Resource):
    def get(self,segment_slug,type_slug):
        active_collection = CatalogItemCollections.query.filter(CatalogItemCollections.active==1).first()
        segment = CatalogItemSegment.query.filter(CatalogItemSegment.collection_id==active_collection.id,CatalogItemSegment.slug==segment_slug).first()
        if (type_slug!='*'):
            stype = CatalogItemType.query.filter(
                    CatalogItemType.parent_id==segment.id,
                    CatalogItemType.slug==type_slug).first()
            result = [ i.__to_dict__() for i in stype.items ]
            return {'info':stype.__to_dict__(),'data':result}
        else:
            stypes = CatalogItemType.query.filter(CatalogItemType.parent_id==segment.id).all()
            r = []
            for st in stypes:
                r+=[i.__to_dict__() for i in st.items]
            return {
                'info':{
                    'display_name':segment.name,
                    'item_example':{
                        'data':r}
                    },
                    'data':r
                }

class CatalogTypes(Resource):
    def get(self,slug):
        active_collection = CatalogItemCollections.query.filter(CatalogItemCollections.active==1).first()
        segment = CatalogItemSegment.query.filter(CatalogItemSegment.collection_id==active_collection.id,CatalogItemSegment.slug==slug).first()
        result = [ i.__to_dict__() for i in segment.types]
        return {'info':segment.__to_dict__(),'data':result}

class CatalogSegments(Resource):
    def get(self):
        collection_slug = False
        try:
            data = json.loads(request.data.decode('utf-8'))
            collection_slug = data['collection']
        except:
            pass
        if (not collection_slug):
            collection = CatalogItemCollections.query.filter(CatalogItemCollections.active==1).first()
        else:
            collection = CatalogItemCollections.query.filter(CatalogItemCollections.slug==collection_slug).first()
        return {'data':[i.__to_dict__() for i in collection.segments]}
    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        sdata = data['data']['data']
        grouped_segment = False
        for  segment in sdata:
            if 'id' in'id' in  segment:
                item = CatalogItemSegment.query.get(segment['id'])
            else:
                item = CatalogItemSegment(segment['collection_id'],segment['name'])
                db.session.add(item)
                db.session.commit()

            if ('group' in segment and segment['group']==1):
                if not grouped_segment:
                    grouped_segment = CatalogItemSegment(segment['collection_id'],segment['name'])
                else:
                    grouped_segment.name+=' '+segment['name']
                grouped_segment.types+=item.types
                db.session.delete(item)
            else:
                if ('parent_id' in segment): item.parent_id = segment['parent_id']
                item.name = segment['name']
                db.session.add(item)
        if grouped_segment:
            for t in grouped_segment.types:
                for i in grouped_segment.types:
                    if t.slug == i.slug and t.id != i.id:
                        t.items+=i.items
                        i.items=[]
                        db.session.add(t)
                        db.session.add(i)
            db.session.add(grouped_segment)
        db.session.commit()

        all_types = CatalogItemType.query.all()
        for a in all_types:
            if len(a.items)==0:
                db.session.delete(a)
        db.session.commit()
        return self.get()



# '/catalog/collection' - for seasons 
# '/catalog/ for collestions
#Зимал ли, лето, конец ли света
class CatalogCollections(Resource):
    def get(self):
        #all = True
        ##all = (request.args.get('all')) or False
        #if (not all):
        #    filt = CatalogItem.group_catalog_id!=None
        #else: 
        #    filt = True
        #return {'data':[i.__to_dict__() for i in \
        return {'data':[ {'id':i.id,'name':i.name,'slug':i.slug} for i in    CatalogItemCollections.query.all()]}
        #//CatalogItem.query.group_by(CatalogItem.season).\
        #filter(filt,CatalogItem.season!=None).all()]}
        #db.session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
        pass

    """ delete collection e.g. all segments in this collection. fail """
    def delete(self):
        collection = (request.args.get('collection')) or False
        CatalogItemCollections.query.delete()
        CatalogItemSegment.query.delete()
        CatalogItemType.query.delete()
        CatalogItem.query.delete()
        db.session.commit()
        return {}

    """ set collection as active """ 
    def put(self):
        data = json.loads(request.data.decode('utf-8'))
        #collection = (request.args.get('collection')) or False
        collection_slug = data['collection']
        if (data['collection']):
            CatalogItemCollections.query.filter(CatalogItemCollections.slug!=collection_slug).update({'active':0})
            CatalogItemCollections.query.filter(CatalogItemCollections.slug==collection_slug).update({'active':1})
        db.session.commit()
        return {}

    def post(self):
        file = False
        try:
            file = request.files["Files"]
        except:
            pass
        if file:
            collection = (request.args.get('season')) or False
            self.processCsv(file,collection)
            #current_date = datetime.now()
            #f = file.read().decode('utf-8').split("\n")
            #columns = [ i[0] for i in csv.reader(f[0],delimiter=',',quotechar='"') if len(i) == 1]
            ##CatalogItem.query.delete()
            #del(f[0])
            #for row in csv.reader(f,delimiter=',',quotechar='"'):
            #    data =  { columns[k]:v   for k,v in enumerate(row)  }
            #    db.session.add(CatalogItem(current_date,season, data))
            #db.session.commit()
            return self.get()
        return self.get()

    def processCsv(self,file,collection_name):
        f = file.read().decode('utf8').split("\n")
        #1. create collection from name
        #columns = [ i[0] for i in csv.reader(f[0],delimiter=',',quotechar='"') if len(i) == 1]
        #print(f[0])
        columns = f[0].split(',')
        del(f[0])
        #collection = False

        collection = CatalogItemCollections.query.filter(CatalogItemCollections.name==collection_name).first() or CatalogItemCollections(collection_name)
        db.session.add(collection)
        db.session.commit()
        for row in csv.reader(f,delimiter=',',quotechar='"'):
            artikul = None
            if (len(row)>=2):
                #return {}
                #2 proc
                segment      = CatalogItemSegment.query.filter(CatalogItemSegment.collection_id==collection.id,CatalogItemSegment.name==row[columns.index('Сегмент')]).first() or CatalogItemSegment(collection.id,row[columns.index('Сегмент')])
                if not segment.id:
                    db.session.add(segment)
                    db.session.commit()
                
                item_type    = CatalogItemType.query.filter(CatalogItemType.parent_id==segment.id,CatalogItemType.name==row[columns.index('Тип обуви')]).first() or CatalogItemType(segment.id,row[columns.index('Тип обуви')]) 
                if not item_type.id:
                    db.session.add(item_type)
                    db.session.commit()

                #try:
                artikul      = CatalogItem(item_type.id,row[columns.index('Артикул')],1,json.dumps({columns[i]:row[i] for i in range(0,len(row)) }))
                if (artikul.sku):
                    db.session.add(artikul)
                #except Exception as e:
                #    print(e)
                #    print("!!some error")
                #data =  { columns[k]:v   for k,v in enumerate(row)  }
        db.session.commit()
        return self.get()


class Rating(Resource):
    def put(self,id,rating):
        id = unquote_twice(id)
        rating = int(rating)
        rating = rating if rating<=5 else 5
        irating = ItemRating.query.get(id) or ItemRating(id,rating)
        irating.update_rating(rating)
        db.session.add(irating)
        db.session.commit()
        return {'status':True}

