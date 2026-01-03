"""
Custom Authentication Backend for DynamoDB
Replaces Django's built-in authentication system
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password, check_password
from dynamodb_helpers import UserHelper


class DynamoDBAuthBackend:
    """Custom authentication backend using DynamoDB"""
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate a user with username and password"""
        user = UserHelper.get_by_username(username)
        if user and check_password(password, user.get('password')):
            return user
        return None
    
    @staticmethod
    def login(request, user):
        """Log in a user by storing their info in session"""
        request.session['user_id'] = user.get('id')
        request.session['username'] = user.get('username')
        request.session['first_name'] = user.get('first_name', '')
        request.session['last_name'] = user.get('last_name', '')
        request.session['email'] = user.get('email', '')
        request.session['groups'] = user.get('groups', [])
        request.session['is_staff'] = user.get('is_staff', False)
        request.session['is_superuser'] = user.get('is_superuser', False)
    
    @staticmethod
    def logout(request):
        """Log out the current user"""
        request.session.flush()
    
    @staticmethod
    def get_user(request):
        """Get the current logged-in user from session"""
        user_id = request.session.get('user_id')
        if user_id:
            return UserHelper.get_by_id(user_id)
        return None
    
    @staticmethod
    def is_authenticated(request):
        """Check if user is authenticated"""
        return 'user_id' in request.session


class CustomUser:
    """
    Custom user object to replace Django's User model
    Provides an interface compatible with Django templates
    """
    def __init__(self, session_data):
        self.id = session_data.get('user_id')
        self.username = session_data.get('username', '')
        self.first_name = session_data.get('first_name', '')
        self.last_name = session_data.get('last_name', '')
        self.email = session_data.get('email', '')
        self.groups_list = session_data.get('groups', [])
        self.is_staff = session_data.get('is_staff', False)
        self.is_superuser = session_data.get('is_superuser', False)
        self.is_authenticated = True
    
    def has_group(self, group_name):
        """Check if user belongs to a group"""
        return group_name in self.groups_list
    
    @property
    def is_active(self):
        return True


class AnonymousUser:
    """Anonymous user object"""
    id = None
    username = ''
    first_name = ''
    last_name = ''
    email = ''
    is_staff = False
    is_superuser = False
    is_authenticated = False
    groups_list = []
    
    def has_group(self, group_name):
        return False


class AuthenticationMiddleware:
    """Middleware to inject user object into request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Attach user object to request
        if 'user_id' in request.session:
            request.user = CustomUser(request.session)
        else:
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response


# Decorators to replace Django's auth decorators
def login_required(login_url='/'):
    """Decorator to require login"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def user_passes_test(test_func, login_url='/'):
    """Decorator to test if user passes a test"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url)
            if not test_func(request.user):
                return redirect('/')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def superuser_required(login_url='/adminlogin'):
    """Decorator to require superuser status"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.is_superuser:
                return redirect(login_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
