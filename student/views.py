from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect
from auth_backend import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from db_adapter import CourseAdapter, QuestionAdapter, ResultAdapter, TeacherAdapter, StudentAdapter, UserAdapter


def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST)
        
        if userForm.is_valid() and studentForm.is_valid():
            username = userForm.cleaned_data['username']
            password = userForm.cleaned_data['password']
            first_name = userForm.cleaned_data['first_name']
            last_name = userForm.cleaned_data['last_name']
            mobile = studentForm.cleaned_data['mobile']
            
            try:
                user_data = UserAdapter.create(
                    username=username,
                    email='',
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                UserAdapter.add_to_group(user_data.id, 'STUDENT')
                
                StudentAdapter.create(
                    user_id=user_data.id,
                    mobile=mobile
                )
                
                return HttpResponseRedirect('studentlogin')
            except Exception as e:
                print(f"Error creating student: {e}")
            
    return render(request, 'student/studentsignup.html', {'userForm': userForm, 'studentForm': studentForm})

def is_student(user):
    return user.has_group('STUDENT')

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    all_courses = CourseAdapter.get_all()
    all_questions = QuestionAdapter.get_all()
    
    dict = {
        'total_course': len(all_courses),
        'total_question': len(all_questions),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses = CourseAdapter.get_all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    if '.' in pk or pk.endswith('.png') or pk.endswith('.jpg'):
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Invalid course ID")
    
    course = CourseAdapter.get_by_id(pk)
    if not course:
        return HttpResponseRedirect('/student/student-exam')
    
    questions = QuestionAdapter.get_by_course_id(pk)
    
    total_questions = len(questions)
    total_marks = 0
    for q in questions:
        total_marks = total_marks + q.get('marks', 0)
    
    return render(request,'student/take_exam.html',{
        'course': course,
        'course_id': pk,
        'total_questions': total_questions,
        'total_marks': total_marks
    })

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    if '.' in pk or pk.endswith('.png') or pk.endswith('.jpg'):
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Invalid course ID")
    
    course = CourseAdapter.get_by_id(pk)
    if not course:
        return HttpResponseRedirect('/student/student-exam')
    
    questions = QuestionAdapter.get_by_course_id(pk)
    
    if request.method == 'POST':
        pass
    response = render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id', pk)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    course_id_cookie = request.COOKIES.get('course_id')
    if course_id_cookie is not None:
        course_id = course_id_cookie
        
        course = CourseAdapter.get_by_id(course_id)
        
        import json
        
        total_marks = 0
        has_text_questions = False
        student_answers_dict = {}
        
        questions = QuestionAdapter.get_by_course_id(course_id)
        questions.sort(key=lambda x: x.get('id', 0))
        
        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i+1))
            question = questions[i]
            
            student_answers_dict[str(question.get('id'))] = {
                'answer': selected_ans if selected_ans else '',
                'question_number': i+1,
                'question_type': question.get('question_type', 'radio')
            }
            
            is_correct = False
            
            if question.get('question_type') == 'radio':
                actual_answer = question.get('answer')
                if selected_ans == actual_answer:
                    is_correct = True
                    
            elif question.get('question_type') == 'checkbox':
                actual_answers = question.get('multiple_answers')
                if selected_ans and actual_answers:
                    selected_sorted = ','.join(sorted(selected_ans.split(',')))
                    actual_sorted = ','.join(sorted(actual_answers.split(',')))
                    if selected_sorted == actual_sorted:
                        is_correct = True
                        
            elif question.get('question_type') == 'text':
                has_text_questions = True
                continue
            
            if is_correct:
                total_marks = total_marks + question.get('marks', 0)
        
        students = StudentAdapter.get_by_user_id(request.user.id)
        student = students[0] if students else None
        
        if not student:
            return HttpResponseRedirect('studentlogin')
        
        from datetime import datetime
        
        print(f"DEBUG: Saving result for student {student.get('id')} for course {course_id}")
        print(f"DEBUG: Total marks: {total_marks}")
        
        ResultAdapter.create(
            student_id=student.get('id'),
            exam_id=course_id,
            marks=total_marks,
            needs_review=has_text_questions,
            student_answers=json.dumps(student_answers_dict),
            date=datetime.now().isoformat()
        )
        
        print(f"DEBUG: Result saved successfully!")

        return HttpResponseRedirect('/student/view-result')


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    students = StudentAdapter.get_by_user_id(request.user.id)
    student = students[0] if students else None
    
    if not student:
        return HttpResponseRedirect('studentlogin')
    
    print(f"DEBUG view_result: Student ID = {student.get('id')}")
    
    all_results = ResultAdapter.get_all()
    print(f"DEBUG view_result: Total results in DB = {len(all_results)}")
    
    student_results = [r for r in all_results if r.get('student_id') == student.get('id')]
    print(f"DEBUG view_result: Student results found = {len(student_results)}")
    
    if student_results:
        print(f"DEBUG view_result: First result student_id = {student_results[0].get('student_id')}")
        print(f"DEBUG view_result: Comparing with student ID = {student.get('id')}")
    
    course_ids = list(set([r.get('exam_id') for r in student_results]))
    print(f"DEBUG view_result: Course IDs = {course_ids}")
    
    courses = []
    for course_id in course_ids:
        course = CourseAdapter.get_by_id(course_id)
        if course:
            course['course_id'] = course_id
            courses.append(course)
    
    print(f"DEBUG view_result: Courses to display = {len(courses)}")
    
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    from datetime import datetime, timedelta
    course = CourseAdapter.get_by_id(pk)
    students = StudentAdapter.get_by_user_id(request.user.id)
    student = students[0] if students else None
    
    if not student:
        return HttpResponseRedirect('studentlogin')
    
    all_results = ResultAdapter.get_all()
    results = [r for r in all_results if r.get('exam_id') == pk and r.get('student_id') == student.get('id')]
    
    for result in results:
        if course:
            result['exam'] = course.get('course_name', 'Unknown Course')
        else:
            result['exam'] = 'Unknown Course'
        
        date_str = result.get('date')
        if date_str:
            try:
                utc_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                ist_dt = utc_dt + timedelta(hours=5, minutes=30)
                result['date'] = ist_dt
            except:
                pass
    
    questions = QuestionAdapter.get_by_course_id(pk)
    total_marks = 0
    for q in questions:
        total_marks = total_marks + q.get('marks', 0)
    
    return render(request,'student/check_marks.html',{'results':results, 'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses = CourseAdapter.get_all()
    return render(request,'student/student_marks.html',{'courses':courses})
  