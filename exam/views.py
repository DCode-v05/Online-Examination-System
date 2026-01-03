from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect
from auth_backend import login_required, user_passes_test, superuser_required
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from exam import models as QMODEL
from db_adapter import CourseAdapter, QuestionAdapter, ResultAdapter, TeacherAdapter, StudentAdapter, UserAdapter



def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'exam/index.html')


def is_teacher(user):
    return user.has_group('TEACHER')

def is_student(user):
    return user.has_group('STUDENT')

def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student/student-dashboard')
                
    elif is_teacher(request.user):
        # Use TeacherAdapter instead of Django ORM
        teachers = TeacherAdapter.get_by_user_id(request.user.id)
        accountapproval = [t for t in teachers if t.get('status') == True]
        if accountapproval:
            return redirect('teacher/teacher-dashboard')
        else:
            return render(request,'teacher/teacher_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # Use adapters instead of Django ORM
    all_students = StudentAdapter.get_all()
    all_teachers = TeacherAdapter.get_all()
    approved_teachers = [t for t in all_teachers if t.get('status') == True]
    all_courses = CourseAdapter.get_all()
    all_questions = QuestionAdapter.get_all()
    
    dict={
    'total_student': len(all_students),
    'total_teacher': len(approved_teachers),
    'total_course': len(all_courses),
    'total_question': len(all_questions),
    }
    return render(request,'exam/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    # Use TeacherAdapter instead of Django ORM
    all_teachers = TeacherAdapter.get_all()
    approved_teachers = [t for t in all_teachers if t.get('status') == True]
    pending_teachers = [t for t in all_teachers if t.get('status') == False]
    
    # Calculate total salary
    total_salary = sum(t.get('salary', 0) for t in approved_teachers)
    
    dict={
    'total_teacher': len(approved_teachers),
    'pending_teacher': len(pending_teachers),
    'salary': total_salary,
    }
    return render(request,'exam/admin_teacher.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    # Use TeacherAdapter instead of Django ORM
    all_teachers = TeacherAdapter.get_all()
    teachers = [t for t in all_teachers if t.get('status') == True]
    
    # Enrich teacher data with user and course information
    for teacher in teachers:
        # Get user data
        user = UserAdapter.get_by_id(teacher.get('user_id'))
        if user:
            teacher['name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            teacher['get_name'] = teacher['name']  # For template compatibility
        else:
            teacher['name'] = 'Unknown'
            teacher['get_name'] = 'Unknown'
        
        # Get course data
        course_id = teacher.get('course_id')
        if course_id:
            course = CourseAdapter.get_by_id(course_id)
            if course:
                teacher['course'] = {
                    'id': course.get('id'),
                    'course_name': course.get('course_name')
                }
            else:
                teacher['course'] = None
        else:
            teacher['course'] = None
    
    return render(request,'exam/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def update_teacher_view(request,pk):
    # Use DynamoDB adapters for both User and Teacher
    teacher_data = TeacherAdapter.get_by_id(pk)
    if not teacher_data:
        return HttpResponseRedirect('/admin-view-teacher')
    
    user_data = UserAdapter.get_by_id(teacher_data.get('user_id'))
    if not user_data:
        return HttpResponseRedirect('/admin-view-teacher')
    
    # Get course data
    course_data = None
    if teacher_data.get('course_id'):
        course_data = CourseAdapter.get_by_id(teacher_data.get('course_id'))
    
    if request.method == 'POST':
        # Update user data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        course_id = request.POST.get('course')
        
        # Get old course_id before updating
        old_course_id = teacher_data.get('course_id')
        
        UserAdapter.update(
            user_data.get('id'),
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        TeacherAdapter.update(
            pk,
            mobile=mobile,
            course_id=course_id if course_id else None
        )
        
        # Update course assignments
        # Remove teacher from old course if it changed
        if old_course_id and old_course_id != course_id:
            CourseAdapter.update(old_course_id, assigned_teacher_id=None)
        
        # Assign teacher to new course
        if course_id:
            CourseAdapter.update(course_id, assigned_teacher_id=pk)
        
        return HttpResponseRedirect('/admin-view-teacher')
    
    # Get all courses for dropdown
    all_courses = CourseAdapter.get_all()
    mydict = {
        'user': user_data,
        'teacher': teacher_data,
        'courses': all_courses,
        'selected_course': course_data
    }
    return render(request, 'exam/update_teacher.html', context=mydict)


@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def delete_teacher_view(request,pk):
    teacher_data = TeacherAdapter.get_by_id(pk)
    if teacher_data:
        user_id = teacher_data.get('user_id')
        
        # Remove teacher assignment from course if exists
        course_id = teacher_data.get('course_id')
        if course_id:
            CourseAdapter.update(course_id, assigned_teacher_id=None)
        
        # Delete user from DynamoDB
        UserAdapter.delete(user_id)
        # Delete teacher from DynamoDB
        TeacherAdapter.delete(pk)
    
    return HttpResponseRedirect('/admin-view-teacher')





@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    # Use TeacherAdapter instead of Django ORM
    all_teachers = TeacherAdapter.get_all()
    teachers = [t for t in all_teachers if t.get('status') == False]
    
    # Enrich teacher data with user information and course information
    for teacher in teachers:
        user = UserAdapter.get_by_id(teacher.get('user_id'))
        if user:
            teacher['name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            teacher['get_name'] = teacher['name']
        else:
            teacher['name'] = 'Unknown'
            teacher['get_name'] = 'Unknown'
        
        # Add course information
        course_id = teacher.get('course_id')
        if course_id:
            course = CourseAdapter.get_by_id(course_id)
            if course:
                teacher['course'] = {'course_name': course.get('course_name', 'Unknown Course')}
            else:
                teacher['course'] = None
        else:
            teacher['course'] = None
    
    return render(request,'exam/admin_view_pending_teacher.html',{'teachers':teachers})

@login_required(login_url='adminlogin')
def approve_teacher_view(request,pk):
    teacherSalary = forms.TeacherSalaryForm()
    if request.method == 'POST':
        teacherSalary = forms.TeacherSalaryForm(request.POST)
        if teacherSalary.is_valid():
            # Get teacher data first
            teacher_data = TeacherAdapter.get_by_id(pk)
            
            # Update teacher in DynamoDB
            TeacherAdapter.update(
                pk,
                salary=teacherSalary.cleaned_data['salary'],
                status=True
            )
            
            # Update the course's assigned_teacher_id if teacher has a course
            if teacher_data and teacher_data.get('course_id'):
                course_id = teacher_data.get('course_id')
                CourseAdapter.update(course_id, assigned_teacher_id=pk)
            
        return HttpResponseRedirect('/admin-view-pending-teacher')
    return render(request, 'exam/salary_form.html', {'teacherSalary': teacherSalary})

@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def reject_teacher_view(request,pk):
    teacher_data = TeacherAdapter.get_by_id(pk)
    if teacher_data:
        user_id = teacher_data.get('user_id')
        # Delete user from DynamoDB
        UserAdapter.delete(user_id)
        # Delete teacher from DynamoDB
        TeacherAdapter.delete(pk)
    
    return HttpResponseRedirect('/admin-view-pending-teacher')

@login_required(login_url='adminlogin')
def admin_view_teacher_salary_view(request):
    # Use TeacherAdapter instead of Django ORM
    all_teachers = TeacherAdapter.get_all()
    teachers = [t for t in all_teachers if t.get('status') == True]
    return render(request,'exam/admin_view_teacher_salary.html',{'teachers':teachers})




@login_required(login_url='adminlogin')
def admin_student_view(request):
    # Use StudentAdapter instead of Django ORM
    all_students = StudentAdapter.get_all()
    dict={
    'total_student': len(all_students),
    }
    return render(request,'exam/admin_student.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    # Use StudentAdapter instead of Django ORM
    students = StudentAdapter.get_all()
    
    # Enrich student data with user information
    for student in students:
        user = UserAdapter.get_by_id(student.get('user_id'))
        if user:
            student['name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            student['get_name'] = student['name']
        else:
            student['name'] = 'Unknown'
            student['get_name'] = 'Unknown'
    
    return render(request,'exam/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
def update_student_view(request,pk):
    # Use DynamoDB adapters for both User and Student
    student_data = StudentAdapter.get_by_id(pk)
    if not student_data:
        return HttpResponseRedirect('/admin-view-student')
    
    user_data = UserAdapter.get_by_id(student_data.get('user_id'))
    if not user_data:
        return HttpResponseRedirect('/admin-view-student')
    
    userForm = SFORM.StudentUserForm()
    studentForm = SFORM.StudentForm()
    
    if request.method == 'POST':
        userForm = SFORM.StudentUserForm(request.POST)
        studentForm = SFORM.StudentForm(request.POST)
        
        if userForm.is_valid() and studentForm.is_valid():
            # Update user data
            first_name = userForm.cleaned_data['first_name']
            last_name = userForm.cleaned_data['last_name']
            username = userForm.cleaned_data['username']
            password = userForm.cleaned_data['password']
            mobile = studentForm.cleaned_data['mobile']
            
            UserAdapter.update(
                user_data.get('id'),
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password  # This will be hashed by the adapter
            )
            
            # Update student data
            StudentAdapter.update(
                pk,
                mobile=mobile
            )
            
            return redirect('admin-view-student')
    else:
        # Pre-populate forms with existing data
        userForm = SFORM.StudentUserForm(initial={
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'username': user_data.get('username'),
            'password': ''  # Don't pre-populate password
        })
        studentForm = SFORM.StudentForm(initial={
            'mobile': student_data.get('mobile')
        })
    
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    return render(request, 'exam/update_student.html', context=mydict)



@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student_data = StudentAdapter.get_by_id(pk)
    if student_data:
        user_id = student_data.get('user_id')
        # Delete user from DynamoDB
        UserAdapter.delete(user_id)
        # Delete student from DynamoDB
        StudentAdapter.delete(pk)
    
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_course_view(request):
    return render(request,'exam/admin_course.html')


@login_required(login_url='adminlogin')
def admin_add_course_view(request):
    courseForm = forms.CourseForm()
    # Note: AssignTeacherToCourseForm removed as we don't have that form anymore
    
    if request.method == 'POST':
        courseForm = forms.CourseForm(request.POST)
        
        if courseForm.is_valid():
            course_name = courseForm.cleaned_data['course_name']
            
            # Save to DynamoDB
            CourseAdapter.create(course_name)
            
            return HttpResponseRedirect('/admin-view-course')
    
    return render(request, 'exam/admin_add_course.html', {'courseForm': courseForm})


@login_required(login_url='adminlogin')
def admin_view_course_view(request):
    # Use CourseAdapter instead of Django ORM
    courses = CourseAdapter.get_all()
    
    # Enrich courses with assigned teacher information
    for course in courses:
        assigned_teacher_id = course.get('assigned_teacher_id')
        if assigned_teacher_id:
            teacher_data = TeacherAdapter.get_by_id(assigned_teacher_id)
            if teacher_data:
                user = UserAdapter.get_by_id(teacher_data.get('user_id'))
                if user:
                    # Create an object with get_name for template compatibility
                    course['assigned_teacher'] = {
                        'get_name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
                        'id': assigned_teacher_id
                    }
                else:
                    course['assigned_teacher'] = None
            else:
                course['assigned_teacher'] = None
        else:
            course['assigned_teacher'] = None
    
    return render(request,'exam/admin_view_course.html',{'courses':courses})

@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def edit_course_view(request, pk):
    # Get course from DynamoDB (pk is DynamoDB UUID)
    course_data = CourseAdapter.get_by_id(pk)
    if not course_data:
        return HttpResponseRedirect('/admin-view-course')
    
    # Get all teachers for assignment
    all_teachers = TeacherAdapter.get_all()
    approved_teachers = [t for t in all_teachers if t.get('status') == True]
    
    # Enrich teachers with user names
    for teacher in approved_teachers:
        user = UserAdapter.get_by_id(teacher.get('user_id'))
        if user:
            teacher['name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        teacher_id = request.POST.get('teacher_id')
        
        # Update course in DynamoDB
        CourseAdapter.update(pk, course_name=course_name)
        
        # Handle teacher assignment
        # First, remove this course from any other teacher
        for teacher in all_teachers:
            if teacher.get('course_id') == pk and teacher.get('id') != teacher_id:
                TeacherAdapter.update(teacher.get('id'), course_id=None)
        
        # Assign to new teacher if selected
        if teacher_id:
            TeacherAdapter.update(teacher_id, course_id=pk)
        
        return HttpResponseRedirect('/admin-view-course')
    
    # Find current teacher
    current_teacher = None
    for teacher in approved_teachers:
        if teacher.get('course_id') == pk:
            current_teacher = teacher
            break
    
    return render(request, 'exam/admin_edit_course.html', {
        'course': course_data,
        'teachers': approved_teachers,
        'current_teacher': current_teacher
    })

@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def delete_course_view(request,pk):
    # Delete from DynamoDB only
    CourseAdapter.delete(pk)
    return HttpResponseRedirect('/admin-view-course')



@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'exam/admin_question.html')


@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm = forms.QuestionForm()
    if request.method == 'POST':
        questionForm = forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            course_id = questionForm.cleaned_data['courseID']
            marks = questionForm.cleaned_data['marks']
            question = questionForm.cleaned_data['question']
            question_type = questionForm.cleaned_data['question_type']
            option1 = questionForm.cleaned_data['option1']
            option2 = questionForm.cleaned_data['option2']
            option3 = questionForm.cleaned_data['option3']
            option4 = questionForm.cleaned_data['option4']
            answer = questionForm.cleaned_data['answer']
            multiple_answers = questionForm.cleaned_data['multiple_answers']
            text_answer = questionForm.cleaned_data['text_answer']
            
            # Save to DynamoDB
            QuestionAdapter.create(
                course_id=course_id,
                marks=marks,
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
        return HttpResponseRedirect('/admin-view-question')
    return render(request, 'exam/admin_add_question.html', {'questionForm': questionForm})


@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    # Use CourseAdapter instead of Django ORM
    courses = CourseAdapter.get_all()
    return render(request,'exam/admin_view_question.html',{'courses':courses})

@login_required(login_url='adminlogin')
def view_question_view(request,pk):
    # Use QuestionAdapter instead of Django ORM
    questions = QuestionAdapter.get_by_course_id(pk)
    return render(request,'exam/view_question.html',{'questions':questions})

@login_required(login_url='adminlogin')
@superuser_required(login_url='adminlogin')
def delete_question_view(request,pk):
    # Delete from DynamoDB only
    QuestionAdapter.delete(pk)
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    # Use StudentAdapter instead of Django ORM
    students = StudentAdapter.get_all()
    return render(request,'exam/admin_view_student_marks.html',{'students':students})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    # Use CourseAdapter instead of Django ORM
    courses = CourseAdapter.get_all()
    response = render(request,'exam/admin_view_marks.html',{'courses':courses})
    response.set_cookie('student_id',str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request,pk):
    # Use adapters instead of Django ORM
    course_data = CourseAdapter.get_by_id(pk)
    student_id = request.COOKIES.get('student_id')
    student_data = StudentAdapter.get_by_id(student_id)
    questions = QuestionAdapter.get_by_course_id(pk)
    
    # Get student name
    student_name = "Unknown Student"
    if student_data:
        user = UserAdapter.get_by_id(student_data.get('user_id'))
        if user:
            student_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    
    total_marks = 0
    for q in questions:
        total_marks = total_marks + q.get('marks', 0)

    # Get results for this student and course
    all_results = ResultAdapter.get_all()
    results = [r for r in all_results if r.get('exam_id') == pk and r.get('student_id') == int(student_id)]
    
    # Add exam name to results
    for result in results:
        if course_data:
            result['exam'] = course_data.get('course_name', 'Unknown Course')
        else:
            result['exam'] = 'Unknown Course'
    
    return render(request,'exam/admin_check_marks.html',{
        'results': results, 
        'total_marks': total_marks,
        'student_name': student_name
    })
    




def aboutus_view(request):
    return render(request,'exam/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'exam/contactussuccess.html')
    return render(request, 'exam/contactus.html', {'form':sub})


