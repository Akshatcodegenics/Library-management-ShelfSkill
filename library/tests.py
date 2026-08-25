from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from library.models import Author, Book, Member, BorrowRecord, BorrowStatus, Category, Fine, AuditLog

User = get_user_model()


class LibraryRefactoredTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin user
        self.admin_user = User.objects.create_user(
            username='admin_test', email='admin@test.com', password='password123', role='ADMIN', is_staff=True
        )

        # Normal User
        self.normal_user = User.objects.create_user(
            username='user_test', email='user@test.com', password='password123', role='USER'
        )
        self.member = Member.objects.create(
            user=self.normal_user, name='User Test', email='user@test.com', phone='12345'
        )

        # Author
        self.author = Author.objects.create(
            name='Test Author', email='author@test.com', biography='Bio'
        )

        # Category
        self.category = Category.objects.create(
            name='Programming', slug='programming', description='Software dev'
        )

        # Book
        self.book = Book.objects.create(
            title='Architecture Fundamentals',
            isbn='111-222-333',
            author=self.author,
            category='Programming',
            total_copies=3,
            available_copies=3,
            cover_image_url='http://example.com/cover.jpg',
            rating=4.90,
            is_featured=True
        )

    def test_normal_user_cannot_access_admin_api(self):
        self.client.force_authenticate(user=self.normal_user)
        # Attempt to access audit logs
        res = self.client.get('/api/audit-logs/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_audit_logs(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get('/api/audit-logs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_can_borrow_book(self):
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.post('/api/borrow/', {'book_id': self.book.id})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

    def test_fine_generated_on_overdue_return(self):
        # Create an overdue borrowing record (due 3 days ago)
        rec = BorrowRecord.objects.create(
            book=self.book,
            member=self.member,
            due_date=timezone.now() - timedelta(days=3),
            status=BorrowStatus.BORROWED
        )
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.post(f'/api/borrow/{rec.id}/return/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Fine should be generated ($3.00)
        fine = Fine.objects.get(borrow_record=rec)
        self.assertEqual(fine.amount, 3.00)
        self.assertFalse(fine.paid_status)
