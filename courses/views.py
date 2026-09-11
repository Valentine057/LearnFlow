from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from enrollments.models import Enrollment, LessonProgress
from .models import Category, Course, Lesson


def course_list(request):
    courses = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('category', 'instructor__user')
    category = request.GET.get('category')
    level = request.GET.get('level')
    if category:
        courses = courses.filter(category__slug=category)
    if level:
        courses = courses.filter(level=level)
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': Category.objects.all(),
        'selected_category': category,
        'selected_level': level,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related('category', 'instructor__user'), slug=slug, status=Course.Status.PUBLISHED)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first() if request.user.is_authenticated else None
    return render(request, 'courses/course_detail.html', {'course': course, 'enrollment': enrollment})


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.PUBLISHED)
    Enrollment.objects.get_or_create(student=request.user, course=course, defaults={'amount_paid': course.price})
    return redirect('learn_course', slug=slug)


@login_required
def learn_course(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.PUBLISHED)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, payment_status='paid')
    progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=course.lessons.first()) if course.lessons.exists() else (None, False)
    return render(request, 'courses/learn_course.html', {'course': course, 'enrollment': enrollment, 'active_lesson': progress.lesson if progress else None})


@login_required
def complete_lesson(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course, payment_status='paid')
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    LessonProgress.objects.update_or_create(enrollment=enrollment, lesson=lesson, defaults={'completed': True, 'completed_at': timezone.now()})
    return redirect('learn_course', slug=slug)


@login_required
def certificate(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    if enrollment.progress_percent < 100:
        raise Http404('Complete every lesson to unlock this certificate.')
    return render(request, 'courses/certificate.html', {'course': course, 'enrollment': enrollment})
