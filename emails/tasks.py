import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def build_email(recipients, subject, message, template=None, context=None):
    mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
    if template:
        html = render_to_string(f'emails/{template}.html', context or {})
        mail.attach_alternative(html, 'text/html')
    return mail


@shared_task(bind=True, max_retries=3)
def send_email_task(self, recipient_email, subject, message, template=None, context=None):
    try:
        mail = build_email([recipient_email], subject, message, template, context)
        mail.send()
    except Exception as exc:
        logger.error('Email to %s failed: %s', recipient_email, exc)
        raise self.retry(exc=exc, countdown=30)

    logger.info('Email sent to %s', recipient_email)
    return f'sent to {recipient_email}'


@shared_task
def send_bulk_email_task(recipient_list, subject, message, template=None, context=None):
    sent, failed = [], []

    for recipient in recipient_list:
        try:
            build_email([recipient], subject, message, template, context).send()
            sent.append(recipient)
        except Exception as exc:
            logger.error('Email to %s failed: %s', recipient, exc)
            failed.append(recipient)

    logger.info('Bulk email: %d sent, %d failed', len(sent), len(failed))
    return {'sent': sent, 'failed': failed}


@shared_task
def send_daily_report():
    recipients = [settings.DEFAULT_FROM_EMAIL]
    send_bulk_email_task.delay(recipients, 'Daily Report', 'Your scheduled daily report.')
    return f'report queued for {len(recipients)} recipients'
