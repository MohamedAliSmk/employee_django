# base/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from base.tasks import add_attendance_records

scheduler = None

def start():
    global scheduler
    if not scheduler or not scheduler.running:
        scheduler = BackgroundScheduler()
        # scheduler.add_job(add_attendance_records, 'interval', minutes=2)
        scheduler.add_job(add_attendance_records, 'cron', day_of_week='thu', hour=22, minute=0)
        scheduler.start()
