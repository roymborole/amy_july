from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from ddtrace import patch
patch(sqlalchemy=True)

db = SQLAlchemy()
migrate = Migrate()

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)