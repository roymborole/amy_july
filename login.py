from flask import Blueprint
from flask_security import SQLAlchemyUserDatastore
from extensions import security
from models import User, Role

auth_bp = Blueprint('auth', __name__)


def init_auth(app, db):
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)