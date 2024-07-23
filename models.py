# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    reports_generated = db.Column(db.Integer, default=0)

# Add other models as needed
class TempSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    asset_name = db.Column(db.String(120), nullable=False)
    confirmation_token = db.Column(db.String(36), unique=True, nullable=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    asset_name = db.Column(db.String(120), nullable=False)