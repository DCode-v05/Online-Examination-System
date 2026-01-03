from django.urls import path
from student import views
from exam import auth_views as custom_auth_views

urlpatterns = [
path('studentclick', views.studentclick_view),
path('studentlogin', custom_auth_views.studentlogin_view, name='studentlogin'),
path('studentsignup', views.student_signup_view,name='studentsignup'),
path('student-dashboard', views.student_dashboard_view,name='student-dashboard'),
path('student-exam', views.student_exam_view,name='student-exam'),
path('take-exam/<str:pk>', views.take_exam_view,name='take-exam'),
path('start-exam/<str:pk>', views.start_exam_view,name='start-exam'),

path('calculate-marks', views.calculate_marks_view,name='calculate-marks'),
path('view-result', views.view_result_view,name='view-result'),
path('check-marks/<str:pk>', views.check_marks_view,name='check-marks'),
path('student-marks', views.student_marks_view,name='student-marks'),
]