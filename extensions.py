import os
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from flask_mail import Mail
from celery.schedules import crontab

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

# Celery configuration
celery = Celery(__name__)

def get_redis_url():
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    redis_password = os.getenv('REDIS_PASSWORD', '')
    if redis_password:
        return f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
    return f"redis://{redis_host}:{redis_port}/0"

redis_url = get_redis_url()
celery.conf.broker_url = redis_url
celery.conf.result_backend = redis_url

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    init_celery(app)
    init_redis(app)
    
    from analytics import init_mixpanel
    init_mixpanel(app)

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

def init_redis(app):
    redis_url = app.config.get('REDIS_URL', get_redis_url())
    app.redis = redis.from_url(redis_url)

@celery.task
def check_and_update_trial_statuses():
    from models import User, check_trial_status
    
    users = User.query.filter_by(is_trial_active=True).all()
    for user in users:
        check_trial_status(user)
    db.session.commit()

celery.conf.beat_schedule = {
    'check-trial-statuses-daily': {
        'task': 'extensions.check_and_update_trial_statuses',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}