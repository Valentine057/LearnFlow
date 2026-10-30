import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import InstructorProfile, SchoolOwnerProfile
from enrollments.models import Enrollment
from .models import Book, Category, Course


class BookLibraryTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media_dir.cleanup)

        user_model = get_user_model()
        self.instructor_user = user_model.objects.create_user(
            username='teacher',
            password='test-password',
        )
        self.other_instructor_user = user_model.objects.create_user(
            username='other-teacher',
            password='test-password',
        )
        self.student = user_model.objects.create_user(
            username='student',
            password='test-password',
        )
        self.owner = user_model.objects.create_user(
            username='owner',
            password='test-password',
        )
        self.instructor = InstructorProfile.objects.create(user=self.instructor_user)
        self.other_instructor = InstructorProfile.objects.create(
            user=self.other_instructor_user,
        )
        SchoolOwnerProfile.objects.create(user=self.owner, school_name='LearnFlow')
        self.category = Category.objects.create(name='Science', slug='science')
        self.course = self.create_course(
            self.instructor,
            title='Biology',
            slug='biology',
        )
        self.other_course = self.create_course(
            self.other_instructor,
            title='Chemistry',
            slug='chemistry',
        )
        self.book = self.create_book(self.course, 'Biology Basics')

    def create_course(self, instructor, *, title, slug, status=Course.Status.PUBLISHED):
        return Course.objects.create(
            instructor=instructor,
            category=self.category,
            title=title,
            slug=slug,
            description=f'Learn about {title}.',
            status=status,
        )

    def create_book(self, course, title):
        return Book.objects.create(
            course=course,
            title=title,
            file=SimpleUploadedFile(
                f'{title.lower().replace(" ", "-")}.pdf',
                b'%PDF-1.4 test book',
                content_type='application/pdf',
            ),
        )

    def test_owner_can_add_and_edit_books_from_library(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('book_create'),
            {
                'course': self.course.id,
                'title': 'New textbook',
                'author': 'A Teacher',
                'description': 'Read alongside the lessons.',
                'file': SimpleUploadedFile('new-book.pdf', b'%PDF-1.4 new book'),
            },
        )
        self.assertRedirects(response, reverse('book_library'))
        book = Book.objects.get(title='New textbook')

        response = self.client.post(
            reverse('book_edit', args=[book.id]),
            {
                'course': self.course.id,
                'title': 'Updated textbook',
                'author': 'A Teacher',
                'description': '',
            },
        )
        self.assertRedirects(response, reverse('book_library'))
        book.refresh_from_db()
        self.assertEqual(book.title, 'Updated textbook')

    def test_instructor_can_only_manage_books_for_their_course(self):
        self.client.force_login(self.instructor_user)
        response = self.client.get(reverse('book_edit', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)

        other_book = self.create_book(self.other_course, 'Chemistry Basics')
        response = self.client.get(reverse('book_edit', args=[other_book.id]))
        self.assertEqual(response.status_code, 404)

    def test_students_must_be_paid_enrolled_to_download(self):
        self.client.force_login(self.student)
        download_url = reverse(
            'download_book',
            args=[self.course.slug, self.book.id],
        )
        self.assertEqual(self.client.get(download_url).status_code, 404)

        Enrollment.objects.create(
            student=self.student,
            course=self.course,
            payment_status=Enrollment.PaymentStatus.PAID,
        )
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Disposition'].startswith('attachment;'))
        response.close()

    def test_library_lists_books_and_gates_download_links(self):
        response = self.client.get(reverse('book_library'))
        self.assertContains(response, 'Biology Basics')
        self.assertContains(response, 'Log in to access')
        download_url = reverse('download_book', args=[self.course.slug, self.book.id])
        self.assertNotContains(response, f'href="{download_url}"')

        self.client.force_login(self.owner)
        response = self.client.get(reverse('book_library'))
        self.assertContains(response, f'href="{download_url}"')

    def test_owner_can_delete_book(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('book_delete', args=[self.book.id]))
        self.assertRedirects(response, reverse('book_library'))
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
