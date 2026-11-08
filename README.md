# Online-Examination-System

A Django exam platform with admin, teacher and student roles, built on AWS DynamoDB instead of the Django ORM. It started from a stock SQLite exam app; I replaced the data layer, authentication and sessions so nothing touches a relational database.

A teacher signs up and waits for admin approval. The admin approves, sets a salary and assigns a course. The teacher writes questions, and students take the exam. Single-choice and multiple-choice answers are graded on submission. Free-text answers are flagged for the teacher to mark by hand.

## How it works

Requests go through the usual Django URL conf and views, but the views call adapters instead of the ORM:

```
view -> db_adapter.*Adapter -> dynamodb_helpers -> PynamoDB model (dynamodb_models.py) -> DynamoDB
```

- `dynamodb_models.py` defines six PynamoDB models (users, courses, questions, results, teachers, students) with global secondary indexes for the lookups the app uses, such as `username-index` and `course_id-index`.
- `dynamodb_helpers.py` holds the CRUD and query code.
- `db_adapter.py` exposes static-method adapters (`CourseAdapter`, `QuestionAdapter`, `ResultAdapter`, `TeacherAdapter`, `StudentAdapter`, `UserAdapter`) for the views.
- `dynamodb_config.py` builds the boto3 clients from env vars and maps logical names to table names (`OnlineExam_Courses`, etc., overridable with `DYNAMODB_*_TABLE`).

`django.contrib.auth`, `admin` and `contenttypes` are not installed. `auth_backend.py` provides the replacement: a backend that looks users up by username and checks the hash with Django's `check_password`, a middleware that sets `request.user` from the session, and `login_required`, `user_passes_test` and `superuser_required` equivalents. Teacher and student membership is stored as groups on the user. Sessions use signed cookies, so there is no session table.

Grading is in `calculate_marks_view` in `student/views.py`. Radio questions compare the chosen option to the stored answer. Checkbox answers are sorted before comparing, so selection order does not matter. If any question is free text, the result is saved with `needs_review` set. The student's answers are stored as JSON on the result.

## Stack

Django 4.2.7, PynamoDB 5.5.1, boto3, django-widget-tweaks, Bootstrap templates, Gunicorn, WhiteNoise.

## Setup

You need Python 3 and an AWS account with permission to create and use DynamoDB tables.

```bash
pip install -r requirements.txt
```

Create a `.env` in the project root:

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
SECRET_KEY=...
DEBUG=True
```

For the contact form, set `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (a Gmail app password) and `EMAIL_RECEIVING_USER`; `settings.py` reads them from the environment.

There is no `migrate` step. Create the tables, create an admin, then run the server:

```bash
python create_dynamodb_tables.py
python create_superuser.py
python manage.py runserver
```

`create_dynamodb_tables.py` uses on-demand billing and skips tables that already exist. The admin logs in at `/adminlogin`. `migrate_sqlite_to_dynamodb.py` is there to move data from the old SQLite database. For production, `gunicorn onlinexam.wsgi` with WhiteNoise serving static files.

## Project structure

```
onlinexam/     Django project (settings, urls, wsgi)
exam/          admin side: dashboard, courses, questions, marks, login views
teacher/       teacher signup, approval wait, question authoring
student/       student signup, exam taking, results
templates/     HTML templates split by role
static/        CSS, images, sample profile pictures
dynamodb_*.py  models, config, helpers
db_adapter.py  adapter API used by views
auth_backend.py
create_dynamodb_tables.py, create_superuser.py, migrate_sqlite_to_dynamodb.py
```

## Notes

- The `migrations/` folders are left over from the SQL version. They are not used.
- `settings.py` falls back to a hard-coded `SECRET_KEY` and `ALLOWED_HOSTS = *` when the env vars are missing. Set both for any real deployment.
