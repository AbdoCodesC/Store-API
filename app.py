from datetime import timedelta
from models.blocklist import TokenBlocklist
from flask import Flask, jsonify
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from db import db
import os
import dotenv
dotenv.load_dotenv()
from flask_jwt_extended import JWTManager

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
  app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')  # change this in real apps!
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
  
  db.init_app(app)
  with app.app_context():
    db.create_all()
  
  api = Api(app)
  jwt = JWTManager(app)
  
  @jwt.token_in_blocklist_loader
  def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    jti = TokenBlocklist.query.filter_by(jti=jti).first()
    print("Checking if token is in blocklist:", jti is not None)
    return jti is not None
  
  @jwt.revoked_token_loader
  def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has been revoked.", "error": "token_revoked"}), 401
  
  @jwt.additional_claims_loader
  def add_claims_to_jwt(identity):
    # Identity is passed as-is from create_access_token before JSON serialization
    if int(identity) == 1:
      return {'is_admin': True}
    return {'is_admin': False}
  
  @jwt.expired_token_loader
  def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401
  
  
  @jwt.invalid_token_loader
  def invalid_token_callback(error):
    return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401
  
  @jwt.unauthorized_loader
  def missing_token_callback(error):
    return jsonify({"message": "Request does not contain an access token.", "error": "authorization_required"}), 401
  
  api.register_blueprint(ItemBlueprint)
  api.register_blueprint(StoreBlueprint)
  api.register_blueprint(TagBlueprint)
  api.register_blueprint(UserBlueprint)

  return app

if __name__ == '__main__':
  application = createApp()
  application.run(port=3000, debug=True)