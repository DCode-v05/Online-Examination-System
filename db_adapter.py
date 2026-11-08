"""
Database Adapter Layer - DynamoDB Only
Provides interface for DynamoDB operations
"""
from dynamodb_helpers import (
    CourseHelper, QuestionHelper, ResultHelper,
    TeacherHelper, StudentHelper, UserHelper, DynamoDBHelper
)


class CourseAdapter:
    """Interface for Course operations"""
    
    @staticmethod
    def create(course_name, course_id=None):
        return CourseHelper.create(course_name, course_id)
    
    @staticmethod
    def get_by_id(course_id):
        return CourseHelper.get_by_id(str(course_id))
    
    @staticmethod
    def get_all():
        return CourseHelper.get_all()
    
    @staticmethod
    def get_by_name(course_name):
        return CourseHelper.get_by_name(course_name)
    
    @staticmethod
    def update(course_id, course_name=None, assigned_teacher_id=None):
        return CourseHelper.update(str(course_id), course_name=course_name, assigned_teacher_id=assigned_teacher_id)
    
    @staticmethod
    def delete(course_id):
        return CourseHelper.delete(str(course_id))
    
    @staticmethod
    def count():
        return len(CourseHelper.get_all())


class QuestionAdapter:
    """Interface for Question operations"""
    
    @staticmethod
    def create(course_id, marks, question, question_type='radio',
               option1=None, option2=None, option3=None, option4=None,
               answer=None, multiple_answers=None, text_answer=None):
        return QuestionHelper.create(
            str(course_id), marks, question, question_type,
            option1, option2, option3, option4,
            answer, multiple_answers, text_answer
        )
    
    @staticmethod
    def get_by_id(question_id):
        return QuestionHelper.get_by_id(str(question_id))
    
    @staticmethod
    def get_by_course(course_id):
        return QuestionHelper.get_by_course(str(course_id))
    
    @staticmethod
    def get_by_course_id(course_id):
        return QuestionHelper.get_by_course(str(course_id))
    
    @staticmethod
    def get_all():
        return QuestionHelper.get_all()
    
    @staticmethod
    def delete(question_id):
        return QuestionHelper.delete(str(question_id))
    
    @staticmethod
    def count():
        return QuestionHelper.count()


class ResultAdapter:
    """Interface for Result operations"""
    
    @staticmethod
    def create(student_id, exam_id, marks, needs_review=False, student_answers=None, date=None):
        return ResultHelper.create(
            str(student_id), str(exam_id), marks,
            needs_review, student_answers
        )
    
    @staticmethod
    def get_by_id(result_id):
        return ResultHelper.get_by_id(str(result_id))
    
    @staticmethod
    def get_by_student_and_exam(student_id, exam_id):
        return ResultHelper.get_by_student_and_exam(str(student_id), str(exam_id))
    
    @staticmethod
    def get_pending_reviews(exam_id):
        return ResultHelper.get_pending_reviews(str(exam_id))
    
    @staticmethod
    def get_all():
        return ResultHelper.get_all()
    
    @staticmethod
    def update(result_id, marks=None, needs_review=None):
        return ResultHelper.update(str(result_id), marks, needs_review)


class TeacherAdapter:
    """Interface for Teacher operations"""
    
    @staticmethod
    def create(user_id, mobile, course_id=None, status=False, salary=None):
        return TeacherHelper.create(user_id, mobile, str(course_id) if course_id else None, status, salary)
    
    @staticmethod
    def get_by_id(teacher_id):
        return TeacherHelper.get_by_id(str(teacher_id))
    
    @staticmethod
    def get_by_user_id(user_id):
        return TeacherHelper.get_by_user_id(user_id)
    
    @staticmethod
    def get_all():
        return TeacherHelper.get_all()
    
    @staticmethod
    def get_by_status(status):
        return TeacherHelper.get_by_status(status)
    
    @staticmethod
    def count():
        return TeacherHelper.count()
    
    @staticmethod
    def update(teacher_id, mobile=None, course_id=None, status=None, salary=None):
        return TeacherHelper.update(str(teacher_id), mobile, str(course_id) if course_id else None, status, salary)
    
    @staticmethod
    def delete(teacher_id):
        return TeacherHelper.delete(str(teacher_id))


class StudentAdapter:
    """Interface for Student operations"""
    
    @staticmethod
    def create(user_id, mobile):
        return StudentHelper.create(user_id, mobile)
    
    @staticmethod
    def get_by_id(student_id):
        return StudentHelper.get_by_id(str(student_id))
    
    @staticmethod
    def get_by_user_id(user_id):
        return StudentHelper.get_by_user_id(user_id)
    
    @staticmethod
    def get_all():
        return StudentHelper.get_all()
    
    @staticmethod
    def count():
        return StudentHelper.count()
    
    @staticmethod
    def update(student_id, mobile=None):
        return StudentHelper.update(str(student_id), mobile)
    
    @staticmethod
    def delete(student_id):
        return StudentHelper.delete(str(student_id))


class UserAdapter:
    """Interface for User operations"""
    
    @staticmethod
    def create(username, email, password, first_name='', last_name='', 
               is_staff=False, is_superuser=False, groups=None):
        return UserHelper.create(username, email, password, first_name, last_name, 
                                is_staff, is_superuser, groups)
    
    @staticmethod
    def get_by_id(user_id):
        return UserHelper.get_by_id(user_id)
    
    @staticmethod
    def get_by_username(username):
        return UserHelper.get_by_username(username)
    
    @staticmethod
    def get_all():
        return UserHelper.get_all()
    
    @staticmethod
    def update(user_id, **kwargs):
        return UserHelper.update(user_id, **kwargs)
    
    @staticmethod
    def delete(user_id):
        return UserHelper.delete(user_id)
    
    @staticmethod
    def authenticate(username, password):
        return UserHelper.authenticate(username, password)
    
    @staticmethod
    def add_to_group(user_id, group_name):
        return UserHelper.add_to_group(user_id, group_name)
    
    @staticmethod
    def set_password(user_id, password):
        return UserHelper.set_password(user_id, password)
    
    @staticmethod
    def count():
        return UserHelper.count()
