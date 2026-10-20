# Django Celery Email

Background email sending with Celery and Redis. API endpoints, HTML templates,
retries on failure, and a daily scheduled email.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Gmail address and a 16-character app
password (Google Account > Security > App passwords — the normal password won't work).

```bash
python manage.py migrate
python manage.py setup_periodic_tasks
```

## Running

Four terminals:

```bash
docker run -d -p 6379:6379 redis:7-alpine
celery -A config worker -l info --pool=solo
celery -A config beat -l info
python manage.py runserver
```

Form at http://localhost:8000/, admin at /admin/. `--pool=solo` is needed on Windows.

## API

```bash
curl -X POST localhost:8000/api/send-email/ -H "Content-Type: application/json" \
  -d '{"recipient":"someone@gmail.com","subject":"Hello","message":"Sent in the background"}'
```

Returns `{"task_id": "...", "status": "queued"}`. Check it with:

```bash
curl localhost:8000/api/email-status/<task_id>/
```

Status is PENDING, RETRY, SUCCESS or FAILURE.

Use `recipients` as a list to send to several people. Add `"template": "welcome"`
or `"notification"` for HTML, with `context` for the values. Bad requests get a 400
before anything is queued.

## Tasks

- `send_email_task` — one recipient, retries 3 times 30 seconds apart
- `send_bulk_email_task` — many recipients, reports which worked
- `send_daily_report` — daily at 9 AM via a crontab in Celery Beat

Schedules live in the database so they can be edited in the admin under Periodic
Tasks without restarting beat.

## Settings

Gmail SMTP on port 587 with TLS, credentials from `.env`. Timezone is Asia/Kolkata
for both Django and Celery.

## Layout

```
config/    celery.py  settings.py
emails/    tasks.py  views.py  urls.py
           templates/emails/  (base, welcome, notification, form)
           management/commands/setup_periodic_tasks.py
```
