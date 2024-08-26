
from extensions import celery
from weekly_reports import process_weekly_reports

@celery.task
def send_weekly_reports():
    process_weekly_reports()
pass

from celery.schedules import crontab

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls send_weekly_reports every Monday at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        send_weekly_reports.s(),
    )

