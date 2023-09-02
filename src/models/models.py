from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Ad(db.Model):
    __tablename__ = 'ads'

    id = db.Column(db.Integer, primary_key=True)
    ad_copy = db.Column(db.String(255), nullable=False)
    target_audiences = db.Column(db.String(255), nullable=False)
    keyword_recommendations = db.Column(db.String(255), nullable=False)
    clicks_number = db.Column(db.Integer, nullable=False, default=0)
    approved = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    interactions = db.relationship(
            'UserInteraction', backref='ad', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, ad_copy, target_audiences, keyword_recommendations, clicks_number, approved, user_id):
        self.ad_copy = ad_copy
        self.target_audiences = target_audiences
        self.keyword_recommendations = keyword_recommendations
        self.clicks_number = clicks_number
        self.approved = approved
        self.user_id = user_id

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    ads = db.relationship('Ad', backref='user', lazy=True, cascade='all, delete-orphan')

    interactions = db.relationship(
        'UserInteraction', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, username, password, role):
        self.username = username
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        self.password = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('ads.id'), nullable=False)
    clicked = db.Column(db.Boolean, default=False)