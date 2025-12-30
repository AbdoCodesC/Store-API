from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel, StoreModel
from db import db
from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint('Items','items', __name__, description="Operations on items")

@blp.route('/item/<int:item_id>')
class Item(MethodView):
  @blp.response(200, ItemSchema)
  def get(self, item_id):
    item = ItemModel.query.get_or_404(item_id)
    try:
      return item, 200
    except KeyError:
      abort(404, message="Item not found.")
      
  @blp.arguments(ItemUpdateSchema)
  @blp.response(200, ItemSchema)
  @jwt_required()
  def put(self, item_data, item_id):
    item = ItemModel.query.get(item_id)
    
    if item:
      item.name, item.price = item_data['name'], item_data['price']
    else:
      item = ItemModel(id=item_id, **item_data)
    
    try:
      db.session.add(item) 
      db.session.commit()
      return item, 200
    except SQLAlchemyError:
      db.session.rollback()
      abort(400, message="An item with that name already exists.")
    
  @jwt_required()
  def delete(self, item_id):
    item = ItemModel.query.get_or_404(item_id)
    jwt = get_jwt()
    print('jwt is_admin',get_jwt(),jwt.get('is_admin'))
    if not jwt.get('is_admin'):
        abort(401, message="Admin privilege required.")
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
  @jwt_required()
  def post(self, item_data):
    item = ItemModel(**item_data)
    try:   
      db.session.add(item)
      db.session.commit()
      return item, 201
    except SQLAlchemyError:
      abort(500, message="An error occurred while inserting the item.")
   