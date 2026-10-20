from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Create the daily report periodic task'

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='9',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='Asia/Kolkata',
        )

        task, created = PeriodicTask.objects.get_or_create(
            name='Daily report email',
            defaults={'crontab': schedule, 'task': 'emails.tasks.send_daily_report'},
        )

        action = 'Created' if created else 'Already exists'
        self.stdout.write(f'{action}: {task.name} (9:00 AM Asia/Kolkata daily)')
