# application DataBase model의 스크립트 파일
from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(32), unique=True)
    username = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(225))
    member_since = db.Column(db.DateTime(), default=datetime.now)
    profile_name = db.Column(db.String(200), default='default-profile.png')