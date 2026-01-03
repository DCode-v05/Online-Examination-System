"""
DynamoDB Models using PynamoDB
These replace the Django ORM models for DynamoDB operations
"""
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute,
    BooleanAttribute, ListAttribute, MapAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from datetime import datetime
import os
from dynamodb_config import AWS_REGION, TABLE_NAMES

# Indexes for querying
class UserIdIndex(GlobalSecondaryIndex):
    """Index for querying by user_id"""
    class Meta:
        index_name = 'user_id-index'
        projection = AllProjection()
    
    user_id = NumberAttribute(hash_key=True)

class CourseIdIndex(GlobalSecondaryIndex):
    """Index for querying by course_id"""
    class Meta:
        index_name = 'course_id-index'
        projection = AllProjection()
    
    course_id = UnicodeAttribute(hash_key=True)

class ExamIdIndex(GlobalSecondaryIndex):
    """Index for querying by exam_id"""
    class Meta:
        index_name = 'exam_id-index'
        projection = AllProjection()
    
    exam_id = UnicodeAttribute(hash_key=True)

class StudentIdIndex(GlobalSecondaryIndex):
    """Index for querying by student_id"""
    class Meta:
        index_name = 'student_id-index'
        projection = AllProjection()
    
    student_id = UnicodeAttribute(hash_key=True)


class UsernameIndex(GlobalSecondaryIndex):
    """Index for querying by username"""
    class Meta:
        index_name = 'username-index'
        projection = AllProjection()
    
    username = UnicodeAttribute(hash_key=True)


# User Model for DynamoDB
class UserDynamoDB(Model):
    """
    DynamoDB model for User (replaces Django User model)
    """
    class Meta:
        table_name = TABLE_NAMES['user']
        region = AWS_REGION
    
    id = NumberAttribute(hash_key=True)
    username = UnicodeAttribute()
    email = UnicodeAttribute(null=True)
    password = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    is_staff = BooleanAttribute(default=False)
    is_active = BooleanAttribute(default=True)
    is_superuser = BooleanAttribute(default=False)
    date_joined = UTCDateTimeAttribute(default=datetime.utcnow)
    last_login = UTCDateTimeAttribute(null=True)
    groups = ListAttribute(null=True)  # Store group names as list
    
    # Indexes
    username_index = UsernameIndex()


# Course Model
class CourseDynamoDB(Model):
    """
    DynamoDB model for Course
    """
    class Meta:
        table_name = TABLE_NAMES['course']
        region = AWS_REGION
    
    id = UnicodeAttribute(hash_key=True)  # UUID
    course_name = UnicodeAttribute()
    assigned_teacher_id = UnicodeAttribute(null=True)  # Reference to teacher


# Question Model
class QuestionDynamoDB(Model):
    """
    DynamoDB model for Question
    """
    class Meta:
        table_name = TABLE_NAMES['question']
        region = AWS_REGION
    
    id = UnicodeAttribute(hash_key=True)  # UUID
    course_id = UnicodeAttribute()
    
    marks = NumberAttribute()
    question = UnicodeAttribute()
    question_type = UnicodeAttribute(default='radio')  # radio, checkbox, text
    option1 = UnicodeAttribute(null=True)
    option2 = UnicodeAttribute(null=True)
    option3 = UnicodeAttribute(null=True)
    option4 = UnicodeAttribute(null=True)
    answer = UnicodeAttribute(null=True)
    multiple_answers = UnicodeAttribute(null=True)
    text_answer = UnicodeAttribute(null=True)


# Result Model
class ResultDynamoDB(Model):
    """
    DynamoDB model for Result
    """
    class Meta:
        table_name = TABLE_NAMES['result']
        region = AWS_REGION
    
    id = UnicodeAttribute(hash_key=True)  # UUID
    student_id = UnicodeAttribute()
    exam_id = UnicodeAttribute()  # course_id
    
    marks = NumberAttribute()
    date = UnicodeAttribute(null=True)  # Store as ISO format string
    needs_review = BooleanAttribute(default=False)
    student_answers = UnicodeAttribute(null=True)  # JSON string


# Teacher Model
class TeacherDynamoDB(Model):
    """
    DynamoDB model for Teacher
    """
    class Meta:
        table_name = TABLE_NAMES['teacher']
        region = AWS_REGION
    
    id = UnicodeAttribute(hash_key=True)  # UUID
    user_id = NumberAttribute()
    
    mobile = UnicodeAttribute()
    course_id = UnicodeAttribute(null=True)
    status = BooleanAttribute(default=False)
    salary = NumberAttribute(null=True)


# Student Model
class StudentDynamoDB(Model):
    """
    DynamoDB model for Student
    """
    class Meta:
        table_name = TABLE_NAMES['student']
        region = AWS_REGION
    
    id = UnicodeAttribute(hash_key=True)  # UUID
    user_id = NumberAttribute()
    
    mobile = UnicodeAttribute()
