import os
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from mixpanel import Mixpanel

db = SQLAlchemy()
migrate = Migrate()

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

mp_eu = Mixpanel(os.getenv('MIXPANEL_TOKEN'))

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