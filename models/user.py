from db import db 
from passlib.hash import pbkdf2_sha256 as sha

class UserModel(db.Model):
  __tablename__ = 'users'
  
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String(80), nullable=False)
  
  def compare_password(self, password: str, hashedPassword: str) -> bool:
    try:
      return sha.verify(password, hashedPassword)
    except ValueError:
      return password == hashedPassword
  