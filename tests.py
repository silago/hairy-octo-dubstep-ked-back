import os
import unittest
from flask import Flask
from flask.ext.testing import TestCase
from app import app,db
from base.models import MenuItem
import json

#from config import db, app
#from flask.ext.restful import Resource, Api
#from base.models import MenuItem

class DbTest(TestCase):
    TESTING  = True
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class MenuCase(DbTest):
    def create_app(self):
        
        #app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    def setUp(self):
        DbTest.setUp(self)
        item = MenuItem(None,'test_item','test_url')
        db.session.add(item)
        db.session.commit()

    def test_get_existing_menu_item(self):
        response = self.client.get('/menu/1/')
        self.assertEqual(response.json,dict({'id':1,'parent_id':None,'title':'test_item','url':'test_url'}))

    def test_get_unexisting_menu_item(self):
        response = self.client.get('/menu/9999/')
        self.assertEqual(response.json,dict())

    def test_add_menu_item(self):
        item = MenuItem(None,'test_item','test_url')
        # item_id should be equal 2
        data = json.dumps({'title':'subitem','url':'suburl'})
        response = self.client.put('/menu/1/',data=data,content_type='application/json')
        self.assertEqual(response.json,dict({'id':2,'parent_id':1,'title':'subitem','url':'suburl'}))



if __name__ == '__main__':
    unittest.main()
