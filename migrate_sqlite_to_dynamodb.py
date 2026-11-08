"""
Data Migration Script: SQLite → AWS DynamoDB
==============================================
This script migrates all data from SQLite (Django ORM) to AWS DynamoDB.

Usage:
    python migrate_sqlite_to_dynamodb.py [--dry-run]

Options:
    --dry-run    : Show what would be migrated without actually migrating
    --force      : Skip confirmation prompts
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinexam.settings')
django.setup()

from django.contrib.auth.models import User
from exam.models import Course, Question, Result
from teacher.models import Teacher
from student.models import Student
from db_adapter import CourseAdapter, QuestionAdapter, ResultAdapter, TeacherAdapter, StudentAdapter
from datetime import datetime

class DataMigration:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.stats = {
            'courses': {'total': 0, 'migrated': 0, 'failed': 0},
            'questions': {'total': 0, 'migrated': 0, 'failed': 0},
            'teachers': {'total': 0, 'migrated': 0, 'failed': 0},
            'students': {'total': 0, 'migrated': 0, 'failed': 0},
            'results': {'total': 0, 'migrated': 0, 'failed': 0},
        }
    
    def log(self, message, level='INFO'):
        """Print log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = '[DRY-RUN] ' if self.dry_run else ''
        print(f"{prefix}[{timestamp}] [{level}] {message}")
    
    def migrate_courses(self):
        """Migrate all courses from SQLite to DynamoDB"""
        self.log("=" * 60)
        self.log("Migrating Courses...")
        self.log("=" * 60)
        
        courses = Course.objects.all()
        self.stats['courses']['total'] = courses.count()
        
        for course in courses:
            try:
                self.log(f"Course {course.id}: {course.course_name}")
                
                if not self.dry_run:
                    existing = CourseAdapter.get_by_id(course.id)
                    if existing:
                        self.log(f"  → Already exists in DynamoDB, skipping", 'WARN')
                    else:
                        CourseAdapter.create(course.course_name)
                        self.log(f"  → Migrated successfully", 'SUCCESS')
                        self.stats['courses']['migrated'] += 1
                else:
                    self.log(f"  → Would migrate: {course.course_name}")
                    self.stats['courses']['migrated'] += 1
                    
            except Exception as e:
                self.log(f"  → Failed: {str(e)}", 'ERROR')
                self.stats['courses']['failed'] += 1
        
        self.log(f"Courses: {self.stats['courses']['migrated']}/{self.stats['courses']['total']} migrated, {self.stats['courses']['failed']} failed\n")
    
    def migrate_teachers(self):
        """Migrate all teachers from SQLite to DynamoDB"""
        self.log("=" * 60)
        self.log("Migrating Teachers...")
        self.log("=" * 60)
        
        teachers = Teacher.objects.all()
        self.stats['teachers']['total'] = teachers.count()
        
        for teacher in teachers:
            try:
                self.log(f"Teacher {teacher.id}: User {teacher.user.username}")
                
                if not self.dry_run:
                    existing = TeacherAdapter.get_by_id(teacher.id)
                    if existing:
                        self.log(f"  → Already exists in DynamoDB, skipping", 'WARN')
                    else:
                        TeacherAdapter.create(
                            user_id=teacher.user_id,
                            mobile=teacher.mobile,
                            course_id=teacher.course_id if teacher.course else None,
                            status=teacher.status,
                            salary=teacher.salary if teacher.salary else 0
                        )
                        self.log(f"  → Migrated successfully", 'SUCCESS')
                        self.stats['teachers']['migrated'] += 1
                else:
                    self.log(f"  → Would migrate: User {teacher.user_id}, Mobile {teacher.mobile}")
                    self.stats['teachers']['migrated'] += 1
                    
            except Exception as e:
                self.log(f"  → Failed: {str(e)}", 'ERROR')
                self.stats['teachers']['failed'] += 1
        
        self.log(f"Teachers: {self.stats['teachers']['migrated']}/{self.stats['teachers']['total']} migrated, {self.stats['teachers']['failed']} failed\n")
    
    def migrate_students(self):
        """Migrate all students from SQLite to DynamoDB"""
        self.log("=" * 60)
        self.log("Migrating Students...")
        self.log("=" * 60)
        
        students = Student.objects.all()
        self.stats['students']['total'] = students.count()
        
        for student in students:
            try:
                self.log(f"Student {student.id}: User {student.user.username}")
                
                if not self.dry_run:
                    existing = StudentAdapter.get_by_id(student.id)
                    if existing:
                        self.log(f"  → Already exists in DynamoDB, skipping", 'WARN')
                    else:
                        StudentAdapter.create(
                            user_id=student.user_id,
                            mobile=student.mobile
                        )
                        self.log(f"  → Migrated successfully", 'SUCCESS')
                        self.stats['students']['migrated'] += 1
                else:
                    self.log(f"  → Would migrate: User {student.user_id}, Mobile {student.mobile}")
                    self.stats['students']['migrated'] += 1
                    
            except Exception as e:
                self.log(f"  → Failed: {str(e)}", 'ERROR')
                self.stats['students']['failed'] += 1
        
        self.log(f"Students: {self.stats['students']['migrated']}/{self.stats['students']['total']} migrated, {self.stats['students']['failed']} failed\n")
    
    def migrate_questions(self):
        """Migrate all questions from SQLite to DynamoDB"""
        self.log("=" * 60)
        self.log("Migrating Questions...")
        self.log("=" * 60)
        
        questions = Question.objects.all()
        self.stats['questions']['total'] = questions.count()
        
        for question in questions:
            try:
                self.log(f"Question {question.id}: Course {question.course_id}")
                
                if not self.dry_run:
                    existing = QuestionAdapter.get_by_id(question.id)
                    if existing:
                        self.log(f"  → Already exists in DynamoDB, skipping", 'WARN')
                    else:
                        QuestionAdapter.create(
                            course_id=question.course_id,
                            marks=question.marks,
                            question=question.question,
                            question_type=getattr(question, 'question_type', 'radio'),
                            option1=question.option1,
                            option2=question.option2,
                            option3=question.option3,
                            option4=question.option4,
                            answer=question.answer,
                            multiple_answers=getattr(question, 'multiple_answers', ''),
                            text_answer=getattr(question, 'text_answer', '')
                        )
                        self.log(f"  → Migrated successfully", 'SUCCESS')
                        self.stats['questions']['migrated'] += 1
                else:
                    self.log(f"  → Would migrate: {question.question[:50]}...")
                    self.stats['questions']['migrated'] += 1
                    
            except Exception as e:
                self.log(f"  → Failed: {str(e)}", 'ERROR')
                self.stats['questions']['failed'] += 1
        
        self.log(f"Questions: {self.stats['questions']['migrated']}/{self.stats['questions']['total']} migrated, {self.stats['questions']['failed']} failed\n")
    
    def migrate_results(self):
        """Migrate all results from SQLite to DynamoDB"""
        self.log("=" * 60)
        self.log("Migrating Results...")
        self.log("=" * 60)
        
        results = Result.objects.all()
        self.stats['results']['total'] = results.count()
        
        for result in results:
            try:
                self.log(f"Result {result.id}: Student {result.student_id}, Exam {result.exam_id}, Marks {result.marks}")
                
                if not self.dry_run:
                    existing = ResultAdapter.get_by_id(result.id)
                    if existing:
                        self.log(f"  → Already exists in DynamoDB, skipping", 'WARN')
                    else:
                        ResultAdapter.create(
                            student_id=result.student_id,
                            exam_id=result.exam_id,
                            marks=result.marks,
                            needs_review=getattr(result, 'needs_review', False),
                            student_answers=getattr(result, 'student_answers', '')
                        )
                        self.log(f"  → Migrated successfully", 'SUCCESS')
                        self.stats['results']['migrated'] += 1
                else:
                    self.log(f"  → Would migrate: Student {result.student_id}, Exam {result.exam_id}, Marks {result.marks}")
                    self.stats['results']['migrated'] += 1
                    
            except Exception as e:
                self.log(f"  → Failed: {str(e)}", 'ERROR')
                self.stats['results']['failed'] += 1
        
        self.log(f"Results: {self.stats['results']['migrated']}/{self.stats['results']['total']} migrated, {self.stats['results']['failed']} failed\n")
    
    def print_summary(self):
        """Print migration summary"""
        self.log("=" * 60)
        self.log("MIGRATION SUMMARY")
        self.log("=" * 60)
        
        total_migrated = sum(s['migrated'] for s in self.stats.values())
        total_failed = sum(s['failed'] for s in self.stats.values())
        total_records = sum(s['total'] for s in self.stats.values())
        
        for entity, stats in self.stats.items():
            self.log(f"{entity.upper():<12} : {stats['migrated']}/{stats['total']} migrated, {stats['failed']} failed")
        
        self.log("-" * 60)
        self.log(f"TOTAL        : {total_migrated}/{total_records} migrated, {total_failed} failed")
        self.log("=" * 60)
        
        if total_failed > 0:
            self.log("⚠️  Some records failed to migrate. Check the logs above.", 'WARN')
        elif total_migrated > 0:
            self.log("✅ All records migrated successfully!", 'SUCCESS')
        else:
            self.log("ℹ️  No new records to migrate.", 'INFO')
    
    def run(self):
        """Run the complete migration"""
        self.log("Starting Data Migration: SQLite → DynamoDB")
        self.log(f"Dry Run Mode: {self.dry_run}")
        self.log("")
        
        self.migrate_courses()
        self.migrate_teachers()
        self.migrate_students()
        self.migrate_questions()
        self.migrate_results()
        
        self.print_summary()
        
        if self.dry_run:
            self.log("\n⚠️  This was a DRY RUN. No data was actually migrated.")
            self.log("Run without --dry-run to perform actual migration.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate data from SQLite to DynamoDB')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without actually migrating')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    if not args.force and not args.dry_run:
        print("\n" + "=" * 60)
        print("⚠️  WARNING: Data Migration")
        print("=" * 60)
        print("This will migrate data from SQLite to AWS DynamoDB.")
        print("Make sure:")
        print("  1. AWS credentials are configured in .env file")
        print("  2. DynamoDB tables are created (run create_dynamodb_tables.py)")
        print("  3. You have a backup of your SQLite database")
        print("")
        response = input("Do you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Migration cancelled.")
            return
    
    migration = DataMigration(dry_run=args.dry_run)
    migration.run()


if __name__ == '__main__':
    main()
