import sys, os, io
from time import sleep, time
import re
from flask.ext.restful import Resource, Api
from sqlalchemy.sql import func
from flask import request, g, session, make_response
from base.models import *
#from base.blog import *
from base.side import *
from base.map import *
#from base.pages import *
import json
#from urllib3 import PoolManager
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL, STATIC_FILES_SUB, ROOT_DIR, SIDE_CATALOG_URL
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


class SideCatalogItemData(Resource):
    def get(self,segment_slug,type_slug,sku):
        sku  = unquote_twice(sku)
        result = SideCatalogItem.query.filter(SideCatalogItem.sku==sku).first().__to_dict__()
        #rating = SideItemRating.query.filter(SideItemRating.id==result['sku']).first()
        #rating = rating.get_rating() if rating else 3
        #result['rating'] = rating
        return result 

class SideCatalogItems(Resource):
    def get(self,segment_slug,type_slug):
        #active_collection = SdieCatalogItemCollections.query.filter(CatalogItemCollections.active==1).first()
        segment = SideCatalogItemSegment.query.filter(SideCatalogItemSegment.slug==segment_slug).first()
        stype = SideCatalogItemType.query.filter(
                SideCatalogItemType.parent_id==segment.id,
                SideCatalogItemType.slug==type_slug).first()
        result = [ i.__to_dict__() for i in stype.items ]
        return {'info':stype.__to_dict__(),'data':result}

class SideCatalogTypes(Resource):
    def get(self,slug):
        #active_collection = CatalogItemCollections.query.filter(CatalogItemCollections.active==1).first()
        segment = SideCatalogItemSegment.query.filter(SideCatalogItemSegment.slug==slug).first()
        result = [ i.__to_dict__() for i in segment.types]
        return {'info':segment.__to_dict__(),'data':result}

class SideCatalogSegments(Resource):
    def get(self):
        sync_result = SideCatalogCollections().runInterval()
        #collection_slug = False
        #try:
        #    data = json.loads(request.data.decode('utf-8'))
        #    collection_slug = data['collection']
        #except:
        #    pass
        #if (not collection_slug):
        #    collection = SideCatalogItemCollections.query.filter(SideCatalogItemCollections.active==1).first()
        #else:
        #    collection = SideCatalogItemCollections.query.filter(SideCatalogItemCollections.slug==collection_slug).first()
        return {'data':[i.__to_dict__() for i in SideCatalogItemSegment.query.all()]}
    def post(self):
        return self.get()



class SideCatalogCollections(Resource):
    def get(self):
        #return self.runInterval()
        return {}
        #return {'data':[ {'id':i.id,'name':i.name,'slug':i.slug} for i in    CatalogItemCollections.query.all()]}
        #pass

    """ delete collection e.g. all segments in this collection. fail """
    def delete(self):
        #collection = (request.args.get('collection')) or False
        #CatalogItem.query.filter(CatalogItem.season==collection).delete()
        #db.session.commit()
        return {}

    """ set collection as active """ 
    def put(self):
        #data = json.loads(request.data.decode('utf-8'))
        ##collection = (request.args.get('collection')) or False
        #collection_slug = data['collection']
        #if (data['collection']):
        #    CatalogItemCollections.query.filter(CatalogItemCollections.slug!=collection_slug).update({'active':0})
        #    CatalogItemCollections.query.filter(CatalogItemCollections.slug==collection_slug).update({'active':1})
        #db.session.commit()
        return {}
    
    def runInterval(self):
        result = {}
        last_update = SideCatalogData.query.filter(SideCatalogData.name=='last_update').first()
        #last_update = last_update.name if last_update else 0
        if (not last_update):
            last_update = SideCatalogData()
            last_update.name = 'last_update'
            l = 0
        else:
            l = last_update.value
        
        #3600 = one hour
        #
        print(l)
        if (time()-float(l)>12*3600):
        #if True:
            response = requests.get(SIDE_CATALOG_URL)
            #data = response.read()
            if response:
                result =  self.processCsv(response)
        
        last_update.value = str(time())
        db.session.add(last_update)
        db.session.commit()
        
        return result

    def post(self):
        file = False
        try:
            file = request.files["Files"]
        except:
            pass
        if file:
            collection = (request.args.get('season')) or False
            self.processCsv(file,collection)
            return self.get()
        return self.get()

    def processCsv(self,file):
        artikul_index = 6
        segment_index = 19
        type_index = 20
        file.encoding = 'PT154'
        f = file.text.split("\n")
        columns = f[0].split(";")
        #columns = [ i[0] for i in csv.reader(f[0],delimiter=';',quotechar='"') if len(i) == 1]
        #print(f[0].split(";"))
        #return {'f':13}
        del(f[0])

        #collection = CatalogItemCollections.query.filter(CatalogItemCollections.name==collection_name).first() or CatalogItemCollections(collection_name)
        #db.session.add(collection)
        #db.session.commit()

        SideCatalogItem.query.delete()
        SideCatalogItemType.query.delete()
        SideCatalogItemSegment.query.delete()

        db.session.commit()
        counter = 0
        for row in csv.reader(f,delimiter=';',quotechar='"'):
            counter+=1
            print(counter)
            if (len(row)>=2):
                #return {}
                #2 proc
                #segment      = SideCatalogItemSegment.query.filter(CatalogItemSegment.name==row[segment_index]).first() or CatalogItemSegment(row[segment_index])
                
                segment      = SideCatalogItemSegment.query.filter(SideCatalogItemSegment.name=='Обувь').first()
                if segment is None:
                    print('1')
                    segment =SideCatalogItemSegment('Обувь')
                    db.session.add(segment)
                    db.session.commit()
                #if not segment.id:
                #    db.session.add(segment)
                    #db.session.commit()
                
                item_type    = SideCatalogItemType.query.filter(SideCatalogItemType.parent_id==segment.id,SideCatalogItemType.name==row[type_index]).first()
                if item_type is None:
                    print('2')
                    item_type = SideCatalogItemType(segment.id,row[type_index]) 
                    db.session.add(item_type)
                    db.session.commit()

                try:
                    artikul_name = row[artikul_index] 
                    artikul      = SideCatalogItem(item_type.id,artikul_name,1,json.dumps({columns[i]:row[i] for i in range(0,len(row)) }))
                    db.session.add(artikul)
                except:
                    print("!!some error")
                #data =  { columns[k]:v   for k,v in enumerate(row)  }
        db.session.commit()
        return self.get()


class SideRating(Resource):
    def put(self,id,rating):
        id = unquote_twice(id)
        rating = int(rating)
        rating = rating if rating<=5 else 5
        irating = ItemRating.query.get(id) or ItemRating(id,rating)
        irating.update_rating(rating)
        db.session.add(irating)
        db.session.commit()
        return {'status':True}

