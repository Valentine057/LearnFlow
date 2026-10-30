from django.contrib import admin
from .models import Book, Category, Course, Coupon, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class BookInline(admin.TabularInline):
    model = Book
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'status', 'price')
    list_filter = ('status', 'category', 'level')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline, BookInline]


admin.site.register([Category, Lesson, Book, Coupon])
