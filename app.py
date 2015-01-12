from config import db, app
from flask.ext.restful import Resource, Api
from base.models import BlockItem, UserItem
from flask import request
from base import views
from flask.ext.login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)

api  = Api(app)
api.add_resource(views.Block,'/api/block/<string:alias>')
api.add_resource(views.Page,'/api/page/<string:url>')
api.add_resource(views.Auth,'/api/auth')
api.add_resource(views.User,'/api/user')
api.add_resource(views.Files,'/api/files')
api.add_resource(views.Map,'/api/map')
api.add_resource(views.City,'/api/city')
api.add_resource(views.Rights,'/api/rights/<int:group_id>')
api.add_resource(views.Search,'/api/search')


@login_manager.user_loader
def load_user(userid):
    return UserItem.query.get(userid)

if __name__ == '__main__':
    app.run(debug=True)

