# Cloud-Native Online Examination System

## Project Description
This project is a comprehensive **Online Examination System** built with **Django** and modernized to use **AWS DynamoDB** as its primary backend database. It completely replaces the traditional SQL-backed Django ORM with a NoSQL architecture using `pynamodb`. The system supports three distinct user roles—**Admin**, **Teacher**, and **Student**—facilitating a complete workflow from exam creation to automated result processing.

---

## Project Details

### Problem Statement
Traditional online examination systems often rely on relational databases which can face scalability challenges under high concurrent loads. This project addresses modern cloud-native requirements by migrating the data layer to **AWS DynamoDB**, offering a serverless, highly available, and scalable solution for managing users, exams, and results.

### Key Features
- **Role-Based Access Control:**
  - **Admin:** Approves teacher accounts, manages students, and oversees the entire system.
  - **Teacher:** Creates courses/exams, adds questions (MCQ, Text), and reviews results.
  - **Student:** Registers, enrolls in exams, attempts tests, and views instant results.
- **NoSQL Architecture:**
  - Full migration from SQL to DynamoDB.
  - Custom Authentication Backend (`auth_backend.py`) for DynamoDB user management.
  - Optimized PynamoDB models for efficient querying.
- **Exam Management:**
  - Support for multiple question types.
  - auto-grading for objective questions.
- **Cloud Ready:** Uses `boto3` and `pynamodb` for direct AWS integration.

### Database Schema (DynamoDB)
The project uses the following DynamoDB models (defined in `dynamodb_models.py`):
- **UserDynamoDB:** Stores user credentials and profile info (replaces Django User).
- **CourseDynamoDB:** Represents exams/courses.
- **QuestionDynamoDB:** Stores exam questions and options.
- **ResultDynamoDB:** Stores student attempts and marks.
- **TeacherDynamoDB / StudentDynamoDB:** Extension profiles for specific roles.

---

## Tech Stack
- **Backend Framework:** Django 4.2.7
- **Database:** AWS DynamoDB (NoSQL)
- **Database ORM:** PynamoDB 5.5.1
- **Cloud SDK:** Boto3 1.29.7
- **Frontend:** HTML5, CSS3, Bootstrap 4
- **Static Files:** WhiteNoise 6.6.0
- **Utilities:** Python-Dotenv, Pillow

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/Online-Examination-System.git
cd Online-Examination-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory with your AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 4. Setup Database
Unlike standard Django apps, you do not run `migrate`. Instead, initialize the DynamoDB tables:
```bash
python create_dynamodb_tables.py
```
*Note: This script will create the necessary tables in your AWS DynamoDB account.*

### 5. Create Superuser (Admin)
Since we are using a custom auth backend, use the provided script to create an admin:
```bash
python create_superuser.py
```

### 6. Run the Application
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to access the application.

---

## Usage
- **Admin Login:** Use the credentials created via `create_superuser.py` to approve new teachers.
- **Teacher Flow:** Sign up -> Wait for approval -> Login -> Add Course -> Add Questions.
- **Student Flow:** Sign up -> Login -> Take Exam -> View Marks.

---

## Project Structure
```
Online-Examination-System/
│
├── onlinexam/              # Project settings and main configuration
│   ├── settings.py         # Django settings (DynamoDB config)
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI application entry point
│
├── exam/                   # Exam management app
├── student/                # Student portal app
├── teacher/                # Teacher portal app
├── templates/              # HTML templates
├── static/                 # CSS, JS, and Images
│
├── dynamodb_models.py      # PynamoDB model definitions
├── dynamodb_config.py      # DynamoDB table configuration
├── db_adapter.py           # Adapter for DynamoDB operations
├── auth_backend.py         # Custom Django authentication backend
├── create_dynamodb_tables.py # Script to initialize database tables
│
├── manage.py               # Django management script
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
