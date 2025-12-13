# backend/celery_beat.py
from celery import Celery
from celery.schedules import crontab
import os 
import dotenv
dotenv.load_dotenv()

app = Celery('reputrack', broker=os.getenv("REDIS_URL"))
# command = celery -A app.celery_tasks beat --loglevel=info
app.conf.beat_schedule = {
    'scrape-every-14-days': {
        'task': 'celery_tasks.scrape_and_analyze_all',
        'schedule': crontab(hour=3, minute=0, day_of_month='1,15'),  # 1st & 15th at 3 AM
    },
}
app.conf.timezone = 'UTC'