from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .api import CourseViewSet, EnrollmentViewSet, MyCoursesView, course_lessons

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='api-course')
router.register('enrollments', EnrollmentViewSet, basename='api-enrollment')

urlpatterns = [
    path('', include(router.urls)),
    path('courses/<int:pk>/lessons/', course_lessons, name='course-lessons'),
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
]
