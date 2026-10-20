# Django Celery Email

Sends email in the background using Celery with Redis as the broker.
Has API endpoints, HTML templates, retries on failure, and a daily scheduled email.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put in your Gmail address and a 16-character
app password (Google Account > Security > App passwords — your normal password won't work).

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

Form at http://localhost:8000/, admin at http://localhost:8000/admin/

`--pool=solo` is needed on Windows, otherwise the worker picks up tasks but never runs them.

## API

Send an email:

```bash
curl -X POST localhost:8000/api/send-email/ -H "Content-Type: application/json" \
  -d '{"recipient":"someone@gmail.com","subject":"Hello","message":"Sent in the background"}'
```

```json
{"task_id": "10c5b604-2379-49c1-8f53-90986ba15a21", "status": "queued"}
```

Check it:

```bash
curl localhost:8000/api/email-status/10c5b604-2379-49c1-8f53-90986ba15a21/
```

```json
{"task_id": "10c5b604-...", "status": "SUCCESS", "result": "sent to someone@gmail.com"}
```

Status is PENDING, RETRY, SUCCESS or FAILURE.

Use `recipients` as a list instead of `recipient` to send to several people.
Add `"template": "welcome"` or `"notification"` for HTML, with `context` for the template values.

Bad requests get a 400 before anything is queued — missing fields, invalid email, broken JSON.

## Tasks

- `send_email_task` — one recipient, retries 3 times 30 seconds apart if SMTP fails
- `send_bulk_email_task` — many recipients, carries on past failures and returns which worked
- `send_daily_report` — runs daily at 9 AM, schedule set with a crontab in Celery Beat

Schedules are stored in the database, so you can add or change them in the admin
under Periodic Tasks without restarting beat.

## Settings

Gmail SMTP on port 587 with TLS, credentials read from `.env` so nothing secret
is committed. Timezone is Asia/Kolkata and Celery uses the same one, so crontab
times mean local time.

## Layout

```
config/
  celery.py      celery app
  settings.py    smtp, broker, beat
emails/
  tasks.py       the email tasks
  views.py       endpoints and validation
  templates/emails/   base, welcome, notification, form
  management/commands/setup_periodic_tasks.py
```
