from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint('Tags','tags', __name__, description="Operations on tags")

@blp.route('/store/<int:store_id>/tag')
class TagsInStore(MethodView):
  @blp.response(200, TagSchema(many=True))
  def get(self, store_id):
    store = StoreModel.query.get_or_404(store_id)
    try:
      return store.tags.all(), 200
    except SQLAlchemyError:
      abort(404, message="Tag not found.")
    
  @blp.response(200, TagSchema)
  @blp.arguments(TagSchema)
  def post(self, tag_data, store_id):
    tag = TagModel( **tag_data, store_id=store_id)
    try:
      db.session.add(tag)
      db.session.commit()
      return tag, 201
    except IntegrityError:
      abort(400, message="A tag with that name already exists.")
    except SQLAlchemyError:
      abort(500, message="An error occurred while inserting the tag.")  
      
@blp.route('/tag/<int:tag_id>')
class Tag(MethodView):
  @blp.response(200, TagSchema)
  def get(self, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    try:
      return tag, 200
    except SQLAlchemyError:
      abort(404, message="Tag not found.")
      
  @blp.response(200, description="Deletes a tag", example={"message": "Tag deleted."})
  @blp.alt_response(404, description="Tag not found.")
  @blp.alt_response(400, description="Could not delete tag.")
  def delete(self, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    if not tag.items:
      db.session.delete(tag)
      db.session.commit()
      return {"message": "Tag deleted."}, 202
    
    abort(404, message="Tag not found.")
      
@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagToItem(MethodView):
  @blp.response(201, TagSchema)
  def post(self, item_id, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    item = ItemModel.query.get_or_404(item_id)
    try:
      item.tags.append(tag)
      db.session.add(item)
      db.session.commit()
      return tag, 201
    except SQLAlchemyError:
      abort(500, message="An error occurred while linking the tag to the item.")
  
  @blp.response(200, TagSchema)
  def delete(self, item_id, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    item = ItemModel.query.get_or_404(item_id)
    try:
      item.tags.remove(tag)
      db.session.add(item)
      db.session.commit()
      return {"message": "Tag unlinked from item successfully.", "item": item, "tag": tag}, 200
    except SQLAlchemyError:
      abort(500, message="An error occurred while unlinking the tag from the item.")
      