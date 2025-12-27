from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel, StoreModel
from db import db

blp = Blueprint('items', __name__, description="Operatios on items")

@blp.route('/item/<string:item_id>')
class Item(MethodView):
  @blp.response(200, ItemSchema)
  def get(self, item_id):
    item = db.get_or_404(ItemModel, item_id)
    try:
      return item, 200
    except KeyError:
      abort(404, message="Item not found.")
      
  @blp.arguments(ItemUpdateSchema)
  @blp.response(200, ItemSchema)
  def put(self, item_data, item_id):
    item = db.get_or_404(ItemModel, item_id)
    try:
      item.name, item.price = item_data['name'], item_data['price']
      db.session.commit()
      return item, 200
    except SQLAlchemyError:
      abort(404, message="Item not found.")
      
  def delete(self, item_id):
    item = db.get_or_404(ItemModel, item_id)
    try:
      db.session.delete(item)
      db.session.commit()
      return {"message": "Item deleted."}
    except SQLAlchemyError:
      abort(404, message="Item not found.")
    
@blp.route('/item')      
class ItemList(MethodView):
  @blp.response(200, ItemSchema(many=True))
  def get(self):
    return db.session.query(ItemModel).all()
  
  @blp.arguments(ItemSchema)
  @blp.response(201, ItemSchema)
  def post(self, item_data):
    item = ItemModel(**item_data)
    try:   
      db.session.add(item)
      db.session.commit()
      return item, 201
    except SQLAlchemyError:
      abort(500, message="An error occurred while inserting the item.")
   