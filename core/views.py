from django.shortcuts import render
from courses.models import Category, Course


def home(request):
    courses = Course.objects.filter(status=Course.Status.PUBLISHED).select_related('category', 'instructor__user')
    return render(request, 'core/home.html', {
        'featured_courses': courses.filter(is_featured=True)[:3],
        'courses': courses[:6],
        'categories': Category.objects.all()[:8],
    })


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')
