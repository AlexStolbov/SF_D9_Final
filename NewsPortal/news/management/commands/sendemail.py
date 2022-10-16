# runapscheduler.py
import logging

from datetime import datetime

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from news.models import Category, Post
from django.utils import timezone

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def send_email_to_subscribers():
    """
    Если пользователь подписан на какую-либо категорию, то каждую неделю ему приходит
    на почту список новых статей, появившийся за неделю с гиперссылкой на них,
    чтобы пользователь мог перейти и прочесть любую из статей.
    """
    for category in Category.objects.all():
        today = datetime.now()
        start = datetime(today.year, today.month, today.day - 7, tzinfo=timezone.utc)
        finish = datetime(today.year, today.month, today.day, 23, 59, 59, 999999, tzinfo=timezone.utc)
        posted_last_weeks = Post.objects.filter(created__range=[start, finish]).filter(category=category)

        if posted_last_weeks:

            subject = f'News of last week of {category}'

            domain = settings.CURRENT_HOST

            for current_user in category.subscribers.all():
                print(f'send email of cat {category} to user {current_user}')

                html_content = render_to_string(
                    'news_last_week_to_subscr.html',
                    {
                        'posted': posted_last_weeks,
                        'domain': domain,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body='',
                    from_email='',
                    to=[current_user.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_email_to_subscribers,
            # trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            trigger=CronTrigger(second="*/10"),
            id="send_email_to_subscribers",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
