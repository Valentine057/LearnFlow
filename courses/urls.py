from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:slug>/learn/', views.learn_course, name='learn_course'),
    path('<slug:slug>/lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('<slug:slug>/certificate/', views.certificate, name='certificate'),
]
