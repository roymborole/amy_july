# models.py

from extensions import db
from flask_security import UserMixin, RoleMixin
import uuid
from datetime import datetime, timedelta

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    reports_generated = db.Column(db.Integer, default=0)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))
    trial_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    trial_end_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    is_trial_active = db.Column(db.Boolean, default=True)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if not self.fs_uniquifier:
            self.fs_uniquifier = str(uuid.uuid4())

class TempSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    asset_name = db.Column(db.String(120), nullable=False)
    confirmation_token = db.Column(db.String(36), unique=True, nullable=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    asset_name = db.Column(db.String(120), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

class PendingSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    asset_name = db.Column(db.String(120), nullable=False)
    confirmation_token = db.Column(db.String(120), nullable=False)

def check_trial_status(user):
    if user.trial_end_date < datetime.utcnow():
        user.is_trial_active = False
        db.session.commit()