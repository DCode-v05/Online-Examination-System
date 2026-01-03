"""
Create Superuser for DynamoDB-Only System
Run this after creating all DynamoDB tables
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinexam.settings')
django.setup()

from db_adapter import UserAdapter

def create_superuser():
    """Create a superuser account"""
    print("Creating superuser account...")
    print("-" * 50)
    
    username = input("Username: ") or "admin"
    email = input("Email: ") or "admin@example.com"
    first_name = input("First name: ") or "Admin"
    last_name = input("Last name: ") or "User"
    password = input("Password: ") or "admin123"
    
    # Check if user already exists
    existing_user = UserAdapter.get_by_username(username)
    if existing_user:
        print(f"\n❌ User '{username}' already exists!")
        overwrite = input("Do you want to delete and recreate? (yes/no): ")
        if overwrite.lower() == 'yes':
            UserAdapter.delete(existing_user.get('id'))
            print(f"✓ Deleted existing user '{username}'")
        else:
            print("Cancelled.")
            return
    
    try:
        # Create superuser
        user = UserAdapter.create(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            groups=['ADMIN']
        )
        
        print("\n" + "=" * 50)
        print("✓ Superuser created successfully!")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Name: {first_name} {last_name}")
        print("=" * 50)
        print("\nYou can now login at: /adminlogin")
        
    except Exception as e:
        print(f"\n❌ Error creating superuser: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_superuser()
