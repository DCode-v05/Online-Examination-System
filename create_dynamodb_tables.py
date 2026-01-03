"""
Script to create DynamoDB tables
Run this script once to set up all required DynamoDB tables
"""
import boto3
from botocore.exceptions import ClientError
from dynamodb_config import dynamodb_client, TABLE_NAMES, AWS_REGION

def create_courses_table():
    """Create Courses table"""
    try:
        table = dynamodb_client.create_table(
            TableName=TABLE_NAMES['course'],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {TABLE_NAMES['course']}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TABLE_NAMES['course']} already exists")
        else:
            print(f"✗ Error creating {TABLE_NAMES['course']}: {e}")
        return False

def create_questions_table():
    """Create Questions table"""
    try:
        table = dynamodb_client.create_table(
            TableName=TABLE_NAMES['question'],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'course_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'course_id-index',
                    'KeySchema': [
                        {'AttributeName': 'course_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {TABLE_NAMES['question']}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TABLE_NAMES['question']} already exists")
        else:
            print(f"✗ Error creating {TABLE_NAMES['question']}: {e}")
        return False

def create_results_table():
    """Create Results table"""
    try:
        table = dynamodb_client.create_table(
            TableName=TABLE_NAMES['result'],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'student_id', 'AttributeType': 'S'},
                {'AttributeName': 'exam_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'student_id-index',
                    'KeySchema': [
                        {'AttributeName': 'student_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'exam_id-index',
                    'KeySchema': [
                        {'AttributeName': 'exam_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {TABLE_NAMES['result']}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TABLE_NAMES['result']} already exists")
        else:
            print(f"✗ Error creating {TABLE_NAMES['result']}: {e}")
        return False

def create_teachers_table():
    """Create Teachers table"""
    try:
        table = dynamodb_client.create_table(
            TableName=TABLE_NAMES['teacher'],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'N'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {TABLE_NAMES['teacher']}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TABLE_NAMES['teacher']} already exists")
        else:
            print(f"✗ Error creating {TABLE_NAMES['teacher']}: {e}")
        return False

def create_students_table():
    """Create Students table"""
    try:
        table = dynamodb_client.create_table(
            TableName=TABLE_NAMES['student'],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'N'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_id-index',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {TABLE_NAMES['student']}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TABLE_NAMES['student']} already exists")
        else:
            print(f"✗ Error creating {TABLE_NAMES['student']}: {e}")
        return False

def create_users_table():
    """Create Users table (for Django User model)"""
    try:
        table = dynamodb_client.create_table(
            TableName=TABLE_NAMES['user'],
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'N'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✓ Created table: {TABLE_NAMES['user']}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TABLE_NAMES['user']} already exists")
        else:
            print(f"✗ Error creating {TABLE_NAMES['user']}: {e}")
        return False

def create_all_tables():
    """Create all DynamoDB tables"""
    print("=" * 60)
    print("Creating DynamoDB Tables for Online Examination System")
    print("=" * 60)
    print(f"Region: {AWS_REGION}")
    print()
    
    create_courses_table()
    create_questions_table()
    create_results_table()
    create_teachers_table()
    create_students_table()
    create_users_table()
    
    print()
    print("=" * 60)
    print("Table creation process completed!")
    print("Note: It may take a few moments for tables to be fully active.")
    print("=" * 60)

if __name__ == "__main__":
    create_all_tables()
