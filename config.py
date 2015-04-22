from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS, cross_origin
import os


import re
_punct_re = re.compile(r'[ !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim='-'):
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return delim.join(result)

DEBUG=True

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'sooooseeecreet'
CORS(app, resources={r'/api/*':{"origins":"http://localhost:9000","supports_credentials":True}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#app.config['SQLALCHEMY_ECHO']=True
db = SQLAlchemy(app)

#print("!!!!")
#print("!!!!")


ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../frontend/app/')
#ROOT_DIR  = '/home/silago/work/keddo/application/frontend/app/'
STATIC_FILES_SUB = 'static/'
STATIC_FILES_DIR = ROOT_DIR+STATIC_FILES_SUB 
STATIC_FILES_URL = 'static/'
SIDE_CATALOG_URL = 'http://yyees.com/upload/marketing.csv'
