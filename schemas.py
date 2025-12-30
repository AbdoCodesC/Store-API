from marshmallow import Schema, fields

class PlainItemSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  price = fields.Float(required=True)
  
class ItemUpdateSchema(Schema):
  name = fields.Str()
  price = fields.Float()
  store_id = fields.Int()
  
class PlainStoreSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  
class PlainTagSchema(Schema):
  id = fields.Int(dump_only=True)  
  name = fields.Str(required=True)
  store_id = fields.Int(required=True)
  
class ItemSchema(PlainItemSchema):
  store_id = fields.Int(required=True, load_only=True)
  store = fields.Nested(PlainStoreSchema(), dump_only=True)
  tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class StoreSchema(PlainStoreSchema):
  items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
  tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)
  
class TagSchema(PlainTagSchema):
  store_id = fields.Int(load_only=True)
  store = fields.Nested(PlainStoreSchema(), dump_only=True)
  items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

class TagAndItemSchema(Schema):
  message = fields.Str()
  item = fields.Nested(PlainItemSchema())
  tag = fields.Nested(PlainTagSchema())
  
class UserSchema(Schema):
  id = fields.Int(dump_only=True)
  email = fields.Str(required=True)
   # load only = true does not return password when deserializing data
  password = fields.Str(required=True, load_only=True)
  