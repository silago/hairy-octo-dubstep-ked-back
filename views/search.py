import sys, os, io
from flask.ext.restful import Resource, Api
from flask import request, g, session, make_response
from base.models import *
import json
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL, STATIC_FILES_SUB, ROOT_DIR
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.cors import CORS, cross_origin

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
