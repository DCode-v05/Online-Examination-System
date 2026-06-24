# Online Examination System

**A Django exam platform that runs entirely on AWS DynamoDB — no SQL, no Django ORM. Admins, teachers, and students share one role-based workflow from course creation to auto-graded results.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django_4.2-092E20?style=flat&logo=django&logoColor=white) ![Amazon DynamoDB](https://img.shields.io/badge/AWS_DynamoDB-4053D6?style=flat&logo=amazondynamodb&logoColor=white) ![PynamoDB](https://img.shields.io/badge/PynamoDB-5.5-FF9900?style=flat&logo=amazonaws&logoColor=white) ![Boto3](https://img.shields.io/badge/Boto3-FF9900?style=flat&logo=amazonwebservices&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat&logo=gunicorn&logoColor=white) ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white)

## Overview

This is a web-based online examination system written in Django 4.2.7. It started life as a standard SQLite + Django-ORM exam app and I re-engineered the whole data layer to run on **AWS DynamoDB** instead. That meant tearing out `django.contrib.auth`, `django.contrib.admin`, and the relational models, then rebuilding authentication, sessions, and every CRUD path on top of a NoSQL store accessed through PynamoDB and Boto3.

The app handles three roles — **Admin**, **Teacher**, and **Student** — and covers the full exam lifecycle: a teacher signs up and waits for admin approval, the admin assigns a course and salary, the teacher writes questions, and students attempt the exam and get marked. Objective questions (single and multiple choice) are graded automatically; written answers are flagged for a teacher to grade by hand.

The interesting part isn't the exam UI — plenty of those exist — it's that the entire persistence and auth stack was swapped from relational to key-value while keeping the existing Django views, templates, and request flow working. Built as a college / learning project to get hands-on with DynamoDB's single-table-style modelling, global secondary indexes, and the work involved in running Django without its built-in ORM.

## Key Features

- **Three role-based portals** — Admin, Teacher, and Student, each with its own dashboard, URL namespace (`teacher/`, `student/`), and access decorators.
- **Teacher approval workflow** — teachers self-register, land in a "wait for approval" state, and an admin approves them, sets a salary, and assigns a course before they can log in.
- **Admin console** — manage students and teachers (view / update / delete), approve or reject pending teachers, create and edit courses, add and view questions, view per-student marks, and see live totals (students, teachers, courses, questions) plus aggregate teacher salary.
- **Course and question authoring** — admins and teachers create courses and attach questions with configurable marks.
- **Three question types** — single-choice radio (`radio`), multiple-choice checkbox (`checkbox`), and free-text (`text`).
- **Automatic grading** — radio and checkbox questions are scored on submission; checkbox answers are order-normalised before comparison so a different selection order still matches.
- **Manual review for written answers** — text questions are not auto-scored; the result is flagged `needs_review` and surfaced to the teacher, who grades the answers and finalises the mark.
- **Answer capture** — every submission stores the student's per-question answers as JSON inside the result record, so teachers can review exactly what was entered.
- **Custom DynamoDB authentication** — a hand-written auth backend replaces Django's auth app: password hashing with Django's `make_password` / `check_password`, login state in the session, and a middleware that injects a `CustomUser` / `AnonymousUser` onto every request.
- **Group-based permissions** — `TEACHER` and `STUDENT` group membership stored per user and checked via `user.has_group(...)`, plus `login_required`, `user_passes_test`, and `superuser_required` decorator equivalents.
- **Contact form** with SMTP email delivery (Gmail) via Django's email backend.
- **Production-ready static serving** — WhiteNoise with compressed manifest storage, and Gunicorn as the WSGI server.
- **One-shot table provisioning** — a script creates all six DynamoDB tables (with their global secondary indexes) in on-demand billing mode.
- **SQLite-to-DynamoDB migration script** for moving data off the old relational backend.

## How It Works

### Architecture at a glance

It's a regular Django project (`onlinexam`) with three apps — `exam`, `teacher`, `student` — and a set of standalone modules at the repo root that form the DynamoDB layer. The request flow is normal Django (URL conf → view → template), but underneath, views never touch the ORM. Instead they call **adapters**, which call **helpers**, which talk to **PynamoDB models**, which map to DynamoDB tables.

```
Request -> URL conf -> View -> *Adapter -> *Helper -> PynamoDB Model -> DynamoDB
                         |
                  AuthenticationMiddleware attaches request.user (from session)
```

### Authentication without django.contrib.auth

`INSTALLED_APPS` deliberately drops `django.contrib.admin`, `django.contrib.auth`, and `django.contrib.contenttypes`. In their place, `auth_backend.py` provides:

- `DynamoDBAuthBackend` — `authenticate()` looks up a user by username (via a `username-index` GSI) and verifies the hash with `check_password`; `login()` / `logout()` write and flush session keys.
- `AuthenticationMiddleware` — on every request, reads `user_id` from the session and attaches either a `CustomUser` (with `is_authenticated`, `is_staff`, `is_superuser`, `has_group()`) or an `AnonymousUser`. This keeps existing templates that reference `request.user` working unchanged.
- Decorator replacements — `login_required`, `user_passes_test`, and `superuser_required` mirror Django's, but check the custom user object and redirect to the right login URL.

Sessions use the **signed-cookie** backend (`django.contrib.sessions.backends.signed_cookies`) so there's no session table — fitting for a setup with no relational database at all.

### The data layer (three thin tiers)

1. **PynamoDB models** (`dynamodb_models.py`) define the six tables — `UserDynamoDB`, `CourseDynamoDB`, `QuestionDynamoDB`, `ResultDynamoDB`, `TeacherDynamoDB`, `StudentDynamoDB` — plus global secondary indexes (`username-index`, `user_id-index`, `course_id-index`, `exam_id-index`, `student_id-index`) for the lookups the app actually does. Most primary keys are UUIDs stored as strings; users key on a numeric `id`.
2. **Helpers** (`dynamodb_helpers.py`) hold the CRUD logic and queries against those models.
3. **Adapters** (`db_adapter.py`) expose a clean static-method API — `CourseAdapter`, `QuestionAdapter`, `ResultAdapter`, `TeacherAdapter`, `StudentAdapter`, `UserAdapter` — that the Django views import and call. This is the seam that let the views stop using `.objects.all()` and start using `Adapter.get_all()` without changing their shape much.

`dynamodb_config.py` builds the Boto3 resource and client from `.env` credentials, validates that AWS keys are present, and maps logical names (`course`, `question`, …) to real table names (overridable via env vars, defaulting to `OnlineExam_Courses`, `OnlineExam_Questions`, and so on).

### Grading logic

When a student submits (`calculate_marks_view`), the app walks each question and grades by type:

- **radio** — compare the selected option against the stored `answer`; award the question's marks on an exact match.
- **checkbox** — sort both the student's selection and the stored `multiple_answers` (comma-separated), then compare, so order doesn't matter; full marks only on a full match.
- **text** — never auto-scored. The presence of any text question flips `needs_review = True` on the result so a teacher picks it up.

The total is written to a `ResultDynamoDB` record along with the JSON dump of every answer the student gave, keyed by question id, for later review.

### Table provisioning and migration

`create_dynamodb_tables.py` creates each table in `PAY_PER_REQUEST` (on-demand) billing mode with the right key schema and GSIs, and is safe to re-run — it detects `ResourceInUseException` and skips tables that already exist. `migrate_sqlite_to_dynamodb.py` moves data from the legacy SQLite database into DynamoDB, and `create_superuser.py` seeds an admin account directly into the user table (since `manage.py createsuperuser` no longer applies without the auth app).

## Tech Stack

- **Language:** Python 3
- **Framework:** Django 4.2.7 (ORM disabled; custom auth, sessions, and middleware)
- **Database:** AWS DynamoDB (six tables, on-demand billing, global secondary indexes)
- **AWS access:** PynamoDB 5.5.1 (object mapping) and Boto3 1.29.7 (client/resource + table creation)
- **Frontend:** Django templates, HTML5/CSS3, Bootstrap, `django-widget-tweaks` for form rendering
- **Serving:** Gunicorn 21.2.0 (WSGI) and WhiteNoise 6.6.0 (compressed static files)
- **Utilities:** `python-dotenv` (config), Pillow (image handling), `pytz`, `sqlparse`

## Getting Started

### Prerequisites

- Python 3 and `pip`
- An AWS account with DynamoDB access and an access key / secret pair
- The IAM permissions to create and read/write DynamoDB tables in your chosen region

### Installation

```bash
git clone https://github.com/DCode-v05/Online-Examination-System.git
cd Online-Examination-System
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1
SECRET_KEY=your_django_secret_key
DEBUG=True
USE_DYNAMODB=True
```

### Running

This project does **not** use `python manage.py migrate` — there's no relational database. Provision the DynamoDB tables, seed an admin, then start the server:

```bash
# 1. Create the six DynamoDB tables (safe to re-run)
python create_dynamodb_tables.py

# 2. Create an admin / superuser account
python create_superuser.py

# 3. Start the dev server
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. For production, serve with Gunicorn (`gunicorn onlinexam.wsgi`); WhiteNoise handles static files.

## Usage

- **Admin** — log in at `/adminlogin` with the account from `create_superuser.py`. From the dashboard you can approve or reject pending teachers (and set their salary), manage students and courses, add questions, and view marks.
- **Teacher** — sign up, then wait on the approval screen until an admin approves the account and assigns a course. Once approved, log in to add questions for the assigned course, review submitted exams, and grade written answers.
- **Student** — sign up, log in, pick an available exam, attempt it, and view results. Objective questions return marks immediately; exams containing text questions show a final mark after the teacher has reviewed them.

If you want to switch back to the legacy relational backend for local testing, set `USE_DYNAMODB=False` in `.env`.

## Project Structure

```
Online-Examination-System/
├── onlinexam/                  # Django project config
│   ├── settings.py             # DynamoDB-only setup; custom auth/session config
│   ├── urls.py                 # Admin + root routes
│   └── wsgi.py / asgi.py       # Server entry points
├── exam/                       # Admin-side app: dashboard, courses, questions, marks
│   ├── views.py                # Admin views (all calls go through adapters)
│   ├── auth_views.py           # Admin/teacher/student login views
│   └── migrations/             # Legacy ORM migrations (kept from the SQL version)
├── teacher/                    # Teacher portal: signup, dashboard, question authoring, grading
├── student/                    # Student portal: signup, exam taking, grading, results
│   └── views.py                # calculate_marks_view holds the grading logic
├── templates/                  # HTML templates, split by app (exam/ student/ teacher/)
├── static/                     # Bootstrap assets, images, profile pictures
├── dynamodb_models.py          # PynamoDB models + global secondary indexes
├── dynamodb_config.py          # Boto3 clients, table names, region from .env
├── dynamodb_helpers.py         # CRUD + query logic per model
├── db_adapter.py               # Static-method adapter API used by the views
├── auth_backend.py             # Custom auth backend, middleware, decorators
├── create_dynamodb_tables.py   # One-time table provisioning (on-demand billing)
├── create_superuser.py         # Seed an admin user into DynamoDB
├── migrate_sqlite_to_dynamodb.py  # Move data off the legacy SQLite backend
├── manage.py                   # Django management entry point
├── requirements.txt            # Pinned dependencies
└── README.md
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
