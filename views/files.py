import sys, os, io
from flask.ext.restful import Resource, Api
from flask import request, g, session, make_response
from base.models import *
import json
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL, STATIC_FILES_SUB, ROOT_DIR
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.cors import CORS, cross_origin
from views.common import unquote_twice

class Files(Resource):
    def get(self,dir=''):
        if (dir): dir = unquote_twice(dir)
        #return {'data':[STATIC_FILES_URL+i for i in os.listdir(STATIC_FILES_DIR) if os.path.splitext(i)[1] in ['.jpg','.jpeg','.gif','.png']]}
        return {'data':[ {'path': STATIC_FILES_URL+i,'type': 'dir' if os.path.isdir(os.path.join(STATIC_FILES_DIR,dir,i)) else 'file'} for i in os.listdir(os.path.join(STATIC_FILES_DIR,dir)) if os.path.splitext(i)[1] in ['.jpg','.jpeg','.gif','.png'] or os.path.isdir(os.path.join(STATIC_FILES_DIR,dir,i)) ] }

    #@login_required
    def post(self):
        file = request.files["Files"]
        if file:
            filename = str(time())+secure_filename(file.filename)
            file.save(os.path.join(STATIC_FILES_DIR,filename))
        return self.get()
