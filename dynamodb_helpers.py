"""
DynamoDB Helper Functions
Provides a Django-like interface for DynamoDB operations
"""
import uuid
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.hashers import make_password, check_password
from dynamodb_models import (
    CourseDynamoDB, QuestionDynamoDB, ResultDynamoDB,
    TeacherDynamoDB, StudentDynamoDB, UserDynamoDB
)
from pynamodb.exceptions import DoesNotExist


class DynamoDBHelper:
    """Helper class for DynamoDB operations"""
    
    @staticmethod
    def generate_id():
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def to_decimal(value):
        """Convert int/float to Decimal for DynamoDB"""
        if value is None:
            return None
        return Decimal(str(value))
    
    @staticmethod
    def from_decimal(value):
        """Convert Decimal to int"""
        if value is None:
            return None
        return int(value)
    
    @staticmethod
    def sanitize_data(value):
        """Recursively convert Decimal objects to float or int for safe JSON serialization"""
        if isinstance(value, list):
            return [DynamoDBHelper.sanitize_data(v) for v in value]
        elif isinstance(value, dict):
            return {k: DynamoDBHelper.sanitize_data(v) for k, v in value.items()}
        elif isinstance(value, Decimal):
            return int(value) if value % 1 == 0 else float(value)
        else:
            return value
    
    @staticmethod
    def model_to_dict(model_instance):
        """Convert PynamoDB model instance to dictionary"""
        if model_instance is None:
            return None
        result = {}
        for attr_name in model_instance.get_attributes().keys():
            value = getattr(model_instance, attr_name, None)
            if isinstance(value, Decimal):
                result[attr_name] = int(value) if value % 1 == 0 else float(value)
            else:
                result[attr_name] = value
        return result


class CourseHelper:
    """Helper functions for Course operations"""
    
    @staticmethod
    def create(course_name, course_id=None):
        """Create a new course with optional ID (for Django ORM compatibility)"""
        if not course_id:
            course_id = DynamoDBHelper.generate_id()
        course = CourseDynamoDB(
            id=str(course_id),
            course_name=course_name
        )
        course.save()
        return course
    
    @staticmethod
    def get_by_id(course_id):
        """Get course by ID"""
        try:
            course = CourseDynamoDB.get(course_id)
            return DynamoDBHelper.model_to_dict(course)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_all():
        """Get all courses"""
        courses = list(CourseDynamoDB.scan())
        return [DynamoDBHelper.model_to_dict(c) for c in courses]
    
    @staticmethod
    def get_by_name(course_name):
        """Get course by name"""
        all_courses = CourseDynamoDB.scan()
        for course in all_courses:
            if course.course_name == course_name:
                return DynamoDBHelper.model_to_dict(course)
        return None
    
    @staticmethod
    def update(course_id, course_name=None, assigned_teacher_id=None):
        """Update course"""
        try:
            course = CourseDynamoDB.get(course_id)
            if course_name:
                course.course_name = course_name
            if assigned_teacher_id is not None:
                course.assigned_teacher_id = assigned_teacher_id
            course.save()
            return course
        except DoesNotExist:
            return None
    
    @staticmethod
    def delete(course_id):
        """Delete course"""
        try:
            course = CourseDynamoDB.get(course_id)
            course.delete()
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    def get_total_questions(course_id):
        """Get total questions for a course"""
        questions = list(QuestionDynamoDB.course_id_index.query(course_id))
        return len(questions)
    
    @staticmethod
    def get_total_marks(course_id):
        """Get total marks for a course"""
        questions = list(QuestionDynamoDB.course_id_index.query(course_id))
        return sum(int(q.marks) for q in questions)


class QuestionHelper:
    """Helper functions for Question operations"""
    
    @staticmethod
    def create(course_id, marks, question, question_type='radio', 
               option1=None, option2=None, option3=None, option4=None,
               answer=None, multiple_answers=None, text_answer=None):
        """Create a new question"""
        question_id = DynamoDBHelper.generate_id()
        q = QuestionDynamoDB(
            id=question_id,
            course_id=course_id,
            marks=DynamoDBHelper.to_decimal(marks),
            question=question,
            question_type=question_type,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            answer=answer,
            multiple_answers=multiple_answers,
            text_answer=text_answer
        )
        q.attribute_values = DynamoDBHelper.sanitize_data(q.attribute_values)
        q.save()
        return q
    
    @staticmethod
    def get_by_id(question_id):
        """Get question by ID"""
        try:
            question = QuestionDynamoDB.get(question_id)
            return DynamoDBHelper.model_to_dict(question)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_course(course_id):
        """Get all questions for a course"""
        all_questions = QuestionDynamoDB.scan()
        filtered = [q for q in all_questions if q.course_id == course_id]
        return [DynamoDBHelper.model_to_dict(q) for q in filtered]
    
    @staticmethod
    def get_all():
        """Get all questions"""
        questions = list(QuestionDynamoDB.scan())
        return [DynamoDBHelper.model_to_dict(q) for q in questions]
    
    @staticmethod
    def delete(question_id):
        """Delete question"""
        try:
            question = QuestionDynamoDB.get(question_id)
            question.delete()
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    def count():
        """Count total questions"""
        return QuestionDynamoDB.count()


class ResultHelper:
    """Helper functions for Result operations"""
    
    @staticmethod
    def create(student_id, exam_id, marks, needs_review=False, student_answers=None):
        """Create a new result"""
        result_id = DynamoDBHelper.generate_id()
        result = ResultDynamoDB(
            id=result_id,
            student_id=student_id,
            exam_id=exam_id,
            marks=DynamoDBHelper.to_decimal(marks),
            date=datetime.utcnow().isoformat(),
            needs_review=needs_review,
            student_answers=student_answers
        )
        result.attribute_values = DynamoDBHelper.sanitize_data(result.attribute_values)
        result.save()
        return result
    
    @staticmethod
    def get_by_id(result_id):
        """Get result by ID"""
        try:
            result = ResultDynamoDB.get(result_id)
            return DynamoDBHelper.model_to_dict(result)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_student(student_id):
        """Get all results for a student"""
        all_results = ResultDynamoDB.scan()
        filtered = [r for r in all_results if r.student_id == student_id]
        return [DynamoDBHelper.model_to_dict(r) for r in filtered]
    
    @staticmethod
    def get_by_exam(exam_id):
        """Get all results for an exam"""
        all_results = ResultDynamoDB.scan()
        filtered = [r for r in all_results if r.exam_id == exam_id]
        return [DynamoDBHelper.model_to_dict(r) for r in filtered]
    
    @staticmethod
    def get_by_student_and_exam(student_id, exam_id):
        """Get results for a specific student and exam"""
        all_results = ResultDynamoDB.scan()
        filtered = [r for r in all_results if r.student_id == student_id and r.exam_id == exam_id]
        return [DynamoDBHelper.model_to_dict(r) for r in filtered]
    
    @staticmethod
    def update(result_id, marks=None, needs_review=None):
        """Update result"""
        try:
            result = ResultDynamoDB.get(result_id)
            if marks is not None:
                result.marks = DynamoDBHelper.to_decimal(marks)
            if needs_review is not None:
                result.needs_review = needs_review
            result.attribute_values = DynamoDBHelper.sanitize_data(result.attribute_values)
            result.save()
            return result
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_pending_reviews(exam_id):
        """Get results that need review for an exam"""
        all_results = ResultDynamoDB.scan()
        filtered = [r for r in all_results if r.exam_id == exam_id and r.needs_review]
        return [DynamoDBHelper.model_to_dict(r) for r in filtered]
    
    @staticmethod
    def get_all():
        """Get all results"""
        results = list(ResultDynamoDB.scan())
        return [DynamoDBHelper.model_to_dict(r) for r in results]


class TeacherHelper:
    """Helper functions for Teacher operations"""
    
    @staticmethod
    def create(user_id, mobile, course_id=None, status=False, salary=None):
        """Create a new teacher"""
        teacher_id = DynamoDBHelper.generate_id()
        teacher = TeacherDynamoDB(
            id=teacher_id,
            user_id=user_id,
            mobile=mobile,
            course_id=course_id,
            status=status,
            salary=DynamoDBHelper.to_decimal(salary) if salary else None
        )
        teacher.attribute_values = DynamoDBHelper.sanitize_data(teacher.attribute_values)
        teacher.save()
        return teacher
    
    @staticmethod
    def get_by_id(teacher_id):
        """Get teacher by ID"""
        try:
            teacher = TeacherDynamoDB.get(teacher_id)
            return DynamoDBHelper.model_to_dict(teacher)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get teacher by user ID"""
        all_teachers = TeacherDynamoDB.scan()
        results = [t for t in all_teachers if int(t.user_id) == user_id]
        if results:
            return [DynamoDBHelper.model_to_dict(results[0])]
        return []
    
    @staticmethod
    def get_all():
        """Get all teachers"""
        teachers = list(TeacherDynamoDB.scan())
        return [DynamoDBHelper.model_to_dict(t) for t in teachers]
    
    @staticmethod
    def get_by_status(status):
        """Get teachers by status"""
        all_teachers = TeacherDynamoDB.scan()
        filtered = [t for t in all_teachers if t.status == status]
        return [DynamoDBHelper.model_to_dict(t) for t in filtered]
    
    @staticmethod
    def update(teacher_id, mobile=None, course_id=None, status=None, salary=None):
        """Update teacher"""
        try:
            teacher = TeacherDynamoDB.get(teacher_id)
            if mobile:
                teacher.mobile = mobile
            if course_id is not None:
                teacher.course_id = course_id
            if status is not None:
                teacher.status = status
            if salary is not None:
                teacher.salary = DynamoDBHelper.to_decimal(salary)
            teacher.attribute_values = DynamoDBHelper.sanitize_data(teacher.attribute_values)
            teacher.save()
            return teacher
        except DoesNotExist:
            return None
    
    @staticmethod
    def delete(teacher_id):
        """Delete teacher"""
        try:
            teacher = TeacherDynamoDB.get(teacher_id)
            teacher.delete()
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    def count():
        """Count total teachers"""
        return TeacherDynamoDB.count()
    
    @staticmethod
    def get_total_salary():
        """Get total salary of all approved teachers"""
        teachers = TeacherHelper.get_by_status(True)
        return sum(int(t.salary) for t in teachers if t.salary)


class StudentHelper:
    """Helper functions for Student operations"""
    
    @staticmethod
    def create(user_id, mobile):
        """Create a new student"""
        student_id = DynamoDBHelper.generate_id()
        student = StudentDynamoDB(
            id=student_id,
            user_id=user_id,
            mobile=mobile
        )
        student.attribute_values = DynamoDBHelper.sanitize_data(student.attribute_values)
        student.save()
        return student
    
    @staticmethod
    def get_by_id(student_id):
        """Get student by ID"""
        try:
            student = StudentDynamoDB.get(student_id)
            return DynamoDBHelper.model_to_dict(student)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get student by user ID"""
        all_students = StudentDynamoDB.scan()
        results = [s for s in all_students if int(s.user_id) == user_id]
        if results:
            return [DynamoDBHelper.model_to_dict(results[0])]
        return []
    
    @staticmethod
    def get_all():
        """Get all students"""
        students = list(StudentDynamoDB.scan())
        return [DynamoDBHelper.model_to_dict(s) for s in students]
    
    @staticmethod
    def update(student_id, mobile=None):
        """Update student"""
        try:
            student = StudentDynamoDB.get(student_id)
            if mobile:
                student.mobile = mobile
            student.attribute_values = DynamoDBHelper.sanitize_data(student.attribute_values)
            student.save()
            return student
        except DoesNotExist:
            return None
    
    @staticmethod
    def delete(student_id):
        """Delete student"""
        try:
            student = StudentDynamoDB.get(student_id)
            student.delete()
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    def count():
        """Count total students"""
        return StudentDynamoDB.count()


class UserHelper:
    """Helper functions for User operations"""
    
    @staticmethod
    def create(username, email, password, first_name='', last_name='', 
               is_staff=False, is_superuser=False, groups=None):
        """Create a new user with hashed password"""
        all_users = list(UserDynamoDB.scan())
        if all_users:
            max_id = max(int(u.id) for u in all_users)
            user_id = max_id + 1
        else:
            user_id = 1
        
        user = UserDynamoDB(
            id=user_id,
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            date_joined=datetime.utcnow(),
            groups=groups or []
        )
        user.save()
        return user
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            user = UserDynamoDB.get(int(user_id))
            return DynamoDBHelper.model_to_dict(user)
        except DoesNotExist:
            return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        all_users = UserDynamoDB.scan()
        for user in all_users:
            if user.username == username:
                return DynamoDBHelper.model_to_dict(user)
        return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        users = list(UserDynamoDB.scan())
        return [DynamoDBHelper.model_to_dict(u) for u in users]
    
    @staticmethod
    def update(user_id, **kwargs):
        """Update user fields"""
        try:
            user = UserDynamoDB.get(int(user_id))
            
            if 'username' in kwargs:
                user.username = kwargs['username']
            if 'email' in kwargs:
                user.email = kwargs['email']
            if 'password' in kwargs:
                user.password = make_password(kwargs['password'])
            if 'first_name' in kwargs:
                user.first_name = kwargs['first_name']
            if 'last_name' in kwargs:
                user.last_name = kwargs['last_name']
            if 'is_staff' in kwargs:
                user.is_staff = kwargs['is_staff']
            if 'is_superuser' in kwargs:
                user.is_superuser = kwargs['is_superuser']
            if 'groups' in kwargs:
                user.groups = kwargs['groups']
            if 'last_login' in kwargs:
                user.last_login = kwargs['last_login']
            
            user.save()
            return user
        except DoesNotExist:
            return None
    
    @staticmethod
    def delete(user_id):
        """Delete user"""
        try:
            user = UserDynamoDB.get(int(user_id))
            user.delete()
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user with username and password"""
        user = UserHelper.get_by_username(username)
        if user and check_password(password, user.get('password')):
            return user
        return None
    
    @staticmethod
    def add_to_group(user_id, group_name):
        """Add user to a group"""
        try:
            user = UserDynamoDB.get(int(user_id))
            if user.groups is None:
                user.groups = []
            if group_name not in user.groups:
                user.groups.append(group_name)
                user.save()
            return True
        except DoesNotExist:
            return False
    
    @staticmethod
    def set_password(user_id, password):
        """Set user password (hashed)"""
        return UserHelper.update(user_id, password=password)
    
    @staticmethod
    def count():
        """Count total users"""
        return UserDynamoDB.count()
