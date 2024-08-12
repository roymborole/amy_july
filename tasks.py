from celery_worker import celery
from flask import current_app
from weekly_reports import process_weekly_reports

@celery.task
def send_weekly_reports():
    with current_app.app_context():
        process_weekly_reports()