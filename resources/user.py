import datetime
from db import db
from models import UserModel, TokenBlocklist
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import UserSchema
from passlib.hash import pbkdf2_sha256 as sha
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# Blueprint(name, import_name, **kwargs)
blp = Blueprint('Users','users', __name__, description="Operations on users")

@blp.route('/user/<int:user_id>')
class User(MethodView):
  @blp.response(200, UserSchema)
  def get(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    try:
      return user, 200
    except SQLAlchemyError:
      abort(404, message="User not found.")
  
  def delete(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    try:
      db.session.delete(user)
      db.session.commit()
      return {"message": "User deleted."}
    except SQLAlchemyError:
      abort(404, message="User not found.")
  
  @blp.arguments(UserSchema)
  def put(self, user_data, user_id):
    user = UserModel.query.get(user_id)
    if user:
      user.username = user_data['username']
      user.password = sha.using(rounds=10).hash(user_data['password'])
    else:
      user = UserModel(id=user_id, username=user_data['username'], password=sha.using(rounds=10).hash(user_data['password'])) # create new user if not exists
    try:
      db.session.add(user)
      db.session.commit()
      return user, 200
    except SQLAlchemyError:
      abort(500, message="An error occurred while updating the user.")

@blp.route('/user')
class UserList(MethodView):
  @blp.response(200, UserSchema(many=True))
  def get(self):
    return UserModel.query.all(), 200
  
  # register new user
  @blp.response(201, description="User created", example={"message": "User created successfully."})
  @blp.arguments(UserSchema)
  def post(self, user_data):
    user = UserModel(username=user_data['username'], password=sha.using(rounds=10).hash(user_data['password']))
    
    try:
      db.session.add(user)
      db.session.commit()
      return {"message": "User created successfully."}, 201
    except SQLAlchemyError:
      abort(500, message="An error occurred while inserting the user.")
    except IntegrityError:
      abort(400, message="A user with that username already exists.")
  
@blp.route('/login')
class UserLogin(MethodView):
  @blp.response(200, description="User login", example={"message": "Login successful."})
  @blp.arguments(UserSchema)
  def post(self, user_data):
    user = UserModel.query.filter_by(username=user_data['username']).first()
    try:
      if user and user.compare_password(user_data['password'], user.password):
        response = jsonify({"msg": "login successful"})
        access_token = create_access_token(identity=str(user.id))
        return {"message": "Login successful.", "access_token": access_token}, 200
      else:
        abort(401, message="Invalid credentials.")
    except SQLAlchemyError:
      abort(500, message="An error occurred during login.")
      
  #test: user still logged in
  @jwt_required() # might cause issue.
  @blp.response(200)
  def get(self):
    user_id = get_jwt_identity()
    user = UserModel.query.get_or_404(int(user_id))
    return {"message": f"User {user.username} is logged in."}, 200
      
@blp.route('/logout')
class UserLogout(MethodView):
  @jwt_required()
  @blp.response(200, description="User logout", example={"message": "Logout successful."})
  def post(self):
    try:
      jti = get_jwt()["jti"]
      token = TokenBlocklist(jti=jti)
      db.session.add(token)
      db.session.commit()
      return {"message": "Logout successful."}, 200
    except SQLAlchemyError:
      abort(500, message="An error occurred during logout.")  