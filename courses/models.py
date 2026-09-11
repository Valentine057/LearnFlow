from decimal import Decimal
from django.db import models
from accounts.models import InstructorProfile


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='courses')
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.FileField(upload_to='courses/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def platform_fee(self):
        return self.price * Decimal('0.30')

    @property
    def instructor_earning(self):
        return self.price * Decimal('0.70')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=180)
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)
    duration_minutes = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f'{self.course.title}: {self.title}'


class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='coupons')
    discount_percentage = models.PositiveIntegerField()
    max_uses = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    @property
    def is_available(self):
        return self.active and self.times_used < self.max_uses

    def __str__(self):
        return self.code
