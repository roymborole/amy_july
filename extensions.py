from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import os


db = SQLAlchemy()
migrate = Migrate()

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

if not redis_url.startswith('redis://'):
    redis_url = 'redis://' + redis_url

celery = Celery(__name__, broker=redis_url, backend=redis_url)

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