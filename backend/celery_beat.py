# backend/celery_beat.py
from celery import Celery
from celery.schedules import crontab

app = Celery('reputrack', broker='redis://default:AXr_AAIncDJjNGE2ZTc5M2JiYmM0YjQ0OWE2OTlmZjdlYjU5YzJmNXAyMzE0ODc@factual-dodo-31487.upstash.io:6379')

app.conf.beat_schedule = {
    'scrape-every-14-days': {
        'task': 'celery_tasks.scrape_and_analyze_all',
        'schedule': crontab(hour=3, minute=0, day_of_month='1,15'),  # 1st & 15th at 3 AM
    },
}
app.conf.timezone = 'UTC'