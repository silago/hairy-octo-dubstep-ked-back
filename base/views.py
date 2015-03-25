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

def unquote_twice(st):
    return unquote(unquote(st))



class _Catalog(Resource):
    def get(self):
        pass


CATALOG_CACHE = {}

class CatalogCacheContainer():
    def foo(self):
        pass

#Мужская или женская или жетская
class CatalogSegments(Resource):
    def putAllItemsHere(self):
        items = []
        SideCatalogItem.query.delete()
        SideCatalogGroup.query.delete()
        SideCatalogItemImage.query.delete()
        url='http://keddoshop.com/api/rest/categories/'
        root_id = 2
        #    url = 'http://keddoshop.com/api/rest/products?limit=100&page='+str(page)
        #    page+=1
        response = requests.get(url+str(root_id))
        data = json.loads(response.content.decode('utf-8'))
        #    prev_first_sku = curr_first_sku
        #    curr_first_sku = list(data.items())[0][1]['sku']
        #   print(prev_first_sku)
        #    print(curr_first_sku)
        #    if (prev_first_sku!=curr_first_sku):
        for j in data:
            if j['parent_id']==root_id:
                item = SideCatalogGroup(j['category_id'],j['parent_id'],j['name'])
                db.session.add(item)
                if j['child_id']:
                    for k in j['child_id'].split(','):
                        sub_data = json.loads(requests.get(url+str(k)).content.decode('utf-8'))
                        for s in sub_data:
                            sub_item = SideCatalogGroup(s['category_id'],s['parent_id'],s['name'])
                            db.session.add(sub_item)
        db.session.commit()
        return {'status':'ok'}
    
    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        data = data["data"]
        item = SideCatalogGroup.query.get(data["id"]) 
        item.description = data["description"]
        item.after_menu = data["after_menu"]
        db.session.add(item)
        db.session.commit()
        return self.get()

    def get(self):
        global CATALOG_CACHE
        if (db.session.query(SideCatalogGroup.id).count() == 0):
            self.putAllItemsHere()
            

        result_data = [{'id':i.id,'parent_id':i.parent_id,'segment':i.name,'after_menu':i.after_menu,'description':i.description,'name':i.name} for i in SideCatalogGroup.query.filter(SideCatalogGroup.parent_id=='2',SideCatalogGroup.active==1).all()]
        #""" here get catalog from keddoshop """
        #""" get all items with parent id 12 """
        #""" except brands """
        #""" need to implement data cache """
        ##http = PoolManager()
        #url = 'http://keddoshop.com/api/rest/categories/2/'
        #if 'CatalogSegments' not in CATALOG_CACHE:
        #    response = requests.get(url)
        #    data = json.loads(response.content.decode('utf-8')) 
        #    """ adapter """
        #    result_data = []
        #    for i in data:
        #        if (i['parent_id'] == 2):
        #            result_data+=[{'segment':i['name'],'category_id':i['category_id']}]
        #    CATALOG_CACHE['CatalogSegments']=result_data
        #result_data = CATALOG_CACHE['CatalogSegments']
        result = {'data':result_data}
        #print(tree)
        #r = http.request('GET', url)
        #print(r.status, r.data)
        #return {'data':[i.__to_dict__() for i in CatalogItem.query.group_by(CatalogItem.segment).filter(CatalogItem.coll_status==1,CatalogItem.group_catalog_id!=None).order_by(CatalogItem.segment.desc()).all()]}
        return  result
        pass



# '/catalog/collection' - for seasons 
# '/catalog/ for collestions
#Зимал ли, лето, конец ли света
class CatalogCollections(Resource):
    def get(self):
        all = True
        #all = (request.args.get('all')) or False
        if (not all):
            filt = CatalogItem.group_catalog_id!=None
        else: 
            filt = True
        return {'data':[i.__to_dict__() for i in \
        CatalogItem.query.group_by(CatalogItem.season).\
        filter(filt,CatalogItem.season!=None).all()]}
        #db.session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
        pass

    """ delete collection e.g. all segments in this collection. fail """
    def delete(self):
        collection = (request.args.get('collection')) or False
        CatalogItem.query.filter(CatalogItem.season==collection).delete()
        db.session.commit()
        return {}

    """ set collection as active """ 
    def put(self):
        data = json.loads(request.data.decode('utf-8'))
        collection = (request.args.get('collection')) or False
        if (data['set']=='active'):
            CatalogItem.query.filter(CatalogItem.season!=collection).update({'coll_status':0})
            CatalogItem.query.filter(CatalogItem.season==collection).update({'coll_status':1})
        db.session.commit()
        return {}

    def post(self):
        file = False
        try:
            file = request.files["Files"]
        except:
            pass
        if file:
            season = (request.args.get('season')) or False
            current_date = datetime.now()
            f = file.read().decode('utf-8').split("\n")

            columns = [ i[0] for i in csv.reader(f[0],delimiter=',',quotechar='"') if len(i) == 1]
            #CatalogItem.query.delete()
            del(f[0])
            for row in csv.reader(f,delimiter=',',quotechar='"'):
                data =  { columns[k]:v   for k,v in enumerate(row)  }
                db.session.add(CatalogItem(current_date,season, data))
            db.session.commit()
            return self.get()
        return self.get()


class CatalogTypes(Resource):
    def get(self,segment_alias):
        parent_item = SideCatalogGroup.query.filter(SideCatalogGroup.name==segment_alias).first()
        child_items = SideCatalogGroup.query.filter(SideCatalogGroup.parent_id==parent_item.id).all()
        rand_item   = SideCatalogItem.query.order_by(func.random()).limit(1).first()
        result_data = [{'id':i.id,'parent_id':i.parent_id,'item_type':i.name,'description':i.description,'name':i.name} for i in child_items] 
        return {'rand_item':rand_item.__to_dict__(),'description':parent_item.description,'data':result_data}
        #global CATALOG_CACHE
        #if 'CatalogSegments' not in CATALOG_CACHE: CatalogSegments().get() 
        #for i in CATALOG_CACHE['CatalogSegments']:
        #    if i['segment']==segment_alias:
        #        if 'CatalogTypes'+segment_alias not in CATALOG_CACHE:
        #            url = 'http://keddoshop.com/api/rest/categories/'+i['category_id']+'/'
        #            response = requests.get(url)
        #            data = json.loads(response.content.decode('utf-8')) 
        #            result_data = []
        #            for j in data:
        #                if (str(j['parent_id']) == str(i['category_id'])):
        #                    result_data+=[{'item_type':j['name'],'category_id':j['category_id']}]
        #            CATALOG_CACHE['CatalogTypes'+segment_alias]=result_data
        #        result_data = CATALOG_CACHE['CatalogTypes'+segment_alias]
        #        return {'data':result_data}
        return []
        #return {'data':[i.__to_dict__() for i in CatalogItem.query.group_by(CatalogItem.item_type).filter(CatalogItem.coll_status==1,CatalogItem.group_catalog_id!=None,CatalogItem.segment==segment_alias).all()]}
        #pass

class CatalogGroups(Resource):
    def getItemMap(self,key):
        map_dict = {
                    'entity_id':'id',
                    'image_url':'base_image',
                    'sku':'sku',
                    'onec_cvetnasaite':'color',
                    'onec_materialverha':'material_top',
                    'lining':False,
                    'analpa_size':False,
                    'insole':False,
                    'segment':False,
                    'season':False,
                    'mark':False,
                    'item_type':False,
                    'created_time':False,
                    'group_catalog_id':False,
                    'coll_status':False,
                    'image_2':False,
                    'image_3':False,
                    }
        if key in map_dict:
            return map_dict[key]
        else: return key
        return map_dict

    def putAllItemsHere(self):
        page = 1
        items = []
        prev_first_sku = '-1'
        curr_first_sku = '-2'
        SideCatalogItem.query.delete()
        img_url_prefix='http://keddoshop.com/api/rest/products/'
        while (prev_first_sku!=curr_first_sku):
            url = 'http://keddoshop.com/api/rest/products?limit=100&page='+str(page)
            print(url)
            page+=1
            response = requests.get(url)
            data = json.loads(response.content.decode('utf-8'))
            prev_first_sku = curr_first_sku
            curr_first_sku = list(data.items())[0][1]['sku']
            print(prev_first_sku)
            print(curr_first_sku)
            if (prev_first_sku!=curr_first_sku):
                for jkey,j in data.items():
                    item = SideCatalogItem(jkey,j['sku'],json.dumps(j))
                    db.session.add(item)
                    for image in json.loads(requests.get(img_url_prefix+jkey+'/images').content.decode('utf-8')):
                        if (image['url']):
                            img = SideCatalogItemImage(jkey,image['url'])
                            db.session.add(img)
        db.session.commit()
        return {'status':'ok'}

            

    def get(self,segment_alias,type_alias):
        global CATALOG_CACHE
        if (db.session.query(SideCatalogItem.id).count() == 0):
            self.putAllItemsHere()
        parent_item = SideCatalogGroup.query.filter(SideCatalogGroup.name==segment_alias).first()

        items = SideCatalogItem.query.limit(20).all() or []
        result = []
        for i in items:
            result+=[i.__to_dict__()]
        return {'data':result,'description':parent_item.description}
        #if 'CatalogTypes'+segment_alias not in CATALOG_CACHE: CatalogTypes().get(segment_alias)
        #type_alias = type_alias.replace('---','/')
        #for i in CATALOG_CACHE['CatalogTypes'+segment_alias]:
        #    if i['item_type']==type_alias:
        #        if 'CatalogTypes'+segment_alias+type_alias not in CATALOG_CACHE: 
        #            #url = 'http://keddoshop.com/api/rest/products?filter[1][attribute]=onec_vidobuvi&filter[1][in]='+i['category_id']
        #            url = 'http://keddoshop.com/api/rest/products'
        #            print(url)
        #            response = requests.get(url)
        #            data = json.loads(response.content.decode('utf-8')) 
        #            result_data = {}
        #            for jk,j in data.items():
        #                if True:
        #            #    if (str(j['parent_id']) == str(i['category_id'])):
        #                   d = self.getItemMap
        #            #       #a = [v for k,v in data.items()]o
        #                   result_data[jk]={}
        #                   result_data[jk]={  d(item_key)  :item_data for (item_key,item_data) in j.items()} 
        #                   #result_data+=[{'id':j['ent'],'category_id':j['category_id']}]
        #            CATALOG_CACHE['CatalogTypes'+segment_alias+type_alias]=result_data
        #        result_data = CATALOG_CACHE['CatalogTypes'+segment_alias+type_alias]
        #        return {'data':result_data}

            #CatalogTypes().get(segment_alias)
        return []
        #for i in 'CatalogTypes'+segment_alias:
        print(CATALOG_CACHE['CatalogTypes'+segment_alias])


        print("CatalogGroups.Get")
        type_alias = type_alias.replace('---','/')
        filt = True if type_alias=='*' else CatalogItem.item_type==type_alias 
        return {'data':[i.__to_dict__() for i in GroupCatalogItem.query.join(GroupCatalogItem.items).filter(filt,CatalogItem.coll_status==1,CatalogItem.segment==segment_alias).all()]}
        pass


class CatalogItems(Resource):
    def get(self,segment_alias,type_alias,group_id):
        group_id = unquote_twice(group_id)
        result = []
        items = SideCatalogItem.query.get(group_id)
        result = items.__to_dict__()
        #url = 'http://keddoshop.com/api/rest/products/'+group_id
        #print(url)
        #print('####')
        #if 'CatalogGroups'+group_id not in CATALOG_CACHE:
        #    response = requests.get(url)
        #    data = json.loads(response.content.decode('utf-8')) 
        #    result_data = []
        #    result_data = data
        #    #for j in data:
        #    #    if (str(j['parent_id']) == str(i['category_id'])):
        #    #        result_data+=[{'item_type':j['name'],'category_id':j['category_id']}]
        #    CATALOG_CACHE['CatalogGroups'+group_id]=result_data
        #result_data = CATALOG_CACHE['CatalogGroups'+group_id]
        #return {'data':result_data}
        #result = GroupCatalogItem.query.get(group_id).__to_dict__()
        #dir = STATIC_FILES_DIR+'/catalog/keddo'
        #url = STATIC_FILES_URL+'catalog/keddo/'
        #for i in result['items']:
        #    i['files'] = [STATIC_FILES_URL+'catalog/'+i['base_image'],]
        #    i['files']+= [url+f for f in os.listdir(dir) if i['sku'].replace('/','-') in f ]
        return {'data':result}

""" catalog groups """
class Gcatalog(Resource):
    def get(self):
        collection = (request.args.get('collection')) or False
        state = (request.args.get('state')) or False
        
        # data = [i.__to_dict__() for i in GroupCatalogItem.query.all()]
        if (state=='items'):
            return {'data':[i.__to_dict__() for i in CatalogItem.query.filter(CatalogItem.season==collection,CatalogItem.group_catalog_id==None).all()]}
        else: 
            return {'data':[i.__to_dict__() for i in GroupCatalogItem.query.join(GroupCatalogItem.items).filter(CatalogItem.season==collection).all()]}

        return {'data':data}

    def put(self):
        data = json.loads(request.data.decode('utf-8'))['data']
        group = GroupCatalogItem(data['info'])
        group.items = [CatalogItem.query.get(i) for i in data['items']]
        db.session.add(group)
        db.session.commit()
        return self.get()

    def post(self):
        data = json.loads(request.data.decode('utf-8'))['data']
        group = GroupCatalogItem.query.get(data['id'])
        group.items = [CatalogItem.query.get(i['id']) for i in data['items']]
        group.similar = [GroupCatalogItem.query.get(i['id']) for i in data['similar']]
        db.session.add(group)
        db.session.commit()
        return self.get()
        

    def foo(self):
        return {'data':'foo'}





class Catalog(Resource):
    def get(self):
        #data = [i.__to_dict__() for i in CatalogItem.query.get()]
        data = [ i.__to_dict__() for i in CatalogItem.query.filter(CatalogItem.coll_status==1).all() ]
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
    def addCity(self,country,city_name):
        url = "http://geocode-maps.yandex.ru/1.x/?&geocode="+country+","+city_name
        try:
            response = requests.get(url)
        except:
            sleep(10)
            response = requests.get(url)

        #name= ElementTree.fromstring(response.content.decode('utf-8'))[0][1][0][0][0][3][0][3][1][1][0].text
        #pos  = etree.fromstring(response.content.decode('utf-8'))[0][1][0][2].text
        tree = etree.fromstring(response.content)
        pos  = tree.find('.//{*}pos').text.split(' ')[::-1]
        country = tree.find('.//{*}CountryName').text
        #city = CityItem.query.filter(CityItem.name==city_name).first() or CityItem(city_name,pos,country)
        #db.session.add(city)
        #db.session.commit()
        
        return {'name':city_name,'pos':pos,'country':country}
       
    def getFromUrl(self,row,t=False):
            name = row[0].lstrip()
            city    = row[1].lstrip()
            if not t:
                address = row[2]
                address = re.sub(' тел\..*', '', address)
                address = re.sub('([ТтЦц]{2}|Универмаг)\ \w+?,','',address)
                address = re.sub('м\.\w+?,','',address)
                #address = re.sub('Дом обуви "ТТ",?','', address)
                address = re.sub('-', ' ', address)
                address = address.lstrip()
                if (city[1:-1] not in address and re.sub('-',' ',city[1:-1]) not in address):
                    address = city+' '+address
            else:
                address = t
            #address="Невинномысск, ул. Гагарина, д. 1 в, ТЦ," 
            url = "http://geocode-maps.yandex.ru/1.x/?&geocode="+address
            print(url)
            #print(name)
            #print(address)
            try:
                response = requests.get(url)
            except:
                sleep(10)
                response = requests.get(url)

            #country =  ElementTree.fromstring(response.content.decode('utf-8'))[0][1][0][0][0][3]
            try: 
                tree = etree.fromstring(response.content)
                country = tree.find('.//{*}CountryName').text
                pos  = tree.find('.//{*}pos').text.split(' ')[::-1]
            except:
                return self.getFromUrl(row,row[3])
            return country, pos
            #cc = country+', '+city
            #city_el = self.addCity(country,city)
            #item = MapItem(name,pos,city_el.id,row[3])
            #db.session.add(item)

    def runOnce(self):
        #getObjectCollection->featureMember->geoObject->point
        #url='http://keddoshop.com/api/rest/categories/'
        CityItem.query.delete()
        MapItem.query.delete()

        
        shops = []
        city_arr = []
        res = {'countries':{}}
        with open(ROOT_DIR+'../../../sources/shops.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                name = row[0].lstrip()
                #address = row[3]
                #address = re.sub('тел.*', '', address)
                #address = re.sub('Дом обуви "ТТ",?','', address)
                #address = re.sub('-', ' ', address)
                #address = address.lstrip()
                city    = row[1].lstrip()
                
                #if (city[1:-1] not in address and re.sub('-',' ',city[1:-1]) not in address):
                #    address = city+' '+address
                country,pos = self.getFromUrl(row)

                cc = country+', '+city
                #city_el = self.addCity(country,city)
                #city_arr = [self.addCity(country,city),]
                if country not in res['countries']: res['countries'][country] = {'name':country,'cities':{}}
                if city not in res['countries'][country]['cities']: res['countries'][country]['cities'][city] = {'name':city,'shops':[]}
                if country=='Болгария':
                    print("############")
                    sleep(20)
                res['countries'][country]['cities'][city]['shops']+=[{'name':name,'coords':pos,'description':row[3],'type':row[4]},]
                print(country+'->'+city+'->'+row[3])
        b = BlockItem.query.get(231)
        b.data = json.dumps(res)
        db.session.add(b)
        db.session.commit()
        return(res)
                

                #item = MapItem(name,pos,city_el.id,row[3])
                #db.session.add(item)
        #db.session.commit()

        #for j in data:
        #    if j['parent_id']==root_id:
        #        item = SideCatalogGroup(j['category_id'],j['parent_id'],j['name'])
        #        db.session.add(item)
        #        if j['child_id']:
        #            for k in j['child_id'].split(','):
        #                sub_data = json.loads(requests.get(url+str(k)).content.decode('utf-8'))
        #                for s in sub_data:
        #                    sub_item = SideCatalogGroup(s['category_id'],s['parent_id'],s['name'])
        #                    db.session.add(sub_item)
        #db.session.commit()
        return {'status':'ok'}
    def get(self):
        #if (db.session.query(MapItem.id).count() == 0):
        return self.runOnce() 
        #b = BlockItem.query.get(231)
        #b.data = json.loads(b.data)
        #db.session.add(b)
        #db.session.commit()

        return([])
        items = MapItem.query.all()
        result = []
        countries = CityItem.query.group_by(CityItem.country).all()
        for i in countries:
            result+=[{'name':i.country,'cities':[]}]
        for i in result:
            i['cities']+= [{'name':z.name,'id':z.id} for z in CityItem.query.filter(CityItem.country==i['name']).all()]
            for c in i['cities']:
                c['shops'] = []
                c['shops']+=[{'name':s.name,'description':s.address,'coords':s.position} for s in MapItem.query.filter(CityItem.id==c['id']).all()]
        bi  = BlockItem.query.get(231)
        result = {'countries':result,'map_type':'partner'}
        #return({'r':(result)})
         
        
        bi.data = json.dumps(result)
        
        db.session.add(bi)
        db.session.commit()
        return {'data':bi.data}
        return {'data':[i.__to_dict__() for i in items]} or dict()

    def post(self):
        data = json.loads(request.data.decode('utf-8'))
        MapItem.query.delete()
        for obj in data["data"]:
            if ("city_id" not in obj or not obj["city_id"]): obj["city_id"] =  None 
            db.session.add(MapItem(obj["name"],obj["position"],obj['city_id'],obj['address']))
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
        #return {'data':[STATIC_FILES_URL+i for i in os.listdir(STATIC_FILES_DIR) if os.path.splitext(i)[1] in ['.jpg','.jpeg','.gif','.png']]}
        return {'data':[STATIC_FILES_SUB+i for i in os.listdir(STATIC_FILES_DIR) if os.path.splitext(i)[1] in ['.jpg','.jpeg','.gif','.png']]}

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
        q = data['data']
        q = "%"+q+"%"
        #q = q.encode('raw_unicode_escape').decode('utf-8')

        p_result = []
        b_result = []
        c_result = []
        page_search_result = BlockItem.query.filter(BlockItem.data.like(q)).all()
        blog_search_result = BlogBlockItem.query.filter(BlogBlockItem.data.like(q)).all()
        catalog_search_result = GroupCatalogItem.query.join(GroupCatalogItem.items).\
        filter(CatalogItem.item_type.like(q)).all()

        for  r in page_search_result :
            _p = r.__get_page__()
            if (_p): p_result+= [_p.__to_dict__()]

        for  r in blog_search_result :
            _b = r.__get_page__()
            if (_b): b_result+= [_b.__to_dict__()]

        for  r in catalog_search_result:
            c_result+= [r.__to_dict__()]
        return {'data':{'pages':p_result,'items':c_result,'blog':b_result}}


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


class Subscribe(Resource):
    def get(self):
        fieldnames = ['email', 'birthday', 'city', 'gender']
        result = io.StringIO()
        writer = csv.DictWriter(result, fieldnames=fieldnames)
        writer.writeheader()
        for s in  (SubscribedUsers.query.all() or []):
            writer.writerow(s.__to_dict__())
        #writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
        #writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

        response = make_response(result.getvalue())
        response.headers['content-type'] = 'text/csv'
        return response
        pass
    def put(self):
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except:
            print("cannot load json data")
        data = data['data']
        #password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
        item = SubscribedUsers(data['email'],data['birthday'],data['city'],data['gender'])
        db.session.add(item)
        db.session.commit()
        return []

    def delete(self):
        pass

class Rating(Resource):
    def put(self,id,rating):
        id = unquote_twice(id)
        rating = int(rating)
        rating = rating if rating<=5 else 5
        irating = ItemRating.query.get(id) or ItemRating(id,rating)
        irating.update_rating(rating)
        db.session.add(irating)
        db.session.commit()

class Blog(Resource):
    def get(self):
        coll = (request.args.get('categories')) or False
        if (coll):
            return {'data':[{'name':i.name,'id':i.id,'visible':i.visible} for i in BlogCategory.query.all()]}
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
            cat = (BlogCategory.query.get(i["id"]) if "id" in i else BlogCategory(i["name"])) or BlogCategory(i["name"])
            cat.name=(i["name"])
            cat.visible=(i["visible"])
            db.session.add(cat)
        db.session.commit()
        return self.get()

class BlogPageBlock(Resource):
    def get(self,page_name,alias,id):
       return BlogBlockItem.query.filter(BlogBlockItem.id==id).first().__to_dict__()

# page name - it is category name
class BlogPages(Resource):
    def get(self,page_name):
       return {'name':page_name,'subitems':[ i.__to_dict__() for i in BlogCategory.query.filter(BlogCategory.name==page_name).first().pages]}
    def post(self,page_name):
        category = BlogCategory.query.filter(BlogCategory.name==page_name).first()
        data = request.data.decode('utf-8')
        try:
            data = json.loads(data)
        except Exception:
            print("cannot load json data")
        data = data["data"]
        category_pages = []
        for page in data["subitems"]:
            page_item = BlogPageItem.query.get(page["id"]) if "id" in page else BlogPageItem("","")
            page_item.category_id = page["category_id"]
            page_item.blocks = self.__create_blocks(page['subitems'])
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
        db.session.commit()
        return self.get(page_name)

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

