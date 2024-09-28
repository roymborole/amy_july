from flask import Blueprint
from flask_security import SQLAlchemyUserDatastore
from flask_security import current_user, login_required
from models import User, Role

