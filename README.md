# Django Celery Email

Sends email in the background using Celery with Redis as the broker.

## Setup

Copy `.env.example` to `.env` and add your Gmail address and a 16-character app
password (Google Account > Security > App passwords).

```bash
pip install -r requirements.txt
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

Form at http://localhost:8000/. `--pool=solo` is needed on Windows.

## API

```bash
curl -X POST localhost:8000/api/send-email/ -H "Content-Type: application/json" \
  -d '{"recipient":"someone@gmail.com","subject":"Hello","message":"Sent in the background"}'

curl localhost:8000/api/email-status/<task_id>/
```

First returns `{"task_id": "...", "status": "queued"}`, second gives PENDING, RETRY,
SUCCESS or FAILURE. Use `recipients` as a list for bulk, add `"template": "welcome"`
for HTML. Bad input returns 400 before queueing.

Tasks retry 3 times on SMTP failure. The daily report runs at 9 AM, editable in the
admin under Periodic Tasks.
