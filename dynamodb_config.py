"""
DynamoDB Configuration and Connection
"""
import os
from dotenv import load_dotenv
import boto3
from pynamodb.models import Model
from pynamodb.connection import Connection

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

dynamodb_client = boto3.client(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

TABLE_NAMES = {
    'course': os.getenv('DYNAMODB_COURSE_TABLE', 'OnlineExam_Courses'),
    'question': os.getenv('DYNAMODB_QUESTION_TABLE', 'OnlineExam_Questions'),
    'result': os.getenv('DYNAMODB_RESULT_TABLE', 'OnlineExam_Results'),
    'teacher': os.getenv('DYNAMODB_TEACHER_TABLE', 'OnlineExam_Teachers'),
    'student': os.getenv('DYNAMODB_STUDENT_TABLE', 'OnlineExam_Students'),
    'user': os.getenv('DYNAMODB_USER_TABLE', 'OnlineExam_Users'),
}

Connection(
    region=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def get_table(table_name):
    """Get a DynamoDB table resource"""
    return dynamodb.Table(table_name)

def table_exists(table_name):
    """Check if a table exists"""
    try:
        dynamodb_client.describe_table(TableName=table_name)
        return True
    except dynamodb_client.exceptions.ResourceNotFoundException:
        return False
    except Exception as e:
        print(f"Error checking table {table_name}: {e}")
        return False
