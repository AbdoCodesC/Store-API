from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from models import StoreModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint('Stores','stores', __name__, description="Operations on stores")

@blp.route('/store/<int:store_id>')
class Store(MethodView):
  @blp.response(200, StoreSchema)
  def get(self, store_id):
    try:
      return StoreModel.query.get_or_404(store_id), 200
    except SQLAlchemyError:
      abort(404, message="Store not found.")
  
  def delete(self, store_id):
    store = StoreModel.query.get_or_404(store_id)
    # items = store.items
    try:
      # for item in items:
      #   db.session.delete(item)
      db.session.delete(store)
      db.session.commit()
      return {"message": "Store deleted."}
    except IntegrityError:
      db.session.rollback()
      abort(400, message="Could not delete store with items.")
    except SQLAlchemyError:
      abort(404, message="Store not found.")

@blp.route('/store')
class StoreList(MethodView):
  @blp.response(200, StoreSchema(many=True))
  def get(self):
    return StoreModel.query.all(), 200
  
  @blp.arguments(StoreSchema)
  @blp.response(201, StoreSchema)
  def post(self, store_data):
    store = StoreModel(**store_data)
    try:
      db.session.add(store)
      db.session.commit()
      return store, 201
    except IntegrityError:
      abort(400, message="A store with that name already exists.")
    except SQLAlchemyError:
      abort(500, message="An error occurred while inserting the store.")