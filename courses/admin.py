from django.contrib import admin
from .models import Category, Course, Coupon, Lesson

admin.site.register([Category, Course, Lesson, Coupon])
