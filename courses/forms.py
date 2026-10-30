from django import forms

from accounts.models import SchoolOwnerProfile
from .models import Book, Course


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('course', 'title', 'author', 'description', 'file')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        courses = Course.objects.all()
        is_school_owner = user.is_staff or SchoolOwnerProfile.objects.filter(user=user).exists()
        if not is_school_owner:
            courses = courses.filter(instructor__user=user)
        self.fields['course'].queryset = courses.order_by('title')


def can_manage_course(user, course):
    if not user.is_authenticated:
        return False
    return (
        user.is_staff
        or SchoolOwnerProfile.objects.filter(user=user).exists()
        or course.instructor.user_id == user.id
    )


def can_access_book(user, book):
    if can_manage_course(user, book.course):
        return True
    if not user.is_authenticated:
        return False
    from enrollments.models import Enrollment

    return Enrollment.objects.filter(
        student=user,
        course=book.course,
        payment_status=Enrollment.PaymentStatus.PAID,
    ).exists()
