from config import db, app
from flask.ext.restful import Resource, Api
from flask import request
#from base import views
from views import subscribe, pages, blog, auth, catalog, files, search, buy

from flask.ext.login import LoginManager
from base.models import UserItem


login_manager = LoginManager()
login_manager.init_app(app)

api  = Api(app)

#@api.representation('text/csv')
#def csv(data, code, headers=None):
#    resp = api.make_response(data, code)
#    resp.headers.extend(headers or {})
#    return resp

api.add_resource(subscribe.Subscribe,'/api/subscribe')
api.add_resource(pages.Block,'/api/block/<string:alias>')
api.add_resource(pages.Page,'/api/page/<string:url>')
api.add_resource(blog.Blog,'/api/blog')
api.add_resource(blog.BlogPages,'/api/blog/<string:url>')
api.add_resource(blog.BlogPageBlock,'/api/blog/<string:page_name>/<string:alias>')
api.add_resource(auth.Auth,'/api/auth')
api.add_resource(auth.User,'/api/user')
api.add_resource(files.Files,'/api/files')
#api.add_resource(views.Map,'/api/map')
#api.add_resource(ymap.Map,'/api/map')
#api.add_resource(ymap.City,'/api/city')
api.add_resource(auth.Rights,'/api/rights/<int:group_id>')
api.add_resource(search.Search,'/api/search')
#api.add_resource(views.Catalog,'/api/catalog')
#api.add_resource(views.Gcatalog,'/api/gcatalog')


# vesna / man / item
#api.add_resource(views.Catalog,'/api/catalog/')

# show all collections
#api.add_resource(CatalogCollections,'/api/catalog')

# show segments from actvie collection if no specific collections is provided
api.add_resource(catalog.Rating,'/api/rate/<string:id>/<string:rating>')
api.add_resource(catalog.CatalogCollections,'/api/catalog')
api.add_resource(catalog.CatalogSegments,'/api/catalog/collection')
api.add_resource(catalog.CatalogTypes,'/api/catalog/collection/<string:slug>/')
api.add_resource(catalog.CatalogItems,'/api/catalog/collection/<string:segment_slug>/<string:type_slug>/')
api.add_resource(catalog.CatalogItemData,'/api/catalog/collection/<string:segment_slug>/<string:type_slug>/<string:sku>/')


#api.add_resource(catalog.Rating,'/api/rate/<string:id>/<string:rating>')
api.add_resource(buy.SideCatalogCollections,'/api/sidecatalog')
api.add_resource(buy.SideCatalogSegments,   '/api/sidecatalog/collection')
api.add_resource(buy.SideCatalogTypes,      '/api/sidecatalog/collection/<string:slug>/')
api.add_resource(buy.SideCatalogItems,      '/api/sidecatalog/collection/<string:segment_slug>/<string:type_slug>/')
api.add_resource(buy.SideCatalogItemData,   '/api/sidecatalog/collection/<string:segment_slug>/<string:type_slug>/<string:sku>/')

@login_manager.user_loader
def load_user(userid):
    return UserItem.query.get(userid)

if __name__ == '__main__':
    app.run(debug=True)

