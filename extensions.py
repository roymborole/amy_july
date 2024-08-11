from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from ddtrace import patch

patch(sqlalchemy=True)

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

def make_celery(app):
    global celery
    celery.conf.update(app.config)
    return celery