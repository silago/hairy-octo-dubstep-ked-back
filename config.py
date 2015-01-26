from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS, cross_origin

DEBUG=True

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'sooooseeecreet'
CORS(app, resources={r'/api/*':{"origins":"http://localhost:9000","supports_credentials":True}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_ECHO']=True
db = SQLAlchemy(app)
STATIC_FILES_DIR = '/home/silago/work/keddo/application/frontend/app/static'
STATIC_FILES_URL = 'http://localhost:9000/static/'
