from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from enrollments.models import Enrollment
from courses.models import Course
from .models import InstructorProfile


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if request.POST.get('role') == 'instructor':
                InstructorProfile.objects.create(
                    user=user,
                    bio=request.POST.get('bio', ''),
                    expertise=request.POST.get('expertise', ''),
                    photo=request.FILES.get('photo'),
                )
            login(request, user)
            messages.success(request, 'Welcome to LearnFlow.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    instructor = getattr(request.user, 'instructor_profile', None)
    teaching_courses = instructor.courses.all() if instructor else Course.objects.none()
    sales = sum(course.enrollments.filter(payment_status='paid').count() for course in teaching_courses)
    revenue = sum(course.enrollments.filter(payment_status='paid').count() * course.instructor_earning for course in teaching_courses)
    return render(request, 'accounts/dashboard.html', {
        'enrollments': enrollments,
        'teaching_courses': teaching_courses,
        'sales': sales,
        'revenue': revenue,
    })
