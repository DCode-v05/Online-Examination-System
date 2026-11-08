"""
Custom authentication views for DynamoDB
Replaces Django's built-in authentication views
"""
from django.shortcuts import render, redirect
from django.http import HttpResponse
from auth_backend import DynamoDBAuthBackend
from db_adapter import UserAdapter
from exam.forms import LoginForm


def custom_login_view(request, template_name, redirect_url='/afterlogin'):
    """Generic login view"""
    if request.user.is_authenticated:
        return redirect(redirect_url)
    
    form = LoginForm()
    error = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = UserAdapter.authenticate(username, password)
            if user:
                DynamoDBAuthBackend.login(request, user)
                from datetime import datetime
                UserAdapter.update(user.get('id'), last_login=datetime.utcnow())
                return redirect(redirect_url)
            else:
                error = 'Invalid username or password'
    
    return render(request, template_name, {'form': form, 'error': error})


def adminlogin_view(request):
    """Admin login view"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('/admin-dashboard')
    
    form = LoginForm()
    error = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = UserAdapter.authenticate(username, password)
            if user and user.get('is_superuser'):
                DynamoDBAuthBackend.login(request, user)
                from datetime import datetime
                UserAdapter.update(user.get('id'), last_login=datetime.utcnow())
                return redirect('/admin-dashboard')
            else:
                error = 'Invalid admin credentials'
    
    return render(request, 'exam/adminlogin.html', {'form': form, 'error': error})


def teacherlogin_view(request):
    """Teacher login view"""
    return custom_login_view(request, 'teacher/teacherlogin.html', '/afterlogin')


def studentlogin_view(request):
    """Student login view"""
    return custom_login_view(request, 'student/studentlogin.html', '/afterlogin')


def logout_view(request):
    """Logout view"""
    DynamoDBAuthBackend.logout(request)
    return render(request, 'exam/logout.html')
