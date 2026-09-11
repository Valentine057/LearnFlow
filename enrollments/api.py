from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from courses.models import Course, Lesson
from .models import Enrollment


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.CharField(source='instructor.user.get_full_name', read_only=True)
    lesson_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'category', 'instructor', 'price', 'level', 'lesson_count']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'duration_minutes']


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'payment_status', 'amount_paid', 'progress_percent', 'enrolled_at']
        read_only_fields = ['payment_status', 'amount_paid']

    def create(self, validated_data):
        course = validated_data['course']
        enrollment, _ = Enrollment.objects.get_or_create(student=self.context['request'].user, course=course, defaults={'amount_paid': course.price})
        return enrollment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_lessons(request, pk):
    enrollment = get_object_or_404(Enrollment, student=request.user, course_id=pk, payment_status='paid')
    return Response(LessonSerializer(enrollment.course.lessons.all(), many=True).data)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('instructor__user')
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course')


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        return Response(EnrollmentSerializer(enrollments, many=True).data)
