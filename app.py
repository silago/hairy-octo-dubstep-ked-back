from config import db, app
from flask.ext.restful import Resource, Api
from base.models import BlockItem, UserItem
from flask import request
from base import views
from flask.ext.login import LoginManager


login_manager = LoginManager()
login_manager.init_app(app)

api  = Api(app)

#@api.representation('text/csv')
#def csv(data, code, headers=None):
#    resp = api.make_response(data, code)
#    resp.headers.extend(headers or {})
#    return resp

api.add_resource(views.Subscribe,'/api/subscribe')
api.add_resource(views.Block,'/api/block/<string:alias>')
api.add_resource(views.Page,'/api/page/<string:url>')
api.add_resource(views.Blog,'/api/blog')
api.add_resource(views.BlogPages,'/api/blog/<string:page_name>')
api.add_resource(views.BlogPageBlock,'/api/blog/<string:page_name>/<string:alias>/<string:id>')
api.add_resource(views.Auth,'/api/auth')
api.add_resource(views.User,'/api/user')
api.add_resource(views.Files,'/api/files')
#api.add_resource(views.Map,'/api/map')
api.add_resource(views.Map,'/api/map')
api.add_resource(views.City,'/api/city')
api.add_resource(views.Rights,'/api/rights/<int:group_id>')
api.add_resource(views.Search,'/api/search')
#api.add_resource(views.Catalog,'/api/catalog')
api.add_resource(views.Gcatalog,'/api/gcatalog')


# vesna / man / item
#api.add_resource(views.Catalog,'/api/catalog/')
api.add_resource(views.Rating,'/api/rate/<string:id>/<string:rating>')
api.add_resource(views.CatalogCollections,'/api/catalog')
api.add_resource(views.CatalogSegments,'/api/catalog/collection')
api.add_resource(views.CatalogTypes,'/api/catalog/collection/<string:segment_alias>/')
api.add_resource(views.CatalogGroups,'/api/catalog/collection/<string:segment_alias>/<string:type_alias>/')
api.add_resource(views.CatalogItems,'/api/catalog/collection/<string:segment_alias>/<string:type_alias>/<string:group_id>/')


@login_manager.user_loader
def load_user(userid):
    return UserItem.query.get(userid)

if __name__ == '__main__':
    app.run(debug=True)

