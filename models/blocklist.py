from db import db

class TokenBlocklist(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  jti = db.Column(db.String(128), nullable=False, index=True) # index for faster lookups