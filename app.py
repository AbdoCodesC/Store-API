from flask import Flask
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from db import db
import models
import os

app = Flask(__name__)

def createApp(db_url=None):
  app.config['PROPAGATE_EXCEPTIONS'] = True
  app.config['API_TITLE'] = 'Stores REST API'
  app.config['API_VERSION'] = 'v1'
  app.config['OPENAPI_VERSION'] = '3.0.3'
  app.config['OPENAPI_URL_PREFIX'] = '/'
  app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
  app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
  # sqlalchemy database uri
  app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('FLASK_DATABASE_URI', 'sqlite:///data.db')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

  db.init_app(app)
  with app.app_context():
    db.create_all()
  
  api = Api(app)
  api.register_blueprint(ItemBlueprint)
  api.register_blueprint(StoreBlueprint)

  return app

if __name__ == '__main__':
  application = createApp()
  application.run(port=3000, debug=True)