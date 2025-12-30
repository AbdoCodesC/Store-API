from datetime import timedelta
from models.blocklist import TokenBlocklist
from flask import Flask, jsonify
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from db import db
from flask_migrate import Migrate
import os
from flask_jwt_extended import JWTManager

def create_app(db_url=None):
  app = Flask(__name__)
  app.config['PROPAGATE_EXCEPTIONS'] = True
  app.config['API_TITLE'] = 'Stores REST API'
  app.config['API_VERSION'] = 'v1'
  app.config['OPENAPI_VERSION'] = '3.0.3'
  app.config['OPENAPI_URL_PREFIX'] = '/'
  app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
  app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
  app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('FLASK_DATABASE_URI', 'sqlite:///data.db')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
  app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'super-secret-key')  # change this in real apps!
  print('JWT secret key: ', os.getenv('JWT_SECRET_KEY', 'super-secret-key'))
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
  app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
  
  db.init_app(app)
  migrate = Migrate(app, db)
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
  
  @jwt.needs_fresh_token_loader
  def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token is not fresh.", "error": "fresh_token_required"}), 401
  
  @jwt.additional_claims_loader
  def add_claims_to_jwt(identity):
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
  application = create_app()
  application.run(port=3000, debug=True)