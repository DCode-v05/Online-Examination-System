from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect
from auth_backend import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from student import models as SMODEL
from exam import forms as QFORM
from django.forms import modelformset_factory
from db_adapter import CourseAdapter, QuestionAdapter, ResultAdapter, TeacherAdapter, StudentAdapter, UserAdapter


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm = forms.TeacherUserForm()
    teacherForm = forms.TeacherForm()
    
    if request.method == 'POST':
        userForm = forms.TeacherUserForm(request.POST)
        teacherForm = forms.TeacherForm(request.POST)
        
        if userForm.is_valid() and teacherForm.is_valid():
            # Get form data
            username = userForm.cleaned_data['username']
            password = userForm.cleaned_data['password']
            first_name = userForm.cleaned_data['first_name']
            last_name = userForm.cleaned_data['last_name']
            mobile = teacherForm.cleaned_data['mobile']
            course_id = teacherForm.cleaned_data.get('course')
            
            # Create user in DynamoDB
            try:
                user_data = UserAdapter.create(
                    username=username,
                    email='',  # Email not required in current form
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Add to TEACHER group
                UserAdapter.add_to_group(user_data.id, 'TEACHER')
                
                # Create teacher profile
                TeacherAdapter.create(
                    user_id=user_data.id,
                    mobile=mobile,
                    status=False,  # Needs admin approval
                    salary=None,
                    course_id=course_id if course_id else None
                )
                
                return HttpResponseRedirect('teacherlogin')
            except Exception as e:
                print(f"Error creating teacher: {e}")
                # You can add error handling here
            
    return render(request, 'teacher/teachersignup.html', {'userForm': userForm, 'teacherForm': teacherForm})


def is_teacher(user):
    return user.has_group('TEACHER')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    # Use TeacherAdapter instead of Django ORM
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    if not teacher:
        return HttpResponseRedirect('/teacher/teacherlogin')
    
    assigned_course_id = teacher.get('course_id')
    assigned_course = CourseAdapter.get_by_id(assigned_course_id) if assigned_course_id else None
    
    # Get questions only for teacher's assigned course
    if assigned_course:
        total_question = len(QuestionAdapter.get_by_course_id(assigned_course_id))
        # Get results that need review
        all_results = ResultAdapter.get_all()
        pending_reviews = len([r for r in all_results if r.get('exam_id') == assigned_course_id and r.get('needs_review') == True])
    else:
        total_question = 0
        pending_reviews = 0
    
    all_students = StudentAdapter.get_all()
    
    dict = {
        'assigned_course': assigned_course,
        'total_course': 1 if assigned_course else 0,
        'total_question': total_question,
        'total_student': len(all_students),
        'pending_reviews': pending_reviews
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm = QFORM.CourseForm()
    if request.method == 'POST':
        courseForm = QFORM.CourseForm(request.POST)
        if courseForm.is_valid():
            course_name = courseForm.cleaned_data['course_name']
            # Save to DynamoDB
            CourseAdapter.create(course_name)
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    # Use CourseAdapter instead of Django ORM
    courses = CourseAdapter.get_all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    # Delete from DynamoDB
    CourseAdapter.delete(pk)
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    # Get teacher's assigned course using TeacherAdapter
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    if not teacher:
        return HttpResponseRedirect('/teacher/teacherlogin')
    
    course_id = teacher.get('course_id')
    if not course_id:
        # If teacher has no assigned course, show error message
        return render(request, 'teacher/no_course_assigned.html')
    
    course = CourseAdapter.get_by_id(course_id)

    if request.method == 'POST':
        # Handle form submission
        questionForm = QFORM.QuestionFormNoCourse(request.POST)
        
        if questionForm.is_valid():
            # Save to DynamoDB
            try:
                QuestionAdapter.create(
                    course_id=course_id,
                    marks=int(questionForm.cleaned_data.get('marks', 0)),
                    question=questionForm.cleaned_data.get('question', ''),
                    question_type=questionForm.cleaned_data.get('question_type', 'radio'),
                    option1=questionForm.cleaned_data.get('option1', ''),
                    option2=questionForm.cleaned_data.get('option2', ''),
                    option3=questionForm.cleaned_data.get('option3', ''),
                    option4=questionForm.cleaned_data.get('option4', ''),
                    answer=questionForm.cleaned_data.get('answer', ''),
                    multiple_answers=questionForm.cleaned_data.get('multiple_answers', ''),
                    text_answer=questionForm.cleaned_data.get('text_answer', '')
                )
                # Redirect back to same page to allow adding more questions
                return HttpResponseRedirect('/teacher/teacher-add-question')
            except Exception as e:
                print(f"Error adding question: {e}")
    else:
        questionForm = QFORM.QuestionFormNoCourse()
    
    return render(request, 'teacher/teacher_add_question.html', {'questionForm': questionForm, 'course': course})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    # Use TeacherAdapter instead of Django ORM
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    # Only show teacher's assigned course
    if teacher and teacher.get('course_id'):
        course = CourseAdapter.get_by_id(teacher.get('course_id'))
        if course:
            # Get all questions for this course
            all_questions = QuestionAdapter.get_all()
            course_questions = [q for q in all_questions if q.get('course_id') == course.get('id')]
            
            # Calculate total questions and total marks
            course['total_questions'] = len(course_questions)
            course['total_marks'] = sum(int(q.get('marks', 0)) for q in course_questions)
            
            courses = [course]
        else:
            courses = []
    else:
        courses = []
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    # Verify that the course belongs to this teacher
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    if teacher and teacher.get('course_id') == pk:
        questions = QuestionAdapter.get_by_course_id(pk)
        return render(request,'teacher/see_question.html',{'questions':questions})
    else:
        return HttpResponseRedirect('/teacher/teacher-view-question')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    # Verify that the question belongs to teacher's course
    question_data = QuestionAdapter.get_by_id(pk)
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    if teacher and question_data and question_data.get('course_id') == teacher.get('course_id'):
        # Delete from DynamoDB only
        QuestionAdapter.delete(pk)
    
    return HttpResponseRedirect('/teacher/teacher-view-question')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_review_answers_view(request):
    """View to show all pending exams that need teacher review"""
    from datetime import datetime, timedelta
    
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    if not teacher or not teacher.get('course_id'):
        return render(request, 'teacher/no_course_assigned.html')
    
    course_id = teacher.get('course_id')
    course = CourseAdapter.get_by_id(course_id)
    
    # Get all results for teacher's course that need review
    all_results = ResultAdapter.get_all()
    pending_results = [r for r in all_results if r.get('exam_id') == course_id and r.get('needs_review') == True]
    
    # Enrich pending results with student and course data
    for result in pending_results:
        # Add course info
        result['exam'] = course
        
        # Add student info
        student_id = result.get('student_id')
        if student_id:
            student = StudentAdapter.get_by_id(student_id)
            if student:
                user_id = student.get('user_id')
                user = UserAdapter.get_by_id(user_id)
                if user:
                    student['user'] = user
                result['student'] = student
        
        # Convert ISO date string to IST datetime object
        date_str = result.get('date')
        if date_str:
            try:
                # Parse ISO format and convert to IST (UTC+5:30)
                utc_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                ist_dt = utc_dt + timedelta(hours=5, minutes=30)
                result['date'] = ist_dt
            except:
                pass
    
    # Sort by date (descending)
    pending_results.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render(request, 'teacher/teacher_review_answers.html', {
        'pending_results': pending_results,
        'course': course
    })


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_grade_exam_view(request, result_id):
    """View to grade a specific student's exam with text answers"""
    import json
    from datetime import datetime, timedelta
    
    teachers = TeacherAdapter.get_by_user_id(request.user.id)
    teacher = teachers[0] if teachers else None
    
    result_data = ResultAdapter.get_by_id(result_id)
    
    if not result_data:
        return HttpResponseRedirect('/teacher/teacher-review-answers')
    
    # Get student information
    student_id = result_data.get('student_id')
    student = StudentAdapter.get_by_id(student_id) if student_id else None
    user = UserAdapter.get_by_id(student.get('user_id')) if student else None
    
    # Enrich student with user data
    if student and user:
        student['user'] = user
        result_data['student'] = student
    
    # Convert ISO date string to IST datetime object
    date_str = result_data.get('date')
    if date_str:
        try:
            # Parse ISO format and convert to IST (UTC+5:30)
            utc_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            ist_dt = utc_dt + timedelta(hours=5, minutes=30)
            result_data['date'] = ist_dt
        except:
            pass
    
    # Security check: verify this result belongs to teacher's course
    if not teacher or not teacher.get('course_id') or result_data.get('exam_id') != teacher.get('course_id'):
        return HttpResponseRedirect('/teacher/teacher-review-answers')
    
    course_id = teacher.get('course_id')
    course = CourseAdapter.get_by_id(course_id)
    
    # Get all questions for this course
    questions = QuestionAdapter.get_by_course_id(course_id)
    questions.sort(key=lambda x: x.get('id', 0))
    
    # Parse student answers
    student_answers = json.loads(result_data.get('student_answers', '{}')) if result_data.get('student_answers') else {}
    
    # Create a list of questions with student answers
    questions_with_answers = []
    for question in questions:
        q_id = str(question.get('id'))
        answer_data = student_answers.get(q_id, {})
        student_ans = answer_data.get('answer', 'Not Answered')
        
        # Check if answer is correct
        is_correct = False
        if question.get('question_type') == 'radio':
            is_correct = (student_ans == question.get('answer'))
        elif question.get('question_type') == 'checkbox':
            is_correct = (student_ans == question.get('multiple_answers'))
        
        questions_with_answers.append({
            'question': question,
            'student_answer': student_ans,
            'question_number': answer_data.get('question_number', 0),
            'is_text': question.get('question_type') == 'text',
            'is_correct': is_correct
        })
    
    if request.method == 'POST':
        # Process grading
        additional_marks = 0
        
        for question in questions:
            if question.get('question_type') == 'text':
                # Get marks awarded by teacher for this text question
                marks_key = f'marks_{question.get("id")}'
                awarded_marks = request.POST.get(marks_key, '0')
                try:
                    awarded_marks = int(awarded_marks)
                    # Validate marks don't exceed question marks
                    if awarded_marks > question.get('marks', 0):
                        awarded_marks = question.get('marks', 0)
                    if awarded_marks < 0:
                        awarded_marks = 0
                    additional_marks += awarded_marks
                except ValueError:
                    pass
        
        # Update result with additional marks from text questions
        current_marks = result_data.get('marks', 0)
        new_marks = current_marks + additional_marks
        
        ResultAdapter.update(
            result_id,
            marks=new_marks,
            needs_review=False
        )
        
        # Also update in Django ORM for compatibility
        try:
            result = QMODEL.Result.objects.get(id=result_id)
            result.marks = new_marks
            result.needs_review = False
            result.save()
        except:
            pass
        
        return HttpResponseRedirect('/teacher/teacher-review-answers')
    
    return render(request, 'teacher/teacher_grade_exam.html', {
        'result': result_data,
        'questions_with_answers': questions_with_answers,
        'course': course
    })
