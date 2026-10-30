from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import FileResponse, Http404
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.models import SchoolOwnerProfile
from enrollments.models import Enrollment, LessonProgress
from .forms import BookForm, can_access_book, can_manage_course
from .models import Book, Category, Course, Lesson


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
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'enrollment': enrollment,
        'can_access_books': enrollment is not None and enrollment.payment_status == Enrollment.PaymentStatus.PAID
        or can_manage_course(request.user, course),
        'can_manage_books': can_manage_course(request.user, course),
    })


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.PUBLISHED)
    Enrollment.objects.get_or_create(student=request.user, course=course, defaults={'amount_paid': course.price})
    return redirect('learn_course', slug=slug)


@login_required
def learn_course(request, slug):
    course = get_object_or_404(Course.objects.select_related('instructor__user'), slug=slug)
    can_manage = can_manage_course(request.user, course)
    if course.status != Course.Status.PUBLISHED and not can_manage:
        raise Http404

    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course,
        payment_status=Enrollment.PaymentStatus.PAID,
    ).first()
    if not (enrollment or can_manage):
        raise Http404

    progress = None
    if enrollment and course.lessons.exists():
        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=course.lessons.first(),
        )
    return render(request, 'courses/learn_course.html', {
        'course': course,
        'enrollment': enrollment,
        'active_lesson': progress.lesson if progress else None,
        'can_manage_books': can_manage,
    })


@login_required
def download_book(request, slug, book_id):
    book = get_object_or_404(
        Book.objects.select_related('course__instructor__user'),
        id=book_id,
        course__slug=slug,
    )
    if not can_access_book(request.user, book):
        raise Http404

    return FileResponse(
        book.file.open('rb'),
        as_attachment=True,
        filename=book.file.name.rsplit('/', 1)[-1],
    )


def book_library(request):
    books = Book.objects.select_related(
        'course__category',
        'course__instructor__user',
    )
    if request.user.is_authenticated:
        is_school_owner = (
            request.user.is_staff
            or SchoolOwnerProfile.objects.filter(user=request.user).exists()
        )
        if not is_school_owner:
            books = books.filter(
                Q(course__status=Course.Status.PUBLISHED)
                | Q(course__instructor__user=request.user)
            )
    else:
        books = books.filter(course__status=Course.Status.PUBLISHED)

    books = list(books.order_by('course__title', 'title'))
    is_school_owner = request.user.is_authenticated and (
        request.user.is_staff
        or SchoolOwnerProfile.objects.filter(user=request.user).exists()
    )
    manageable_course_ids = {
        book.course_id for book in books
        if is_school_owner
        or (
            request.user.is_authenticated
            and book.course.instructor.user_id == request.user.id
        )
    }
    if request.user.is_authenticated:
        enrolled_course_ids = set(
            Enrollment.objects.filter(
                student=request.user,
                payment_status=Enrollment.PaymentStatus.PAID,
                course_id__in={book.course_id for book in books},
            ).values_list('course_id', flat=True)
        )
    else:
        enrolled_course_ids = set()

    return render(request, 'courses/book_library.html', {
        'books': books,
        'manageable_course_ids': manageable_course_ids,
        'accessible_course_ids': manageable_course_ids | enrolled_course_ids,
    })


@login_required
def book_create(request):
    form = BookForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        messages.success(request, f'"{book.title}" was added to the library.')
        return redirect('book_library')
    return render(request, 'courses/book_form.html', {
        'form': form,
        'heading': 'Add a book',
    })


@login_required
def book_edit(request, book_id):
    book = get_object_or_404(
        Book.objects.select_related('course__instructor__user'),
        id=book_id,
    )
    if not can_manage_course(request.user, book.course):
        raise Http404

    form = BookForm(
        request.POST or None,
        request.FILES or None,
        instance=book,
        user=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        old_file = book.file
        updated_book = form.save()
        if old_file.name != updated_book.file.name:
            transaction.on_commit(
                lambda storage=old_file.storage, name=old_file.name: storage.delete(name)
            )
        messages.success(request, f'"{updated_book.title}" was updated.')
        return redirect('book_library')
    return render(request, 'courses/book_form.html', {
        'form': form,
        'heading': 'Edit book',
        'book': book,
    })


@login_required
def book_delete(request, book_id):
    book = get_object_or_404(
        Book.objects.select_related('course__instructor__user'),
        id=book_id,
    )
    if not can_manage_course(request.user, book.course):
        raise Http404

    if request.method == 'POST':
        file_storage = book.file.storage
        file_name = book.file.name
        title = book.title
        book.delete()
        transaction.on_commit(
            lambda storage=file_storage, name=file_name: storage.delete(name)
        )
        messages.success(request, f'"{title}" was deleted.')
        return redirect('book_library')
    return render(request, 'courses/book_confirm_delete.html', {'book': book})


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
