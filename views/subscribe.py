import sys, os, io
from flask.ext.restful import Resource, Api
from flask import request, g, session, make_response
from base.models import *
import json
from config import db, STATIC_FILES_DIR, STATIC_FILES_URL, STATIC_FILES_SUB, ROOT_DIR
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.cors import CORS, cross_origin

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
