from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from ...tasks import add_attendance_records
from django.utils import timezone
from django.conf import settings

scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler.add_job(add_attendance_records, "cron", day_of_week="thu", hour=0, replace_existing=True)
        # scheduler.add_job(add_attendance_records, "cron", minute='*', replace_existing=True)
        register_events(scheduler)
        scheduler.start()
        
def printDate():
    time = timezone.now().strftime('%X')
    print("It's now %s" % time)