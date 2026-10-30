from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('library/', views.book_library, name='book_library'),
    path('library/books/add/', views.book_create, name='book_create'),
    path('library/books/<int:book_id>/edit/', views.book_edit, name='book_edit'),
    path('library/books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:slug>/learn/', views.learn_course, name='learn_course'),
    path('<slug:slug>/books/<int:book_id>/download/', views.download_book, name='download_book'),
    path('<slug:slug>/lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('<slug:slug>/certificate/', views.certificate, name='certificate'),
]
