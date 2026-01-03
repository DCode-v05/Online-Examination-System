from django.urls import path
from teacher import views
from exam import auth_views as custom_auth_views

urlpatterns = [
path('teacherclick', views.teacherclick_view),
path('teacherlogin', custom_auth_views.teacherlogin_view, name='teacherlogin'),
path('teachersignup', views.teacher_signup_view,name='teachersignup'),
path('teacher-dashboard', views.teacher_dashboard_view,name='teacher-dashboard'),

path('teacher-question', views.teacher_question_view,name='teacher-question'),
path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),
path('teacher-view-question', views.teacher_view_question_view,name='teacher-view-question'),
path('see-question/<str:pk>', views.see_question_view,name='see-question'),
path('remove-question/<str:pk>', views.remove_question_view,name='remove-question'),

path('teacher-review-answers', views.teacher_review_answers_view,name='teacher-review-answers'),
path('teacher-grade-exam/<str:result_id>', views.teacher_grade_exam_view,name='teacher-grade-exam'),
]