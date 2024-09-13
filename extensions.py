import os
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from flask_mail import Mail
from flask_security import Security

db = SQLAlchemy()
security = Security()
migrate = Migrate()
celery = Celery()
mail = Mail()

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', '')

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True  # This ensures responses are returned as strings, not bytes
)


def get_redis_url():
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_password = os.getenv('REDIS_PASSWORD', '')
    if redis_password:
        return f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
    return f"redis://{redis_host}:{redis_port}/0"

redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
celery = Celery(__name__, broker=redis_url, backend=redis_url)

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

celery = Celery(__name__)

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

redis_client = None

def init_redis(app):
    global redis_client
    redis_url = app.config.get('REDIS_URL')
    if redis_url:
        redis_client = redis.from_url(redis_url)
    else:
        raise ValueError("REDIS_URL not set in configuration")

def create_celery_app(app):
    celery.main = app.import_name
    return celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery