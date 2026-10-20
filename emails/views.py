import json
import re

from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .tasks import send_bulk_email_task, send_email_task

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validate(data):
    errors = []
    recipient = data.get('recipient')
    recipients = data.get('recipients')

    if recipients is None and recipient is None:
        errors.append('recipient or recipients is required')
    elif recipients is not None and not isinstance(recipients, list):
        errors.append('recipients must be a list')
    else:
        for address in recipients or [recipient]:
            if not isinstance(address, str) or not EMAIL_RE.match(address):
                errors.append(f'invalid email address: {address}')

    if not data.get('subject'):
        errors.append('subject is required')
    if not data.get('message'):
        errors.append('message is required')

    return errors


@csrf_exempt
def send_email(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'errors': ['invalid JSON body']}, status=400)

    errors = validate(data)
    if errors:
        return JsonResponse({'errors': errors}, status=400)

    subject = data['subject']
    message = data['message']
    template = data.get('template')
    context = data.get('context', {'subject': subject, 'message': message})

    if data.get('recipients'):
        task = send_bulk_email_task.delay(data['recipients'], subject, message, template, context)
    else:
        task = send_email_task.delay(data['recipient'], subject, message, template, context)

    return JsonResponse({'task_id': task.id, 'status': 'queued'}, status=202)


def email_status(request, task_id):
    result = AsyncResult(task_id)
    return JsonResponse({
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None,
    })


def email_form(request):
    return render(request, 'emails/form.html')
